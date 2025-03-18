import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import *
from bot.voice_handler import VoiceHandler
from bot.ask_docs_bot import AskDocsBot
from bot.history_manager import HistoryManager
from bot.database import Database
from model.llm import LLM
from config import LOCAL_LLM_CONFIG
import asyncio
from pathlib import Path
import PyPDF2

# Глобальные переменные
llm = None

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загрузка переменных окружения
load_dotenv()

# Инициализация компонентов
ask_docs_bot = AskDocsBot()
voice_handler = VoiceHandler()
history_manager = HistoryManager()
database = Database()
llm = LLM()  # Инициализация LLM

# Создаем директорию для книг, если она не существует
books_dir = Path("books")
books_dir.mkdir(exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я ваш умный помощник для работы с книгами и документами.\n\n"
        "📚 Вот что я умею:\n\n"
        "1. 📝 Отвечать на вопросы по загруженным книгам\n"
        "2. 🎤 Принимать голосовые вопросы (команда /voice)\n"
        "3. 📜 Показывать историю наших диалогов (команда /history)\n"
        "4. ❓ Отвечать на вопросы о командах (команда /help)\n"
        "5. 📤 Загружать новые книги (команда /upload)\n"
        "6. 🗑 Удалять книги (команда /delete <id>)\n"
        "7. 📖 Показывать список книг (команда /books)\n"
        "8. 🔄 Изменять размер модели (команда /model <size>)\n\n"
        "💡 Просто отправьте мне вопрос, и я найду ответ в ваших книгах!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📚 *Доступные команды:*\n\n"
        "🎯 /start - Начать работу с ботом\n"
        "❓ /help - Показать это сообщение\n"
        "🎤 /voice - Ввести запрос голосом\n"
        "📜 /history - Показать историю запросов\n"
        "📤 /upload - Загрузить новую книгу\n"
        "🗑 /delete <id> - Удалить книгу по ID\n"
        "📖 /books - Показать список загруженных книг\n"
        "🔄 /model <size> - Изменить размер модели\n\n"
        "💡 Также вы можете просто отправить текстовый запрос, "
        "и я постараюсь найти релевантную информацию в базе документов."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /upload"""
    await update.message.reply_text(
        "📤 Пожалуйста, отправьте файл в формате PDF или TXT.\n\n"
        "💡 Поддерживаемые форматы:\n"
        "• PDF файлы\n"
        "• Текстовые файлы (TXT)"
    )
    context.user_data['waiting_for_file'] = True

async def books_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список загруженных книг"""
    books = database.get_all_documents()
    if not books:
        await update.message.reply_text("📚 У вас пока нет загруженных книг.\nИспользуйте команду /upload для загрузки новой книги.")
        return
    
    books_list = "📚 Загруженные книги:\n\n"
    for book in books:
        books_list += f"📖 ID: {book[0]}\n"
        books_list += f"📑 Название: {book[2] or 'Без названия'}\n"
        books_list += f"📄 Тип: {book[3] or 'Не указан'}\n"
        books_list += f"🕒 Загружено: {book[4]}\n"
        books_list += "➖➖➖➖➖➖➖➖\n\n"
    
    books_list += "\n💡 Используйте команду /delete <id> для удаления книги"
    await update.message.reply_text(books_list)

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление книги по ID"""
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите ID книги: /delete <id>")
        return
        
    try:
        book_id = int(context.args[0])
        if database.delete_document(book_id):
            await update.message.reply_text(f"✅ Книга с ID {book_id} успешно удалена.")
        else:
            await update.message.reply_text(f"❌ Книга с ID {book_id} не найдена.")
    except ValueError:
        await update.message.reply_text("❌ ID книги должен быть числом.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженных файлов"""
    if not context.user_data.get('waiting_for_file'):
        return
        
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    
    if not (file_name.endswith('.pdf') or file_name.endswith('.txt')):
        await update.message.reply_text("❌ Пожалуйста, отправьте файл в формате PDF или TXT.")
        context.user_data['waiting_for_file'] = False
        return
        
    file_path = books_dir / file_name
    await file.download_to_drive(file_path)
    
    try:
        # Обработка файла
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
            file_type = 'pdf'
        else:
            text = file_path.read_text(encoding='utf-8')
            file_type = 'txt'
            
        # Добавляем документ в базу данных
        title = file_name.rsplit('.', 1)[0]  # Имя файла без расширения
        database.add_document(
            text=text,
            title=title,
            file_type=file_type
        )
        
        await update.message.reply_text(f"✅ Книга '{title}' успешно загружена!")
        
        # Переинициализируем индекс для поиска
        ask_docs_bot.initialize_index()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при обработке файла: {str(e)}")
    finally:
        context.user_data['waiting_for_file'] = False

def extract_text_from_pdf(file_path):
    """Извлечение текста из PDF файла"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /history"""
    user_id = update.effective_user.id
    messages = history_manager.get_user_history(user_id)
    history_text = history_manager.format_history(messages)
    await update.message.reply_text(history_text)

async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /voice"""
    await update.message.reply_text(
        "🎤 Говорите...\n\n"
        "⏳ Запись начнется через 3 секунды\n"
        "💡 Говорите четко и не слишком быстро"
    )
    
    # Даем пользователю время подготовиться
    await asyncio.sleep(3)
    
    try:
        # Записываем и обрабатываем голосовую команду
        text = voice_handler.process_voice_command(duration=10)
        
        if text:
            user_id = update.effective_user.id
            history_manager.add_message(user_id, text)
            
            await update.message.reply_text(f"🎯 Распознанный текст:\n{text}")
            # Обрабатываем распознанный текст как обычный запрос
            response = await ask_docs_bot.process_query(text)
            history_manager.add_message(user_id, response, is_bot=True)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(
                "❌ Не удалось распознать речь.\n\n"
                "💡 Попробуйте:\n"
                "• Говорить четче\n"
                "• Уменьшить фоновый шум\n"
                "• Попробовать еще раз"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Произошла ошибка при обработке голосовой команды: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Сохраняем сообщение пользователя
    history_manager.add_message(user_id, message_text)
    
    # Отправляем сообщение о начале обработки
    processing_message = await update.message.reply_text("🔍 Ищу ответ на ваш вопрос...")
    
    # Обрабатываем запрос
    response = await ask_docs_bot.process_query(message_text)
    
    # Сохраняем ответ бота
    history_manager.add_message(user_id, response, is_bot=True)
    
    # Удаляем сообщение о обработке
    await processing_message.delete()
    
    # Отправляем ответ
    await update.message.reply_text(response)

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command to change model size"""
    global llm  # Теперь это объявление корректно
    
    if not context.args:
        # Show current model info
        model_info = llm.get_model_info()
        message = f"Current model:\n"
        message += f"Type: {model_info['type']}\n"
        message += f"Model: {model_info['model']}\n"
        if model_info['type'] == 'local':
            message += f"Size: {model_info['size']}\n"
        message += f"Description: {model_info['description']}\n\n"
        message += "Available sizes for local model:\n"
        for size, config in LOCAL_LLM_CONFIG.items():
            message += f"- {size}: {config['description']}\n"
        message += "\nTo change model size, use: /model <size>"
        await update.message.reply_text(message)
        return

    size = context.args[0].lower()
    if size not in LOCAL_LLM_CONFIG:
        await update.message.reply_text(
            f"Invalid model size. Available sizes: {', '.join(LOCAL_LLM_CONFIG.keys())}"
        )
        return

    llm = LLM(model_size=size)
    await update.message.reply_text(f"Model changed to {size} size!")

def main():
    """Основная функция запуска бота"""
    # Получаем токен бота из переменных окружения
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("voice", voice_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("upload", upload_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("books", books_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Бот остановлен...")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise

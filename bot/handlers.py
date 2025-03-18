from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from model.pipeline import Pipeline
from model.database import Database
from .config import Config
import os
from pathlib import Path
import PyPDF2
import io
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, config: Config):
        self.config = config
        self.pipeline = Pipeline(
            embedding_model=config.EMBEDDING_MODEL,
            llm_model=config.LLM_MODEL,
            top_k=config.TOP_K
        )
        self.database = Database(config.DATABASE_URL)
        self.books_dir = Path(config.BOOKS_DIR)
        self.books_dir.mkdir(exist_ok=True)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для работы с документами. Используйте /help для получения справки."
        )
        
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/voice - Ввести запрос голосом\n"
            "/history - Показать историю запросов"
        )
        await update.message.reply_text(help_text)

    async def upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /upload"""
        await update.message.reply_text(
            "Пожалуйста, отправьте файл в формате PDF или TXT."
        )
        context.user_data['waiting_for_file'] = True

    async def books(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список загруженных книг"""
        books = self.database.get_all_books()
        if not books:
            await update.message.reply_text("У вас пока нет загруженных книг.")
            return
        
        books_list = "Загруженные книги:\n\n"
        for book in books:
            books_list += f"ID: {book.id}\n"
            books_list += f"Название: {book.title}\n"
            books_list += f"Тип: {book.file_type.upper()}\n"
            books_list += f"Загружено: {book.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
            if book.description:
                books_list += f"Описание: {book.description}\n"
            books_list += "\n"
        
        await update.message.reply_text(books_list)
        
    async def delete_book(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление книги по ID"""
        try:
            book_id = int(context.args[0])
            if self.database.delete_book(book_id):
                await update.message.reply_text(f"Книга с ID {book_id} успешно удалена.")
            else:
                await update.message.reply_text(f"Книга с ID {book_id} не найдена.")
        except (IndexError, ValueError):
            await update.message.reply_text("Пожалуйста, укажите ID книги: /delete <id>")
        
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик загруженных файлов"""
        if not context.user_data.get('waiting_for_file'):
            return
            
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
        
        if not (file_name.endswith('.pdf') or file_name.endswith('.txt')):
            await update.message.reply_text("Пожалуйста, отправьте файл в формате PDF или TXT.")
            return
            
        file_path = self.books_dir / file_name
        await file.download_to_drive(file_path)
        
        # Обработка файла
        if file_name.endswith('.pdf'):
            text = self._extract_text_from_pdf(file_path)
            file_type = 'pdf'
        else:
            text = file_path.read_text(encoding='utf-8')
            file_type = 'txt'
            
        # Добавляем документ в пайплайн
        self.pipeline.add_document(text, file_name)
        
        # Добавляем книгу в базу данных
        title = file_name.rsplit('.', 1)[0]  # Имя файла без расширения
        self.database.add_book(
            title=title,
            filename=file_name,
            file_path=str(file_path),
            file_type=file_type
        )
        
        await update.message.reply_text(f"Книга '{title}' успешно загружена и обработана!")
        context.user_data['waiting_for_file'] = False
        
    def _extract_text_from_pdf(self, file_path):
        """Извлечение текста из PDF файла"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        await update.message.reply_text(
            "Извините, я не могу обработать это сообщение. Используйте /help для получения справки."
        )
        
    def get_handlers(self):
        """Возвращает список обработчиков команд"""
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("upload", self.upload),
            CommandHandler("books", self.books),
            CommandHandler("delete", self.delete_book),
            MessageHandler(filters.Document.ALL, self.handle_file),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        ] 
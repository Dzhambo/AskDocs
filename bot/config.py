import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Токен Telegram бота
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # OpenAI API ключ
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # URL базы данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books.db')
    
    # Директория для хранения книг
    BOOKS_DIR = os.getenv('BOOKS_DIR', 'books')
    
    # Модель для эмбеддингов
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')
    
    # Модель для генерации ответов
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    # Количество ближайших документов для поиска
    TOP_K = int(os.getenv('TOP_K', '3'))
    
    # Использовать локальную модель
    USE_LOCAL_MODEL = not bool(OPENAI_API_KEY)
    
    def __init__(self):
        # Проверяем наличие обязательных переменных
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
            
        # Создаем директорию для книг, если она не существует
        Path(self.BOOKS_DIR).mkdir(exist_ok=True) 
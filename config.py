import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# OpenAI API Key (optional)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books.db')

# Директория для хранения книг
BOOKS_DIR = os.getenv('BOOKS_DIR', 'books')

# Модель для эмбеддингов
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')

# Количество ближайших документов для поиска
TOP_K = int(os.getenv('TOP_K', '3'))

# Local LLM Configuration
LOCAL_LLM_CONFIG = {
    'small': {
        'model_name': 't5-small',
        'max_length': 512,
        'temperature': 0.7,
        'top_p': 0.9,
        'description': 'Fast but less accurate'
    },
    'medium': {
        'model_name': 't5-base',
        'max_length': 512,
        'temperature': 0.7,
        'top_p': 0.9,
        'description': 'Balanced performance'
    },
    'large': {
        'model_name': 't5-large',
        'max_length': 512,
        'temperature': 0.7,
        'top_p': 0.9,
        'description': 'More accurate but slower'
    }
}

# Default model size
DEFAULT_MODEL_SIZE = 'medium'

# Model type (openai or local)
MODEL_TYPE = 'local' if not OPENAI_API_KEY else 'openai'

# Проверяем наличие обязательных переменных
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

# Создаем директорию для книг, если она не существует
Path(BOOKS_DIR).mkdir(exist_ok=True) 
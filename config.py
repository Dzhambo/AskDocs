import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# OpenAI API Key (optional)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books.db')

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
from datetime import datetime
from typing import List, Dict
import json
import os

class HistoryManager:
    def __init__(self, history_file: str = "chat_history.json"):
        self.history_file = history_file
        self.history: Dict[int, List[Dict]] = {}  # user_id -> list of messages
        self.load_history()

    def load_history(self):
        """Загружает историю из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = {}
        else:
            self.history = {}

    def save_history(self):
        """Сохраняет историю в файл"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_message(self, user_id: int, message: str, is_bot: bool = False):
        """Добавляет сообщение в историю"""
        if user_id not in self.history:
            self.history[user_id] = []
        
        self.history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "is_bot": is_bot
        })
        self.save_history()

    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получает историю сообщений пользователя"""
        if user_id not in self.history:
            return []
        return self.history[user_id][-limit:]

    def format_history(self, messages: List[Dict]) -> str:
        """Форматирует историю сообщений для вывода"""
        if not messages:
            return "История пуста"
        
        result = "📜 История последних сообщений:\n\n"
        for msg in messages:
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%d.%m.%Y %H:%M")
            prefix = "🤖" if msg["is_bot"] else "👤"
            result += f"{prefix} {timestamp}\n{msg['message']}\n\n"
        return result 
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="books.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем таблицу для документов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                title TEXT,
                file_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_document(self, text: str, title: str = None, file_type: str = None):
        """Добавление нового документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO documents (text, title, file_type) VALUES (?, ?, ?)",
            (text, title, file_type)
        )

        conn.commit()
        conn.close()

    def get_all_documents(self):
        """Получение всех документов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents")
        documents = cursor.fetchall()

        conn.close()
        return documents

    def delete_document(self, doc_id: int):
        """Удаление документа по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0 
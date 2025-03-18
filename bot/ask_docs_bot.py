from typing import Optional
import asyncio
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sqlite3
import os
from llm import LLM

class AskDocsBot:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.texts = []
        self.db_path = "books.db"
        self.llm = LLM()
        self.initialize_index()

    def initialize_index(self):
        """Инициализирует индекс FAISS и загружает тексты из базы данных"""
        if not os.path.exists(self.db_path):
            print(f"База данных {self.db_path} не найдена")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем все тексты из базы данных
        cursor.execute("SELECT text FROM documents")
        self.texts = [row[0] for row in cursor.fetchall()]
        
        if not self.texts:
            print("База данных пуста")
            return

        # Создаем эмбеддинги для всех текстов
        embeddings = self.model.encode(self.texts)
        
        # Создаем и настраиваем индекс FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        conn.close()

    async def process_query(self, query: str) -> str:
        """Обрабатывает запрос пользователя"""
        if not self.index or not self.texts:
            return "Извините, база данных документов пуста или не инициализирована."

        # Создаем эмбеддинг для запроса
        query_embedding = self.model.encode([query])[0]
        
        # Ищем ближайшие документы
        k = 3  # количество ближайших документов
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            k
        )
        
        # Собираем контекст из найденных документов
        context = "\n\n".join([self.texts[idx] for idx in indices[0] if idx < len(self.texts)])
        
        # Генерируем ответ с помощью LLM
        try:
            response = self.llm.generate_response(query, context)
            return response
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа. Попробуйте позже." 
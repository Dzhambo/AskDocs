import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity

class Retriever:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self.documents = []
        self.embeddings = None
        
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        """Добавление документов и их эмбеддингов"""
        self.documents.extend(documents)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            
    def retrieve(self, query_embedding: np.ndarray) -> List[Dict[str, Any]]:
        """Поиск наиболее релевантных документов"""
        if not self.documents or self.embeddings is None:
            return []
            
        # Вычисляем косинусное сходство
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Получаем индексы top_k наиболее релевантных документов
        top_indices = np.argsort(similarities)[-self.top_k:][::-1]
        
        # Возвращаем документы
        return [self.documents[i] for i in top_indices] 
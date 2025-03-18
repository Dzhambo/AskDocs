from typing import List, Dict, Any
from .embeddings import Embeddings
from .retriever import Retriever
from .llm import LLM

class Pipeline:
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-3.5-turbo",
        top_k: int = 3
    ):
        self.embeddings = Embeddings(model_name=embedding_model)
        self.retriever = Retriever(top_k=top_k)
        self.llm = LLM(model_name=llm_model)
        
    def add_document(self, text: str, filename: str):
        """Добавление нового документа в пайплайн"""
        # Разбиваем текст на чанки
        chunks = self._split_text(text)
        
        # Создаем документы
        documents = [
            {
                "content": chunk,
                "source": filename,
                "chunk_id": i
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Получаем эмбеддинги для чанков
        chunk_embeddings = self.embeddings.get_embeddings_batch(chunks)
        
        # Добавляем документы и их эмбеддинги в retriever
        self.retriever.add_documents(documents, chunk_embeddings)
        
    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Разбиение текста на чанки"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
        
    def _get_docs(self, query: str) -> List[Dict[str, Any]]:
        """Получение релевантных документов"""
        query_embedding = self.embeddings.get_embedding(query)
        docs = self.retriever.retrieve(query_embedding)
        return docs
    
    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        """Форматирование контекста для LLM"""
        context = "\n\n".join([doc["content"] for doc in docs])
        return context
    
    def run(self, query: str) -> str:
        """Запуск полного пайплайна"""
        # Получаем релевантные документы
        docs = self._get_docs(query)
        
        # Форматируем контекст
        context = self._format_context(docs)
        
        # Генерируем ответ с помощью LLM
        response = self.llm.generate(query, context)
        
        return response 
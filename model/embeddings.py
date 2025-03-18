from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

class Embeddings:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """Получение эмбеддинга для текста"""
        if isinstance(text, str):
            text = [text]
        return self.model.encode(text)
    
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Получение эмбеддингов для батча текстов"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.get_embedding(batch)
            embeddings.append(batch_embeddings)
        return np.vstack(embeddings) 
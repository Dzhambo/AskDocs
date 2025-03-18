from openai import OpenAI
from typing import Optional
import os
from dotenv import load_dotenv
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Загружаем переменные окружения
load_dotenv()

class LLM:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.model_name = model_name
        
        # Инициализируем открытую модель, если ключ OpenAI недоступен
        if not self.openai_api_key:
            print("⚠️ OpenAI API ключ не найден, используется открытая модель")
            self.openai_client = None
            self.tokenizer = AutoTokenizer.from_pretrained("t5-base")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
        else:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.tokenizer = None
            self.model = None
        
    def generate(self, query: str, context: str) -> str:
        """Генерация ответа на основе запроса и контекста"""
        prompt = f"""На основе следующего контекста ответьте на вопрос. 
        Если в контексте нет информации для ответа, так и скажите.

        Контекст:
        {context}

        Вопрос: {query}

        Ответ:"""
        
        try:
            if self.openai_client:
                # Используем OpenAI
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Вы - помощник, который отвечает на вопросы о книгах на основе предоставленного контекста."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content
            else:
                # Используем открытую модель
                inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
                if torch.cuda.is_available():
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Извлекаем только ответ из полного текста
                response = response.split("Ответ:")[-1].strip()
                return response
                
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            raise 
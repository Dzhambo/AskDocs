from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from config import MODEL_TYPE, OPENAI_API_KEY, LOCAL_LLM_CONFIG, DEFAULT_MODEL_SIZE

class LLM:
    def __init__(self, model_size=DEFAULT_MODEL_SIZE):
        self.model_type = MODEL_TYPE
        self.model_size = model_size
        
        if self.model_type == 'openai':
            import openai
            openai.api_key = OPENAI_API_KEY
        else:
            self._load_local_model()
    
    def _load_local_model(self):
        """Load local model based on selected size"""
        config = LOCAL_LLM_CONFIG[self.model_size]
        self.model_name = config['model_name']
        self.max_length = config['max_length']
        self.temperature = config['temperature']
        self.top_p = config['top_p']
        
        print(f"Loading {self.model_name} model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        if torch.cuda.is_available():
            self.model = self.model.to('cuda')
        elif torch.backends.mps.is_available():
            self.model = self.model.to('mps')
    
    def generate_response(self, prompt, context=None):
        if self.model_type == 'openai':
            return self._generate_openai_response(prompt, context)
        else:
            return self._generate_local_response(prompt, context)
    
    def _generate_openai_response(self, prompt, context=None):
        import openai
        
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def _generate_local_response(self, prompt, context=None):
        if context:
            prompt = f"Context: {context}\nQuestion: {prompt}"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=self.max_length, truncation=True)
        
        if torch.cuda.is_available():
            inputs = inputs.to('cuda')
        elif torch.backends.mps.is_available():
            inputs = inputs.to('mps')
        
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            temperature=self.temperature,
            top_p=self.top_p,
            num_return_sequences=1,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def get_model_info(self):
        """Get information about current model"""
        if self.model_type == 'openai':
            return {
                'type': 'openai',
                'model': 'gpt-3.5-turbo',
                'description': 'OpenAI GPT-3.5 Turbo model'
            }
        else:
            config = LOCAL_LLM_CONFIG[self.model_size]
            return {
                'type': 'local',
                'model': config['model_name'],
                'size': self.model_size,
                'description': config['description']
            } 
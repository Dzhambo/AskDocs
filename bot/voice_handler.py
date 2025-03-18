import sounddevice as sd
import numpy as np
import whisper
import tempfile
import os
from scipy.io import wavfile

class VoiceHandler:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.sample_rate = 16000
        self.channels = 1
        
    def record_audio(self, duration=5):
        """Записывает аудио с микрофона"""
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32
        )
        sd.wait()
        return recording
    
    def save_audio(self, recording, filename):
        """Сохраняет аудио во временный файл"""
        wavfile.write(filename, self.sample_rate, recording)
    
    def transcribe_audio(self, audio_path):
        """Транскрибирует аудио файл в текст"""
        result = self.model.transcribe(audio_path)
        return result["text"].strip()
    
    def process_voice_command(self, duration=5):
        """Записывает голосовую команду и возвращает её текстовую версию"""
        # Создаем временный файл для записи
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Записываем аудио
            recording = self.record_audio(duration)
            self.save_audio(recording, temp_path)
            
            # Транскрибируем аудио в текст
            text = self.transcribe_audio(temp_path)
            return text
        finally:
            # Удаляем временный файл
            os.unlink(temp_path) 
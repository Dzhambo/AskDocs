from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf или txt
    description = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def add_book(self, title: str, filename: str, file_path: str, file_type: str, description: str = None) -> Book:
        """Добавление новой книги в базу данных"""
        book = Book(
            title=title,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            description=description
        )
        self.session.add(book)
        self.session.commit()
        return book
        
    def get_book(self, book_id: int) -> Book:
        """Получение книги по ID"""
        return self.session.query(Book).filter(Book.id == book_id).first()
        
    def get_all_books(self) -> list[Book]:
        """Получение списка всех книг"""
        return self.session.query(Book).all()
        
    def delete_book(self, book_id: int) -> bool:
        """Удаление книги по ID"""
        book = self.get_book(book_id)
        if book:
            self.session.delete(book)
            self.session.commit()
            return True
        return False
        
    def __del__(self):
        """Закрытие сессии при удалении объекта"""
        self.session.close() 
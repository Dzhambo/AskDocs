# AskDocs
📖 RAG-powered QA System for Books & Articles
This repository contains a Retrieval-Augmented Generation (RAG) application that enables users to ask questions about books, research papers, and various documents. The system retrieves relevant excerpts and generates accurate responses, providing a powerful AI-driven knowledge assistant.

✨ Features:
Advanced Retrieval: Finds relevant passages from books, articles, and documents.
AI-powered Responses: Uses generative models to answer questions concisely and accurately.
Multi-source Support: Works with PDFs, text files, and structured data.
Efficient Processing: Optimized for real-time question-answering with minimal latency.
Easy Integration: API support for seamless embedding into other applications.

## Features

- Upload books in PDF and TXT formats
- Ask questions about uploaded books
- View list of uploaded books
- Delete books from the library
- Powered by RAG (Retrieval-Augmented Generation)
- Uses OpenAI's GPT models for question answering
- Efficient document retrieval with embeddings

## Requirements

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Dzhambo/AskDocs.git
cd AskDocs
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in the project root and add your tokens:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///books.db
```

## Usage

1. Start the bot:
```bash
python main.py
```

2. In Telegram, start a chat with your bot and use the following commands:
- `/start` - Start the bot
- `/help` - Show available commands
- `/upload` - Upload a new book (PDF or TXT)
- `/books` - List all uploaded books
- `/delete <id>` - Delete a book by ID

3. Ask questions about your books by simply sending text messages to the bot.

## Project Structure

```
BookOracle/
├── bot/
│   ├── handlers.py    # Telegram bot command handlers
│   └── config.py      # Configuration settings
├── model/
│   ├── pipeline.py    # Main RAG pipeline
│   ├── embeddings.py  # Text embeddings
│   ├── retriever.py   # Document retrieval
│   ├── llm.py         # Language model interface
│   └── database.py    # Database operations
├── books/             # Directory for uploaded books
├── main.py           # Bot entry point
├── requirements.txt  # Python dependencies
└── .env             # Environment variables
```

## Storage

- Books are stored in the `books/` directory
- Book metadata is stored in SQLite database (`books.db`)
- Each book entry contains:
  - Title
  - Filename
  - File path
  - File type (PDF/TXT)
  - Upload date
  - Optional description

## AskDocs - Telegram Bot for Document Processing

A bot for uploading and analyzing documents using RAG (Retrieval-Augmented Generation) and LLM.

## Features

- 📚 Document upload (PDF, TXT)
- 🔍 Semantic document search
- 🤖 Question answering using RAG and LLM
- 🎤 Voice input support
- 📝 Query history
- 📱 User-friendly Telegram interface

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/askdocs.git
cd askdocs
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key  # Optional
```

### 4. Running the Bot

#### Local Run
```bash
python main.py
```

#### Docker Run
1. Make sure you have Docker and Docker Compose installed
2. Build and run the container:
```bash
docker compose up --build
```

For running in background:
```bash
docker compose up -d --build
```

To stop the bot:
```bash
docker compose down
```

## Usage

1. Open Telegram and find your bot
2. Send `/start` command to begin
3. Use `/upload` command to upload documents
4. Ask questions via text or voice
5. Use `/history` to view query history
6. Use `/help` for assistance

## Project Structure

```
askdocs/
├── main.py              # Main bot file
├── config.py           # Configuration
├── database.py         # Database operations
├── llm.py             # Language model integration
├── rag.py             # RAG implementation
├── voice_handler.py   # Voice message processing
├── history_manager.py # Query history management
├── requirements.txt   # Project dependencies
├── Dockerfile        # Docker configuration
├── docker-compose.yml # Docker Compose configuration
└── .env              # Environment variables
```

## Requirements

- Python 3.12+
- Docker and Docker Compose (for containerized deployment)
- Internet access for Telegram API and models

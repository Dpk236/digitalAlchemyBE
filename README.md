# AskDoubt - AI-Powered Doubt Resolution System

AskDoubt is a retrieval-augmented generation (RAG) platform designed to help students resolve doubts using their video lectures and study materials (PDFs). It uses advanced embeddings and vector search to provide context-aware answers and study aids.

## 🚀 Key Features

- **Real-time AI Chat**: Instant answers to student queries via Socket.IO.
- **Video Transcript Ingestion**: Process video transcripts (JSON/VTT) and index them for semantic search.
- **Multimodal PDF Ingestion**: Process PDF pages as images and text using vision-language models (Qwen VL).
- **AI-Generated Study Aids**:
  - **Hierarchical Summaries**: Multi-level video summaries.
  - **Interactive Quizzes**: Auto-generated practice questions.
  - **Visual Views**: HTML-based visual representations of concepts.
  - **Flashcards**: Quick-review cards for key concepts.
- **Advanced Query Routing**: Smart detection of user intent to provide the most relevant response type.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Socket.IO, Eventlet
- **Vector Database**: Qdrant
- **LLM / Embeddings**:
  - OpenAI (GPT models & Embeddings)
  - Google Generative AI (Gemini)
  - Sentence Transformers (`all-MiniLM-L6-v2`)
  - Qwen VL (Vision-Language embeddings)
- **Infrastructure**: Docker Compose

## 📁 Directory Structure

- `main.py`: Main Socket.IO and Flask server entry point.
- `VideoEmbedding/`: Logic for ingesting and retrieving video transcript data.
- `PDFEmbedding/`: Logic for processing and indexing PDF documents.
- `Retrieval/`: Specialized retrieval components.
- `LLMQueries/`: Prompts and logic for generating specific AI responses (quiz, flashcards, etc.).
- `Services/`: Core business logic and shared utilities.
- `store/`: Chat history and metadata storage handlers.
- `Helpers/`: Utility functions for chat history, JSON parsing, etc.

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Docker & Docker Compose

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Vector Database
```bash
docker-compose up -d
```

### 4. Configuration
Create a `.env` file in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
# Other configuration items
```

## 📖 Usage

### Running the Server
```bash
python main.py
```

### Data Ingestion
To index video transcripts:
```bash
python VideoEmbedding/ingest_video.py
```
To index PDFs:
```bash
python PDFEmbedding/ingest_data.py
```

## 📄 License
[Include License Information Here]

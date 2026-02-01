# AskDoubt Project Summary

## Overview
**AskDoubt** is an AI-powered retrieval-augmented generation (RAG) platform designed to assist students by resolving doubts using video lectures and PDF study materials. It leverages advanced embeddings, vector search (Qdrant), and Large Language Models (LLMs) to provide context-aware answers, summaries, quizzes, and flashcards.

## Architecture
The application is built as a real-time web service using **Flask** and **Socket.IO**.

### High-Level Data Flow
1.  **Ingestion:**
    *   **Videos:** Transcripts (VTT/JSON) are processed, chunked semantically, and embedded into a Vector DB.
    *   **PDFs:** Documents are processed (likely using OCR/Vision models) and indexed.
2.  **Interaction:**
    *   Users connect via a Socket.IO client.
    *   Queries are sent to the server.
    *   **Intent Detection:** The system (`route_query.py`) analyzes the user's query to determine intent (e.g., General Question, Quiz Request, Video Summary, Timestamp lookup).
3.  **Processing:**
    *   Based on intent, the request is routed to specific handlers (`Retrieval/`, `Services/`).
    *   **Context Retrieval:** Replaces simple keyword search with semantic search over the vector database to find relevant video segments or PDF sections.
    *   **LLM Generation:** Retrieved context is fed into an LLM (OpenAI, Gemini) to generate a natural language response.
4.  **Response:**
    *   The AI response (text, quiz JSON, html view) is sent back to the client via Socket.IO events.

## Key Features
*   **Real-time AI Chat:** Instant doubt resolution via robust Socket.IO handling.
*   **Multi-Modal RAG:** Supports both Video transcripts and PDF documents as knowledge sources.
*   **Smart Query Routing:** Distinguishes between simple questions, requests for quizzes, summary requests, and specific timestamp lookups.
*   **Study Aids:**
    *   **Hierarchical Summaries:** Generates multi-level summaries of video content.
    *   **AI Quizzes:** Automatically creates quizzes based on the content.
    *   **Flashcards:** Generates review cards.
    *   **Visual Views:** Creates HTML-based visual explanations.

## Tech Stack
*   **Backend:** Python, Flask, Socket.IO, Eventlet
*   **Database:** Qdrant (Vector Database), Redis (likely for caching/session store, implied by `Helpers.RedisKey`)
*   **AI Models:**
    *   **LLMs:** OpenAI (GPT-4/3.5), Google Gemini
    *   **Embeddings:** OpenAI Embeddings, Sentence Transformers (`all-MiniLM-L6-v2`)
    *   **Vision:** Qwen VL (for PDF/Image understanding)
*   **Infrastructure:** Docker Compose

## Key Directories & Files
*   **`main.py`**: Entry point for the Flask-SocketIO server. Handles connection lifecycle and HTTP endpoints for specific resources (quizzes, summaries).
*   **`ask_doubt.py`**: Script handling video transcript chunking and vector database ingestion.
*   **`route_query.py`**: Central logic for dispatching user queries to the correct handler based on detected intent.
*   **`VideoEmbedding/` & `PDFEmbedding/`**: Scripts and logic for ingesting raw data into Qdrant.
*   **`Retrieval/`**: Contains specialized logic for different query types (e.g., `QuizGeneration`, `SummarizeQuery`, `TimestampQuery`).
*   **`Services/`**: Shared services for Embeddings, LLM interaction, and other core business logic.
*   **`LLMQueries/`**: Stores prompt templates or specific query construction logic.
*   **`Context/`**: Manages session context (video ID, user ID).

## Setup
1.  **Dependencies:** `pip install -r requirements.txt`
2.  **Environment:** Requires `.env` with API keys (OpenAI, Google).
3.  **Vector DB:** Run Qdrant via `docker-compose up -d`.
4.  **Ingest:** Run ingestion scripts in `VideoEmbedding/` or `PDFEmbedding/`.
5.  **Run:** `python main.py`

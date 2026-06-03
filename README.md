<h1 align="center">🚀 Full Stack RAG Application</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=black&labelColor=white&color=FFD43B" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=black&labelColor=white&color=009688" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=black&labelColor=white&color=4169E1" />
  <img src="https://img.shields.io/badge/pgvector-234452?style=for-the-badge&logoColor=black&labelColor=white&color=336791" />
  <img src="https://img.shields.io/badge/Google%20Gemini-234452?style=for-the-badge&logo=Google&logoColor=black&labelColor=white&color=4285F4" />
  <img src="https://img.shields.io/badge/Cohere-234452?style=for-the-badge&logoColor=black&labelColor=white&color=D4AF37" />
  <img src="https://img.shields.io/badge/Groq-234452?style=for-the-badge&logoColor=black&labelColor=white&color=f4a852" />
  <img src="https://img.shields.io/badge/FAISS-234452?style=for-the-badge&logoColor=black&labelColor=white&color=00BFFF" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=black&labelColor=white&color=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=TypeScript&logoColor=black&labelColor=white&color=3178C6" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=for-the-badge&logo=TailwindCSS&logoColor=black&labelColor=white&color=06B6D4" />
</p>

<h3 align="center">End-to-End RAG Application: "Intelligent Document Question-Answering System"</h3>
<h3 align="center">Production-Ready Retrieval-Augmented Generation with FastAPI</h3>

<br>

# 🚀 Live Application
🌐 The application is deployed and live

👉 [Access the web app here](https://rag-frontend-b75n.onrender.com/)

> [!NOTE]
> The initial load of the web app may take 1-2 minutes. Once loaded, refresh the page to ensure all features work correctly.

> [!TIP]
> For the best experience, please refer to the [Usage Guide](#-usage-guide) section below to learn how to navigate and use the web app effectively.

<br>

# 📌 Overview

This project is a **full-stack Retrieval-Augmented Generation (RAG) application** that enables users to upload and query documents, retrieve semantically relevant context, and generate grounded answers using Large Language Models. Built with **FastAPI, PostgreSQL + pgvector, FAISS, Google Gemini Embeddings, Cohere Reranker, and Groq & Gemini LLMs**.

The application combines Semantic Search, Vector Databases, Cross-Encoder Reranking, LLM-Based Answer Generation, and a Modern React Frontend to deliver accurate and explainable answers from custom document collections.

<br>

# 🎯 Project Overview

### 1. Multi-Format Document Support
- Supports ingestion of **PDF, Markdown, and Plain Text** documents
- Each document type has a dedicated cleaning pipeline for high-quality preprocessing

### 2. Intelligent Document Preprocessing
- **PDF Cleaning**: Removes headers/footers, website artifacts, OCR-style word fragmentation, image placeholders, and normalizes whitespace
- **Markdown Cleaning**: Removes navigation sections and Mermaid diagrams, converts markdown links to clean text, preserves document hierarchy, and repairs broken tables
- **Text Cleaning**: Removes citation markers, repairs paragraph flow, normalizes whitespace, and handles formatting artifacts

### 3. Metadata-Aware Chunking
- Implemented markdown header-aware splitting with recursive character chunking
- Configurable chunk size and overlap with section preservation
- Deterministic chunk IDs with rich metadata stored per chunk including source file, file type, page number, section name, chunk index, and parent document ID

### 4. Embedding Generation
- Leveraged **Google Gemini Embeddings** (`gemini-embedding-001`) for vector embeddings
- Supports document and query embeddings with batch processing
- Includes free-tier rate-limit protection with automatic throttling

### 5. Vector Storage with PostgreSQL + pgvector
- Persistent knowledge base backed by **PostgreSQL** with the **pgvector** extension
- Stores chunk text, embeddings, and source metadata
- Supports similarity search, metadata filtering, and persistent storage

### 6. Advanced Retrieval Pipeline
- Two-stage retrieval: pgvector similarity search followed by **Cohere Cross-Encoder Reranking** (`rerank-v3.5`)
- Reranking improves precision, reduces irrelevant chunks, and raises overall answer quality

### 7. LLM Answer Generation
- Integrated **Llama 3.3 70B Versatile** via **Groq** for fast, grounded answer generation
- The model only answers from retrieved context, cites sources, reduces hallucinations, and returns explainable responses

### 8. Session-Based Document Chat
- Users can upload documents at runtime; these are chunked, embedded, and indexed in **FAISS** without modifying the global database
- Provides temporary workspaces with fast retrieval and session isolation

### 9. Modern React Frontend
- Built with **React, TypeScript, Vite, and Tailwind CSS**
- Features a chat interface, source chunk viewer, session uploads, responsive design, and real-time API integration

<br>

# 🚀 Features
- **Multi-Format Ingestion**: Upload and query **PDF, Markdown, and Text** documents seamlessly
- **Intelligent Preprocessing**: Dedicated cleaning pipelines per document type for high-quality chunking
- **Semantic Search**: Dense vector retrieval using **Google Gemini Embeddings** and **pgvector**
- **Cross-Encoder Reranking**: Uses **Cohere rerank-v3.5** to improve retrieval precision
- **Grounded LLM Answers**: **Llama 3.3 70B** via Groq answers only from retrieved context, reducing hallucinations
- **Session-Based Chat**: Upload documents at runtime, indexed in **FAISS** without touching the global database
- **Source Transparency**: Every answer includes source chunks so users can verify the retrieved context
- **Modern Frontend**: Responsive chat UI built with **React, TypeScript, and Tailwind CSS**

<br>

# 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │ React Frontend   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ FastAPI Backend  │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                                       │
         ▼                                       ▼

 ┌─────────────────┐                 ┌─────────────────┐
 │ Global RAG      │                 │ Session RAG     │
 │ PostgreSQL      │                 │ FAISS           │
 │ + pgvector      │                 │ In-Memory Index │
 └────────┬────────┘                 └────────┬────────┘
          │                                   │
          ▼                                   ▼

    Similarity Search                 Similarity Search
          │                                   │
          ▼                                   ▼

     Cohere Reranker                  Retrieved Chunks
          │                                   |
          ▼                                   ▼

     Groq LLM Generator               Groq LLM Generator
          │                                   |
          ▼                                   ▼

      Final Answer                      Final Answer
         
```

<br>

# 🏗️ Tech Stack
- **Python**
- **FastAPI** (Backend API framework with Pydantic & Psycopg)
- **PostgreSQL + pgvector** (Persistent vector database)
- **Google Gemini Embeddings** (`gemini-embedding-001`)
- **Cohere Rerank** (`rerank-v3.5` for cross-encoder reranking)
- **FAISS** (In-memory vector index for session-based retrieval)
- **Groq API** (Accessing Llama 3.3 70B Versatile)
- **PyMuPDF4LLM + LangChain Text Splitters** (Document processing)
- **React + TypeScript + Vite** (Modern frontend)
- **Tailwind CSS** (Frontend styling)

<br>

# 📂 Project Structure

```text
fullstack-rag-application
│
├── documents/                        # Source documents used for ingestion
│   ├── markdown/                     # Markdown files (NemoClaw documentation)
│   ├── pdfs/                         # PDF files (Apple product tech specs)
│   └── text/                         # Plain text files (Space exploration articles)
│
├── frontend/                         # React + TypeScript frontend application
│   └── src/
│       ├── components/               # Reusable UI components (chat, input, source chunks)
│       ├── types/                    # TypeScript type definitions
│       ├── api.ts                    # API calls to the FastAPI backend
│       ├── App.tsx                   # Root application component
│       └── main.tsx                  # Application entry point
│
├── notebooks/                        # Jupyter notebooks for experiments and pipeline testing
│
├── src/                              # Core backend source code
│   ├── core/                         # Main RAG pipeline modules
│   │   ├── chunker.py                # Document chunking logic
│   │   ├── embedding.py              # Gemini embedding generation
│   │   ├── generator.py              # Groq LLM answer generation
│   │   ├── reranker.py               # Cohere cross-encoder reranking
│   │   ├── retriever.py              # Vector similarity retrieval
│   │   └── vector_store.py           # pgvector and FAISS store management
│   ├── loaders/                      # Document loaders for each file type (pdf, md, txt)
│   ├── preprocess/                   # Document cleaners for each file type (pdf, md, txt)
│   ├── models/                       # Pydantic data models
│   └── utils/                        # Config and path utility helpers
│
├── app.py                            # FastAPI application and route definitions
├── ingest.py                         # Document ingestion pipeline (load → clean → chunk → embed → store)
├── session_pipeline.py               # Session-based FAISS pipeline for runtime document uploads
├── golden_QA.md                      # Golden Q&A dataset for evaluation and benchmarking
├── requirements.txt                  # Python dependencies
└── pyproject.toml                    # Project metadata and build configuration
```

<br>

# 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/fullstack-rag-application.git
cd fullstack-rag-application
```

### 2️⃣ Create a Virtual Environment
```bash
conda create -p env python=3.11 -y
conda activate env
```
or
```bash
python -m venv env
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file in the root directory and add:
```env
GEMINI_API_KEY=xxxxxxxxxxxx
GROQ_API_KEY=xxxxxxxxxxxx
COHERE_API_KEY=xxxxxxxxxxxx
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db
```

### 5️⃣ Ingest Documents
```bash
python ingest.py
```

### 6️⃣ Run the Backend
```bash
uvicorn app:app --reload
```
Backend available at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### 7️⃣ Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend available at `http://localhost:5173`

<br>

# 🌐 Usage Guide

👉 [Access the web app](https://rag-frontend-b75n.onrender.com/)

- **Global Knowledge Base Chat**: Ask questions about any pre-ingested documents
    - "What is NemoClaw?"
    - "Summarize the key points from the research paper."
- **Session Document Upload**: Upload your own PDF, Markdown, or Text file and chat with it
    - "Summarize the uploaded document."
    - "What are the main conclusions?"
- **Source Verification**: Every answer displays the retrieved source chunks so you can verify context
- **API Access**:
    - Global chat: `POST /api/chat/global`
    - Session chat: `POST /api/chat/session` with `x-session-id` header
    - Upload: `POST /api/upload` with `x-session-id` header

<br>

# 🧪 Evaluation Framework

> 📂 Full Q&A pairs with expected answers are available here → [`golden_QA.md`](golden_QA.md)

A **Golden Q&A dataset** is included to benchmark and validate the RAG pipeline's retrieval and answer quality across all three supported document types — Markdown, Text, and PDF.

The dataset covers **30 primary evaluation pairs** and **5 documented failed cases**, making it suitable for both pass/fail testing and analysis.

<br>

# 📊 Retrieval Pipeline

```text
Documents Loader
    │
    ▼
Preprocessing
    │
    ▼
Chunking
    │
    ▼
Gemini Embeddings
    │
    ▼
pgvector Store
    │
    ▼
Similarity Search
    │
    ▼
Cohere Reranking
    │
    ▼
Groq LLM
    │
    ▼
Grounded Response
```

<br>

# 📡 API Endpoints

## Global Knowledge Base Chat
```http
POST /api/chat/global
```
Request:
```json
{
  "question": "What is NemoClaw?"
}
```

## Upload Documents
```http
POST /api/upload
```
Headers:
```text
x-session-id: session_123
```

## Session Chat
```http
POST /api/chat/session
```
Headers:
```text
x-session-id: session_123
```
Request:
```json
{
  "question": "Summarize the uploaded document"
}
```

<br>

# 📸 Screenshots
### Screenshot of the web application: 
<img src="readme_images/screenshot_1.png" width="950" height="550">

<br>

### Screenshot of the chat interface:
<img src="readme_images/screenshot_2.png" width="950" height="550">

<br>

# 🎯 Future Improvements
- User authentication and chat history persistence
- Hybrid search (BM25 + Dense Retrieval)
- HNSW indexing
- Multi-modal retrieval
- Citation highlighting in the UI
- Docker and Kubernetes deployment
- LangGraph agent workflows
- Evaluation framework integration (RAGAS)

<br>

# 🤝 Contributing
💡 Have an idea? Feel free to contribute or open an issue and pull requests!

<br>

# 📄 License
This project is licensed under the **MIT License** – [LICENSE](LICENSE)

<br>


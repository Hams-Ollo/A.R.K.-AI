# 🎓 Research Assistant - Bhaktivedanta Institute

A robust research assistant and intelligent semantic knowledge base repository for the academic study of consciousness, developed for the Bhaktivedanta Institute.

## ✨ Features

### 🤖 Core Capabilities

- Advanced AI-powered research assistant
- Semantic knowledge base for consciousness studies
- Intelligent document search and analysis
- Interactive chat interface with citation support
- Document management system
- Real-time processing and responses
- Academic-focused research tools

### 📚 Document Processing

- Intelligent PDF processing and text extraction
- Smart document chunking with citation preservation
- Comprehensive metadata extraction
- Page-level content tracking
- Multi-format document support

### 🔍 Search & Retrieval

- Advanced semantic search with ChromaDB
- Hybrid search capabilities (semantic + keyword)
- Metadata filtering and faceted search
- Relevance scoring and ranking
- Batch processing support

### 📝 Citation System

- Robust source verification and citation tracking
- Wikipedia-style reference management
- Page-level citation linking
- Citation export in multiple academic formats
- Source integrity verification
- Citation network visualization

### 📊 Performance & Monitoring

- Comprehensive logging system
- Performance monitoring and metrics
- Error tracking and handling
- System health monitoring
- Resource usage optimization

## 🚀 Quick Start

1. Clone the repository and create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up environment variables:
Create a `.env` file in the project root with:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=your_host
POSTGRES_PORT=your_port

# Redis Configuration
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
```

1. Run the application:

```bash
streamlit run app/frontend/Home.py
```

1. Access the application at `http://localhost:8501`

## 📁 Project Structure

```curl
research-assistant/
├── app/
│   ├── backend/
│   │   ├── agents/          # AI agents and LLM integration
│   │   ├── api/            # FastAPI endpoints
│   │   ├── processing/     # Document processing pipeline
│   │   ├── vector_store/   # Vector storage implementation
│   │   └── models.py       # Data models
│   ├── frontend/
│   │   ├── Home.py        # Main application entry
│   │   └── pages/         # Additional UI pages
│   └── utils/             # Shared utilities
├── data/                  # Data storage
│   ├── vector_store/     # ChromaDB storage
│   └── test_documents/   # Test PDFs
├── docs/                 # Documentation
├── logs/                 # Application logs
├── tests/               # Test suite
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── README.md
```

## 🛠️ Tech Stack

### Core Components

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Vector Store**: ChromaDB (with planned migration to PostgreSQL/pgvector)
- **AI/ML**: LangChain, Groq
- **Document Processing**: PyMuPDF, LangChain
- **Embeddings**: Sentence Transformers

### Dependencies

- fastapi >= 0.104.0
- streamlit >= 1.28.0
- langchain >= 0.0.350
- chromadb >= 0.4.22
- PyMuPDF >= 1.23.0
- sentence-transformers >= 2.2.2
- python-json-logger >= 2.0.7
- And more in requirements.txt

## 🔧 Development

### Setting Up Development Environment

1. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

1. Run tests:

```bash
pytest tests/
```

1. Manual testing:

```bash
python tests/manual_test.py
```

### Logging and Monitoring

The application includes comprehensive logging:

- Structured JSON logging
- Performance monitoring
- Error tracking
- Log rotation
- Component-specific logging

### Vector Store

Currently using ChromaDB for vector storage with planned migration to PostgreSQL/pgvector:

- Document storage and retrieval
- Similarity search
- Metadata filtering
- Batch processing

## 🤝 Contributing

1. Fork the repository

1. Create and switch to a new branch:

```bash
git checkout -b feature-branch
```

1. Make changes and commit:

```bash
git add .
git commit -m "Description of changes"
```

1. Push changes:

```bash
git push -u origin feature-branch
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Special thanks to the Bhaktivedanta Institute for their support and guidance in developing this research tool for consciousness studies.

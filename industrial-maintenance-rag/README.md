# 🏭 Industrial Maintenance Assistant

A **Multimodal RAG (Retrieval Augmented Generation)** system designed for the Italian manufacturing sector. This assistant allows factory workers to take photos of machine errors or components, retrieves the specific manual page (text + diagrams), and generates fix instructions in Italian or English.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/docker-required-blue.svg)

## ✨ Features

- 🌍 **Bilingual Support**: Switch between Italian and English
- 📸 **Image Analysis**: Upload photos of machine components for visual troubleshooting
- 📚 **Smart Search**: Vector-based semantic search through technical manuals
- 🤖 **AI-Powered Responses**: Context-aware answers using Ollama (Mistral/LLaVA)
- 🔒 **Privacy-First**: Local inference with Ollama - no data leaves your server
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │ ← User Interface (Italian/English)
└────────┬────────┘
         │
    ┌────▼─────────────────────────────┐
    │  RAG Pipeline                    │
    │  ┌──────────┐  ┌──────────────┐ │
    │  │ LLaVA    │  │ Mistral LLM  │ │
    │  │ (Vision) │  │ (Text Gen)   │ │
    │  └──────────┘  └──────────────┘ │
    └────────┬─────────────────────────┘
             │
    ┌────────▼────────┐
    │ Qdrant Vector DB│ ← Semantic Search
    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Docker Desktop** (for Qdrant)
- **Ollama** (for AI models)
- At least **8GB RAM** (16GB recommended for larger models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/industrial-maintenance-rag.git
   cd industrial-maintenance-rag
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama**
   
   Download and install from [ollama.com/download](https://ollama.com/download)
   
   Then pull the required models:
   ```bash
   ollama pull llava
   ollama pull mistral
   ```

4. **Start Qdrant with Docker**
   ```bash
   docker-compose up -d
   ```

5. **Ingest your manuals**
   
   Place PDF manuals in the `data_manuals/` directory, then run:
   ```bash
   python -m src.ingest_pipeline
   ```

6. **Launch the application**
   ```bash
   streamlit run app.py
   ```

The app will be available at `http://localhost:8501`

## 📖 Usage

### Text-Based Queries

1. Select **Text** mode
2. Type your maintenance question (e.g., "How do I fix the oil pressure error?")
3. Click **Search Solution**
4. View relevant manual sections and AI-generated answer

### Image-Based Queries

1. Select **Image** mode
2. Upload a photo of the machine component or error display
3. The system will analyze the image and search for relevant diagrams
4. Receive context-aware maintenance instructions

### Language Selection

Use the sidebar to switch between **Italian** and **English** - all UI elements and AI responses will adapt accordingly.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Vector DB** | Qdrant | Semantic search & storage |
| **Vision Model** | LLaVA (via Ollama) | Image understanding |
| **LLM** | Mistral (via Ollama) | Answer generation |
| **Embeddings** | SentenceTransformers | Text vectorization |
| **PDF Processing** | Unstructured | Document parsing |
| **Orchestration** | LangChain | RAG pipeline |

## 📁 Project Structure

```
industrial-maintenance-rag/
├── app.py                      # Streamlit application
├── docker-compose.yml          # Qdrant container config
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data_manuals/               # Place your PDF manuals here
│   └── manuale_fervi.pdf      # Example manual
│
├── extracted_images/           # Auto-extracted diagrams
│
├── src/
│   ├── ingest_pipeline.py     # PDF processing & indexing
│   ├── vector_db.py           # Qdrant client wrapper
│   └── vision_utils.py        # LLaVA image analysis
│
└── qdrant_storage/            # Qdrant data (auto-created)
```

## ⚙️ Configuration

### Environment Variables (Optional)

```bash
# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
```

### Model Selection

Edit `app.py` to change the default LLM model:
```python
model_name = st.selectbox("LLM Model", ["mistral", "llama3", "gemma"])
```

## 🔧 Advanced Setup

### Using Poppler for Image Extraction

To extract diagrams from PDFs, install Poppler:

**Windows:**
1. Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
2. Add to PATH

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

### Custom Embedding Models

Modify `src/vector_db.py` to use different embeddings:
```python
self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

## 🐛 Troubleshooting

### Ollama Connection Issues

If you see "Ollama unreachable":
1. Check if Ollama is running: `ollama list`
2. Restart Ollama service
3. Verify models are pulled: `ollama pull llava && ollama pull mistral`

### Qdrant Connection Failed

```bash
# Check if container is running
docker ps

# Restart Qdrant
docker-compose restart
```

### Empty Search Results

- Ensure you've run the ingestion pipeline: `python -m src.ingest_pipeline`
- Check that PDFs are in `data_manuals/` directory
- Verify Qdrant collection exists (check app logs)

## 🔒 Privacy & Compliance

This system is designed for **local inference** using Ollama. This ensures:

- ✅ Proprietary industrial schematics never leave your server
- ✅ GDPR compliant (no external data transmission)
- ✅ Suitable for sensitive manufacturing environments
- ✅ Full control over data and models

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.com/) for local LLM inference
- [Qdrant](https://qdrant.tech/) for vector search
- [Streamlit](https://streamlit.io/) for the web framework
- [LangChain](https://langchain.com/) for RAG orchestration

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for the manufacturing industry**

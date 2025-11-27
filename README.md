# 🤖 AI Chatbot with RAG & Voice

A modern, production-ready AI chatbot built with LangChain, featuring document analysis, web search, and voice capabilities.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.34+-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green)

## ✨ Features

🧠 **Multiple AI Providers**
- Groq (LLaMA models) - Fast & efficient
- Google Gemini - Advanced reasoning
- HuggingFace - Open source models
- Offline mode - Works without internet

📄 **Document Analysis (RAG)**
- Upload PDF and TXT files
- Intelligent document search
- Contextual answers from your documents
- Vector embeddings with FAISS

🌐 **Web Search Integration**
- Real-time web search with SerpAPI
- Current information retrieval
- Fact checking and research

🔊 **Voice Capabilities**
- Text-to-speech responses
- Audio output for accessibility
- Multiple language support

🎨 **Modern Interface**

## 🚀 Quick Start
# Clone repository
git clone <your-repo-url>
cd temp_chatbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements_clean.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# AI Providers (get at least one)
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  
HUGGINGFACE_API_TOKEN=your_huggingface_token_here

# Optional: Web search
SERPAPI_API_KEY=your_serpapi_key_here
```

### 3. Get API Keys

#### Groq (Recommended - Free tier)

#### Google Gemini (Free tier)
3. Excellent for complex reasoning

2. Create a read token
3. Access to open-source models

#### SerpAPI (Optional - Web search)
1. Visit [serpapi.com](https://serpapi.com)
2. Free tier includes 100 searches/month

```bash
Open your browser to `http://localhost:8501`

```bash
docker build -t ai-chatbot .
```bash
docker run --rm -p 8501:8501 --env-file .env ai-chatbot
```

Then visit: http://localhost:8501

Use a different port:
```bash
docker run --rm -p 9000:8501 --env-file .env ai-chatbot
```

## 📖 Usage Guide

### Basic Chat
1. Select your AI provider in the sidebar
2. Choose a model (LLaMA, Gemini, etc.)
3. Start chatting!

### Document Analysis
1. Click "Browse files" in the sidebar
2. Upload a PDF or TXT file
3. Ask questions about your document
4. Get contextual answers with citations

### Voice Features
1. Enable "Text-to-Speech" in settings
2. Responses will include audio playback
3. Great for accessibility and multitasking

### Offline Mode
- Works without any API keys
- Basic conversational capabilities
- Document search still available
- Perfect for privacy-sensitive environments

## 🛠️ Architecture

### Core Components
- **Streamlit**: Web interface and user experience
- **LangChain**: AI orchestration and document processing
- **FAISS**: Vector storage for document embeddings
- **Multiple LLMs**: Groq, Gemini, HuggingFace support

### Key Features
- **Smart Caching**: Responses cached for better performance
- **Error Handling**: Graceful fallbacks and clear error messages
- **Modular Design**: Easy to extend and customize
- **Production Ready**: SSL handling, logging, monitoring

## 📁 Project Structure

```
chatbot/
├── app.py                  # Main application
├── requirements_clean.txt  # Clean dependencies
├── .env                   # Configuration (create this)
├── cache/                 # Response cache
├── logs/                  # Application logs
├── uploads/               # Temporary file storage
└── README.md             # This file
```

## 🔧 Configuration Options

### Environment Variables
```env
# Required: At least one AI provider
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
HUGGINGFACE_API_TOKEN=hf_...

# Optional: Enhanced features
SERPAPI_API_KEY=...        # Web search
```

### Model Options

**Groq Models:**
- `llama3-8b-8192` - Fast, general purpose
- `mixtral-8x7b-32768` - Larger context window
- `gemma-7b-it` - Efficient instruction following

**Gemini Models:**
- `gemini-pro` - Advanced reasoning
- `gemini-pro-vision` - Image understanding

**HuggingFace Models:**
- `microsoft/DialoGPT-medium` - Conversational
- `facebook/blenderbot-400M-distill` - Lightweight

## 🚨 Troubleshooting

### Common Issues

**"No AI providers configured"**
- Add at least one API key to `.env`
- Restart the application
- Check API key format and validity

**"Connection error"** 
- Check internet connection
- Verify API keys are correct
- App will fallback to offline mode

**"Failed to process document"**
- Ensure file is PDF or TXT format
- Check file size (< 200MB recommended)
- Try a simpler document first

**SSL/Certificate errors**
- Check `CONNECTIVITY.md` for variant analysis (env vs system vs insecure)
- Remove broken override bundles; prefer system trust (especially on Windows)
- Set `ALLOW_INSECURE_SSL=true` only for diagnostics (never for production)

### Performance Tips

1. **Use caching** - Responses are automatically cached
2. **Groq for speed** - Fastest response times
3. **Limit document size** - Smaller docs process faster
4. **Clear cache periodically** - Use sidebar button

## � Architecture Assets

Generate a PowerPoint deck:
```powershell
python tools\generate_presentation.py
```
Output: `dist/AI_Chatbot_Architecture.pptx`

Generate PNG architecture diagram:
```powershell
python tools\generate_architecture_png.py
```
Output: `dist/architecture.png`

If you see an import error for `pptx`, ensure you are using the project virtual environment and installed dependencies:
```powershell
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## �🔐 Privacy & Security

- **Local processing** - Documents processed locally
- **API key security** - Stored in environment variables only
- **No data retention** - Conversations not permanently stored
- **Offline capable** - Works without internet when needed

## 🔍 Connectivity Diagnostics

See `CONNECTIVITY.md` (quick guide) and `TROUBLESHOOTING.md` (deep dive) for:
- Error classifications (ssl / timeout / proxy / dns / network)
- Variant behavior (env vs system vs insecure)
- Auto offline degrade logic
- Proxy & corporate CA remediation flow

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 📞 Support

- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub discussions
- **Email**: Contact the maintainer

---

⭐ If this project helps you, please give it a star on GitHub!

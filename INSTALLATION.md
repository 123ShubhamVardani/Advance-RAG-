# Chatbot Installation Guide

## 🚀 Quick Start (Basic Chatbot)

```bash
# Install basic chatbot only
pip install streamlit langchain langchain-groq python-dotenv gtts speechrecognition faiss-cpu

# Or use our installer
python install.py --mode basic
```

## 🔧 Development Setup

```bash
# Install development dependencies
python install.py --mode dev --setup-env

# Or manually:
pip install -r requirements-dev.txt
```

## 🏢 Enterprise Deployment

```bash
# Install all enterprise features
python install.py --mode enterprise --setup-env

# Or manually:
pip install -r requirements-enterprise.txt
```

## 📦 Installation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `basic` | Core chatbot only | POC, testing, simple deployment |
| `dev` | Basic + dev tools | Development, testing, local API |
| `enterprise` | All features | Production, scaling, enterprise |

## 🛠️ Manual Installation

### Option 1: Edit requirements.txt
Uncomment the sections you need in `requirements.txt`

### Option 2: Install specific features
```bash
# Just the chatbot
pip install streamlit langchain-groq python-dotenv

# Add databases
pip install asyncpg motor aioredis

# Add API framework  
pip install fastapi uvicorn

# Add task queue
pip install celery redis

# Add monitoring
pip install prometheus-client psutil
```

## 🔍 What Each Mode Installs

### Basic Mode (POC)
- Streamlit UI
- LangChain + Groq/Gemini
- Voice features
- Document upload
- Basic caching

### Dev Mode (Development)
- Everything in Basic
- FastAPI server
- Redis caching
- Development tools
- Testing framework

### Enterprise Mode (Production)
- Everything in Dev
- All database drivers
- Load balancing
- Task queues
- Monitoring
- Security features
- Distributed processing

## 💡 Why This Approach?

✅ **Single source of truth** - One requirements.txt file
✅ **Modular installation** - Install only what you need
✅ **Easy upgrades** - Simple dependency management
✅ **Clear documentation** - Know exactly what each mode does
✅ **Flexible deployment** - From POC to enterprise scale

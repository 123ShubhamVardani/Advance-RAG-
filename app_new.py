# 🤖 LangChain AI Chatbot - Production Ready

import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import json
import ssl
from pathlib import Path
import importlib.util

# Configure SSL for corporate environments
ssl._create_default_https_context = ssl._create_unverified_context

# LangChain imports with guarded availability checks

if importlib.util.find_spec("langchain") is not None:
    try:
        # Import core langchain components only when available; individual
        # symbols will be assigned to None if the import fails later.
        import langchain.agents as _lc_agents
        Tool = getattr(_lc_agents, 'Tool', None)
        initialize_agent = getattr(_lc_agents, 'initialize_agent', None)
        AgentType = None
        from langchain_groq import ChatGroq
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_community.utilities import SerpAPIWrapper
        from langchain_community.document_loaders import PyPDFLoader, TextLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        # RetrievalQA is optional in our code path; import via getattr to avoid
        # linter complaints when unused in some flows.
        try:
            import langchain.chains as _lc_chains
            RetrievalQA = getattr(_lc_chains, 'RetrievalQA', None)
        except Exception:
            RetrievalQA = None
        from langchain_community.llms import HuggingFaceHub
        LANGCHAIN_AVAILABLE = True
    except Exception:
        # If anything fails during import, mark as unavailable
        LANGCHAIN_AVAILABLE = False
        initialize_agent = None
        Tool = None
        AgentType = None
        ChatGroq = None
        ChatGoogleGenerativeAI = None
        SerpAPIWrapper = None
        PyPDFLoader = None
        TextLoader = None
        RecursiveCharacterTextSplitter = None
        HuggingFaceEmbeddings = None
        FAISS = None
        RetrievalQA = None
        HuggingFaceHub = None
else:
    LANGCHAIN_AVAILABLE = False
    initialize_agent = None
    Tool = None
    AgentType = None
    ChatGroq = None
    ChatGoogleGenerativeAI = None
    SerpAPIWrapper = None
    PyPDFLoader = None
    TextLoader = None
    RecursiveCharacterTextSplitter = None
    HuggingFaceEmbeddings = None
    FAISS = None
    RetrievalQA = None
    HuggingFaceHub = None

# Voice imports with graceful fallbacks
try:
    if importlib.util.find_spec("gtts") is not None:
        _gtts_module = importlib.import_module("gtts")
        gTTS = getattr(_gtts_module, "gTTS", None)
    else:
        gTTS = None
    from io import BytesIO
    VOICE_AVAILABLE = gTTS is not None and BytesIO is not None
except Exception:
    gTTS = None
    BytesIO = None
    VOICE_AVAILABLE = False

# === Configuration ===
load_dotenv()

# Create directories
CACHE_DIR = Path("cache")
LOGS_DIR = Path("logs") 
UPLOADS_DIR = Path("uploads")
for dir_path in [CACHE_DIR, LOGS_DIR, UPLOADS_DIR]:
    dir_path.mkdir(exist_ok=True)

# === API Configuration ===
class APIConfig:
    """Centralized API configuration management"""
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY") 
        self.huggingface_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
    
    @property
    def has_groq(self):
        return bool(self.groq_key and len(self.groq_key) > 10)
    
    @property 
    def has_google(self):
        return bool(self.google_key and len(self.google_key) > 10)
    
    @property
    def has_huggingface(self):
        return bool(self.huggingface_token and len(self.huggingface_token) > 10)
    
    @property
    def has_serpapi(self):
        return bool(self.serpapi_key and len(self.serpapi_key) > 10)
    
    @property
    def available_providers(self):
        providers = []
        if self.has_groq:
            providers.append("groq")
        if self.has_google:
            providers.append("gemini")
        if self.has_huggingface:
            providers.append("huggingface")
        return providers
    
    def get_status_display(self):
        """Get formatted status for sidebar"""
        status = []
        status.append(f"{'✅' if self.has_groq else '❌'} Groq: {'Connected' if self.has_groq else 'Not configured'}")
        status.append(f"{'✅' if self.has_google else '❌'} Gemini: {'Connected' if self.has_google else 'Not configured'}")
        status.append(f"{'✅' if self.has_huggingface else '❌'} HuggingFace: {'Connected' if self.has_huggingface else 'Not configured'}")
        status.append(f"{'✅' if self.has_serpapi else '❌'} Web Search: {'Available' if self.has_serpapi else 'Unavailable'}")
        return status

config = APIConfig()

# === Caching System ===
@st.cache_data(ttl=3600)
def get_cached_response(query_hash):
    """Get cached response if available"""
    cache_file = CACHE_DIR / f"response_{query_hash}.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_cached_response(query_hash, response):
    """Save response to cache"""
    cache_file = CACHE_DIR / f"response_{query_hash}.json"
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "cached": True
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Could not cache response: {e}")

# === Enhanced LLM Management ===
@st.cache_resource
def create_llm(provider, model_name=None):
    """Create LLM with comprehensive error handling"""
    if not LANGCHAIN_AVAILABLE:
        return None
        
    try:
        if provider == "groq" and config.has_groq:
            model = model_name or "llama3-8b-8192"
            if ChatGroq is None:
                st.error("Groq integration is not available (langchain_groq missing). Please install required package.")
                return None
            # Migration map for deprecated Groq model IDs
            groq_migration_map = {
                "llama3-8b-8192": "llama-3.1-8b-instant",
                "llama3-70b-8192": "llama-3.3-70b-versatile",
                "distil-whisper-large-v3-en": "whisper-large-v3-turbo",
            }
            target_model = groq_migration_map.get(model, model)
            if target_model != model:
                try:
                    st.warning(f"Model '{model}' is deprecated; using recommended replacement '{target_model}'")
                except Exception:
                    pass
                try:
                    logger.info("Migrating deprecated Groq model", from_model=model, to_model=target_model)
                except Exception:
                    pass
            # Try robust instantiation supporting different client signatures
            try:
                return ChatGroq(api_key=str(config.groq_key), model=target_model, temperature=0.7, max_tokens=2048)
            except TypeError:
                try:
                    return ChatGroq(api_key=str(config.groq_key), model_name=target_model, temperature=0.7, max_tokens=2048)
                except TypeError:
                    return ChatGroq(str(config.groq_key), target_model, temperature=0.7, max_tokens=2048)
        
        elif provider == "gemini" and config.has_google:
            model = model_name or "gemini-pro"
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=config.google_key,
                temperature=0.7
            )
        
        elif provider == "huggingface" and config.has_huggingface:
            model = model_name or "microsoft/DialoGPT-medium"
            return HuggingFaceHub(
                repo_id=model,
                huggingfacehub_api_token=config.huggingface_token,
                model_kwargs={"temperature": 0.7, "max_length": 512}
            )
        
        return None
        
    except Exception as e:
        error_msg = str(e).lower()
        if any(term in error_msg for term in ['connection', 'network', 'ssl', 'timeout']):
            st.error(f"🌐 Network issue with {provider}: Check internet connection")
        elif 'unauthorized' in error_msg or 'invalid' in error_msg:
            st.error(f"🔑 Invalid API key for {provider}: Check your credentials")
        else:
            st.error(f"❌ Error with {provider}: {e}")
        return None

# === Offline Fallback Bot ===
class OfflineBot:
    """Enhanced offline chatbot with better responses"""
    
    def __init__(self):
        self.responses = {
            'greetings': [
                "Hello! I'm running in offline mode with limited capabilities.",
                "Hi there! I'm in offline mode but I can still help with document search.",
                "Hey! I'm working offline right now but can assist with basic queries."
            ],
            'help': [
                "In offline mode, I can:\n• Search uploaded documents\n• Provide basic responses\n• Help with simple questions\n\nFor full AI capabilities, please configure your API keys.",
                "I'm in offline mode with these features:\n• Document text search\n• Basic conversation\n• File processing\n\nAdd API keys for advanced AI responses!"
            ],
            'default': [
                "I understand you're asking about that topic. I'm in offline mode with limited knowledge, but I can search any documents you've uploaded.",
                "That's an interesting question! I'm running offline, so I can't access external information, but I can help with document analysis if you upload files.",
                "I'd love to help with that! I'm in offline mode right now, but I can search through any documents you provide."
            ]
        }
    
    def invoke(self, prompt):
        """Generate contextual offline responses"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            response = self.responses['greetings'][0]
        elif any(word in prompt_lower for word in ['help', 'what can you do', 'capabilities']):
            response = self.responses['help'][0]
        else:
            response = self.responses['default'][0]
        
        return type('Response', (), {'content': response})()

# === Document Processing ===
@st.cache_resource
def process_document(_uploaded_file):
    """Enhanced document processing with better error handling

    Note: leading underscore in the parameter name tells Streamlit's cache
    machinery not to attempt hashing the uploaded file object (which can be
    unhashable). This makes the function callable programmatically (tests)
    while preserving caching behavior for other hashable parameters.
    """
    if not _uploaded_file:
        return None

    try:
        # Save file temporarily
        temp_path = UPLOADS_DIR / _uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(_uploaded_file.getbuffer())

        # Load document based on type
        if _uploaded_file.name.lower().endswith('.pdf'):
            loader = PyPDFLoader(str(temp_path))
        elif _uploaded_file.name.lower().endswith('.txt'):
            loader = TextLoader(str(temp_path), encoding='utf-8')
        else:
            temp_path.unlink()  # Delete temp file
            st.error("❌ Unsupported file type. Please upload PDF or TXT files.")
            return None

        # Load and split documents
        documents = loader.load()

    # Diagnostics: prepare debug log path (always define to avoid unbound variable)
        debug_log = LOGS_DIR / 'process_document_debug.log'
        try:
            with open(debug_log, 'a', encoding='utf-8') as dbg:
                dbg.write(f"[{datetime.now().isoformat()}] Loaded documents: {len(documents) if documents is not None else 'None'}\n")
        except Exception:
            # Don't let diagnostics break processing
            pass

        # If loader returned nothing (common for tiny text files with some loaders),
        # or loader produced documents with empty content, fall back to reading
        # the raw file contents and wrap in a Document object.
        if not documents or all((getattr(d, 'page_content', '') or '').strip() == '' for d in documents):
            try:
                with open(temp_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()

                # Prefer LangChain's Document type when available for compatibility
                try:
                    from langchain.schema import Document as LangChainDocument
                except Exception:
                    LangChainDocument = None

                if LangChainDocument is not None:
                    documents = [LangChainDocument(page_content=raw_text, metadata={})]
                else:
                    Doc = type('Doc', (), {})
                    documents = [Doc()]
                    documents[0].page_content = raw_text

                try:
                    with open(debug_log, 'a', encoding='utf-8') as dbg:
                        dbg.write(f"[{datetime.now().isoformat()}] Fallback: read raw text length={len(raw_text)}\n")
                except Exception:
                    pass
            except Exception:
                # If fallback fails, ensure temp file is removed and return
                try:
                    temp_path.unlink()
                except Exception:
                    pass
                st.error("❌ Failed to load document content.")
                return None

        temp_path.unlink()  # Clean up temp file

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)

        # If splitting produced no chunks (very small files), create a single chunk
        if not chunks:
            try:
                combined = "\n\n".join(getattr(d, 'page_content', '') for d in documents)
                # Use LangChain Document as chunk if available
                try:
                    from langchain.schema import Document as LangChainDocument
                except Exception:
                    LangChainDocument = None

                if LangChainDocument is not None:
                    chunks = [LangChainDocument(page_content=combined, metadata={})]
                else:
                    Chunk = type('Chunk', (), {})
                    c = Chunk()
                    c.page_content = combined
                    chunks = [c]

                try:
                    with open(debug_log, 'a', encoding='utf-8') as dbg:
                        dbg.write(f"[{datetime.now().isoformat()}] Fallback: created single chunk length={len(combined)}\n")
                except Exception:
                    pass
            except Exception:
                pass

        # Try to create vector store
        try:
            if LANGCHAIN_AVAILABLE:
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                vectorstore = FAISS.from_documents(chunks, embeddings)
                return {"type": "vectorstore", "store": vectorstore, "chunks": chunks}
        except Exception as e:
            st.warning(f"⚠️ Vector search unavailable: {e}")

        # Fallback to simple text search
        return {
            "type": "simple",
            "chunks": chunks,
            "text_content": [chunk.page_content for chunk in chunks]
        }

    except Exception as e:
        st.error(f"❌ Error processing document: {e}")
        return None

# === Search Functions ===
def search_documents(query, doc_data):
    """Search documents with fallback methods"""
    if not doc_data:
        return "No documents available to search."
    
    query_lower = query.lower()
    
    if doc_data["type"] == "vectorstore":
        try:
            # Use vector search
            retriever = doc_data["store"].as_retriever(search_kwargs={"k": 3})
            relevant_docs = retriever.get_relevant_documents(query)
            if relevant_docs:
                return "\n\n".join([doc.page_content[:500] + "..." for doc in relevant_docs])
        except Exception:
            pass
    
    # Fallback to simple text search
    results = []
    for text in doc_data.get("text_content", []):
        if any(term in text.lower() for term in query_lower.split()):
            results.append(text[:400] + "...")
            if len(results) >= 3:
                break
    
    return "\n\n".join(results) if results else "No relevant information found in documents."

@st.cache_data
def web_search(query):
    """Web search with error handling"""
    if not config.has_serpapi:
        return "Web search unavailable - SerpAPI key not configured"
    
    try:
        search = SerpAPIWrapper(serpapi_api_key=config.serpapi_key)
        return search.run(query)
    except Exception as e:
        return f"Web search error: {e}"

# === Voice Functions ===
def text_to_speech(text):
    """Convert text to speech with error handling"""
    if not VOICE_AVAILABLE:
        st.warning("Text-to-speech unavailable - install gtts package")
        return None
        
    try:
        tts = gTTS(text=text[:500], lang='en')  # Limit length
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

# === Main App Interface ===
def setup_page():
    """Configure Streamlit page"""
    st.set_page_config(
        page_title="🤖 AI Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def show_welcome_screen():
    """Show welcome and setup screen"""
    st.title("🤖 Welcome to AI Chatbot")
    
    if not config.available_providers:
        st.warning("⚠️ No AI providers configured!")
        
        with st.expander("🔧 Quick Setup Guide", expanded=True):
            st.markdown("""
            ### Get started in 3 steps:
            
            1. **Create a `.env` file** in your project folder
            2. **Add your API keys:**
            ```
            GROQ_API_KEY=your_groq_key_here
            GOOGLE_API_KEY=your_google_key_here
            HUGGINGFACE_API_TOKEN=your_hf_token_here
            SERPAPI_API_KEY=your_serpapi_key_here
            ```
            3. **Restart the app**
            
            ### Get API Keys:
            - **Groq (Recommended)**: [console.groq.com](https://console.groq.com) - Free tier available
            - **Google Gemini**: [makersuite.google.com](https://makersuite.google.com) - Free tier available  
            - **HuggingFace**: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) - Free
            - **SerpAPI**: [serpapi.com](https://serpapi.com) - Free tier available
            """)
        
        st.info("💡 The chatbot works in offline mode without API keys, but with limited capabilities.")
    
    else:
        st.success(f"✅ Ready to chat! {len(config.available_providers)} AI provider(s) available.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("AI Providers", len(config.available_providers))
        
        with col2:
            st.metric("Web Search", "Available" if config.has_serpapi else "Unavailable")
            
        with col3:
            st.metric("Voice Features", "Available" if VOICE_AVAILABLE else "Limited")

def show_sidebar():
    """Enhanced sidebar with better organization"""
    with st.sidebar:
        st.title("🤖 AI Chatbot")
        
        # Provider selection
        if config.available_providers:
            provider = st.selectbox(
                "🧠 AI Provider:",
                config.available_providers,
                help="Choose your AI provider"
            )
            
            # Model selection
            if provider == "groq":
                model = st.selectbox("Model:", [
                    "llama3-8b-8192",
                    "mixtral-8x7b-32768", 
                    "gemma-7b-it"
                ])
            elif provider == "gemini":
                model = st.selectbox("Model:", [
                    "gemini-pro",
                    "gemini-pro-vision"
                ])
            else:
                model = st.selectbox("Model:", [
                    "microsoft/DialoGPT-medium",
                    "facebook/blenderbot-400M-distill"
                ])
        else:
            provider = "offline"
            model = "offline"
            st.warning("⚠️ Running in offline mode")
        
        st.divider()
        
        # Document upload
        st.subheader("📄 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload document:",
            type=['pdf', 'txt'],
            help="Upload PDF or text files for analysis"
        )
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        use_voice = st.checkbox(
            "🔊 Text-to-Speech", 
            value=False,
            disabled=not VOICE_AVAILABLE,
            help="Enable audio responses"
        )
        
        max_tokens = st.slider(
            "Response Length:",
            100, 2000, 500,
            help="Maximum response length"
        )
        
        st.divider()
        
        # Status
        st.subheader("📊 Status")
        for status_line in config.get_status_display():
            st.write(status_line)
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
    
    return provider, model, uploaded_file, use_voice, max_tokens

def main():
    """Main application"""
    setup_page()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "doc_data" not in st.session_state:
        st.session_state.doc_data = None
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = True
    
    # Show sidebar
    provider, model, uploaded_file, use_voice, max_tokens = show_sidebar()
    
    # Main content area
    if st.session_state.show_welcome and not st.session_state.messages:
        show_welcome_screen()
        if st.button("🚀 Start Chatting"):
            st.session_state.show_welcome = False
            st.rerun()
        return
    
    st.title("💬 Chat")
    
    # Process uploaded document
    if uploaded_file and uploaded_file != st.session_state.get("last_file"):
        with st.spinner("📖 Processing document..."):
            doc_data = process_document(uploaded_file)
            if doc_data:
                st.session_state.doc_data = doc_data
                st.session_state.last_file = uploaded_file
                st.success(f"✅ Document processed: {uploaded_file.name}")
            else:
                st.error("❌ Failed to process document")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            if message.get("cached"):
                st.caption("📚 From cache")
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Check cache first
                    query_hash = hashlib.md5(prompt.encode()).hexdigest()
                    cached = get_cached_response(query_hash)
                    
                    if cached:
                        response = cached["response"]
                        st.markdown(response)
                        st.caption("📚 From cache")
                        
                    else:
                        # Create LLM or use offline bot
                        if provider != "offline":
                            llm = create_llm(provider, model)
                            if not llm:
                                llm = OfflineBot()
                                st.warning("⚠️ Switched to offline mode")
                        else:
                            llm = OfflineBot()
                        
                        # Generate response
                        if st.session_state.doc_data:
                            # Include document search
                            doc_results = search_documents(prompt, st.session_state.doc_data)
                            
                            if isinstance(llm, OfflineBot):
                                response = f"{llm.invoke(prompt).content}\n\n📄 **From your document:**\n{doc_results}"
                            else:
                                enhanced_prompt = f"{prompt}\n\nRelevant document content:\n{doc_results}"
                                response = llm.invoke(enhanced_prompt).content
                        else:
                            # Regular response
                            response = llm.invoke(prompt).content
                        
                        # Display response
                        st.markdown(response)
                        
                        # Save to cache
                        save_cached_response(query_hash, response)
                        
                        # Text-to-speech
                        if use_voice and response:
                            audio = text_to_speech(response)
                            if audio:
                                st.audio(audio, format='audio/mp3')
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "cached": bool(cached)
                    })
                    
                except Exception as e:
                    error_response = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(error_response)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_response
                    })

if __name__ == "__main__":
    main()

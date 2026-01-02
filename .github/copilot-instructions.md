# A.K.A.S.H.A. Chatbot - AI Agent Instructions

## 🎯 Project Overview
**A.K.A.S.H.A.** is a production-ready, multi-language AI chatbot with Retrieval-Augmented Generation (RAG), long-term memory, knowledge base, and voice capabilities. Built with Streamlit (frontend), LangChain (orchestration), and multi-LLM support (Groq, Google Gemini, HuggingFace).

**Core Stack:** Python 3.8+, Streamlit 1.34+, LangChain 0.3+, FAISS, SerpAPI

---

## 🏗️ Architecture Patterns

### System Layers
1. **UI Layer** → [app.py](app.py) (2196 lines): Streamlit dashboard with JARVIS theme, admin panel, chat interface
2. **Memory/RAG Layer** → [memory.py](memory.py): InMemoryStore + MemoryManager for conversational context
3. **Knowledge Base** → [knowledge_base.py](knowledge_base.py): Document storage, semantic search, KB fallback
4. **LLM Routing** → [app.py](app.py#L400-L500) (approx): Try Groq → Gemini → HuggingFace with auto-fallback
5. **Authentication** → [auth.py](auth.py): Session-state gating for admin features (password in `AKASHA_ADMIN_PASSWORD` env)
6. **Theming** → [ui_theme.py](ui_theme.py): Dark JARVIS theme (cyan #00D9FF, gold #FFB703)
7. **Localization** → [multi_lang.py](multi_lang.py): 10 Indian languages + auto-detection

### Data Flow: Chat Pipeline
```
User Input → detect_language() → memory.insert() → memory.query(top_3) 
→ RAG prompt build → LLM route → response cache → TTS (optional) → UI display
```

**Critical Implementation Detail:** Memory scoring prioritizes **recency + substring match**:
```python
score = substring_match(query, entry.content) + recency_bias(entry.timestamp)
```
See [memory.py#L45-L60](memory.py#L45-L60) for exact algorithm.

---

## ⚡ Developer Workflows

### Local Development
```bash
# Setup once
python setup.py          # Install dependencies + create .env template
pip install -r requirements.txt

# Daily development
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
streamlit run app.py       # Runs on http://localhost:8501

# Testing
pytest tests/ -v           # Run unit tests (4 memory tests in tests/test_memory.py)
make test                  # Via Makefile shorthand
```

### Common Debugging Commands
- **Health check:** Access admin panel (password in `.env` `AKASHA_ADMIN_PASSWORD`)
- **Network diagnostics:** Run `python tools/net_diag.py`
- **Provider tests:** Run `python tools/self_test.py` (verifies Groq/Gemini/HF API connectivity)
- **Document pipeline:** Run `python tools/run_document_tests.py`
- **Cache issues:** Delete `cache/` directory and restart

### Docker
```bash
docker build -t ai-chatbot .
docker run -p 8501:8501 --env-file .env ai-chatbot
```

---

## 🎨 Project-Specific Patterns & Conventions

### 1. **Module Initialization Pattern**
Modules use singleton manager instances (see [knowledge_base.py](knowledge_base.py#L260-L280)):
```python
_kb_instance = None
def get_kb_manager() -> KnowledgeBaseManager:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBaseManager()
    return _kb_instance
```
**Use this pattern for:** Any global state (memory, KB, config). Ensures single instance across Streamlit reruns.

### 2. **LLM Fallback Chain**
[app.py](app.py#L450-L550) implements a **3-tier fallback**:
1. Primary: Groq (fastest, free tier)
2. Secondary: Google Gemini (advanced reasoning)
3. Tertiary: HuggingFace (open-source, offline capable)

**When adding new providers:** Insert before HuggingFace in fallback chain. Catch `Exception` broadly—API errors vary.

### 3. **Admin Gating Pattern**
Use `@require_admin` decorator or manual check (see [auth.py](auth.py#L43-L50)):
```python
if not is_admin_authenticated():
    show_admin_login()
    return
# ... admin-only code
```
Password stored in env `AKASHA_ADMIN_PASSWORD` (default: "AKASHA_ADMIN_2025").

### 4. **Session State for Persistence**
Streamlit reruns on every interaction. Use `st.session_state` for persistence across reruns:
```python
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
st.session_state.chat_history.append(message)  # Persists across reruns
```

### 5. **RAG Context Window**
Memory retrieval uses **top-3 entries** (hardcoded in [memory.py](memory.py#L40)):
```python
def query(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
```
For longer contexts, increase `top_k` parameter. Monitor token usage in LLM responses.

### 6. **Configuration Inheritance**
[config.py](config.py) uses dataclass + env fallback:
```python
max_tokens = int(os.getenv("MAX_TOKENS", "2048"))  # env or default
```
Override via `.env` file or pass as env var.

---

## 🔌 Integration Points & Dependencies

### External APIs (Environment Variables)
- `GROQ_API_KEY` → Groq LLaMA models (required for primary chain)
- `GOOGLE_API_KEY` → Google Gemini (fallback)
- `HUGGINGFACE_API_TOKEN` → HuggingFace models (final fallback)
- `SERPAPI_API_KEY` → Web search (optional; disables web search if missing)
- `AKASHA_ADMIN_PASSWORD` → Admin panel unlock (default: "AKASHA_ADMIN_2025")
- `INDIC_NLPCLOUD_API_KEY` → Indian language translation (optional)

### Critical Dependencies
- **LangChain 0.3+** → LLM orchestration & fallback routing
- **Streamlit 1.34+** → Frontend (session state, widgets, theming)
- **FAISS** → Vector search for document embeddings
- **python-dotenv** → Environment variable loading

### Cross-Module Communication
- **app.py** → imports from all modules; central orchestrator
- **memory.py** → standalone (no app.py dependency)
- **knowledge_base.py** → standalone; optionally used by app.py for KB fallback
- **auth.py** → uses only `streamlit.session_state` (stateless module)
- **ui_theme.py** → stateless; only generates CSS strings

---

## ✅ Testing & Validation

### Test Locations
- **Unit tests:** [tests/test_memory.py](tests/test_memory.py) — 4 passing tests for MemoryManager
- **Integration tests:** [test_knowledge_base.py](test_knowledge_base.py) — KB document lifecycle
- **Feature tests:** [test_ui_features.py](test_ui_features.py) — UI widget behavior

### Running Tests
```bash
pytest tests/test_memory.py -v       # Memory manager tests
python test_knowledge_base.py        # Knowledge base tests
python test_ui_features.py           # UI feature tests
make test                            # Run all (via Makefile)
```

### Adding New Tests
- Use pytest for non-Streamlit code (memory, KB, config)
- Use `streamlit.testing.v1` for UI tests ([test_ui_features.py](test_ui_features.py) reference)
- Mock API calls to avoid rate-limiting during tests

---

## 📝 Code Style & Conventions

### Naming
- **Modules:** lowercase with underscores (`memory.py`, `auth.py`)
- **Classes:** PascalCase (`MemoryManager`, `KnowledgeBaseStore`)
- **Functions:** snake_case (`insert_memory()`, `query()`)
- **Constants:** UPPER_SNAKE_CASE (`ADMIN_PASSWORD`, `MAX_TOKENS`)

### Type Hints
Used throughout. Example:
```python
def query(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
```

### Docstrings
Module-level docstrings required (see all `.py` files). Function docstrings optional but encouraged for public APIs.

### Logging
Use [logger.py](logger.py) instead of `print()`:
```python
from logger import logger
logger.warning("This is important")
logger.debug("Detailed trace")
```

---

## 🚀 Common Tasks

### Add a New Language
1. Add language code + name to `SUPPORTED_LANGUAGES` dict in [multi_lang.py](multi_lang.py#L8-L20)
2. Add Unicode pattern to `LANGUAGE_PATTERNS` for detection
3. Test with `detect_language("sample text in that language")`

### Add a New LLM Provider
1. In [app.py](app.py), find `create_llm_with_fallback()` function (~line 450)
2. Add provider initialization before HuggingFace fallback
3. Wrap in try/except; catch broad exceptions for API failures
4. Document new env var in `.env` template

### Implement Knowledge Base Answer
1. Query KB using `kb_manager.search_semantic(query, top_k=3)` in [app.py](app.py#L1800)
2. If results found, augment system prompt: `"Use this context from KB: {results}"`
3. Fall back to LLM if KB search returns no results
4. Cache KB search results in `st.session_state` to avoid repeated searches

### Extend Memory Scoring
Edit [memory.py](memory.py#L50-L60) `InMemoryStore.query()`:
- Current: substring + recency
- Option: Add embedding-based similarity (requires external embeddings library)

---

## 🐛 Troubleshooting Guide

**"Module not found" on import:**
- Ensure `python setup.py` was run (creates `.env`)
- Check `PYTHONPATH` includes project root

**Admin panel won't unlock:**
- Verify `.env` file exists with `AKASHA_ADMIN_PASSWORD=<your_password>`
- Default password: "AKASHA_ADMIN_2025"

**LLM returns empty responses:**
- Check provider is not rate-limited (see `health.py`)
- Verify API key in `.env` is valid
- Check internet connection (if using online provider)

**Memory not accumulating:**
- Verify `memory_manager.insert_memory()` is called in chat flow
- Check `st.session_state` persists (Streamlit browser issue?)
- Review [memory.py](memory.py#L30-L40) pruning logic (max 1000 entries by default)

**Knowledge base searches return no results:**
- Ensure documents added via `kb_manager.add_from_text()` or UI
- Check search query includes relevant keywords from doc content

---

## 📚 Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| [app.py](app.py) | Main Streamlit app + LLM routing | 2196 |
| [memory.py](memory.py) | Long-term memory + RAG pipeline | 119 |
| [knowledge_base.py](knowledge_base.py) | KB storage + semantic search | 297 |
| [auth.py](auth.py) | Admin authentication | 61 |
| [ui_theme.py](ui_theme.py) | JARVIS dark theme + CSS | 213 |
| [multi_lang.py](multi_lang.py) | 10-language support | 194 |
| [config.py](config.py) | Configuration management | 61 |
| [logger.py](logger.py) | Logging utilities | ~ |
| [tests/test_memory.py](tests/test_memory.py) | Memory unit tests | 28 |

---

**Last Updated:** December 2025  
**Maintainer Notes:** This project emphasizes graceful degradation (fallbacks) and memory-aware conversations. Prioritize backward compatibility when refactoring core modules.

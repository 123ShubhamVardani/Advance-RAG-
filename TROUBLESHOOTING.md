# 🔧 TROUBLESHOOTING GUIDE

## 🚨 **Common Issues & Solutions**

### **1. Connection Errors / SSL Certificate Issues** ❌

**Symptoms:**
- `SSLError: CERTIFICATE_VERIFY_FAILED`
- `MaxRetryError: HTTPSConnectionPool`
- Connection timeouts

**Solutions:**
✅ **Fixed in latest version** - SSL verification disabled for corporate networks
✅ **Automatic fallback** - Switches to offline mode when connections fail
✅ **Local processing** - Documents processed without internet connection

**Manual Fix (if needed):**
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**Prefer Safe Toggle:** Instead of forcing globally, set in `.env`:
```
ALLOW_INSECURE_SSL=true
```
Then restart — the app will clearly warn that verification is disabled. Remove the variable to re‑enable validation.

**New Diagnostics (Sidebar > Diagnostics):**
- Adjustable timeout / retries / backoff
- Shows proxy environment variables detected
- Displays last error classifications (ssl / timeout / proxy / dns / network / other)
- Attempts a secondary retry without custom CA bundle if SSL-only failures occur

**Typical Root Causes:**
| Classification | Meaning | Action |
| -------------- | ------- | ------ |
| ssl | Certificate chain / corporate MITM | Use system store (clear overrides) or append full chain to bundle |
| timeout | Network latency / firewall slow path | Increase timeout/backoff; check VPN |
| proxy | Mis-configured proxy or blocked CONNECT | Verify HTTP(S)_PROXY, NO_PROXY settings |
| dns | Name resolution blocked/overridden | Flush DNS, check hosts file, corporate DNS rules |
| network | Connection refused/reset | Check firewall, endpoint availability, local security tools |
| other | Unclassified | Inspect raw detail string in diagnostics |

### **2. HuggingFace Model Download Issues** ❌

**Symptoms:**
- `Error processing file: Max retries exceeded`
- Embedding model download failures
- RAG functionality not working

**Solutions:**
✅ **Smart fallback** - Automatically switches to simple text search
✅ **Offline processing** - No internet required for document upload
✅ **Progress indicators** - Clear error messages and suggestions

**What happens now:**
1. Tries HuggingFace embeddings first
2. If fails → Falls back to simple text search
3. Still provides document search functionality
4. Shows clear warnings about degraded mode

### **3. API Key Issues** ❌

**Symptoms:**
- `API key not found`
- Authentication errors
- Model loading failures

**Solutions:**
✅ **Offline mode** - Works without any API keys
✅ **Multi-provider support** - Try different providers
✅ **Clear status indicators** - Shows which APIs are available

**Check your .env file:**
```
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
SERPAPI_API_KEY=your_serpapi_key_here
```

### **4. Document Upload/RAG Errors** ❌

**Symptoms:**
- `Failed to process document`
- Embedding creation errors
- Vector store failures

**Solutions:**
✅ **Graceful degradation** - Falls back to simple text search
✅ **Multiple formats** - Supports PDF and TXT files
✅ **Error recovery** - Continues working even if embeddings fail

**How it works now:**
1. Upload document → Splits into chunks
2. Try FAISS embeddings → If fails, use simple search
3. Search works either way
4. Clear feedback about search mode

## 🎯 **Current Features That Always Work**

### **✅ Offline Mode**
- Rule-based chatbot responses
- Document text search (without embeddings)
- File upload and processing
- Basic conversation capabilities

### **✅ Online Mode (with API keys)**
- Full LLM responses (Groq, Gemini, HuggingFace)
- Advanced RAG with embeddings
- Web search integration
- Agent-based tool usage

### **✅ Hybrid Mode (partial connectivity)**
- Document search works offline
- LLM responses when API available
- Automatic fallback between modes
- Cached responses for repeated queries

## 🚀 **Testing Your Setup**

### **1. Test Offline Mode**
```bash
# Remove/comment out API keys in .env
python test_offline.py
```

### **2. Test Document Upload**
1. Upload a PDF or TXT file
2. Should work even without internet
3. Try searching the document content

### **3. Test API Connectivity**
1. Add valid API keys to .env
2. Try different providers (Groq, Gemini)
3. Check API Status in sidebar

## 💡 **Pro Tips**

1. **Start offline** - Test basic functionality first
2. **Add APIs gradually** - Test one provider at a time  
3. **Check corporate firewall** - May block HuggingFace downloads
4. **Use simple documents** - Start with TXT files for testing
5. **Monitor logs** - Check terminal for detailed error messages

## 🔄 **Fallback Hierarchy**

```
1. Full Online Mode (Best)
   ↓ (if API fails)
2. Local Embeddings + Offline Chat
   ↓ (if embeddings fail)  
3. Simple Text Search + Offline Chat
   ↓ (always works)
4. Pure Offline Mode (Basic but reliable)
```

Your chatbot will now work in ANY environment! 🎉

---
## 🧪 Advanced Connectivity Reference

### Automatic Degrade Logic
In auto mode the app counts consecutive failed connectivity tests. After `AUTO_OFFLINE_FAIL_THRESHOLD` (default 3) failures, it switches to offline and stores the reason in `session_state.last_offline_reason` (e.g. `ssl`, `timeout`, `proxy`). Raising the threshold:
```
AUTO_OFFLINE_FAIL_THRESHOLD=5
```

### Connection Test Environment Variables
| Variable | Default | Purpose |
| -------- | ------- | ------- |
| CONNECTION_TEST_TIMEOUT | 5 | Seconds per attempt |
| CONNECTION_TEST_RETRIES | 2 | Additional retries per endpoint |
| CONNECTION_TEST_BACKOFF | 0.5 | Initial backoff (exponential) |
| ALLOW_INSECURE_SSL | false | Disable TLS verification (diagnostics only) |
| AUTO_OFFLINE_FAIL_THRESHOLD | 3 | Fail streak before auto offline |

### Proxy Handling
If `HTTP_PROXY` / `HTTPS_PROXY` are set they are recorded in diagnostics. If all failures classify as `proxy`, verify:
1. Proxy host resolves: `ping proxy.host`
2. Port open (if allowed): `Test-NetConnection proxy.host -Port 8080`
3. Add internal endpoints to `NO_PROXY` (comma separated) if they should bypass proxy.

### Root Cause Quick Matrix
| Symptom | Likely Cause | Fast Test | Fix |
| ------- | ------------ | --------- | --- |
| env+system fail, insecure OK | SSL interception / missing CA | Clear overrides & retest | Install corporate root into system trust or CA bundle |
| All variants timeout | Firewall deep inspection | Increase timeout/backoff | Allowlist domains / reduce packet inspection |
| Proxy classification dominates | Bad proxy settings | Temporarily unset proxy vars | Correct env vars / PAC settings |
| DNS failures across endpoints | Internal DNS override | `nslookup www.google.com` | Fix DNS config / hosts interference |

### Provider Self-Test
Run:
```
python -X utf8 tools/self_test.py
```
Outputs JSON with per-provider latency / sample or failure reason.

---
## ✍️ Updating Certificates Safely
1. Export corporate root & intermediates to PEM.
2. Append to certifi bundle (not replace):
   - Locate: `python -c "import certifi,os;print(certifi.where())"`
   - Append your PEM blocks at end.
3. Avoid setting `REQUESTS_CA_BUNDLE` unless absolutely required; rely on system trust when possible (on Windows, `python-certifi-win32`).

---
## 🧾 Glossary
| Term | Definition |
| ---- | ---------- |
| Vectorstore | FAISS index of embedding vectors enabling semantic search |
| Fallback | Automatic substitution to simpler strategy after failure |
| Classification | Error category assigned during diagnostics |


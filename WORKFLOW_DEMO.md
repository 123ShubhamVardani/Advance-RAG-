# Workflow Demo

End-to-end examples for using the chatbot effectively.

## 1. Basic Chat
1. Launch app: `streamlit run app.py`
2. In sidebar select an AI provider (Groq recommended).
3. Ask a question: "Summarize the advantages of vector search.".
4. Adjust model if needed (e.g., switch to mixtral for longer context).

## 2. Document Q&A
1. Upload a PDF (e.g., internal policy) in the sidebar.
2. Ask: "What are the retention rules?".
3. Bot performs: chunking -> embeddings -> retrieval -> augmented generation.
4. If embeddings backend fails, fallback simple text search is used (indicated by shorter extracts).

## 3. Handling Connectivity Issues
1. If responses fail, open Diagnostics in sidebar.
2. Click "Re-check connectivity" (verbose) or run Validator / Self-Test buttons.
3. Interpret variants (see CONNECTIVITY.md). Fix root cause, then re-run.
4. If auto offline degrade occurs, reason stored: `last_offline_reason`.

## 4. Switching Modes
| Mode | Behavior |
| ---- | -------- |
| auto | Tests connectivity; degrades after fail streak |
| online | Always attempts provider calls |
| offline | Forces OfflineBot + doc search only |

## 5. Performance Tuning
- Increase `CONNECTION_TEST_TIMEOUT` for slow corporate networks.
- Raise `CONNECTION_TEST_RETRIES` if transient packet loss.
- Lower `chunk_size` (code change) for very large documents.

## 6. Caching Behavior
- Prompt hash stored in `cache/`.
- Repeated exact questions served instantly (📚 From cache shown).
- Clear via sidebar "Clear Cache" button.

## 7. Voice Workflow
1. Enable voice features.
2. Click "Voice Input"; speak question.
3. Recognized text populates chat input automatically.
4. If TTS enabled, response audio is generated (shortened for speed).

## 8. Multi-Provider Fallback
1. If chosen provider fails, auto tries others (auto mode only).
2. If all fail, auto offline degrade with log entry.
3. Recover by fixing keys/connectivity and selecting Online or Auto.

## 9. Corporate CA Resolution Fast Path
1. Run Validator: env=ssl failures; system variant OK.
2. Remove or repair `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`.
3. Re-run; env variant should match system.

## 10. Minimal Docker Run
```bash
# Build
docker build -t ai-chatbot .
# Provide keys
cp .env.example .env  # if you have a template
# Run
docker run --rm -p 8501:8501 --env-file .env ai-chatbot
```

## 11. Logs & Diagnostics
- Logs: tail inside sidebar (last 200 lines).
- Connection diagnostics stored in session: `connection_diagnostics`.
- Fail streak counter: `connection_fail_streak`.

## 12. Extending
- Add new provider: implement in `try_create_llm` + config detection.
- Add tool: use LangChain Tools list when constructing agent (future extension).
- Add persistence: swap cache JSON for SQLite.

---
For deeper troubleshooting see `TROUBLESHOOTING.md`.

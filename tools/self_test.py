"""Provider self-test utility.
Run inside project venv: python -X utf8 tools/self_test.py
It will attempt lightweight instantiation of each configured provider and optional simple invocation.
"""
import os
import json
import time
from datetime import datetime

RESULT = {"started": datetime.utcnow().isoformat() + "Z", "providers": {}, "env": {}}

for k in ["GROQ_API_KEY", "GOOGLE_API_KEY", "HUGGINGFACE_API_TOKEN", "SERPAPI_API_KEY"]:
    RESULT["env"][k] = bool(os.getenv(k))

def record(name, **fields):
    RESULT["providers"].setdefault(name, {}).update(fields)

try:
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_community.llms import HuggingFaceHub
    OK_LANGCHAIN = True
except Exception as e:
    record("_core", error=f"LangChain import failed: {e}")
    OK_LANGCHAIN = False

if OK_LANGCHAIN:
    # Groq
    if os.getenv("GROQ_API_KEY"):
        t0 = time.time()
        try:
            llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant", max_tokens=5)
            out = llm.invoke("Hi").content[:200]
            record("groq", status="ok", latency_ms=int((time.time()-t0)*1000), sample=out)
        except Exception as e:
            record("groq", status="fail", error=str(e))
    else:
        record("groq", status="skip", reason="no key")

    # Gemini
    if os.getenv("GOOGLE_API_KEY"):
        t0 = time.time()
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
            out = llm.invoke("Hi").content[:200]
            record("gemini", status="ok", latency_ms=int((time.time()-t0)*1000), sample=out)
        except Exception as e:
            record("gemini", status="fail", error=str(e))
    else:
        record("gemini", status="skip", reason="no key")

    # HuggingFace Hub
    if os.getenv("HUGGINGFACE_API_TOKEN"):
        t0 = time.time()
        try:
            llm = HuggingFaceHub(repo_id="microsoft/DialoGPT-medium", huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN"), model_kwargs={"max_length":32})
            out = llm.invoke("Hi").content[:200]
            record("huggingface", status="ok", latency_ms=int((time.time()-t0)*1000), sample=out)
        except Exception as e:
            record("huggingface", status="fail", error=str(e))
    else:
        record("huggingface", status="skip", reason="no token")

print(json.dumps(RESULT, ensure_ascii=False, indent=2))
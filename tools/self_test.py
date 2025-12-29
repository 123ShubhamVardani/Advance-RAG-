"""Provider self-test utility.
Run inside project venv: python -X utf8 tools/self_test.py
It will attempt lightweight instantiation of each configured provider and optional simple invocation.
"""
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

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
            # Try a short list of Gemini models (prefer env override). This helps
            # when the project has no quota for a particular model (429) — we
            # attempt smaller/older models until one succeeds.
            model_env = os.getenv("GOOGLE_MODEL")
            candidates = [m for m in ([model_env] if model_env else []) + [
                "gemini-2.5-flash",
                "gemini-1.5-pro",
                "gemini-1.0",
            ] if m]

            gemini_ok = False
            last_err = None
            for choice in candidates:
                try:
                    llm = ChatGoogleGenerativeAI(model=choice, google_api_key=os.getenv("GOOGLE_API_KEY"))
                    out = llm.invoke("Hi").content[:200]
                    record("gemini", status="ok", model=choice, latency_ms=int((time.time()-t0)*1000), sample=out)
                    gemini_ok = True
                    break
                except Exception as e:
                    last_err = str(e)
                    # If it's explicitly a quota/billing error, capture and continue
                    # to the next candidate so the script can try alternatives.
                    # We don't re-raise here because some projects have zero free-tier
                    # quota for newer models but may allow older/smaller ones.
                    continue

            if not gemini_ok:
                # If nothing worked, show the last error (often a quota/billing message)
                guidance = (
                    "Gemini tests failed for all candidate models. If this is a quota or billing "
                    "issue, enable billing or choose a model your project has access to. See: "
                    "https://ai.google.dev/gemini-api/docs/rate-limits"
                )
                record("gemini", status="fail", error=last_err or "no candidate models tried", guidance=guidance)
        except Exception as e:
            record("gemini", status="fail", error=str(e))
    else:
        record("gemini", status="skip", reason="no key")

    # HuggingFace Hub
    if os.getenv("HUGGINGFACE_API_TOKEN"):
        t0 = time.time()
        try:
            # Prefer the newer InferenceClient (router) when available
            hf_model = os.getenv("HUGGINGFACE_MODEL", "gpt2")
            token = os.getenv("HUGGINGFACE_API_TOKEN")
            sample_text = None
            try:
                from huggingface_hub import InferenceClient
                client = InferenceClient(token=token)
                # Try the high-level text_generation helper if available
                if hasattr(client, "text_generation"):
                    resp = client.text_generation(model=hf_model, inputs="Hi", max_new_tokens=64)
                    # resp can be a list of dicts or a dict-like object
                    if isinstance(resp, list) and resp:
                        first = resp[0]
                        sample_text = (
                            getattr(first, "generated_text", None)
                            or (first.get("generated_text") if isinstance(first, dict) else None)
                            or str(first)
                        )
                    elif isinstance(resp, dict):
                        sample_text = resp.get("generated_text") or resp.get("text") or str(resp)
                    else:
                        sample_text = str(resp)
                else:
                    # Generic request: some InferenceClient versions expose a generic "request" or "post" method
                    if hasattr(client, "request"):
                        resp = client.request(model=hf_model, inputs="Hi")
                    elif hasattr(client, "post"):
                        resp = client.post(model=hf_model, inputs="Hi")
                    else:
                        # fall back to InferenceApi if InferenceClient shape is unexpected
                        raise RuntimeError("InferenceClient missing expected helpers; falling back")
                    sample_text = str(resp)
            except Exception:
                # Fallback to the older InferenceApi shape if InferenceClient isn't available or fails
                from huggingface_hub import InferenceApi
                client2 = InferenceApi(repo_id=hf_model, token=token)
                try:
                    resp = client2(inputs="Hi", raw_response=True)
                    try:
                        data = resp.json()
                    except Exception:
                        data = None
                except TypeError:
                    resp = client2(inputs="Hi")
                    data = resp if isinstance(resp, dict) else None

                if isinstance(data, dict):
                    sample_text = data.get("generated_text") or data.get("text") or data.get("outputs") or str(data)
                elif isinstance(resp, dict):
                    sample_text = resp.get("generated_text") or resp.get("text") or str(resp)
                else:
                    sample_text = str(data or resp)

            record("huggingface", status="ok", latency_ms=int((time.time()-t0)*1000), sample=(sample_text[:200] if sample_text else ""))
        except Exception as e:
            record("huggingface", status="fail", error=str(e))
    else:
        record("huggingface", status="skip", reason="no token")

print(json.dumps(RESULT, ensure_ascii=False, indent=2))
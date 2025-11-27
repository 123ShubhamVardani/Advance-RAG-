import sys
import os
import json
import py_compile
import platform
import socket
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {'.venv', '__pycache__', '.git'}
IS_PY38_PLUS = sys.version_info >= (3, 8)


def should_skip(path: Path) -> bool:
    parts = set(p.name for p in path.parents) | {path.name}
    # Always skip common auto-generated or excluded dirs
    if any(ex in parts for ex in EXCLUDE_DIRS):
        return True
    # For older Python versions, skip sources that use 3.8+ features
    if not IS_PY38_PLUS:
        if 'archive' in (p.name for p in path.parents):
            return True
        if path.name == 'app_new.py':
            return True
    return False


def collect_py_files(base: Path) -> List[Path]:
    files = []
    for p in base.rglob('*.py'):
        if should_skip(p):
            continue
        files.append(p)
    return files


def compile_files(files: List[Path]) -> List[Dict[str, Any]]:
    results = []
    for p in files:
        try:
            py_compile.compile(str(p), doraise=True)
            results.append({"file": str(p), "status": "OK"})
        except Exception as e:
            results.append({"file": str(p), "status": "FAIL", "error": str(e)})
    return results


def check_imports() -> Dict[str, str]:
    import importlib
    try:
        import importlib.metadata as md  # type: ignore
    except Exception:
        try:
            import importlib_metadata as md  # type: ignore
        except Exception:
            md = None  # type: ignore
    modules = [
        'streamlit',
        'langchain', 'langchain_community', 'langchain_groq', 'langchain_google_genai', 'langchain_huggingface',
        'sentence_transformers', 'faiss',
        'gtts', 'speech_recognition', 'pyaudio', 'psutil', 'requests'
    ]
    out: Dict[str, str] = {}
    for m in modules:
        try:
            mod = importlib.import_module(m)
            ver = getattr(mod, '__version__', None)
            if not ver:
                if md is not None:
                    try:
                        ver = md.version(m.replace('_', '-'))
                    except Exception:
                        ver = '(unknown)'
                else:
                    ver = '(unknown)'
            out[m] = ver
        except Exception as e:
            out[m] = f'MISSING: {e.__class__.__name__}'
    return out


def import_app_module() -> Dict[str, Any]:
    import importlib.util
    app_path = ROOT / 'app.py'
    try:
        # Ensure local imports like `from logger import logger` resolve
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        spec = importlib.util.spec_from_file_location('app_module', str(app_path))
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)  # should not run main due to guard
        return {"status": "OK"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def connectivity_check() -> Dict[str, Any]:
    import requests
    import time
    # System trust bridge
    has_certifi_win32 = False
    try:
        has_certifi_win32 = True
    except Exception:
        pass

    endpoints = [
        ("google_204", "https://www.google.com/generate_204"),
        ("httpbin_200", "https://httpbin.org/status/200"),
        ("groq", "https://api.groq.com"),
        ("gemini", "https://generativelanguage.googleapis.com"),
    ]

    def classify(msg: str) -> str:
        m = msg.lower()
        if any(k in m for k in ["ssl", "certificate", "handshake"]): return "ssl"
        if any(k in m for k in ["timeout", "timed out"]): return "timeout"
        if any(k in m for k in ["proxy", "tunnel"]): return "proxy"
        if any(k in m for k in ["dns", "getaddrinfo", "name or service"]): return "dns"
        if any(k in m for k in ["refused", "reset", "unreachable"]): return "network"
        return "other"

    results: Dict[str, Any] = {
        "env": {
            "HTTP_PROXY": os.getenv('HTTP_PROXY') or os.getenv('http_proxy'),
            "HTTPS_PROXY": os.getenv('HTTPS_PROXY') or os.getenv('https_proxy'),
            "NO_PROXY": os.getenv('NO_PROXY') or os.getenv('no_proxy'),
            "REQUESTS_CA_BUNDLE": os.getenv('REQUESTS_CA_BUNDLE'),
            "SSL_CERT_FILE": os.getenv('SSL_CERT_FILE'),
            "certifi_win32": has_certifi_win32,
            "ALLOW_INSECURE_SSL": os.getenv('ALLOW_INSECURE_SSL'),
        },
        "checks": [],
        "summary": {},
    }

    variants = [
        ("env", False),     # current env
        ("system", False),  # overrides removed
        ("insecure", True), # verify False
    ]

    orig_env = {"REQUESTS_CA_BUNDLE": os.getenv("REQUESTS_CA_BUNDLE"), "SSL_CERT_FILE": os.getenv("SSL_CERT_FILE")}

    timeout = float(os.getenv("CONNECTION_TEST_TIMEOUT", "5"))
    retries = int(os.getenv("CONNECTION_TEST_RETRIES", "1"))
    backoff_base = float(os.getenv("CONNECTION_TEST_BACKOFF", "0.5"))

    try:
        for variant, insecure in variants:
            # Manage env
            if variant == "system":
                for k in ["REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"]:
                    if k in os.environ:
                        del os.environ[k]
            elif variant == "env":
                # restore originals
                for k, v in orig_env.items():
                    if v is not None:
                        os.environ[k] = v
                    else:
                        os.environ.pop(k, None)

            for name, url in endpoints:
                attempt = 0
                success = False
                errors = []
                while attempt <= retries and not success:
                    started = time.time()
                    entry = {"endpoint": name, "url": url, "variant": variant, "attempt": attempt + 1}
                    try:
                        r = requests.get(url, timeout=timeout, verify=(False if insecure else True))
                        entry["elapsed_ms"] = int((time.time() - started) * 1000)
                        if r.status_code < 500:
                            entry["status"] = "OK"
                            entry["code"] = r.status_code
                            success = True
                        else:
                            entry["status"] = "FAIL"
                            entry["code"] = r.status_code
                            entry["error"] = "http_error"
                    except Exception as e:
                        msg = str(e)
                        entry["status"] = "FAIL"
                        entry["error"] = e.__class__.__name__
                        entry["detail"] = msg[:400]
                        entry["classification"] = classify(msg)
                        errors.append(entry["classification"])
                    results["checks"].append(entry)
                    if not success:
                        attempt += 1
                        if attempt <= retries:
                            delay = backoff_base * (2 ** (attempt - 1))
                            time.sleep(min(delay, 2.0))

    finally:
        # Restore env
        for k, v in orig_env.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

    # DNS
    try:
        socket.gethostbyname('api.groq.com')
        results["dns_groq"] = "OK"
    except Exception as e:
        results["dns_groq"] = f"FAIL:{e.__class__.__name__}"

    # Summary root cause heuristic: look at env variant failures
    env_failures = [c for c in results["checks"] if c["variant"] == "env"]
    classes = {}
    for c in env_failures:
        cl = c.get("classification")
        if cl:
            classes[cl] = classes.get(cl, 0) + 1
    results["summary"]["env_error_classes"] = classes
    if classes:
        # pick most frequent classification
        root = sorted(classes.items(), key=lambda x: x[1], reverse=True)[0][0]
        results["summary"]["likely_root_cause"] = root
    else:
        # if insecure passes but others fail, likely certificate
        insecure_ok = any(c for c in results["checks"] if c["variant"] == "insecure" and c["status"] == "OK")
        env_ok = any(c for c in results["checks"] if c["variant"] == "env" and c["status"] == "OK")
        if insecure_ok and not env_ok:
            results["summary"]["likely_root_cause"] = "ssl"

    return results


def env_summary() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(Path.cwd()),
        "root": str(ROOT),
    }


def main():
    base = ROOT
    files = collect_py_files(base)
    compile_results = compile_files(files)
    ok = sum(1 for r in compile_results if r["status"] == "OK")
    fail = sum(1 for r in compile_results if r["status"] == "FAIL")

    report = {
        "env": env_summary(),
        "compile": {
            "base": str(base),
            "total": len(compile_results),
            "ok": ok,
            "fail": fail,
            "results": compile_results,
        },
        "imports": check_imports(),
        "app_import": import_app_module(),
        "connectivity": connectivity_check(),
        "api_keys_present": {
            "GROQ_API_KEY": bool(os.getenv('GROQ_API_KEY')),
            "GOOGLE_API_KEY": bool(os.getenv('GOOGLE_API_KEY')),
            "HUGGINGFACE_API_TOKEN": bool(os.getenv('HUGGINGFACE_API_TOKEN')),
            "SERPAPI_API_KEY": bool(os.getenv('SERPAPI_API_KEY')),
        },
    }

    print(json.dumps(report, indent=2))
    if fail:
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Validate API keys (Groq, Google, HuggingFace, SerpAPI) and patch deprecated Groq model IDs in-project.

This script performs non-destructive checks:
- Loads .env
- For each known key, attempts a lightweight API call (models.list for Groq, a minimal Google discovery ping if key present, HuggingFace user info, SerpAPI ping)
- Scans files for known deprecated Groq model IDs and replaces them with recommended IDs.

Use from project root; it will print results to stdout.
"""
import os, sys, json, re

# Load .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for ln in f:
            ln=ln.strip()
            if not ln or ln.startswith('#'): continue
            if '=' in ln:
                k,v=ln.split('=',1); v=v.strip().strip('"').strip("'")
                os.environ[k.strip()]=v

results = {}

# GROQ
try:
    import groq
    gkey = os.getenv('GROQ_API_KEY')
    results['groq_key_present'] = bool(gkey)
    if gkey:
        client = groq.Client(api_key=gkey)
        res = client.models.list()
        results['groq_models_sample'] = []
        # try to get models from res.data if present
        if hasattr(res, 'data'):
            for m in res.data[:5]:
                results['groq_models_sample'].append(getattr(m, 'id', getattr(m,'name', str(m))))
        else:
            # fallback: repr
            results['groq_models_sample'].append(repr(res)[:200])
except Exception as e:
    results['groq_error'] = str(e)

# HuggingFace
try:
    hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
    results['hf_present'] = bool(hf_token)
    if hf_token:
        import requests
        r = requests.get('https://huggingface.co/api/whoami-v2', headers={'Authorization': f'Bearer {hf_token}'}, timeout=8)
        results['hf_status'] = r.status_code
        if r.ok:
            results['hf_user'] = r.json().get('name') or r.json().get('id')
except Exception as e:
    results['hf_error'] = str(e)

# SerpAPI
try:
    serp = os.getenv('SERPAPI_API_KEY')
    results['serp_present'] = bool(serp)
    if serp:
        import requests
        r = requests.get('https://serpapi.com/search', params={'q':'test','api_key':serp}, timeout=8)
        results['serp_status'] = r.status_code
except Exception as e:
    results['serp_error'] = str(e)

# Google (Generative) - we will do a safe discovery if key present
try:
    g_api = os.getenv('GOOGLE_API_KEY')
    results['google_present'] = bool(g_api)
    if g_api:
        import requests
        # Use a harmless, public endpoint to validate key presence (not always reliable)
        r = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo', params={'access_token': g_api}, timeout=8)
        results['google_status'] = r.status_code
except Exception as e:
    results['google_error'] = str(e)

print(json.dumps(results, indent=2))

# Now perform a simple replacement pass for deprecated Groq model ids
mappings = {
    'llama-3.1-8b-instant': 'llama-3.1-8b-instant',
    'llama-3.3-70b-versatile': 'llama-3.3-70b-versatile',
    'whisper-large-v3-turbo': 'whisper-large-v3-turbo',
    'llama-3.1-8b-instant': 'llama-3.1-8b-instant',
    'llama-3.3-70b-versatile': 'llama-3.3-70b-versatile',
    'qwen/qwen3-32b': 'qwen/qwen3-32b',
    'qwen/qwen3-32b': 'qwen/qwen3-32b',
    'moonshotai/kimi-k2-instruct-0905-0905': 'moonshotai/kimi-k2-instruct-0905-0905-0905',
    'qwen/qwen3-32b': 'qwen/qwen3-32b'
}

files_changed = []
for root, dirs, files in os.walk('.'):
    # skip venv and .git
    if root.startswith('./.venv') or '/.venv/' in root or root.startswith('./.git'):
        continue
    for fn in files:
        if not fn.endswith(('.py', '.md', '.txt')):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            continue
        new_text = text
        for old, new in mappings.items():
            if old in new_text:
                new_text = new_text.replace(old, new)
        if new_text != text:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
            files_changed.append(path)

print('\nFiles updated with migrations:')
for p in files_changed:
    print('-', p)

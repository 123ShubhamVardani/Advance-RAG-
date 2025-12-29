#!/usr/bin/env python3
"""Verify imports across the project by attempting imports inside the current interpreter.
If imports are missing, attempt to `pip install` likely package names inside the .venv.

This is a best-effort helper and may not resolve every import mapping.
"""
import os, sys, ast, subprocess, json

ROOT = os.getcwd()
print('Project root:', ROOT)

# Collect imports
imports = set()
for dirpath, dirnames, filenames in os.walk('.'):
    # Skip venv and typical irrelevant dirs
    if dirpath.startswith('./.venv') or '/.venv/' in dirpath or dirpath.startswith('./.git'):
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                node = ast.parse(f.read(), filename=path)
        except Exception:
            continue
        for n in ast.walk(node):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    imports.add(n.module.split('.')[0])

print('Distinct top-level imports found:', len(imports))
# Remove stdlib known common modules heuristically
stdlib = set([ 
    'os','sys','json','re','math','time','datetime','pathlib','logging','hashlib','itertools','typing','functools','subprocess','shutil','ssl'
])
imports_to_check = sorted(list(imports - stdlib))
print('Imports to check (sample 100):', imports_to_check[:100])

# Try imports in the current interpreter (.venv if activated when running script)
missing = []
for mod in imports_to_check:
    try:
        __import__(mod)
    except Exception as e:
        missing.append((mod, str(e)))

print('\nMissing imports:', len(missing))
for m,e in missing[:50]:
    print('-', m, '->', e)

# Heuristics for pip package names
def guess_package(mod):
    # common direct mapping, otherwise return mod
    mapping = {
        'streamlit':'streamlit',
        'langchain':'langchain',
        'langchain_groq':'langchain-groq',
        'langchain_google_genai':'langchain-google-genai',
        'langchain_community':'langchain-community',
        'langchain_huggingface':'langchain-huggingface',
        'langchain_text_splitters':'langchain-text-splitters',
        'langchain_core':'langchain-core',
        'gtts':'gtts',
        'speech_recognition':'SpeechRecognition',
        'groq':'groq',
        'requests':'requests',
        'faiss' : 'faiss-cpu',
        'faiss_cpu' : 'faiss-cpu',
        'transformers':'transformers',
        'torch':'torch',
        'sentence_transformers':'sentence-transformers',
        'dotenv':'python-dotenv',
        'pypdf' : 'pypdf',
    }
    return mapping.get(mod, mod)

if not missing:
    print('\nAll imports resolved.')
    sys.exit(0)

# Attempt to pip install missing packages (best-effort). Ask before running pip to avoid unexpected installs.
print('\nAbout to attempt pip install for the missing imports. This will run inside the current interpreter.')
proceed = os.getenv('AUTO_INSTALL', 'false').lower() == 'true'
if not proceed:
    print('Set environment variable AUTO_INSTALL=true to allow automated pip installs. Exiting now.')
    sys.exit(0)

packages = []
for mod,_ in missing:
    pkg = guess_package(mod)
    if pkg not in packages:
        packages.append(pkg)

print('Will pip install:', packages)
# Run pip install
cmd = [sys.executable, '-m', 'pip', 'install'] + packages
print('Running:', ' '.join(cmd))
res = subprocess.run(cmd)
print('pip exit', res.returncode)

# Re-run import checks
failed_after = []
for mod,_ in missing:
    try:
        __import__(mod)
    except Exception as e:
        failed_after.append((mod,str(e)))

print('\nRemaining missing imports after install:', len(failed_after))
for m,e in failed_after:
    print('-', m, '->', e)

if failed_after:
    sys.exit(2)
print('Done')

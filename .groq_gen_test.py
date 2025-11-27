# Lightweight Groq generation smoke test
import os, sys
# load .env manually
if os.path.exists('.env'):
    with open('.env') as f:
        for ln in f:
            ln=ln.strip()
            if not ln or ln.startswith('#'): continue
            if '=' in ln:
                k,v=ln.split('=',1); v=v.strip().strip('"').strip("'")
                os.environ[k.strip()]=v

key = os.getenv('GROQ_API_KEY')
if not key:
    print('No GROQ_API_KEY in environment')
    sys.exit(2)

import groq
import traceback

client = groq.Client(api_key=key)
# choose a compact model that's likely available; fall back to first model in list
model = os.getenv('GROQ_TEST_MODEL') or 'llama-3.1-8b-instant'
print('Using model:', model)
try:
    # prefer chat completions if available
    chat = getattr(client, 'chat', None)
    created = None
    if chat is not None and hasattr(chat, 'completions') and hasattr(chat.completions, 'create'):
        try:
            created = chat.completions.create(model=model, messages=[{'role':'user','content':'In one short sentence, say hello.'}], max_output_tokens=32)
        except TypeError:
            # different param names
            created = chat.completions.create(model=model, input='In one short sentence, say hello.', max_output_tokens=32)
    elif hasattr(client, 'responses') and hasattr(client.responses, 'create'):
        try:
            created = client.responses.create(model=model, input='In one short sentence, say hello.', max_output_tokens=32)
        except TypeError:
            created = client.responses.create(model=model, input=['In one short sentence, say hello.'], max_output_tokens=32)
    elif hasattr(client, 'completions') and hasattr(client.completions, 'create'):
        try:
            created = client.completions.create(model=model, input='In one short sentence, say hello.', max_output_tokens=32)
        except TypeError:
            created = client.completions.create(model=model, messages=[{'role':'user','content':'In one short sentence, say hello.'}], max_output_tokens=32)
    else:
        raise RuntimeError('No suitable completion endpoint found on client')

    print('Raw response repr:', repr(created)[:1000])
    # extract text
    text = None
    if hasattr(created, 'output_text') and created.output_text:
        text = created.output_text
    if text is None and hasattr(created, 'output'):
        out = getattr(created, 'output')
        if isinstance(out, (list, tuple)) and out:
            first = out[0]
            text = getattr(first, 'text', None) or getattr(first, 'content', None)
            if isinstance(text, (list, tuple)):
                text = text[0] if text else None
    if text is None and hasattr(created, 'choices'):
        ch = getattr(created, 'choices')
        if isinstance(ch, (list, tuple)) and ch:
            text = getattr(ch[0], 'text', None) or getattr(ch[0], 'message', None)
            if hasattr(text, 'get'):
                text = text.get('content') if isinstance(text, dict) else str(text)
    # final fallback
    if text is None:
        # maybe the created object has content attribute directly
        text = getattr(created, 'content', None)
    if text is None:
        text = str(created)
    print('\n=== Generated Text ===\n')
    print(text)
    print('\n=== End ===')
except Exception as e:
    print('Generation test failed:', type(e), e)
    traceback.print_exc()
    sys.exit(1)

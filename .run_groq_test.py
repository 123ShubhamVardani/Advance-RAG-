from dotenv import load_dotenv
load_dotenv()
import os, sys, traceback
sys.path.insert(0, os.getcwd())
import app

print('Loaded app module')
print('GROQ_ENV', bool(os.getenv('GROQ_API_KEY')))

try:
    llm = app.try_create_llm('groq', 'llama3-8b-8192')
    print('LLM object:', type(llm), repr(llm))
    if llm is None:
        print('LLM is None — creation failed or no API key/config')
        sys.exit(2)

    # Test invoke
    try:
        if hasattr(llm, 'invoke') and callable(llm.invoke):
            r = llm.invoke('Hello — test invoke')
            print('invoke ->', getattr(r, 'content', None))
        else:
            print('No invoke; trying __call__')
            r = llm('Hello — test call')
            print('__call__ ->', getattr(r, 'content', None))
    except Exception as e:
        print('invoke/__call__ raised:', e)
        traceback.print_exc()

    # Test generate
    try:
        if hasattr(llm, 'generate') and callable(llm.generate):
            out = llm.generate(['One', 'Two'])
            print('generate -> count', len(out))
            for i, item in enumerate(out):
                print(i, getattr(item, 'content', None))
        else:
            print('No generate method present')
    except Exception as e:
        print('generate raised:', e)
        traceback.print_exc()

except Exception as e:
    print('Error creating LLM:', e)
    traceback.print_exc()
    sys.exit(1)

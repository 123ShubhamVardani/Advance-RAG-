import os, subprocess, sys
env = os.environ.copy()
try:
    with open('.env','r') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if '=' in ln:
                k,v = ln.split('=',1)
                env[k.strip()] = v.strip()
except FileNotFoundError:
    pass
log = open('streamlit_run.log','ab')
proc = subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app.py'], env=env, stdout=log, stderr=subprocess.STDOUT)
print(proc.pid)

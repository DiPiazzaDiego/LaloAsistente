import subprocess
import time
import os
import sys

DIR = "C:/Users/Usuario/LaloAsistente"
PYTHON = "C:/Users/Usuario/LaloAsistente/.mamba_env/Scripts/python.exe"

# Entorno con PYTHONPATH
env = dict(os.environ)
env["PYTHONPATH"] = "C:/Users/Usuario/LaloAsistente/src"

# Iniciar el daemon con stdin como pipe (unidad de archivo en modo binario)
proc = subprocess.Popen(
    [PYTHON, "-m", "jarvis.main"],
    cwd=DIR,
    env=env,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=0,  # binario
)

print(f"Daemon PID: {proc.pid}", flush=True)

# Esperar a que inicie
time.sleep(12)

# Enviar consulta (bytes)
query = b"__CHAT_QUERY__:{\"text\":\"Hola, como te llamas?\"}\n"
try:
    proc.stdin.write(query)
    proc.stdin.flush()
    print("Consulta enviada", flush=True)
except Exception as e:
    print(f"Error escribiendo stdin: {e}", flush=True)

# Leer salidas
import threading
output_bytes = b""

def reader():
    global output_bytes
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output_bytes += line
        try:
            text = line.decode("utf-8", errors="replace")
        except:
            text = str(line)
        print("SALIDA:", text.rstrip(), flush=True)

import threading
t = threading.Thread(target=reader, daemon=True)
t.start()

start = time.time()
while time.time() - start < 55:
    if b"\u270d" in output_bytes or b"\xf0\x9f\x91\x86" in output_bytes:
        break
    time.sleep(1)

print("--- Estado ---", flush=True)
proc.poll()
print(f"Código de retorno: {proc.returncode}", flush=True)

# Terminar
try:
    proc.stdin.close()
except:
    pass
try:
    proc.kill()
except:
    pass

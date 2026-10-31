import subprocess
import time
import os
import sys

DIR = "C:/Users/Usuario/LaloAsistente"
PYTHON = "C:/Users/Usuario/LaloAsistente/.mamba_env/Scripts/python.exe"

print("=== Iniciando daemon Jarvis ===", flush=True)
env = dict(os.environ)
env["PYTHONPATH"] = "C:/Users/Usuario/LaloAsistente/src"

proc = subprocess.Popen(
    [PYTHON, "-m", "jarvis.main"],
    cwd=DIR,
    env=env,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=0,
)

print(f"Daemon PID: {proc.pid}", flush=True)
time.sleep(5)

# Leer la salida en un hilo
output_lines = []

def reader():
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output_lines.append(line.decode("utf-8", errors="replace"))
        print("SALIDA:", line.decode("utf-8", errors="replace").rstrip(), flush=True)

import threading
t = threading.Thread(target=reader, daemon=True)
t.start()

# Esperar a que inicie
time.sleep(10)

# Buscar indicios de que el whisper modelo está siendo descargado
whisper_started = any("Using whisper model" in l for l in output_lines)
print("Whisper modelo listo:", whisper_started, flush=True)

if whisper_started:
    print("Esperando descarga del modelo de voz (puede tardar minutos)...", flush=True)
    # Esperar hasta que el modelo esté listo
    start = time.time()
    while time.time() - start < 120:
        if any("Whisper model loaded" in l or "Whisper downloaded" in l for l in output_lines):
            break
        time.sleep(2)
    print("Modelo de voz listo.", flush=True)
else:
    print("ERROR: No se detectó inicio del whisper.", flush=True)

# Enviar consulta de prueba
query = b"__CHAT_QUERY__:{\"text\":\"Hola, como te llamas?\"}\n"
try:
    proc.stdin.write(query)
    proc.stdin.flush()
    print("Consulta enviada", flush=True)
except Exception as e:
    print(f"Error escribiendo stdin: {e}", flush=True)

# Mantener el pipe abierto mientras el daemon procesa (no cerrar proc.stdin)
# Esto evita que el daemon vea EOF y se cierre prematuramente
# Mantener el pipe abierto mientras el daemon descarga el modelo de voz (puede tardar minutos)
# Esto evita que el daemon vea EOF y se cierre prematuramente
print("Esperando descarga del modelo de voz (puede tardar minutos)...", flush=True)

# Esperar a que el modelo de voz se descargue (el daemon lo carga en un hilo)
# El output puede mostrarse de forma asíncrona
start = time.time()
while time.time() - start < 180:
    combined = b"".join([l for l in output_lines if isinstance(l, bytes)])
    if b"Whisper 'medium' (device" in combined and b"loaded" in combined:
        print("Modelo de voz cargado.", flush=True)
        break
    if proc.poll() is not None:
        print("Daemon terminó inesperadamente", flush=True)
        break
    time.sleep(1)

print("Esperando respuesta del daemon (máx 120s)...", flush=True)
start = time.time()
reply_received = False
while time.time() - start < 120:
    combined = b"".join([l for l in output_lines if isinstance(l, bytes)])
    if b"\u270d" in combined or b"\xf0\x9f\x91\x86" in combined or b"\U0001f4dd" in combined or b"\U0001f60a" in combined:
        reply_received = True
        break
    if proc.poll() is not None:
        print("Daemon terminó inesperadamente", flush=True)
        break
    time.sleep(1)

print("--- Estado ---", flush=True)
proc.poll()
print(f"Código retorno: {proc.returncode}", flush=True)
if proc.poll() is None:
    try:
        proc.kill()
    except:
        pass

print("=== Resumen ===", flush=True)
for l in output_lines:
    if any(k in l for k in ["Using chat model", "Using whisper model", "TTS engine started", "Microphone permission", "faster-whisper", "Reply"]):
        print("  ", l.rstrip())

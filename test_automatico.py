"""
TEST AUTOMÁTICO DE JARVIS
Rinde 3 preguntas y muestra las respuestas del asistente.
Ejecutar: python test_automatico.py
"""
import subprocess
import time
import sys
import os
import threading
import queue

# Preguntas predefinidas
QUESTIONS = [
    ("Básica", "Hola, ¿cómo te llamas?"),
    ("Información", "¿Qué tiempo hará mañana?"),
    ("Tarea", "¿Qué me recomendás hacer esta tarde?"),
]

# Marcador que indentifica las respuestas del daemon
MARKER = "🤖 Jarvis"

# Cola global para leer la salida del daemon
output_queue = queue.Queue()

# Hilo global para leer la salida
stdout_thread = None

def send_query(proc, text):
    """Enviar una pregunta al daemon via stdin."""
    query = f'__CHAT_QUERY__:{{"text":"{text}"}}\n'
    try:
        proc.stdin.write(query.encode('utf-8'))
        proc.stdin.flush()
        return True
    except Exception as e:
        print(f"  ❌ Error escribiendo: {e}", flush=True)
        return False

def start_daemon():
    """Inicia el daemon como proceso."""
    python = os.path.expandvars(r"%USERPROFILE%\.mamba_env\Scripts\python.exe")
    if not os.path.exists(python):
        python = r"C:\Users\Usuario\LaloAsistente\.mamba_env\Scripts\python.exe"
    
    env = dict(os.environ)
    env["PYTHONPATH"] = r"C:\Users\Usuario\LaloAsistente\src"
    
    proc = subprocess.Popen(
        [python, "-m", "jarvis.main"],
        cwd=r"C:\Users\Usuario\LaloAsistente",
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    return proc

def read_stdout_thread(proc):
    """Lee la salida del daemon en un hilo."""
    print(f"[Thread] Iniciando lectura (PID: {proc.pid})", flush=True)
    while True:
        line = proc.stdout.readline()
        if not line:
            print(f"[Thread] Fin de salida (PID: {proc.pid})", flush=True)
            break
        output_queue.put(line.decode('utf-8', errors='replace'))
    proc.stdout.close()
    print(f"[Thread] Terminado (PID: {proc.pid})", flush=True)

def wait_for_listening(proc, timeout=60):
    """Espera a que el daemon muestre 'Listening!'."""
    print("   Esperando a que el daemon esté listo...", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        # Buscar 'Listening!' en las líneas disponibles
        while not output_queue.empty():
            line = output_queue.get_nowait()
            print(f"[Queue] {line.strip()[:80]}...", flush=True)
            if "🎙️ Listening!" in line:
                print("   ✅ Daemon listo para escuchar", flush=True)
                return True
            if "Loading Whisper" in line:
                print("   ⏳ Cargando modelo de voz...", flush=True)
        
        # Verificar si el proceso terminó
        if proc.poll() is not None:
            print("   ❌ Daemon terminó antes de listo", flush=True)
            break
        
        # Verificar si el hilo está vivo
        global stdout_thread
        if stdout_thread is not None and not stdout_thread.is_alive():
            print("   ❌ Hilo de lectura terminó", flush=True)
            break
        
        time.sleep(0.5)
    return False

def main():
    print("=" * 60)
    print("  TEST AUTOMÁTICO DE JARVIS")
    print("=" * 60)
    print()

    # Iniciar el daemon
    print("1. Iniciando el daemon...")
    proc = start_daemon()
    print(f"   Daemon iniciado (PID: {proc.pid})")

    # Esperar a que esté listo
    if not wait_for_listening(proc, timeout=60):
        print("   ❌ No se pudo iniciar el daemon")
        proc.kill()
        return

    # Iniciar hilo para leer la salida
    stdout_thread = threading.Thread(target=read_stdout_thread, args=(proc,), daemon=True)
    stdout_thread.start()

    # Enviar preguntas
    print()
    print("2. Enviando preguntas...")
    responses = []
    for idx, (label, question) in enumerate(QUESTIONS, 1):
        print(f"   Enviando: {label} - {question}", flush=True)
        if not send_query(proc, question):
            print(f"   ❌ No se pudo enviar la pregunta {idx}", flush=True)
            continue
        
        # Esperar la respuesta (esta pregunta y la siguiente)
        # El daemon responde en un segundo (main loop)
        for expected in range(idx):
            time.sleep(3)  # Esperar la respuesta
            # Leer hasta algunos caracteres para ver si hay respuesta
            line = proc.stdout.readline()
            if line:
                text = line.decode('utf-8', errors='replace')
                if MARKER in text:
                    print(f"   ✅ {label}: respuesta recibida", flush=True)
                    # Leer la respuesta completa
                    response = proc.stdout.readline().decode('utf-8', errors='replace')
                    print(f"   🤖 {label}: {response[:150]}...", flush=True)
                    responses.append((label, question, response.strip()))
                    break
    print()

    # Mostrar resultados
    print("=" * 60)
    print("  RESULTADOS")
    print("=" * 60)
    for label, question, response in responses:
        print(f"\n  [{label}] {question}")
        print(f"  🤖 {response}")
    print()
    print("=" * 60)

    # Detener el daemon
    if proc.poll() is None:
        try:
            proc.stdin.write(b"SHUTDOWN\n")
            proc.stdin.flush()
            proc.kill()
        except:
            pass

if __name__ == "__main__":
    main()

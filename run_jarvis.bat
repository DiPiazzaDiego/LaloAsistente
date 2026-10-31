@echo off
rem ── Jarvis Voice Assistant ──────────────────────────────────────────────
rem Arranca el daemon del asistente local (Ollama + Whisper + Piper TTS)
rem
rem Requiere: entorno .mamba_env ya creado (ver README.md / requirements.txt)
rem ───────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

rem Asegura que el paquete jarvis (en src/) se encuentre en el path
set "PYTHONPATH=%CD%\src"

echo.
echo ┌─────────────────────────────────────────────────────────────┐
echo │  Jarvis Voice Assistant v0.1                                │
echo │  Modelo de chat: llama3.2:3b (local, Ollama)               │
echo │  Whisper: medium   [TTS] piper (Piper AI)                   │
echo └─────────────────────────────────────────────────────────────┘
echo.

.mamba_env\Scripts\python.exe -m jarvis.main

echo.
echo Jarvis detenido.
pause

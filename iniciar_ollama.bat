@echo off
rem Liga o Ollama 0.40.4 usado pelo benchmark (ver ambiente.py).
rem Deixe esta janela aberta enquanto o benchmark roda; para desligar, feche a janela.
set OLLAMA_HOST=127.0.0.1:11500
"%LOCALAPPDATA%\Programs\Ollama-0.40.4\ollama.exe" serve

@echo off
chcp 65001 >nul
rem ============================================================================
rem Lançador do benchmark: um duplo clique liga tudo e abre o painel no navegador.
rem Analogia: a chave de ignição do carro. Ela não dirige por você; só liga o
rem motor (Ollama) e acende o painel (dashboard), na ordem certa.
rem
rem O que ele faz:
rem   1. Liga o Ollama 0.40.4 (porta 11500), se ainda não estiver ligado.
rem   2. Liga o painel Streamlit (porta 8501), se ainda não estiver ligado.
rem   3. Espera o painel responder e abre o navegador nele.
rem As duas janelas minimizadas ("Ollama 0.40.4" e "Painel do benchmark") são os
rem servidores: para desligar, feche-as. Esta janela se fecha sozinha no fim.
rem ============================================================================

rem %~dp0 = a pasta onde este .bat está. Assim o atalho funciona de qualquer lugar.
cd /d "%~dp0"

rem --- 1. Ollama fixado --------------------------------------------------------
rem curl pergunta a versão ao servidor. Se ninguém responder, errorlevel fica
rem diferente de 0, e o servidor é ligado numa janela própria e minimizada.
rem A conferência da VERSÃO continua em ambiente.py, antes de cada execução.
curl -s -m 3 http://127.0.0.1:11500/api/version >nul 2>&1
if errorlevel 1 (
    echo Ligando o Ollama 0.40.4 na porta 11500...
    start "Ollama 0.40.4" /min cmd /c "%~dp0iniciar_ollama.bat"
) else (
    echo O Ollama da porta 11500 já estava ligado.
)

rem --- 2. Painel ----------------------------------------------------------------
rem --server.headless true: o Streamlit não abre o navegador nem faz perguntas no
rem primeiro uso; quem abre o navegador é o passo 3.
curl -s -m 3 http://localhost:8501/_stcore/health >nul 2>&1
if errorlevel 1 (
    echo Ligando o painel na porta 8501...
    start "Painel do benchmark" /min ".venv\Scripts\streamlit.exe" run app.py --server.headless true --server.port 8501
) else (
    echo O painel já estava ligado.
)

rem --- 3. Esperar o painel e abrir o navegador ------------------------------------
rem Um laço com contador: tenta até 30 vezes, uma por segundo (ping serve de
rem relógio de 1 s). Se o painel não responder, avisa em vez de esperar para sempre.
set /a tentativas=0
:esperar_painel
curl -s -m 2 http://localhost:8501/_stcore/health >nul 2>&1
if not errorlevel 1 goto abrir
set /a tentativas+=1
if %tentativas% geq 30 goto falhou
ping -n 2 127.0.0.1 >nul
goto esperar_painel

:abrir
echo Abrindo o painel no navegador...
start "" http://localhost:8501
exit /b 0

:falhou
echo.
echo O painel não respondeu em 30 segundos.
echo Abra a janela "Painel do benchmark" na barra de tarefas para ver o erro.
pause
exit /b 1

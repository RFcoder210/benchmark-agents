Ambiente pronto: SIM — 2026-11-20

| item | versão | comando de verificação | status |
|---|---|---|---|
| Python | 3.14.6 | `py --version` | OK |
| Bibliotecas (.venv) | streamlit 1.66.0, altair 6.3.0, ollama 0.6.3, pandas 3.0.6 | `.venv/Scripts/python -c "import streamlit, altair, ollama, pandas"` | OK |
| Recursos do Streamlit (fragment, page_link, cache_resource) | 1.66.0 | `.venv/Scripts/python -c "import streamlit as st; print(all(hasattr(st, n) for n in ['fragment','page_link','cache_resource']))"` | OK (True) |
| Ollama 0.40.4 portátil (arquivo) | 0.40.4 | `ls "$LOCALAPPDATA/Programs/Ollama-0.40.4/ollama.exe"` | OK |
| Servidor Ollama 0.40.4 ligado (porta 11500) | - | `curl -s http://127.0.0.1:11500/api/version` | AGUARDA USUÁRIO (só necessário na T10; ligar com o atalho "Benchmark de agentes" ou `.\iniciar_ollama.bat`) |
| Git | 2.55.0 | `git --version` | OK |
| testar_comparar.py | 14/14 | `.venv/Scripts/python testar_comparar.py` | OK |
| testar_regua.py | 11/11 | `.venv/Scripts/python testar_regua.py` | OK |
| testar_trava_pagamento.py | "Tudo certo." | `.venv/Scripts/python testar_trava_pagamento.py` | OK |
| testar_executar.py | 6/6 (Ollama desligado) | `.venv/Scripts/python testar_executar.py` | OK |
| testar_dashboard.py | 43/43 | `.venv/Scripts/python testar_dashboard.py` | OK |
| testar_mutacao.py | sobreviveram 1/13 e 0/10 | `.venv/Scripts/python testar_mutacao.py` | OK |

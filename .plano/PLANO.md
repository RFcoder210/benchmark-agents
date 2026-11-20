# Plano — App pessoal do benchmark: botão "Executar" ligado

## Resumo do objetivo
Permitir rodar o benchmark do agente de gastos pelo painel Streamlit (`app.py`, página "Executar"), sem a sessão do Claude: escolher o rótulo, confirmar antes de gravar no CSV oficial, rodar em segundo plano com barra de progresso e ver o resultado na "Visão geral". O agente (v15) não muda. O conjunto oculto não aparece no app.

### Critérios de conclusão (de `.plano/OBJETIVO.md`)
- `benchmark.py --rotulo <rótulo>` funciona, com teste automático; sem opções, nada muda.
- Página "Executar" com o botão ligado: confere o Ollama 0.40.4 (porta 11500) e o rótulo, pede confirmação antes de gravar em `resultados/resultados.csv`, roda em segundo plano e mostra o progresso.
- Nenhum botão ou opção para o conjunto oculto.
- Rótulo já existente no CSV é **recusado** (decisão deste plano; ver "Decisões").
- `testar_executar.py`, `testar_dashboard.py` e os demais testes sem modelo passam.
- Execução real `v15-repeticao` feita pelo usuário pelo botão, gravada no CSV e visível como lote de calibração.
- README e CLAUDE.md atualizados.

## Desenho da solução (referência para todas as tarefas)
- **`benchmark.py`** ganha duas funções puras, escritas pelo usuário:
  - `rotulo_invalido(rotulo) -> str | None`: `None` se o rótulo serve; senão, o motivo em português. Regras: não vazio; até 40 caracteres; só letras sem acento, dígitos, `.`, `_` e `-` (o rótulo vai no nome do arquivo de brutos e numa coluna do CSV separado por `;`); não pode terminar em `-oculto` (reservado à validação final).
  - `escolher_execucao(argv=None) -> (arquivo_de_casos, rotulo)`, com `argparse`: sem opções → `(ARQUIVO_CASOS, VERSAO_AGENTE)`; `--rotulo X` → `(ARQUIVO_CASOS, X)`; `--ocultos` → `(ARQUIVO_CASOS_OCULTOS, f"{VERSAO_AGENTE}-oculto")`; `--ocultos` com `--rotulo`, `--rotulo` sem valor, rótulo inválido ou opção desconhecida → erro do argparse (`SystemExit` com código 2).
  - O bloco `__main__` passa a chamar `escolher_execucao()` **antes** de `conferir_ollama()`, para que erros de opção apareçam sem o servidor.
- **`execucao.py`** (módulo novo, sem tela):
  - Funções puras escritas pelo usuário: `ler_progresso(texto_log) -> (feitas, total)` e `pode_executar(versao_ollama, rotulo, ja_gravadas, em_andamento=False) -> str | None` (o motivo do bloqueio ou `None`).
  - Encanamento escrito pelo executor: `montar_comando(rotulo)`, `iniciar(rotulo, comando=None, pasta_logs=PASTA_LOGS)` com `subprocess.Popen` (`-u`, `PYTHONIOENCODING=utf-8`, `CREATE_NO_WINDOW`, log em `resultados/logs/`, ignorado pelo git) e `situacao(execucao)`.
- **`app_pages/executar.py`**: campo de rótulo pré-preenchido com `{VERSAO_AGENTE}-repeticao`, motivo do bloqueio vindo de `pode_executar()`, caixa de confirmação ("acrescentar 45 linhas ao CSV com o rótulo X") que libera o botão, processo guardado em `st.cache_resource`, progresso por `st.fragment(run_every=...)`, resultado final e link para a "Visão geral".
- **Confirmação antes de gravar** = confirmação antes de iniciar. O `benchmark.py` só grava o CSV depois das 45 respostas; interromper no meio não grava nada.

## Pré-requisitos do ambiente
O ambiente já funciona; o `preparacao-terreno` só **verifica e registra** em `.plano/AMBIENTE.md`. Nada a instalar.

| Item | Versão esperada | Comando de verificação (Git Bash, na raiz do projeto) |
|---|---|---|
| Python | 3.14.x | `py --version` |
| Ambiente virtual e bibliotecas | streamlit 1.66.0, altair 6.3.0, ollama 0.6.3, pandas 3.0.6 | `.venv/Scripts/python -c "import streamlit, altair, ollama, pandas; print(streamlit.__version__, altair.__version__)"` |
| Recursos do Streamlit usados no plano | `st.fragment`, `st.page_link`, `st.cache_resource` | `.venv/Scripts/python -c "import streamlit as st; print(all(hasattr(st, n) for n in ['fragment', 'page_link', 'cache_resource']))"` → `True` |
| Ollama 0.40.4 portátil (arquivo) | 0.40.4 | `ls "$LOCALAPPDATA/Programs/Ollama-0.40.4/ollama.exe"` |
| Servidor Ollama 0.40.4 ligado | 0.40.4 na porta 11500 | Só necessário na T10. Marcar **AGUARDA USUÁRIO** (ele liga com o atalho "Benchmark de agentes" ou `.\iniciar_ollama.bat`). Verificação quando ligado: `curl -s http://127.0.0.1:11500/api/version` |
| Git | qualquer 2.x | `git --version` |
| Linha de base dos testes sem modelo | todos passando | ver lista abaixo |

Linha de base dos testes (definir `export PYTHONIOENCODING=utf-8` antes, para os acentos):
- `.venv/Scripts/python testar_comparar.py` → "14/14 exemplos passaram" e nenhuma linha com `FALHA`
- `.venv/Scripts/python testar_regua.py` → "11/11 exemplos passaram"
- `.venv/Scripts/python testar_trava_pagamento.py` → termina com "Tudo certo."
- `.venv/Scripts/python testar_executar.py` → "6/6 verificações passaram" (9/9 com o Ollama ligado)
- `.venv/Scripts/python testar_dashboard.py` → "43/43 verificações passaram"
- `.venv/Scripts/python testar_mutacao.py` → "Sobreviveram aos testes: 1/13" e "Sobreviveram: 0/10"

Outros itens:
- **Skills**: nenhuma nova (cada tarefa traz os próprios comandos).
- **Documentação**: não reorganizar `docs/` nem criar `docs/INDICE.md` (a pasta só tem dois PDFs do usuário).
- **Pastas**: `resultados/logs/` será criada pela T07; não criar antes.
- **Git**: a escolha do ramo é a T01 (AGUARDA USUÁRIO); o `preparacao-terreno` não cria nem troca ramos.
- **Nunca**: abrir `casos/casos_ocultos.json`, rodar `benchmark.py` sem `--help`, gravar em `resultados/resultados.csv`.

## Fases e tarefas

### Fase 0 — Ramo de trabalho
- T01 (U) AGUARDA USUÁRIO: decidir o ramo de trabalho e as permissões pendentes — P

### Fase 1 — Opção `--rotulo` (entrega 1)
- T02 Teste e esqueleto da opção `--rotulo` — P (executor escreve `testar_rotulo.py` e o esqueleto comentado das duas funções)
- T03 (U) AGUARDA USUÁRIO: escrever `rotulo_invalido()` e `escolher_execucao()` e ligar no `__main__` — P
- T04 Conferir a opção `--rotulo` pela linha de comando — P
- Ao final: commit da entrega 1, com aprovação do usuário (pelo orquestrador ou no `/encerrar-dia`).

### Fase 2 — Botão ligado (entrega 2)
- T05 Teste e esqueleto das regras da execução (`execucao.py`, `testar_execucao.py`) — P
- T06 (U) AGUARDA USUÁRIO: escrever `ler_progresso()` e `pode_executar()` — P
- T07 Lançar e acompanhar o benchmark em segundo plano (`execucao.py`, `testar_processo.py`, `.gitignore`) — M
- T08 Página Executar: rótulo, confirmação e botão ligado (`app_pages/executar.py`, `testar_executar.py`) — M
- T09 Página Executar: barra de progresso e resultado — M
- Ao final: commit da entrega 2, com aprovação do usuário.

### Fase 3 — Execução real e documentação (entrega 3)
- T10 (U) AGUARDA USUÁRIO: execução real `v15-repeticao` pelo botão — P
- T11 Conferir a execução real e a suíte de testes — P
- T12 Documentar a página Executar no README e no CLAUDE.md — P
- T13 (U) AGUARDA USUÁRIO: aprovar o commit final e o push — P

**Commits** (sempre com aprovação do usuário, seguidos de `git push`): recomenda-se um commit ao fim de cada tarefa do usuário (T03, T06) e ao fim de cada fase. Motivo: o fiscal automático confere a seção "Não alterar" pelo `git status`, e um arquivo novo ainda não commitado de uma tarefa anterior aparece como "alterado", gerando bloqueios falsos.

Carga do executor: 8 tarefas (5 P + 3 M = 14 unidades). Tarefas do usuário: 5 (T01, T03, T06, T10, T13). Sem prazo fixo; com 2 h por sessão, a estimativa é de 5 a 7 sessões.

## Decisões tomadas neste plano (o usuário pode trocar antes da execução)
1. **Rótulo repetido é recusado** (não há "confirmar mesmo assim"). Para repetir de novo, usa-se outro rótulo (`v15-repeticao2`). Motivo: o painel e a régua comparam pela execução mais recente de cada rótulo, e duas execuções no mesmo rótulo confundem a leitura.
2. **A confirmação acontece antes de iniciar**, por caixa de seleção que libera o botão (e não por janela `st.dialog`, que o AppTest testa mal). Alternativa descartada: rodar sem gravar e pedir confirmação no fim (exigiria uma opção `--sem-csv` e um segundo caminho de gravação).
3. **Rótulo sem hífen é permitido, com aviso** de que aparecerá como versão oficial no painel. O padrão sugerido é `{VERSAO_AGENTE}-repeticao`.
4. **Logs da execução** ficam em `resultados/logs/` e não vão para o git (os brutos já guardam as respostas).
5. **Sem botão de cancelar** nesta versão (pode entrar depois; cancelar seria seguro, porque o CSV só é gravado no fim).

## Riscos principais e contingência
| Risco | Contingência |
|---|---|
| Executor roda o benchmark de verdade e grava no CSV | Todas as tarefas listam `resultados/resultados.csv` em "Não alterar" (o fiscal confere pelo git) e proíbem rodar `benchmark.py` com rótulo válido. Se acontecer: `git checkout -- resultados/resultados.csv` e apagar o brutos criado, com aviso ao usuário. |
| AppTest não aceita a substituição de `execucao.montar_comando` (clique com comando falso) | Testar o encanamento só em `testar_processo.py` (sem página) e, na página, testar apenas os estados sem clicar no botão final; registrar a limitação no Resultado da tarefa. |
| Progresso não aparece durante a execução (buffer) | `-u` e `PYTHONUNBUFFERED=1` no processo filho; `testar_processo.py` confere que a contagem avança antes do fim. |
| Processo perdido ou lançado duas vezes ao recarregar a página | Guardar o processo em `st.cache_resource`; `pode_executar(..., em_andamento=True)` bloqueia um segundo lançamento. Se o servidor do painel for fechado no meio, o processo pode seguir sozinho e gravar no fim: documentar no README. |
| Ollama cai no meio (já houve "CUDA error" em 27/10) | O benchmark termina com erro antes de gravar; a página mostra as últimas linhas do log e diz se algo foi gravado (contando o rótulo no CSV). O usuário roda de novo. |
| Mudança em `benchmark.py` quebra `testar_mutacao.py` | Não tocar em `comparar()`, `classificar_erro()` e `CAMPOS_GASTO`; nada novo no nível do módulo além de funções e constantes. A suíte inteira roda ao fim de cada tarefa. |
| `testar_dashboard.py` ou `testar_executar.py` falham depois da execução real (dados novos no CSV) | Os testes calculam o esperado a partir do CSV; se ainda assim falharem, a T11 registra a pendência sem alterar os testes. |
| Sessão do usuário mais lenta que o previsto | Sem prazo fixo; as tarefas do usuário vêm com teste pronto e esqueleto comentado, para caber numa sessão de 2 h. |

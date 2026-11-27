# Estado do projeto — 2026-11-20

Diagnóstico feito pelo `analise-projeto` a partir de `.plano/OBJETIVO.md` (primeiro uso da orquestração neste projeto).

## O que já existe e funciona
- **Benchmark v1 concluído**: `benchmark.py` roda 15 casos × 3 ordens dos exemplos (45 respostas, 4 a 5 min), grava `resultados/brutos_<rótulo>_<carimbo>.json` e acrescenta 45 linhas em `resultados/resultados.csv` (`;`, vírgula decimal). Base oficial: v15 (44/45; 15/15 no oculto).
- **Rótulo da execução**: definido só por `VERSAO_AGENTE = "v15"` (linha 25 de `benchmark.py`). O bloco `if __name__ == "__main__"` (linhas 456-480) lê `sys.argv` à mão e só conhece `--ocultos` (rótulo fixo `v15-oculto`). Opções desconhecidas são ignoradas. A conferência do Ollama (`ambiente.conferir_ollama()`) é a primeira coisa do bloco.
- **Progresso na tela**: `executar_casos()` imprime uma linha por resposta no formato `[ 7/45] C03 #1 (original) -> registrar (2.8 s)`; ao final, `Resultados acrescentados em ...` e `Acerto geral: 44/45 (98%)`. O CSV só é gravado depois das 45 respostas: uma execução interrompida no meio não grava nada no CSV.
- **Painel**: `app.py` (menu `st.navigation`) com "Visão geral" (`dashboard.py`, só lê o CSV; recarrega sozinho quando o CSV muda, pela data de modificação) e "Executar" (`app_pages/executar.py`, etapa 1: confere o Ollama 0.40.4 na porta 11500 e se `VERSAO_AGENTE` já existe no CSV; botão `Executar` desligado). `contar_execucoes(rotulo)` já existe na página.
- **Lotes de calibração**: o painel trata como calibração todo rótulo com hífen (`dashboard.py`, linha 87). Um rótulo `v15-repeticao` aparecerá automaticamente como calibração, sem mudar o dashboard.
- **Ambiente** (conferido em 2026-11-20): `.venv` com streamlit 1.66.0 e altair 6.3.0 (requisitos em `requirements.txt`); `st.fragment(run_every=...)` e `st.page_link` estão disponíveis nessa versão. Ollama 0.40.4 portátil e lançador `abrir_benchmark.bat` funcionando (segundo o usuário). Nenhuma biblioteca nova é necessária.
- **Testes sem modelo** (rodados em 2026-11-20, todos passando): `testar_comparar.py` (14/14 na Parte A), `testar_regua.py` (11/11), `testar_trava_pagamento.py` ("Tudo certo."), `testar_executar.py` (6/6 com o Ollama desligado; 9/9 com ele ligado), `testar_dashboard.py` (43/43), `testar_mutacao.py` (Partes A e B; 1/13 mutante sobrevivente, o equivalente já conhecido). Esses scripts imprimem o resultado, mas não devolvem código de saída diferente de zero quando falham: confira pelo texto.
- **Git**: ramo atual `config/permissoes-leitura`, com `.claude/settings.json` e `.plano/DIARIO.md` alterados e `.plano/OBJETIVO.md` novo, nada commitado. `main` local igual à do GitHub (público).

## O que falta (o objetivo)
1. Opção `--rotulo` no `benchmark.py`, com teste automático, sem mudar o comportamento sem opções.
2. Botão `Executar` ligado: rótulo escolhido, recusa de rótulo repetido, inválido ou reservado (`-oculto`), confirmação antes de gravar no CSV, execução em segundo plano com barra de progresso, resultado visível no painel. Nenhuma opção para o conjunto oculto.
3. Uma execução real pelo botão (`v15-repeticao`), feita pelo usuário.
4. README e CLAUDE.md atualizados.

## Riscos identificados
- **Gravar no CSV por engano**: rodar `benchmark.py` com um rótulo válido e o Ollama ligado grava 45 linhas no histórico oficial. Nenhuma tarefa de executor pode rodar o benchmark de verdade; só `--help` e rótulos inválidos, e os testes usam comandos falsos.
- **Testes do botão disparando o benchmark real**: o AppTest roda a página por dentro; um clique em `Executar` num teste precisa usar um comando falso (substituição de `execucao.montar_comando`).
- **Processo em segundo plano no Windows**: saída com buffer (sem `-u` o progresso só aparece no fim), acentos no log (definir `PYTHONIOENCODING=utf-8`), janela de console abrindo (`CREATE_NO_WINDOW`) e `os.kill(pid, 0)`, que no Windows **encerra** o processo (não usar para checar se ele está vivo; usar `Popen.poll()`).
- **Recarga da página**: o Streamlit roda o script de novo a cada clique; o processo precisa ficar guardado em `st.cache_resource` para não ser lançado duas vezes nem perdido.
- **`testar_mutacao.py`** lê `benchmark.py` como texto e executa o módulo com outro nome: código novo no nível do módulo (fora de funções) roda nesse momento. A leitura das opções precisa ficar dentro de função, chamada só no bloco `__main__`. Não mexer em `comparar()` nem em `classificar_erro()`.
- **Ritmo de aprendizado**: as partes centrais (leitura das opções, regras de permissão e leitura do progresso) são escritas pelo usuário, com testes prontos antes; isso alonga o calendário, de propósito.

## Tarefas

| ID | Título | Porte | Executor | Revisão | Status | Depende de |
|---|---|---|---|---|---|---|
| T01 | (U) AGUARDA USUÁRIO: decidir o ramo de trabalho e as permissões pendentes | P | usuário | nenhuma | CONCLUIDA | nenhuma |
| T02 | Teste e esqueleto da opção --rotulo | P | executor-tarefa | nenhuma | CONCLUIDA | T01 |
| T03 | (U) AGUARDA USUÁRIO: escrever rotulo_invalido() e escolher_execucao() | P | usuário | nenhuma | CONCLUIDA | T02 |
| T04 | Conferir a opção --rotulo pela linha de comando | P | executor-tarefa | nenhuma | CONCLUIDA | T03 |
| T05 | Teste e esqueleto das regras da execução (execucao.py) | P | executor-tarefa | nenhuma | CONCLUIDA | T04 |
| T06 | (U) AGUARDA USUÁRIO: escrever ler_progresso() e pode_executar() | P | usuário | nenhuma | CONCLUIDA | T05 |
| T07 | Lançar e acompanhar o benchmark em segundo plano (execucao.py) | M | executor-tarefa | nenhuma | CONCLUIDA | T06 |
| T08 | Página Executar: rótulo, confirmação e botão ligado | M | executor-tarefa | nenhuma | CONCLUIDA | T07 |
| T09 | Página Executar: barra de progresso e resultado | M | executor-tarefa | nenhuma | CONCLUIDA | T08 |
| T10 | (U) AGUARDA USUÁRIO: execução real v15-repeticao pelo botão | P | usuário | nenhuma | CONCLUIDA | T09 |
| T11 | Conferir a execução real e a suíte de testes | P | executor-tarefa | nenhuma | CONCLUIDA | T10 |
| T12 | Documentar a página Executar no README e no CLAUDE.md | P | executor-tarefa | nenhuma | PENDENTE | T11 |
| T13 | (U) AGUARDA USUÁRIO: aprovar o commit final e o push | P | usuário | nenhuma | PENDENTE | T12 |

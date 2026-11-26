# T08 — Página Executar: rótulo, confirmação e botão ligado

**Fase:** 2 — Botão ligado (entrega 2)
**Porte:** M
**Depende de:** T07
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
A página "Executar" (`app_pages/executar.py`, aberta pelo menu de `app.py`) está na etapa 1: confere o Ollama e o rótulo `VERSAO_AGENTE`, com o botão desligado. Agora ela passa a: deixar o usuário escolher o rótulo, recusar rótulo inválido, reservado ou repetido, pedir confirmação explícita antes de gravar no CSV oficial e, ao clicar, lançar o benchmark em segundo plano por `execucao.iniciar()`. A barra de progresso e o resultado final ficam para a T09; aqui basta uma mensagem de "execução iniciada".

## Arquivos para ler
- `app_pages/executar.py` (82 linhas, inteiro)
- `testar_executar.py` (72 linhas, inteiro)
- `execucao.py`: assinaturas e docstrings de `pode_executar()`, `iniciar()`, `situacao()`, `montar_comando()` (não precisa ler os corpos)
- `benchmark.py`: constantes `ARQUIVO_CSV`, `ARQUIVO_CASOS`, `VERSAO_AGENTE`, `ORDENS_EXEMPLOS`, `N_EXECUCOES` e a função `carregar_casos()`
- `.streamlit/config.toml` (tema; a página não usa CSS próprio)

## O que fazer
1. Em `app_pages/executar.py` (mantenha os comentários para iniciante e atualize o cabeçalho: etapa 2):
   - Seção 1 (Ollama): sem mudança de comportamento.
   - Seção 2 ("Rótulo da execução"): `st.text_input("Rótulo da execução", value=f"{VERSAO_AGENTE}-repeticao", help=...)`. Mostre que o agente em uso é `VERSAO_AGENTE`. Com `contar_execucoes(rotulo)` (já existe na página): se > 0, `st.warning` com o texto atual "O rótulo **X** já tem N execuções no CSV..." (mantenha a frase "já tem N execuções"); se 0, `st.info` dizendo que é um rótulo novo. Se o rótulo não tiver hífen, `st.warning` avisando que ele aparecerá no painel como **versão oficial** (com hífen, vira lote de calibração).
   - Seção 3 ("Execução"): guarde a execução num registro compartilhado por `@st.cache_resource` (uma função que devolve um dicionário `{"execucao": None}`), para não perdê-la a cada recarga da página. `em_andamento` = há execução e `execucao.situacao(...)["rodando"]`. Calcule `motivo = execucao.pode_executar(ambiente.versao_ollama(), rotulo, contar_execucoes(rotulo), em_andamento)` (reaproveite a versão já lida na seção 1).
     - Com motivo: `st.warning(motivo)` e `st.button("Executar", disabled=True)`.
     - Sem motivo: `st.checkbox` com o texto "Confirmo: acrescentar N linhas a `resultados/resultados.csv` com o rótulo **X**", onde N = `len(carregar_casos(ARQUIVO_CASOS)) * len(ORDENS_EXEMPLOS) * N_EXECUCOES` (45 hoje; não escreva 45 fixo), e `st.button("Executar", type="primary", disabled=not confirmado)`. Ao clicar: `registro["execucao"] = execucao.iniciar(rotulo)` e `st.rerun()`.
     - Havendo execução registrada: `st.info` com o rótulo, a hora de início e o caminho do log (a T09 troca isso pela barra de progresso).
   - Mantenha a nota de que o conjunto oculto não tem botão nesta página. Nenhum widget com a palavra "oculto" no rótulo.
2. Reescreva `testar_executar.py` mantendo o formato (lista de resultados, relatório `N/M verificações passaram`) e acrescentando `sys.exit(0 if tudo passou else 1)`. Antes de cada cenário, chame `st.cache_resource.clear()` para zerar o registro. Para simular o Ollama ligado sem depender dele, troque temporariamente `ambiente.versao_ollama` por uma função que devolve `ambiente.VERSAO_OLLAMA` (o AppTest roda a página no mesmo processo; restaure no fim). Verificações mínimas:
   - Desligado (`OLLAMA_HOST=127.0.0.1:1`, sem troca): sem exceção; erro "não está ligado"; sem sucesso; botão `Executar` existe e está desligado; nenhuma caixa de confirmação.
   - Rótulo padrão do campo == `f"{VERSAO_AGENTE}-repeticao"`.
   - Rótulo `VERSAO_AGENTE`: aviso "já tem {esperadas} execuções" (esperadas contadas direto do CSV, como hoje).
   - Com Ollama simulado: rótulo `VERSAO_AGENTE` → botão desligado e aviso contendo "outro"; rótulo `"a b"` → botão desligado; rótulo `f"{VERSAO_AGENTE}-oculto"` → botão desligado; rótulo `"v99"` → aviso "versão oficial".
   - Com Ollama simulado e rótulo novo (gere um que não exista no CSV, ex.: `teste-pagina-<carimbo>`): caixa de confirmação presente; botão desligado antes de marcar; ligado depois de marcar.
   - Clique com **comando falso**: troque temporariamente `execucao.montar_comando` por uma função que devolve `[sys.executable, "-c", "print('[ 1/1] C01 #1 (original) -> registrar (0.1 s)')"]`; marque, clique e confira: sem exceção, aparece a mensagem de execução iniciada com o rótulo; espere o processo falso terminar (até 10 s) e apague o log que ele criou. Confira que `resultados/resultados.csv` tem o mesmo tamanho e data de modificação de antes do teste e que não surgiu nenhum `resultados/brutos_teste-pagina-*`.
   - Nenhum widget (botão, caixa, campo de texto, seleção) com "oculto" no rótulo.
   - Ligado de verdade (só se `ambiente.versao_ollama()` real devolver a versão fixada; senão, `PULADO`): sem exceção, sucesso, sem erro. **Não clicar em Executar neste cenário.**
3. Rode a suíte inteira.

## Arquivos a criar ou alterar
- `app_pages/executar.py`
- `testar_executar.py`

## Critério de pronto (verificável)
- [ ] `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_executar.py; echo "saida=$?"` → todas as verificações passam (com `PULADO` permitido no cenário do Ollama real), `saida=0`.
- [ ] `git status --short resultados/` não lista `resultados.csv` nem brutos novos; `ls resultados/logs/` não tem logs `execucao_teste-pagina-*`.
- [ ] `testar_dashboard.py` 43/43; `testar_processo.py`, `testar_execucao.py` e `testar_rotulo.py` com saída 0.

## Não alterar
- `testar_dashboard.py`
- `dashboard.py`
- `app.py`
- `benchmark.py`
- `testar_rotulo.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- **Nunca clique em Executar com o comando real.** Todo clique em teste usa `execucao.montar_comando` trocado por um comando falso; confira a troca antes de clicar. O comando real roda o modelo por 4 a 5 minutos e grava 45 linhas no CSV oficial.
- Não altere `execucao.py`, `testar_execucao.py` nem `testar_processo.py` (código e testes das tarefas anteriores; as funções `ler_progresso()` e `pode_executar()` são do usuário). Se algo nelas impedir a tarefa, declare PENDENTE.
- Se o AppTest não enxergar a troca de `execucao.montar_comando` ou de `ambiente.versao_ollama` (o clique lançaria o comando real), **não clique**: remova esse cenário, registre a limitação no Resultado e siga com os demais.
- Sem CSS próprio nem `unsafe_allow_html`: só componentes do Streamlit e o tema.
- `st.dialog` não é usado (o AppTest testa mal janelas); a confirmação é a caixa de seleção.
- Nunca abra `casos/casos_ocultos.json`.

## Resultado
Concluída. `app_pages/executar.py` (etapa 2): campo de rótulo, avisos (já gravado / novo / sem hífen), `pode_executar`, caixa de confirmação com N calculado, botão que chama `execucao.iniciar` via registro `@st.cache_resource`, mensagem de execução iniciada. `testar_executar.py` reescrito: 24/24, saída 0 (cenário do Ollama real PULADO, pois está desligado). Cliques só com comando falso; CSV com mesmo tamanho e data; sem brutos nem logs `teste-pagina-*`. Suíte: testar_dashboard 43/43, testar_processo 13/13, testar_execucao 15/15, testar_rotulo 25/25. `git status resultados/` limpo.

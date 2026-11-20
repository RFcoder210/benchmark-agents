# T09 — Página Executar: barra de progresso e resultado

**Fase:** 2 — Botão ligado (entrega 2)
**Porte:** M
**Depende de:** T08
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
Depois da T08, o botão "Executar" lança o benchmark em segundo plano e a página só diz "execução iniciada". Falta acompanhar: uma barra de progresso que se atualiza sozinha durante os 4 a 5 minutos (45 respostas), o resultado final (acerto geral ou erro, com a informação de se algo foi gravado no CSV), um atalho para a "Visão geral" e um botão para liberar uma nova execução. Tudo testado com comandos falsos.

## Arquivos para ler
- `app_pages/executar.py` (inteiro, como ficou na T08)
- `testar_executar.py` (inteiro, como ficou na T08)
- `execucao.py`: docstring de `situacao()` (chaves `rodando`, `codigo_saida`, `feitas`, `total`, `acerto`, `ultimas_linhas`, `segundos`)
- `app.py` (20 linhas): como as páginas são registradas no menu

## O que fazer
1. Em `app_pages/executar.py`, na seção 3, quando houver execução no registro (`st.cache_resource`):
   - **Rodando**: uma função decorada com `@st.fragment(run_every="2s")` que chama `execucao.situacao()` e mostra `st.progress(feitas / total se total > 0 senão 0, text="N de M respostas · mm:ss")` e, abaixo, a última linha do log em `st.caption`. Quando a situação disser que terminou, a função chama `st.rerun()` (recarrega a página inteira, saindo do modo de atualização automática). Comente para o iniciante o que é um fragmento (analogia: só o placar do jogo se atualiza, não o estádio inteiro).
   - **Terminou com código 0**: `st.success` com o rótulo e a linha `acerto` (ex.: "Acerto geral: 44/45 (98%)"); atalho para a "Visão geral" com `st.page_link("dashboard.py", label="Ver na Visão geral", icon=":material/monitoring:")` e uma linha lembrando de marcar **Incluir lotes de calibração** quando o rótulo tiver hífen.
   - **Terminou com código diferente de 0**: `st.error` com o código, `st.code` com `ultimas_linhas`, e a frase decidida por `contar_execucoes(rotulo)`: se 0, "Nada foi gravado no CSV."; se > 0, "N linhas com este rótulo estão no CSV; confira antes de rodar de novo."
   - Nos dois casos de término: botão "Nova execução" que esvazia o registro e chama `st.rerun()`.
   - Enquanto roda, `pode_executar()` já bloqueia o botão "Executar" (motivo com "andamento"); confira que isso aparece.
2. Se o AppTest der erro de página não encontrada no `st.page_link` (a página é testada sozinha, fora do menu do `app.py`), troque o atalho por um texto ("Abra **Visão geral** no menu à esquerda") e registre a decisão no Resultado.
3. Em `testar_executar.py`, acrescente cenários (mesmas trocas temporárias da T08: `ambiente.versao_ollama` simulado e `execucao.montar_comando` com comando falso; `st.cache_resource.clear()` antes de cada um; rótulos `teste-pagina-<carimbo>` que não existem no CSV):
   - **Comando falso lento** (imprime `[ 1/3] ...`, `[ 2/3] ...`, `[ 3/3] ...` com `time.sleep(1)` entre elas e, no fim, `Acerto geral: 3/3 (100%)`): depois do clique, rodando a página de novo enquanto o processo está vivo → há um `progress` na página; o botão "Executar" está desligado; há um aviso com "andamento".
   - Depois que o processo falso termina (espere até 15 s), rodando a página → `success` contendo "Acerto geral: 3/3 (100%)"; botão "Nova execução" presente; ao clicar nele, a caixa de confirmação volta a aparecer.
   - **Comando falso com erro** (imprime `[ 1/3] ...` e levanta `RuntimeError("falha simulada")`): `error` presente, "falha simulada" no texto da página e a frase "Nada foi gravado no CSV.".
   - Ao final de todos os cenários: apague os logs `execucao_teste-pagina-*` criados; `resultados/resultados.csv` com o mesmo tamanho e data de modificação de antes; nenhum `resultados/brutos_teste-pagina-*`.
4. Abra o painel para uma conferência visual rápida, **sem clicar em Executar**: `.venv/Scripts/streamlit run app.py --server.headless true --server.port 8510` em segundo plano, confira que a página "Executar" carrega (por exemplo, `curl -s http://localhost:8510/` responde) e encerre o processo.
5. Rode a suíte inteira.

## Arquivos a criar ou alterar
- `app_pages/executar.py`
- `testar_executar.py`

## Critério de pronto (verificável)
- [ ] `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_executar.py; echo "saida=$?"` → todas as verificações passam (com `PULADO` permitido só no cenário do Ollama real), `saida=0`.
- [ ] `git status --short resultados/` não lista `resultados.csv` nem brutos novos; sem logs `execucao_teste-pagina-*` em `resultados/logs/`.
- [ ] `testar_dashboard.py` 43/43; `testar_processo.py`, `testar_execucao.py` e `testar_rotulo.py` com saída 0; `testar_comparar.py` 14/14 na Parte A; `testar_regua.py` 11/11; `testar_trava_pagamento.py` "Tudo certo."; `testar_mutacao.py` "Sobreviveram aos testes: 1/13" e "Sobreviveram: 0/10".
- [ ] No Resultado, a proposta de mensagem do commit da entrega 2.

## Não alterar
- `testar_dashboard.py`
- `dashboard.py`
- `app.py`
- `benchmark.py`
- `testar_rotulo.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- **Nunca clique em Executar com o comando real**, nem nos testes nem no painel aberto no passo 4.
- Não altere `execucao.py`, `testar_execucao.py` nem `testar_processo.py`. Se precisar, declare PENDENTE.
- `st.rerun()` dentro de um fragmento recarrega a página inteira por padrão; é o que se quer no término. Não chame `st.rerun()` a cada atualização enquanto roda (a página piscaria e perderia o estado).
- Sem CSS próprio nem `unsafe_allow_html`.
- Nunca abra `casos/casos_ocultos.json`.

## Resultado
(preenchido pelo executor ao terminar: o que foi feito, arquivos alterados, evidência da verificação)

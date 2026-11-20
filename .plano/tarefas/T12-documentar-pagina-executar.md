# T12 — Documentar a página Executar no README e no CLAUDE.md

**Fase:** 3 — Execução real e documentação (entrega 3)
**Porte:** P
**Depende de:** T11
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
O botão "Executar" do painel está ligado e foi usado numa execução real (`v15-repeticao`, T10; conferida na T11). Falta registrar isso na vitrine do projeto (`README.md`, público no GitHub) e no `CLAUDE.md` (memória do projeto para as próximas sessões). Texto formal, objetivo, em português, no estilo já usado nos dois arquivos.

## Arquivos para ler
- `README.md`: seções "Como rodar" (linhas ~118-156) e "Estrutura" (linhas ~158-176)
- `CLAUDE.md`: seção 4, item do **App pessoal** (o parágrafo que cita `app.py`, `app_pages/executar.py`, "Próxima etapa: o botão...") e o item **Benchmark** (que descreve `benchmark.py`)
- `.plano/tarefas/T11-conferir-execucao-real.md`, seção Resultado (acerto da `v15-repeticao` e comparação com a v15)
- `app_pages/executar.py`, `execucao.py` e `benchmark.py`: só cabeçalhos e docstrings, para descrever com precisão

## O que fazer
1. `README.md`:
   - Em "Como rodar", depois do parágrafo sobre o painel, acrescente "Pela página Executar": o que ela confere (Ollama 0.40.4 na porta 11500, rótulo), as regras (rótulo novo, só letras sem acento, dígitos, `.`, `_`, `-`; terminar em `-oculto` é reservado; rótulo com hífen = lote de calibração; confirmação antes de gravar), o tempo (4 a 5 min, barra de progresso), onde fica o log (`resultados/logs/`, fora do git) e que o conjunto oculto não tem botão.
   - No bloco "Com o modelo", acrescente o exemplo `.venv\Scripts\python benchmark.py --rotulo v15-repeticao` com uma frase.
   - No bloco "Sem o modelo", acrescente os testes novos: `testar_rotulo.py`, `testar_execucao.py`, `testar_processo.py`, `testar_executar.py`.
   - Em "Estrutura", acrescente `execucao.py` e os três testes novos, e atualize a descrição de `app_pages/executar.py`.
   - Um aviso curto: fechar o painel durante uma execução não a interrompe; o CSV só é gravado no fim.
2. `CLAUDE.md`, seção 4:
   - No item do App pessoal: troque "etapa 1, só confere..." e "Próxima etapa: o botão 'Executar'..." pela descrição atual: botão ligado, `execucao.py` (`pode_executar()` e `ler_progresso()` escritas pelo usuário; `iniciar()`/`situacao()` com `subprocess.Popen`, `-u`, `PYTHONIOENCODING`, `CREATE_NO_WINDOW`; registro em `st.cache_resource`; progresso por `st.fragment(run_every)`), regras do rótulo, rótulo repetido recusado, confirmação por caixa de seleção, logs em `resultados/logs/` (ignorados pelo git) e o número atual de verificações de `testar_executar.py`.
   - No item do Benchmark: a opção `--rotulo` (`rotulo_invalido()` e `escolher_execucao()` com `argparse`, escritas pelo usuário; lidas antes de `conferir_ollama()`; `--ocultos` com `--rotulo` é recusado) e `testar_rotulo.py`.
   - Uma linha com o resultado da `v15-repeticao` (data, acerto e o que mudou em relação à v15, da T11).
   - Lembrete para testes do painel: cliques em "Executar" só com `execucao.montar_comando` trocado por comando falso.
3. Não altere as seções 1, 2 e 3 do `CLAUDE.md` (regras do usuário).

## Arquivos a criar ou alterar
- `README.md`
- `CLAUDE.md`

## Critério de pronto (verificável)
- [ ] `grep -c -- "--rotulo" README.md` ≥ 2 e `grep -c "execucao.py" README.md` ≥ 1.
- [ ] `grep -n "Próxima etapa: o botão" CLAUDE.md` não encontra nada; `grep -c "v15-repeticao" CLAUDE.md` ≥ 1; `grep -c "testar_rotulo.py" CLAUDE.md` ≥ 1.
- [ ] `git diff --stat` mostra alterações só em `README.md` e `CLAUDE.md` (além das já existentes antes da tarefa, como o CSV da T10).
- [ ] No Resultado, a proposta de mensagem do commit da documentação.

## Não alterar
- `app_pages/executar.py`
- `execucao.py`
- `benchmark.py`
- `testar_executar.py`
- `testar_dashboard.py`
- `casos/casos_ocultos.json`

## Cuidados
- Os números citados (acerto, verificações) vêm da T11 e da saída real dos testes; não invente nem arredonde.
- O README é público: nenhum dado pessoal, caminho com nome de usuário ou e-mail.
- Não edite `resultados/resultados.csv` (pode estar alterado no git por causa da T10; é esperado).
- Linguagem formal, sem emojis.

## Resultado
(preenchido pelo executor ao terminar: o que foi feito, arquivos alterados, evidência da verificação)

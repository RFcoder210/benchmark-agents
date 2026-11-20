# T11 — Conferir a execução real e a suíte de testes

**Fase:** 3 — Execução real e documentação (entrega 3)
**Porte:** P
**Depende de:** T10
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
O usuário rodou `v15-repeticao` pelo botão da página "Executar" (T10), o que acrescentou 45 linhas ao CSV e um arquivo de brutos. Esta tarefa confere, **sem rodar o modelo**, que a gravação está íntegra, compara a repetição com a v15 caso a caso e confirma que todos os testes sem modelo continuam passando com os dados novos. Nada é alterado no código.

## Arquivos para ler
- `.plano/tarefas/T10-usuario-execucao-real.md`, seção Resultado (acerto informado pelo usuário)
- `comparar_versoes.py` (só o cabeçalho, para o uso das opções)
- `resultados/resultados.csv`: **apenas** as linhas com `v15-repeticao` (filtre com `grep`; não leia o arquivo inteiro)

## O que fazer
1. Contar as linhas novas: `grep -c ";v15-repeticao;" resultados/resultados.csv` → 45. Conferir que existe exatamente um `resultados/brutos_v15-repeticao_*.json` e que ele tem 45 registros (`.venv/Scripts/python -c "import json,glob; print(len(json.load(open(glob.glob('resultados/brutos_v15-repeticao_*.json')[0], encoding='utf-8'))))"`).
2. Comparar com a base: `export PYTHONIOENCODING=utf-8; .venv/Scripts/python comparar_versoes.py v15 v15-repeticao` e registrar a saída resumida (acertos, casos que mudaram). Diferenças são dado, não falha (a régua de repetição está no CLAUDE.md, seção 4).
3. Rodar a suíte sem modelo e registrar o resultado de cada uma: `testar_rotulo.py`, `testar_execucao.py`, `testar_processo.py`, `testar_executar.py`, `testar_dashboard.py`, `testar_comparar.py`, `testar_regua.py`, `testar_trava_pagamento.py`, `testar_mutacao.py`.
4. Conferir que o painel trata o rótulo como calibração: `grep -n "str.contains" dashboard.py` mostra a regra do hífen (linha ~87), e `testar_dashboard.py` passa.
5. No Resultado, propor a mensagem do commit da execução real (CSV e brutos novos), a ser aprovado pelo usuário.

## Arquivos a criar ou alterar
- Nenhum (só o Resultado desta tarefa).

## Critério de pronto (verificável)
- [ ] 45 linhas `v15-repeticao` no CSV e um brutos com 45 registros.
- [ ] Saída de `comparar_versoes.py v15 v15-repeticao` registrada no Resultado.
- [ ] Suíte sem modelo: `testar_rotulo.py`, `testar_execucao.py`, `testar_processo.py`, `testar_executar.py` com saída 0; `testar_dashboard.py` com todas as verificações passando; `testar_comparar.py` 14/14 na Parte A; `testar_regua.py` 11/11; `testar_trava_pagamento.py` "Tudo certo."; `testar_mutacao.py` "Sobreviveram: 0/10" na Parte B2 (na B1, registre o número; os brutos novos entram no histórico dela).

## Não alterar
- `testar_dashboard.py`
- `testar_executar.py`
- `dashboard.py`
- `app_pages/executar.py`
- `execucao.py`
- `benchmark.py`
- `casos/casos_ocultos.json`

## Cuidados
- Não edite `resultados/resultados.csv` nem os brutos (é o histórico oficial; ele está alterado no git por causa da T10, e isso é esperado).
- Se algum teste falhar por causa dos dados novos, **não altere o teste**: declare PENDENTE com a saída exata.
- Nunca rode `benchmark.py`; nunca abra `casos/casos_ocultos.json`.

## Resultado
(preenchido pelo executor ao terminar: o que foi feito, arquivos alterados, evidência da verificação)

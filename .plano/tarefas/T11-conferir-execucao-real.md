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

### Resultado (executor, 27/11/2026)
Nada de código alterado; só esta seção.

**Integridade:** 45 linhas `;v15-repeticao;` no CSV; um brutos (`resultados/brutos_v15-repeticao_2026-11-27_1824.json`) com 45 registros.

**comparar_versoes.py v15 v15-repeticao:** 44/45 nos dois lados. Todos os casos iguais (C01–C15 estáveis 3/3, exceto C08 2/3 "sensível" nos dois). Ganhos 0, perdas 0. Decisão: MANTER v15. Repetição idêntica à base.

**Suíte sem modelo (todas saída 0):** testar_rotulo 25/25; testar_execucao 15/15; testar_processo 13/13; testar_executar 36/36; testar_dashboard 43/43; testar_comparar Parte A 14/14; testar_regua 11/11; testar_trava_pagamento "Tudo certo."; testar_mutacao B2 "Sobreviveram: 0/10". B1 (1230 respostas salvas, já com os brutos novos): 11 mutantes detectados, 1 sobrevivente, o já conhecido "sem o teste de campo ausente (equivalente)" (mutante equivalente, histórico 0).

**Painel:** dashboard.py:87 `dados["calibracao"] = dados["versao_agente"].str.contains("-")` trata `v15-repeticao` como calibração; testar_dashboard passa.

**Pontos observados:**
1. Erro único: C08 #2 (invertida) -> perguntar, o limite conhecido da v15 (C08 também deu 2/3 na v15 de 27/10). Não é regressão.
2. "0 de 0 respostas": o log só ganha linha de progresso após a 1ª resposta, e a 1ª levou 31,41 s (carga a frio do modelo; as demais ~2 a 6 s). `ler_progresso` devolve (0, 0) até lá. Isso também explica o tempo médio de 7,08 s contra 5,4 s da v15 (31 s a mais sobre 45 respostas, cerca de 0,6 s de média). Sugestão (não aplicada): ler o total "45" da linha de cabeçalho do log ("15 casos ... 3 ordens") ou mostrar "aquecendo o modelo" quando total = 0.
3. Mensagem de rótulo repetido (app_pages/executar.py:84): sugere "use um rótulo como {VERSAO_AGENTE}-repeticao", que é justamente o rótulo já gravado quando se está nele. Confirmado como falha de texto. Sugestão: sugerir um sufixo novo (ex.: `-repeticao2`) quando o rótulo recusado já for esse.
4. CLAUDE.md diz "ignorar 3/3" para a v15, mas são 2 casos (C04, C11) x 3 ordens = 6; 24+15+6 = 45. Correto: "ignorar 6/6". Erro de texto no CLAUDE.md (seção 4); a execução real não diverge.

**Mensagem de commit proposta (a aprovar):**
`T11: conferência da execução real v15-repeticao (CSV e brutos, 44/45, idêntica à v15)`
(arquivos: resultados/resultados.csv, resultados/brutos_v15-repeticao_2026-11-27_1824.json, log e esta tarefa)

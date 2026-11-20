# T06 — AGUARDA USUÁRIO: escrever ler_progresso() e pode_executar()

**Fase:** 2 — Botão ligado (entrega 2)
**Porte:** P
**Depende de:** T05
**Executor:** AGUARDA USUÁRIO (o usuário escreve o código; a sessão principal orienta, explica os conceitos e revisa, sem escrever a solução por ele)
**Revisão:** nenhuma

## Contexto mínimo
Segunda parte central reservada ao usuário (CLAUDE.md, seção 1). A T05 criou `execucao.py` com o esqueleto comentado de `ler_progresso()` e `pode_executar()` e o teste `testar_execucao.py`, que hoje falha em tudo. Essas duas funções são o "cérebro" do botão: uma decide se ele pode ser liberado, a outra transforma o texto do log em barra de progresso.

## Arquivos para ler
- `execucao.py` (roteiro nos comentários)
- `testar_execucao.py` (o que se espera de cada função)

## O que fazer (o usuário, com orientação)
1. Escrever `ler_progresso(texto_log)` seguindo o roteiro. Rodar `.venv\Scripts\python testar_execucao.py` e ver as verificações de progresso passarem.
2. Escrever `pode_executar(versao_ollama, rotulo, ja_gravadas, em_andamento=False)`, reaproveitando `rotulo_invalido()` (escrita por ele na T03). Rodar o teste de novo.
3. Sessão principal: explicar com analogia cada conceito novo (percorrer linhas de texto, `reversed()`, converter texto em número com `int()` e tratar `ValueError`, "retorno cedo" com `return` dentro de `if`), e revisar o código do usuário apontando problemas, sem reescrevê-lo.

## Arquivos a criar ou alterar
- `execucao.py` (só o corpo das duas funções)

## Critério de pronto (verificável)
- [ ] `.venv\Scripts\python testar_execucao.py` mostra `N/N verificações passaram` (todas) e termina com código 0.
- [ ] `.venv\Scripts\python testar_rotulo.py` continua passando tudo.

## Não alterar
- `testar_execucao.py`
- `testar_rotulo.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- As funções não abrem arquivos, não chamam o Ollama e não leem o CSV: recebem tudo pelos parâmetros (por isso são fáceis de testar).
- Não rodar `benchmark.py` com rótulo válido e o Ollama ligado (grava no CSV oficial).

## Resultado
(preenchido ao terminar: o que o usuário escreveu, dúvidas que surgiram, saída do teste)

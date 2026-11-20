# T04 — Conferir a opção --rotulo pela linha de comando

**Fase:** 1 — Opção `--rotulo` (entrega 1)
**Porte:** P
**Depende de:** T03
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
O usuário escreveu `rotulo_invalido()` e `escolher_execucao()` em `benchmark.py` e ligou a segunda no bloco `__main__` (T03). Esta tarefa confere o comportamento real pela linha de comando, **sem rodar o modelo**, atualiza o cabeçalho de uso do arquivo e fecha a entrega 1. O código do usuário não é reescrito: problemas viram sugestões no Resultado.

## Arquivos para ler
- `benchmark.py`: linhas 1-12 (cabeçalho), a seção `# OPÇÕES DA LINHA DE COMANDO` e o bloco `if __name__ == "__main__":`
- `testar_rotulo.py` (só para rodar)

## O que fazer
1. Rode `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_rotulo.py; echo "saida=$?"`. Se não passar tudo, **pare** e declare PENDENTE (o código é do usuário).
2. Confira pela linha de comando, **sempre com `OLLAMA_HOST=127.0.0.1:1`** (endereço onde ninguém atende; mesmo que algo esteja errado, o benchmark para na trava do Ollama e não roda o modelo):
   - `OLLAMA_HOST=127.0.0.1:1 .venv/Scripts/python benchmark.py --help; echo "saida=$?"` → mostra `--rotulo` e `--ocultos`; `saida=0`.
   - `OLLAMA_HOST=127.0.0.1:1 .venv/Scripts/python benchmark.py --rotulo "a b"; echo "saida=$?"` → mensagem do argparse com o motivo; `saida=2` (se aparecer a mensagem do Ollama com `saida=1`, a leitura das opções está depois de `conferir_ollama()`: anote como problema).
   - O mesmo para `--rotulo v15-oculto`, `--ocultos --rotulo x` e `--desconhecida` → `saida=2`.
   - `OLLAMA_HOST=127.0.0.1:1 .venv/Scripts/python benchmark.py --rotulo v15-conferencia; echo "saida=$?"` → mensagem "O Ollama 0.40.4 não está ligado em 127.0.0.1:1"; `saida=1`; nada gravado.
3. Confira que nada foi gravado: `git status --short resultados/` não lista `resultados.csv` e não há `resultados/brutos_v15-conferencia_*.json`.
4. Atualize **só o cabeçalho** de `benchmark.py` (linhas 7-8, "Execução:"): acrescente uma linha com `.venv\Scripts\python benchmark.py --rotulo v15-repeticao` e uma frase sobre o uso (repetir a base como lote de calibração sem editar o código).
5. Leia o código do usuário e anote no Resultado, em até 5 itens, sugestões de clareza ou de comentário (sem aplicá-las).
6. Rode a suíte sem modelo: `testar_comparar.py`, `testar_regua.py`, `testar_trava_pagamento.py`, `testar_mutacao.py`, `testar_executar.py`, `testar_dashboard.py`.
7. No Resultado, proponha a mensagem do commit da entrega 1 (o commit é feito pelo orquestrador, com aprovação do usuário).

## Arquivos a criar ou alterar
- `benchmark.py` (somente o comentário de cabeçalho)

## Critério de pronto (verificável)
- [ ] `testar_rotulo.py` passa em todas as verificações, com código de saída 0.
- [ ] As 6 chamadas do passo 2 dão os códigos de saída esperados (0, 2, 2, 2, 2, 1), registrados no Resultado.
- [ ] `git status --short resultados/resultados.csv` vazio e nenhum `brutos_v15-conferencia_*.json`.
- [ ] Suíte sem modelo como na linha de base: `testar_comparar.py` 14/14 na Parte A, `testar_regua.py` 11/11, `testar_trava_pagamento.py` "Tudo certo.", `testar_mutacao.py` "Sobreviveram aos testes: 1/13" e "Sobreviveram: 0/10", `testar_executar.py` 6/6 (ou 9/9), `testar_dashboard.py` 43/43.

## Não alterar
- `testar_rotulo.py`
- `resultados/resultados.csv`
- `casos/casos.json`
- `casos/casos_ocultos.json`
- `agente.py`

## Cuidados
- **Nunca rode `benchmark.py` sem `OLLAMA_HOST=127.0.0.1:1`** nesta tarefa. Com o servidor real e um rótulo válido, ele roda 4 a 5 minutos e grava 45 linhas no CSV oficial.
- Não reescreva as funções do usuário; se o comportamento estiver errado, declare PENDENTE com a evidência.
- Nunca abra `casos/casos_ocultos.json`.

## Resultado
(preenchido pelo executor ao terminar: o que foi feito, arquivos alterados, evidência da verificação)

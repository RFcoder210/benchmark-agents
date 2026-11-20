# T02 — Teste e esqueleto da opção --rotulo

**Fase:** 1 — Opção `--rotulo` (entrega 1)
**Porte:** P
**Depende de:** T01
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
O rótulo de uma execução do benchmark hoje só muda editando `VERSAO_AGENTE` em `benchmark.py`. O objetivo é aceitar `benchmark.py --rotulo v15-repeticao`. O usuário está aprendendo Python e vai **escrever ele mesmo** as duas funções centrais (tarefa T03). Esta tarefa prepara o terreno no estilo "teste primeiro": um teste automático pronto, que define o comportamento, e o esqueleto comentado das funções, que por enquanto só levanta `NotImplementedError`. O bloco `__main__` **não** é alterado aqui.

## Arquivos para ler
- `benchmark.py`: linhas 1-30 (cabeçalho, imports, `ARQUIVO_CASOS`, `ARQUIVO_CASOS_OCULTOS`, `VERSAO_AGENTE`) e 453-480 (bloco `__main__`, que lê `sys.argv` à mão).
- `testar_regua.py` (44 linhas): estilo dos testes do projeto (lista de exemplos, `OK`/`FALHA`, contagem final).
- `CLAUDE.md`, seção 1 (comentários em português, explicação para iniciante).

## O que fazer
1. Em `benchmark.py`, logo antes da seção `# EXECUÇÃO` (antes do `if __name__ == "__main__":`), crie uma seção nova `# OPÇÕES DA LINHA DE COMANDO` com `import argparse` e `import re` no topo do arquivo (junto dos outros imports, com comentário de uma linha cada) e **duas funções-esqueleto**, com docstring completa e o corpo `raise NotImplementedError("Sua vez: veja o roteiro nos comentários")`:
   - `rotulo_invalido(rotulo)` → devolve `None` se o rótulo serve, ou um texto em português com o motivo. Regras (escreva-as na docstring): não vazio; até 40 caracteres (constante nova `TAMANHO_MAXIMO_ROTULO = 40`); só letras sem acento, dígitos, `.`, `_` e `-` (o rótulo vai no nome do arquivo de brutos e numa coluna do CSV separado por `;`); não pode terminar em `-oculto` (reservado à validação final).
   - `escolher_execucao(argv=None)` → devolve a tupla `(arquivo_de_casos, rotulo)`, usando `argparse`. Sem opções: `(ARQUIVO_CASOS, VERSAO_AGENTE)`. `--rotulo X`: `(ARQUIVO_CASOS, X)`. `--ocultos`: `(ARQUIVO_CASOS_OCULTOS, f"{VERSAO_AGENTE}-oculto")`, como hoje. Erro do argparse (`SystemExit` com código 2) para: `--rotulo` sem valor, rótulo inválido segundo `rotulo_invalido()`, `--ocultos` junto com `--rotulo` (o oculto tem rótulo fixo), opção desconhecida. `argv=None` significa "usar `sys.argv[1:]`" (é o padrão do `parse_args`).
2. Acima de cada esqueleto, escreva um **roteiro comentado** para o usuário (iniciante em Python), sem escrever a solução: passos numerados, a analogia (argparse = recepcionista que confere a ficha de entrada antes de deixar a pessoa subir), os conceitos que ele vai usar (`return None`, `len()`, `str.endswith()`, `re.fullmatch()` ou um laço com `in`; `argparse.ArgumentParser`, `add_argument`, `type=` com uma função que levanta `argparse.ArgumentTypeError`, `parser.error()` ou `add_mutually_exclusive_group()`), e o lembrete de que a leitura das opções fica dentro da função (código no nível do módulo roda quando `testar_mutacao.py` carrega o arquivo).
3. Crie `testar_rotulo.py` (sem modelo, sem Ollama, sem CSV), no estilo de `testar_regua.py`, com cabeçalho comentado (o que testa e como rodar). Cada verificação roda dentro de `try/except Exception` para que um `NotImplementedError` vire `FALHA` e o teste continue. Silencie a saída de erro do argparse com `contextlib.redirect_stderr(io.StringIO())`. No fim, imprima `N/M verificações passaram` e termine com `sys.exit(0 if tudo passou else 1)`. Verificações mínimas:
   - `rotulo_invalido` devolve `None` para: `"v15-repeticao"`, `"v2-t0.7"`, `"v16"`, `"v15_teste"`, `"a" * 40`.
   - `rotulo_invalido` devolve um texto não vazio (`str`) para: `""`, `" "`, `" v15"`, `"v15 repeticao"`, `"v15;x"`, `"v15/x"`, `"v15\\x"`, `"versão"`, `"v15-oculto"`, `"a" * 41`.
   - `escolher_execucao([])` == `(ARQUIVO_CASOS, VERSAO_AGENTE)` (importe as constantes de `benchmark`; não escreva `"v15"` no teste).
   - `escolher_execucao(["--rotulo", "v15-repeticao"])` e `escolher_execucao(["--rotulo=v15-repeticao"])` == `(ARQUIVO_CASOS, "v15-repeticao")`.
   - `escolher_execucao(["--ocultos"])` == `(ARQUIVO_CASOS_OCULTOS, VERSAO_AGENTE + "-oculto")`.
   - `SystemExit` com `code == 2` para: `["--rotulo"]`, `["--rotulo", "a b"]`, `["--rotulo", "v15-oculto"]`, `["--ocultos", "--rotulo", "x"]`, `["--desconhecida"]`.
   - Com `sys.argv` trocado temporariamente por `["benchmark.py"]` (restaure no `finally`), `escolher_execucao()` == `(ARQUIVO_CASOS, VERSAO_AGENTE)`.
4. Rode o teste novo (deve falhar em tudo, por causa do esqueleto) e a suíte existente (deve continuar passando).

## Arquivos a criar ou alterar
- `benchmark.py` (só acrescentar imports, a constante e as duas funções-esqueleto; nada mais)
- `testar_rotulo.py` (novo)

## Critério de pronto (verificável)
- [ ] `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_rotulo.py; echo "saida=$?"` roda sem erro de importação, mostra `FALHA` em todas as verificações (efeito do `NotImplementedError`), imprime `0/N verificações passaram` e `saida=1`.
- [ ] `.venv/Scripts/python -c "import benchmark"` não dá erro.
- [ ] Continuam passando: `testar_comparar.py` (14/14 na Parte A), `testar_regua.py` (11/11), `testar_trava_pagamento.py` ("Tudo certo."), `testar_mutacao.py` ("Sobreviveram aos testes: 1/13" e "Sobreviveram: 0/10").
- [ ] `git diff benchmark.py` mostra só acréscimos (nenhuma linha removida), fora do bloco `__main__`.

## Não alterar
- `resultados/resultados.csv`
- `casos/casos.json`
- `casos/casos_ocultos.json`
- `agente.py`
- `testar_mutacao.py`
- `testar_comparar.py`
- `testar_regua.py`

## Cuidados
- **Não escreva a solução das funções**: o corpo é só `raise NotImplementedError(...)`. O roteiro orienta; quem implementa é o usuário (T03).
- Não altere o bloco `if __name__ == "__main__":` nem `comparar()`, `classificar_erro()` e `CAMPOS_GASTO` (`testar_mutacao.py` procura trechos exatos desse código).
- **Nunca rode `benchmark.py`** nesta tarefa: com o Ollama ligado, ele roda o modelo e grava 45 linhas no CSV oficial.
- Nunca abra `casos/casos_ocultos.json` (o teste só compara o caminho, que é texto).
- Comentários em português, formais e objetivos.

## Resultado
Feito: imports argparse/re, constante TAMANHO_MAXIMO_ROTULO e esqueletos rotulo_invalido/escolher_execucao (com roteiros) em benchmark.py (65 acréscimos, 0 remoções); testar_rotulo.py novo (25 verificações).
Evidência: testar_rotulo.py = 0/25 e saida=1; import benchmark ok; testar_regua 11/11; testar_trava_pagamento "Tudo certo."; testar_mutacao 1/13 e 0/10; testar_comparar passou.

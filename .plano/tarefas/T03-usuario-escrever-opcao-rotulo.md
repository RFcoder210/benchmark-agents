# T03 — AGUARDA USUÁRIO: escrever rotulo_invalido() e escolher_execucao()

**Fase:** 1 — Opção `--rotulo` (entrega 1)
**Porte:** P
**Depende de:** T02
**Executor:** AGUARDA USUÁRIO (o usuário escreve o código; a sessão principal orienta, explica os conceitos e tira dúvidas, sem escrever a solução por ele)
**Revisão:** nenhuma

## Contexto mínimo
Esta é uma parte central do projeto, reservada ao usuário para aprendizado (CLAUDE.md, seção 1). A T02 deixou em `benchmark.py` o esqueleto comentado de `rotulo_invalido()` e `escolher_execucao()` e o teste `testar_rotulo.py`, que hoje falha em tudo. A tarefa termina quando o teste passa e o bloco `__main__` usa a função nova.

## Arquivos para ler
- `benchmark.py`: seção `# OPÇÕES DA LINHA DE COMANDO` (roteiro nos comentários) e o bloco `if __name__ == "__main__":`
- `testar_rotulo.py` (o que se espera de cada função)

## O que fazer (o usuário, com orientação)
1. Escrever `rotulo_invalido(rotulo)` seguindo o roteiro. Rodar `.venv\Scripts\python testar_rotulo.py` e ver as verificações de rótulo passarem.
2. Escrever `escolher_execucao(argv=None)` com `argparse`, usando `rotulo_invalido()` para validar o `--rotulo`. Rodar o teste de novo.
3. No bloco `__main__`, trocar o `if "--ocultos" in sys.argv: ... else: ...` por `arquivo, rotulo = escolher_execucao()` e colocar essa linha **antes** de `conferir_ollama()` (assim um erro de digitação na opção aparece sem precisar do servidor ligado).
4. Sessão principal: ao surgir cada conceito novo (retorno `None`, `str.endswith`, expressão regular ou laço, tupla, `argparse`, exceção `SystemExit`), explicar brevemente com analogia, e revisar o código escrito pelo usuário, apontando problemas em vez de reescrevê-lo.

## Arquivos a criar ou alterar
- `benchmark.py` (as duas funções e o bloco `__main__`)

## Critério de pronto (verificável)
- [ ] `.venv\Scripts\python testar_rotulo.py` mostra `N/N verificações passaram` (todas) e termina com código 0.
- [ ] O bloco `__main__` chama `escolher_execucao()` antes de `conferir_ollama()` e não lê mais `sys.argv` diretamente.

## Não alterar
- `testar_rotulo.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- Para testar à mão, use só `.venv\Scripts\python benchmark.py --help` ou rótulos inválidos (ex.: `--rotulo "a b"`). **Não rode o benchmark com um rótulo válido com o Ollama ligado**: isso grava 45 linhas no CSV oficial (a execução real é a T10).
- Não mexer em `comparar()`, `classificar_erro()` nem `CAMPOS_GASTO` (`testar_mutacao.py` depende do texto exato delas).
- Se o `import sys` deixar de ser usado em `benchmark.py`, pode ser removido; confirme com o teste.

## Resultado
(preenchido ao terminar: o que o usuário escreveu, dúvidas que surgiram, saída do teste)

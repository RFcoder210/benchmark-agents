# T05 — Teste e esqueleto das regras da execução (execucao.py)

**Fase:** 2 — Botão ligado (entrega 2)
**Porte:** P
**Depende de:** T04
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
A página "Executar" do painel (`app_pages/executar.py`) vai lançar `benchmark.py --rotulo X` em segundo plano e mostrar o progresso. A lógica fica num módulo novo, `execucao.py`, **sem tela** (testável sem navegador). Duas funções desse módulo são centrais e serão escritas pelo usuário na T06: `ler_progresso()` (lê o log do benchmark e diz quantas respostas já saíram) e `pode_executar()` (decide se o botão pode ser liberado e, se não, por quê). Esta tarefa cria o teste dessas duas funções e o esqueleto comentado delas, no estilo "teste primeiro". O lançamento do processo é a T07.

## Arquivos para ler
- `benchmark.py`: função `executar_casos()` (linhas ~134-185; formato da linha de progresso, ex.: `[ 7/45] C03 #1 (original) -> registrar (2.8 s)`), a seção `# OPÇÕES DA LINHA DE COMANDO` (`rotulo_invalido()`, escrita pelo usuário) e o bloco `__main__` (mensagens finais).
- `ambiente.py` (45 linhas): `VERSAO_OLLAMA`.
- `testar_rotulo.py`: estilo do teste criado na T02 (reaproveite o formato).

## O que fazer
1. Crie `execucao.py` com cabeçalho comentado (para que serve, analogia curta: a "torre de controle" que libera a decolagem e acompanha o voo; não tem tela) e imports: `import ambiente` e `from benchmark import rotulo_invalido`. Escreva **dois esqueletos** com docstring completa e corpo `raise NotImplementedError("Sua vez: veja o roteiro nos comentários")`, cada um precedido de roteiro comentado para iniciante (passos, conceitos, sem a solução):
   - `ler_progresso(texto_log)` → tupla `(feitas, total)` de inteiros, tirada da **última** linha completa no formato `[ n/total] ...` (pode haver espaços antes de `n`). Linhas de outro formato são ignoradas, inclusive uma última linha cortada pela metade (ex.: `[ 7/4`). Sem nenhuma linha de progresso → `(0, 0)`. Conceitos do roteiro: `str.splitlines()`, laço `for` (de trás para a frente com `reversed()`), `str.strip()`, `str.startswith()`, `str.split()`, `int()`, `try/except ValueError`; alternativa com `re.match(r"\[\s*(\d+)/(\d+)\]", linha)`.
   - `pode_executar(versao_ollama, rotulo, ja_gravadas, em_andamento=False)` → `None` se pode executar; senão, o motivo (texto em português). Ordem das regras (a primeira que falhar decide): (1) `em_andamento` verdadeiro → motivo com a palavra "andamento"; (2) `versao_ollama is None` → motivo com "não está ligado" e `ambiente.VERSAO_OLLAMA`; (3) `versao_ollama != ambiente.VERSAO_OLLAMA` → motivo com a versão encontrada e a exigida; (4) `rotulo_invalido(rotulo)` não é `None` → devolve exatamente esse motivo; (5) `ja_gravadas > 0` → motivo com o rótulo, o número de linhas e a palavra "outro" (sugere escolher outro rótulo). Conceitos: `if`/`return` cedo, `is None`, f-string, reaproveitar uma função já escrita.
2. Crie `testar_execucao.py` (sem modelo, sem Ollama, sem CSV), com cabeçalho comentado, cada verificação em `try/except Exception` (o `NotImplementedError` vira `FALHA`), relatório `N/M verificações passaram` e `sys.exit(0 if tudo passou else 1)`. Verificações mínimas:
   - `ler_progresso("")` == `(0, 0)`; texto só com `15 casos carregados de casos/casos.json; ...` == `(0, 0)`.
   - Log com 3 linhas de progresso `[ 1/45]`, `[ 2/45]`, `[ 3/45]` (copie o formato real) == `(3, 45)`.
   - Log com `[45/45] ...` seguido de `Respostas salvas em ...`, `Resultados acrescentados em ...` e `Acerto geral: 44/45 (98%)` == `(45, 45)` (a linha "Acerto geral" não é de progresso).
   - Log terminando numa linha cortada `[ 8/4` depois de `[ 7/45] ...` == `(7, 45)`.
   - Log com acentos e quebras de linha do Windows (`\r\n`) funciona.
   - `pode_executar(ambiente.VERSAO_OLLAMA, "v15-repeticao", 0)` is `None`.
   - `em_andamento=True` bloqueia mesmo com tudo certo (motivo contém "andamento").
   - `versao_ollama=None` → motivo contém "não está ligado".
   - `versao_ollama="0.40.13"` → motivo contém "0.40.13" e `ambiente.VERSAO_OLLAMA`.
   - rótulo `"a b"` → motivo == `rotulo_invalido("a b")`; rótulo `"v15-oculto"` → motivo não `None`.
   - `ja_gravadas=45` com `"v15"` → motivo contém `"v15"`, `"45"` e `"outro"`.
   - Ordem: Ollama desligado **e** rótulo inválido → o motivo é o do Ollama.
3. Rode `testar_execucao.py` (deve falhar em tudo) e a suíte existente (deve passar).

## Arquivos a criar ou alterar
- `execucao.py` (novo; só os dois esqueletos e os imports)
- `testar_execucao.py` (novo)

## Critério de pronto (verificável)
- [ ] `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_execucao.py; echo "saida=$?"` roda sem erro de importação, mostra `FALHA` em todas as verificações, `0/N verificações passaram` e `saida=1`.
- [ ] `.venv/Scripts/python -c "import execucao"` não dá erro.
- [ ] `testar_rotulo.py` continua passando tudo (saída 0); `testar_executar.py` 6/6 (ou 9/9) e `testar_dashboard.py` 43/43.

## Não alterar
- `benchmark.py`
- `testar_rotulo.py`
- `app_pages/executar.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- **Não escreva a solução** das duas funções: só o roteiro e o `raise NotImplementedError(...)`. Quem implementa é o usuário (T06).
- Nada de código no nível do módulo além de imports, constantes e funções (o módulo será importado pela página a cada recarga).
- Nunca rode `benchmark.py`; nunca abra `casos/casos_ocultos.json`.
- Comentários em português, formais e objetivos.

## Resultado
Criados `execucao.py` (imports, roteiros comentados e dois esqueletos com `NotImplementedError`) e `testar_execucao.py` (15 verificações). Evidência: `testar_execucao.py` -> FALHA em todas, 0/15, saida=1; `import execucao` ok; `testar_rotulo.py` 25/25, `testar_executar.py` 6/6, `testar_dashboard.py` 43/43. Modelo, CSV e arquivos de "Não alterar" intocados.

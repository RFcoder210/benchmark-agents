# T07 — Lançar e acompanhar o benchmark em segundo plano (execucao.py)

**Fase:** 2 — Botão ligado (entrega 2)
**Porte:** M
**Depende de:** T06
**Executor:** executor-tarefa
**Revisão:** nenhuma

## Contexto mínimo
`execucao.py` já tem as regras escritas pelo usuário (`ler_progresso()` e `pode_executar()`, T06). Falta o "encanamento": lançar `benchmark.py --rotulo X` como processo separado (para a página do Streamlit continuar respondendo durante os 4 a 5 minutos), gravar a saída num arquivo de log e consultar a situação (rodando, quantas respostas, código de saída). A página usará isso nas T08 e T09. Tudo é testado com **comandos falsos**, sem rodar o benchmark de verdade.

## Arquivos para ler
- `execucao.py` (inteiro; as funções do usuário não mudam)
- `benchmark.py`: bloco `__main__` (o que ele imprime no fim: `Respostas salvas em ...`, `Resultados acrescentados em ...`, `Acerto geral: ...`)
- `testar_execucao.py` (estilo do relatório de testes)
- `.gitignore`

## O que fazer
1. Em `execucao.py`, numa seção nova `# LANÇAR E ACOMPANHAR` abaixo das funções do usuário, acrescente (com comentários em português para iniciante):
   - Constantes `PASTA_PROJETO` (pasta do próprio arquivo, por `os.path.abspath(__file__)`) e `PASTA_LOGS` (`resultados/logs` dentro dela).
   - `montar_comando(rotulo)` → `[sys.executable, "-u", <caminho absoluto de benchmark.py>, "--rotulo", rotulo]`. Nunca inclui `--ocultos`.
   - `iniciar(rotulo, comando=None, pasta_logs=PASTA_LOGS)` → dicionário `{"processo", "rotulo", "log", "inicio"}`. Levanta `ValueError` se `rotulo_invalido(rotulo)` não for `None` (defesa extra; nenhum processo é criado). Cria a pasta de logs; log com nome `execucao_<rotulo>_<AAAA-MM-DD_HHMMSS>.log`. Lança com `subprocess.Popen(comando or montar_comando(rotulo), cwd=PASTA_PROJETO, stdout=<arquivo do log>, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=<cópia de os.environ com PYTHONIOENCODING=utf-8 e PYTHONUNBUFFERED=1>, creationflags=subprocess.CREATE_NO_WINDOW no Windows)`. O processo filho herda `OLLAMA_HOST` do ambiente (definido por `ambiente.py`).
   - `ler_log(caminho)` → o texto do log (`encoding="utf-8", errors="replace"`), ou `""` se ainda não existir.
   - `situacao(execucao)` → dicionário `{"rodando", "codigo_saida", "feitas", "total", "acerto", "ultimas_linhas", "segundos"}`: `rodando` = `processo.poll() is None`; `feitas`/`total` por `ler_progresso()`; `acerto` = a linha que começa com `Acerto geral:` (ou `None`); `ultimas_linhas` = as 10 últimas linhas do log; `segundos` = tempo desde o início.
2. Crie `testar_processo.py` (sem modelo, sem Ollama, sem CSV; mesmo formato de relatório e `sys.exit(0/1)` de `testar_execucao.py`). Todos os logs numa `tempfile.TemporaryDirectory()` passada em `pasta_logs`. Comandos falsos do tipo `[sys.executable, "-c", SCRIPT]` (**sem `-u`**, para provar que `iniciar()` desliga o buffer pelo ambiente), onde `SCRIPT` imprime uma linha com acento (`1 execução por ordem`), 3 linhas de progresso no formato real (`[ 1/3] C01 #1 (original) -> registrar (0.1 s)`), com `time.sleep(0.5)` entre elas, e `Acerto geral: 3/3 (100%)`. Verificações:
   - Logo após `iniciar()`, `situacao()["rodando"]` é `True`.
   - Consultando a cada 0,1 s (limite total de 30 s), aparece pelo menos uma situação com `rodando` verdadeiro e `0 < feitas < 3` (o progresso chega antes do fim).
   - No fim: `rodando` falso, `codigo_saida == 0`, `(feitas, total) == (3, 3)`, `acerto == "Acerto geral: 3/3 (100%)"`, e o log contém `execução` com o acento correto.
   - Comando falso que imprime `[ 1/3] ...` e termina com `raise RuntimeError("falha simulada")` → `codigo_saida != 0` e `"falha simulada"` aparece em `ultimas_linhas`.
   - `iniciar("a b", comando=<falso>)` levanta `ValueError` e não cria log.
   - `montar_comando("v15-repeticao")`: primeiro item `sys.executable`, contém `"-u"`, `"--rotulo"`, `"v15-repeticao"`, termina com o caminho de `benchmark.py` antes das opções, não contém `"--ocultos"`.
   - Espere cada processo terminar antes de sair do `TemporaryDirectory` (no Windows, arquivo aberto não pode ser apagado).
3. Em `.gitignore`, acrescente `resultados/logs/` com comentário (os logs são passageiros; os brutos já guardam as respostas).
4. Rode `testar_processo.py`, `testar_execucao.py`, `testar_rotulo.py` e a suíte existente.

## Arquivos a criar ou alterar
- `execucao.py` (só acréscimos na seção nova)
- `testar_processo.py` (novo)
- `.gitignore`

## Critério de pronto (verificável)
- [ ] `export PYTHONIOENCODING=utf-8; .venv/Scripts/python testar_processo.py; echo "saida=$?"` → todas as verificações passam, `saida=0`.
- [ ] `testar_execucao.py` e `testar_rotulo.py` continuam com todas as verificações passando (saída 0).
- [ ] `testar_executar.py` 6/6 (ou 9/9), `testar_dashboard.py` 43/43, `testar_mutacao.py` "Sobreviveram aos testes: 1/13" e "Sobreviveram: 0/10".
- [ ] `git status --short resultados/` não lista `resultados.csv` nem brutos novos.

## Não alterar
- `testar_execucao.py`
- `testar_rotulo.py`
- `benchmark.py`
- `app_pages/executar.py`
- `resultados/resultados.csv`
- `casos/casos_ocultos.json`

## Cuidados
- Não alterar o corpo de `ler_progresso()` nem de `pode_executar()` (código do usuário). Se parecerem erradas, declare PENDENTE com a evidência.
- **Nunca** chame `iniciar()` sem `comando=` falso nos testes nem rode `benchmark.py`: o comando real roda o modelo e grava 45 linhas no CSV oficial.
- **Não use `os.kill(pid, 0)`** para saber se o processo está vivo: no Windows isso **encerra** o processo. Use `processo.poll()`.
- Abra o arquivo de log no processo pai só para entregá-lo ao `Popen`; feche a cópia do pai depois de lançar (o filho mantém a dele).
- Nada no nível do módulo além de imports, constantes e funções.

## Resultado
Concluída (26/11). Seção "LANÇAR E ACOMPANHAR" em execucao.py (montar_comando, iniciar, ler_log, situacao), testar_processo.py novo (13/13, saída 0), .gitignore com resultados/logs/. Outros testes: testar_execucao 15/15, testar_rotulo 25/25, testar_executar 6/6, testar_dashboard 43/43, testar_mutacao 1/13 e 0/10. git status sem mudanças em resultados/. Funções do usuário intocadas; só comandos falsos.

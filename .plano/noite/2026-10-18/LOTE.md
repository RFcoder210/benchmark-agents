# Lote noturno — 2026-10-18 (benchmark-agents)

## 1. Projeto
- Raiz: a pasta do projeto (no Git Bash, o mesmo caminho com barras normais)
- Windows 11. Python pelo ambiente virtual: `.venv\Scripts\python arquivo.py` (nunca `python`; `py` só fora do venv).
- Modelo do agente: Ollama local, `qwen3:4b-instruct` (custo zero; sem API paga).
- Benchmark: `.venv\Scripts\python benchmark.py` (15 casos × 3 ordens = 45 linhas no CSV; poucos minutos).

## 2. Regras do projeto que valem para a noite (origem: CLAUDE.md, seção 2)
- **Não abrir `casos/casos_ocultos.json`** (nem ler, nem rodar o benchmark sobre ele). Só `casos/casos.json`.
- **Uma mudança por vez** no agente: a v8 muda só a regra de categoria no `PROMPT_SISTEMA`.
- Cada caso roda nas 3 ordens (padrão do `benchmark.py`; não alterar).
- Isolamento: nada de Notion ou Telegram reais. Nenhuma API paga.
- Código comentado em português, no estilo do projeto.
- A régua (`comparar_versoes.py`, `versao_aprovada()`) **não pode ser alterada** para fazer a v8 passar.
- O C08 não deve ser consertado acrescentando "abastecer" ao prompt (decisão do usuário, RETOMADA de 17/10).

## 3. Sistema de tarefas
- Não há pasta de tarefas: a pendência vem de `.plano/RETOMADA.md` ("Próxima ação").
- Status da noite: só no `REGISTRO.md` desta pasta (`em andamento`, `concluida`, `reprovada`, `bloqueada`).
- Resultado registrado onde o projeto registra versões: comentário junto de `VERSAO_AGENTE` em `benchmark.py`, `HISTORICO` em `dashboard.py`, `OFICIAIS` em `testar_dashboard.py`, seção 4 do `CLAUDE.md`, e a análise em `resultados/analise_v8_2026-10-18.md`.

## 4. Agentes
- Executor: `general-purpose` com `executor.md` da skill (o `executor-tarefa` do projeto exige `.plano/tarefas/Txx`, que não existe aqui).
- Diagnóstico: `resolutivo-diagnostico` do projeto (opus).
- Revisor: `general-purpose` + `revisor.md` (opus).
- Retomada: agente `contexto-tokens` do projeto (haiku).

## 5. Tabela do lote
| Ordem | Id | Descrição | Critério de pronto | Tamanho | Executor | Em cadeia de |
|---|---|---|---|---|---|---|
| 1 | V8 | v8 = v7 + regra de categoria da v6 (texto na mensagem do commit `7617401`, inserido na seção "## Categorias" do `PROMPT_SISTEMA` de `agente.py`). Rodar o benchmark, comparar com a v7 pela régua normal, analisar e registrar o resultado. | (a) `git diff main -- agente.py` só altera o `PROMPT_SISTEMA` na seção Categorias (texto idêntico ao do commit 7617401) e nada mais; (b) `VERSAO_AGENTE = "v8"` com o histórico atualizado; (c) 45 linhas `v8` acrescentadas a `resultados/resultados.csv` e nenhuma linha antiga alterada (`git diff --numstat main -- resultados/resultados.csv` com 0 remoções) e um `resultados/brutos_v8_*.json` novo; (d) saída de `.venv\Scripts\python comparar_versoes.py v7 v8` (sem `--neutra`) copiada na análise; (e) `resultados/analise_v8_2026-10-18.md` com total, taxas por ação, caso a caso v7×v8, veredito da régua e o C10 ordem por ordem (resposta crua de cada ordem, citada do brutos); (f) decisão aplicada conforme a seção 6; (g) `testar_comparar.py` e `testar_dashboard.py` passando (o dashboard conhece a v8). | média | opus | — |

## 6. Decisões do usuário para a noite (palavra por palavra)
- Veredito da v8: **"Seguir o padrão de sempre"** — opção descrita como: "Se a regra aprovar, a v8 vira a nova base. Se reprovar, o agente.py volta à v7 e os dados ficam, como aconteceu com a v5 e a v6."
  - Aprovada: espelhar o commit `9e15bfe` (v7): HISTORICO "aprovada (base atual)" e a v7 passa a "aprovada"; CLAUDE.md seção 4 com a v8 como base.
  - Reprovada: espelhar o commit `7617401` (v6): `agente.py` idêntico à v7 (`git diff main -- agente.py` vazio no fim); dados da v8 ficam no CSV e no brutos; HISTORICO "reprovada"; CLAUDE.md registra a v8 reprovada e o oficial segue a v7.
- Início: **"Agora e silenciar (Recommended)"**. Horário de volta: não informado.

## 7. Protegidos (instantâneo)
casos
especificacao-agente.md
contexto-benchmark-agentes.md
comparar_versoes.py
testar_comparar.py
lote.py
analisar_lote.py
teste_conexao.py
requirements.txt
docs
.claude
.plano/historico
resultados/brutos_v1_2026-10-14_1929.json
resultados/brutos_v1_2026-10-14_1949.json
resultados/brutos_v2-loteA_2026-10-15_2226.json
resultados/brutos_v2-ordemB_2026-10-15_2234.json
resultados/brutos_v2-ordemC_2026-10-15_2236.json
resultados/brutos_v2-ordemD_2026-10-15_2238.json
resultados/brutos_v2-t0.7_2026-10-15_2232.json
resultados/brutos_v2_2026-10-14_2001.json
resultados/brutos_v2_2026-10-16_0653.json
resultados/brutos_v3-candidato_2026-10-15_2240.json
resultados/brutos_v3_2026-10-16_1002.json
resultados/brutos_v4_2026-10-16_1012.json
resultados/brutos_v4_2026-10-16_1031.json
resultados/brutos_v5_2026-10-16_1021.json
resultados/brutos_v6_2026-10-17_1728.json
resultados/brutos_v7_2026-10-17_2015.json
resultados/lote_2026-10-15.log
resultados/lote_2026-10-15_config.json
resultados/relatorio_lote_2026-10-15.md
resultados/tabelas_lote_2026-10-15.md

Observações: `resultados/resultados.csv` não entra no instantâneo porque o benchmark acrescenta linhas; a checagem dele é "só acréscimos" (critério c). `.plano/historico` pode ganhar um arquivo novo se o agente `contexto-tokens` arquivar a retomada anterior (só acréscimo é aceitável).

## 8. Verificação geral
- `.venv\Scripts\python testar_comparar.py`
- `.venv\Scripts\python testar_dashboard.py`
- `git diff --numstat main -- resultados/resultados.csv` (0 remoções)

## 9. Horários e consumo
- Preparação: 2026-10-18 20:23–20:40. Início: logo após a preparação, nesta sessão. Volta do usuário: não informada.
- Consumo na preparação: janela de 5 h 12% (renova 01:09 de 19/10); semana 26%.

## 10. Notificações
Silenciadas em 18/10 ~20:40. Valores anteriores, para restaurar:
- `notification_sound` = `system`
- `task_complete_notifications` = `banner`
- `question_notifications` = `banner`
- `permission_request_notifications` = `banner`

## 11. Git
- Origem: `main` (456fbd0). Branch da noite: `noite/2026-10-18`. Sem push, sem merge.
- Vão junto para o branch da noite: esta pasta e a linha do Dia 4 em `.plano/DIARIO.md` (feitas na preparação).

## 12. Fora do lote
- Adaptar o hook `testar-ao-parar.ps1` para Python: mexe em configuração do Claude Code (proibido à noite).
- Revisão do vocabulário das categorias (C08) e redução de tokens: adiadas pelo usuário.
- Harness de agentes de pesquisa: só depois de concluir a v1.
- v9 ou qualquer passo após a v8: depende da decisão e análise do usuário.

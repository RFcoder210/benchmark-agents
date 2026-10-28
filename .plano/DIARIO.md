# Diário de sessões

Uma linha por dia de trabalho. O hook `iniciar-sessao.ps1` lê a última linha para sugerir o nome da sessão (`Dia N · DD/MM · foco`); a skill `/encerrar-dia` fecha a linha do dia.

| Dia | Data | Sessão | Resumo |
|---|---|---|---|
| 1 | 2026-10-13 | Dia 1 · 11–13/10 · Casos e ambiente | Estrutura inicial, especificação do agente, 20 casos de teste, venv e Ollama. |
| 2 | 2026-10-14 | Dia 2 · 14/10 · Agente, benchmark e v2 | Agente mínimo, benchmark completo, linha de base v1 (56%) e v2 (67%); rotina diária. |
| 3 | 2026-10-17 | Dia 3 · 17/10 · v6, régua neutra e v7 | v6 reprovada (perdeu C10), régua neutra criada e v7 (trava do valor 0) aprovada como nova base; ideia do laboratório de agentes registrada. |
| 4 | 2026-10-18 | Dia 4 · 18/10 · v8 noturna | Lote noturno: v8 (v7 + regra de categoria) deu 40/45, mas foi reprovada por perder o C10; oficial seguiu a v7. |
| 5 | 2026-10-22 | Dia 5 · 22/10 · v9 a v12 e classificador | v9, v10 e v12 aprovadas (34 → 41/45), v11 reprovada; classificador de categoria, regra de repetição da base e dashboard ajustado. |
| 6 | 2026-10-23 | Dia 6 · 23/10 · v13 e régua dirigida | Régua dirigida criada; v13 (dica do classificador) reprovada com 40/45 por inventar o pagamento; trava do pagamento simulada (v13 → 44/45) para a v14. |
| 7 | 2026-10-27 | Dia 7 · 27/10 · v14 e v15: 44/45 | v14 (trava do pagamento inventado) aprovada pela régua neutra com 41/45 e v15 (dica religada) aprovada pela régua dirigida com 44/45, nova base. |
| 8 | 2026-10-28 | Dia 8 · 28/10 · C08 ou validação final | (em andamento) |

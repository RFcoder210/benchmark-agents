# Cronograma — 2026-11-27 (sexta-feira)
Prazo final: sem prazo fixo (OBJETIVO.md) | Dias úteis restantes: não se aplica | Situação: NO PRAZO (sem data final; sem risco de prazo)
Progresso: 9 de 13 tarefas concluídas (69%) | Carga restante: 4 unidades (4 P, nenhuma M)
Orçamento de hoje: 6 unidades (limitado por: janelas) | Semana: 4% usada, renova 03/12 (quinta, 13:59)

Cálculo do orçamento: teto pela semana = (100 − 4) ÷ 7 dias (27/11 a 03/12) = 13,7% por dia ÷ 2 = 6,9 unidades; teto pelas janelas = 6 × 1 (2 h ÷ 5 h, arredondado para cima) = 6 unidades. Vale o menor: 6. A janela de 5 h está em 8% (renova 22:09), sem aperto. A carga restante (4 unidades) cabe numa única sessão de 2 h.

## Hoje (em ordem)
| # | Tarefa | Agente | Porte | Depende de | Observação |
|---|---|---|---|---|---|
| 1 | T10 (U) Execução real v15-repeticao pelo botão da página Executar | usuário | P | T09 (concluída) | Ligar o Ollama 0.40.4 antes (`iniciar_ollama.bat` ou pelo lançador); execução leva de 4 a 5 min; confirmar a gravação no CSV |
| 2 | T11 Conferir a execução real e a suíte de testes | executor-tarefa | P | T10 | Só depois que T10 gravar o lote no CSV; conferir também no painel |
| 3 | T12 Documentar a página Executar no README e no CLAUDE.md | executor-tarefa | P | T11 | Atualizar a documentação com o uso da página Executar |
| 4 | T13 (U) Aprovar o commit final e o push | usuário | P | T12 | Após a aprovação, commit (com Co-Authored-By) e `git push` na `main` |

Cadeia de hoje: T10 → T11 → T12 → T13, 4 unidades de agente no total (T10 e T13 dependem de decisão do usuário). Cabe no orçamento de 6.

## Se sobrar cota hoje
- Nenhuma tarefa adiantável: todas as pendentes formam uma cadeia sequencial. Não há tarefa extra a puxar.

## Lembretes antecipados
- Nenhuma entrega com data nos próximos 7 dias: as entregas intermediárias não têm data e não há prazo final fixo (OBJETIVO.md).
- Cota semanal: renova em 03/12 (quinta, 13:59), daqui a 6 dias. Não é entrega; apenas referência para o orçamento.
- Restam só as entregas da execução real (T10), da conferência (T11), da documentação (T12) e do commit final (T13).

## Próximos 3 dias úteis (previsão, dias corridos, sem dias fixos)
- 28/11 (sábado): sem tarefa prevista. Reserva: T13 se a aprovação de hoje ficar para depois.
- 29/11 (domingo): sem tarefa prevista. Reserva: T10 ou T11 se a cadeia de hoje não terminar.
- 30/11 (segunda): sem tarefa prevista se a cadeia de hoje fechar. Caso contrário, retomar pela primeira tarefa pendente (T10 → T11 → T12 → T13).

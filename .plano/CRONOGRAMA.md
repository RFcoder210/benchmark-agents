# Cronograma — 2026-11-26 (quinta-feira)
Prazo final: sem prazo fixo (OBJETIVO.md) | Dias úteis restantes: não se aplica | Situação: NO PRAZO (sem data final; sem risco de prazo)
Progresso: 3 de 13 tarefas concluídas (23%) | Carga restante: 16 unidades (7 P + 3 M)
Orçamento de hoje: 6 unidades (limitado por: janelas) | Semana: 1% usada, renova 03/12 (quinta, 14:00)

Cálculo do orçamento: teto pela semana = (100 − 1) ÷ 7 dias (26/11 a 02/12) = 14,1% por dia ÷ 2 = 7 unidades (7,07); teto pelas janelas = 6 × 1 (2 h ÷ 5 h, arredondado para cima) = 6 unidades. Vale o menor: 6.
Observação: a janela de 5 h está em 9% (renova 21:50), sem aperto. Carga restante de 16 unidades cabe em cerca de 3 sessões de 2 h.

## Hoje (em ordem)
| # | Tarefa | Agente | Porte | Depende de | Observação |
|---|---|---|---|---|---|
| 1 | T04 Conferir a opção --rotulo pela linha de comando | executor-tarefa | P | T03 (concluída) | Primeira tarefa aberta; T03 já está pronta |
| 2 | T05 Teste e esqueleto das regras da execução (execucao.py) | executor-tarefa | P | T04 | Só depois que T04 passar |
| 3 | T06 (U) Escrever ler_progresso() e pode_executar() | usuário | P | T05 | Parte central, escrita pelo usuário com orientação |
| 4 | T07 Lançar e acompanhar o benchmark em segundo plano (execucao.py) | executor-tarefa | M | T06 | Fecha o orçamento de hoje (6 de 6 unidades); só começa se T06 estiver pronta |

Cadeia de hoje: 6 unidades. T08 (M, 3 unidades) não cabe no orçamento de hoje.

## Se sobrar cota hoje
- Nenhuma tarefa P independente disponível: a cadeia é sequencial (T04 → T05 → T06 → T07). Não puxar T08 hoje.

## Lembretes antecipados
- Nenhuma entrega com data nos próximos 7 dias: as entregas intermediárias não têm data e não há prazo final fixo (OBJETIVO.md).
- Cota semanal: renova em 03/12 (quinta, 14:00), daqui a 7 dias. Não é entrega; apenas referência para o orçamento.
- Entregas, para referência: (1) opção --rotulo, T04 e T05 (T03 concluída); (2) botão ligado com progresso, T06 a T09 (T06 do usuário); (3) execução real pelo botão (T10, do usuário) e documentação (T11 a T13).

## Próximos 3 dias úteis (previsão, dias corridos, sem dias fixos)
- 27/11 (sexta): T08 (M, Página Executar: rótulo, confirmação e botão ligado) = 3 unidades. Depende de T07.
- 28/11 (sábado): T09 (M, barra de progresso e resultado) = 3 unidades. Depende de T08.
- 29/11 (domingo): T10 (U, execução real v15-repeticao pelo botão, com Ollama 0.40.4 ligado), T11 (P), T12 (P) e T13 (U, aprovar commit e push) = 4 unidades. Depende de T09 e, em sequência, de T10 → T11 → T12 → T13.

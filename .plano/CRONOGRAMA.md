# Cronograma — 2026-11-20 (sexta-feira)
Prazo final: sem prazo fixo (OBJETIVO.md) | Dias úteis restantes: não se aplica | Situação: NO PRAZO (sem data final; sem risco de prazo)
Progresso: 1 de 13 tarefas concluídas (8%) | Carga restante: 18 unidades (9 P + 3 M)
Orçamento de hoje: 6 unidades (limitado por: janelas) | Semana: 3% usada, renova 26/11 (quinta, 13:59)

Cálculo do orçamento: teto pela semana = (100 − 3) ÷ 6 dias (20 a 25/11) = 16,2% por dia ÷ 2 = 8 unidades; teto pelas janelas = 6 × 1 (2 h ÷ 5 h, arredondado para cima) = 6 unidades. Vale o menor: 6.
Observação: a janela de 5 h atual já está com 17% usados (renova 22:09). Os 6 unidades supõem janela de uso normal; se a janela estiver perto do limite, adie o T06.

## Hoje (em ordem)
| # | Tarefa | Agente | Porte | Depende de | Observação |
|---|---|---|---|---|---|
| 1 | T02 Teste e esqueleto da opção --rotulo | executor-tarefa | P | T01 (concluída) | Primeira tarefa aberta; sem pendência |
| 2 | T03 (U) Escrever rotulo_invalido() e escolher_execucao() | usuário | P | T02 | Parte central, escrita pelo usuário com orientação |
| 3 | T04 Conferir a opção --rotulo pela linha de comando | executor-tarefa | P | T03 | Só depois que T03 estiver pronta |
| 4 | T05 Teste e esqueleto das regras da execução (execucao.py) | executor-tarefa | P | T04 | |
| 5 | T06 (U) Escrever ler_progresso() e pode_executar() | usuário | P | T05 | Parte central; fecha o orçamento de hoje (5 de 6 unidades) |

Cadeia de hoje: 5 unidades. T07 (M, 3 unidades) não cabe no orçamento de hoje.

## Se sobrar cota hoje
- Nenhuma tarefa P independente disponível: a cadeia é sequencial. A 6ª unidade fica livre; não puxar T07 hoje.

## Lembretes antecipados
- Nenhum com data nos próximos 7 dias: as entregas intermediárias não têm data e não há prazo final fixo (OBJETIVO.md).
- Entregas, para referência: (1) opção --rotulo, T02 a T04; (2) botão ligado com progresso, T07 a T09; (3) execução real pelo botão (T10, do usuário) e documentação (T11 a T13).

## Próximos 3 dias úteis (previsão, dias corridos, sem dias fixos)
- 21/11 (sábado): T07 (M) e T08 (M) = 6 unidades. Depende de T06.
- 22/11 (domingo): T09 (M), T10 (U, execução real pelo botão, com Ollama 0.40.4 ligado), T11 (P) e T12 (P) = 6 unidades.
- 23/11 (segunda): T13 (U, aprovar o commit final e o push) = 1 unidade.

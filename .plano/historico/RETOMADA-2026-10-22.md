# Retomada — 2026-10-22
Motivo do checkpoint: fim do dia

## Feito hoje
- v9 aprovada (régua neutra, 34/45): trava do pagamento já informado (af6afc7).
- v10 aprovada (régua normal, 41/45): v9 + regra de categoria da v6 (5ec44f0).
- v11 reprovada (42/45, C08 0→2/3, C13 2→1/3): revisão do vocabulário; texto no commit d01de06.
- v12 aprovada pelo usuário (41/45, C13 3/3): classificador especialista de categoria + trava (dfa1748); perda do C09 comprovada como ruído da própria v10.
- Dashboard: referência padrão = base atual (ed1b0ec); acerto por grupo em linhas (825392b).

## Onde paramos
- Base oficial = v12 (`VERSAO_AGENTE` = "v12"). Tudo commitado no `main`, exceto este encerramento (RETOMADA e DIARIO), se o usuário não o tiver commitado.
- Tarefa em andamento: nenhuma.

## Próxima ação (a primeira coisa de amanhã)
1. Desenhar a v13 = v12 + etiqueta do classificador como dica para o agente (alvo C08) e mostrar o desenho ao usuário ANTES de implementar. Decidir a régua antes de rodar.

## Decisões tomadas que não estão em outro arquivo
- No C08, o classificador acerta "transporte" nas 3 ordens; o agente é que não usa a informação. Na v12 as divergências ficam anotadas na coluna observacao ("categoria divergente").
- A dica da v13 deve entrar na mensagem do usuário, não no prompt de sistema (preserva o cache do prompt).
- O C08 na ordem original pergunta o VALOR (que está na mensagem): a dica de categoria provavelmente não conserta essa ordem.
- Custo da v12: 5,6 s e 2781 tokens por mensagem; reduzir fica para depois (foco na assertividade).
- Conjunto oculto: só depois de encerrar os ajustes do C08/C13; uma vez aberto, deixa de ser oculto.
- Commits com aspas no PowerShell: gravar a mensagem num arquivo e usar `git commit -F`.

## Aguardando o usuário
- Aprovar o desenho da v13 (ou decidir ir direto à validação final no conjunto oculto).

## Ler se necessário
- `CLAUDE.md`, seção 4: itens v9 a v12 e a regra de repetição da base.
- `agente.py`: seção "v12: CLASSIFICADOR ESPECIALISTA DE CATEGORIA + TRAVA".
- `resultados/brutos_v12_2026-10-22_2003.json` (campos `categoria_classificador` e `categoria_divergente`).

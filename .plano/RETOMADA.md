# Retomada — 2026-10-30
Motivo do checkpoint: fim do dia

## Feito hoje
- Teste de mutação do benchmark (`testar_mutacao.py`): comparação com o gabarito aprovada e 8 lacunas dos testes corrigidas (5 exemplos em `testar_comparar.py`; `testar_regua.py` novo).
- Na 0.40.4, 5 de 8 falhas do agente foram detectadas; sobreviveram v4, v9 e o prompt sem "o que não é gasto".
- Descoberta: a atualização automática do Ollama (0.40.13, em 30/10) tira a v15 de 44/45 para 41 a 44/45.
- Benchmark fixado na 0.40.4, com trava de versão (`ambiente.py`, `iniciar_ollama.bat`); a v15 pelo caminho novo deu 44/45, igual a 27/10.

## Onde paramos
- A v1 está concluída; a base segue v15, e os fatos estão em `CLAUDE.md`.
- O trabalho de 30/10 está commitado.
- O servidor fixado está desligado.

## Próxima ação (a primeira coisa de amanhã)
1. Perguntar ao usuário o caminho, recomendando o README de portfólio: (a) README e decisão de publicar; (b) mutantes de entrada; (c) 1º degrau do harness de pesquisa.
2. Se o próximo passo rodar o modelo, lembrar de ligar `.\iniciar_ollama.bat` em outro terminal.

## Decisões tomadas que não estão em outro arquivo
- O `/encerrar-dia` só funciona enviado sozinho pelo usuário; não dá para acioná-lo pela ferramenta Skill.
- Para ligar o servidor pelas ferramentas do Claude, use a ferramenta PowerShell (`.\iniciar_ollama.bat`); `cmd //c` no Bash não encontra o arquivo.
- As mensagens acentuadas da trava saíram corrompidas na captura do Git Bash; a exibição no PowerShell não foi conferida.

## Aguardando o usuário
- Escolher o próximo caminho.

## Ler se necessário
- `resultados/analise_mutacao_2026-10-30.md`
- `CLAUDE.md`: seção 3 (ambiente) e item "Teste de mutação" da seção 4.
- `contexto-benchmark-agentes.md`, seção 8 (evoluções futuras).

# Retomada — 2026-10-23
Motivo do checkpoint: fim do dia

## Feito hoje
- Régua dirigida criada e aceita (`comparar_versoes.py BASE NOVA --alvo CASO`) + encanamento da v13 (bca27f1).
- v13 rodada e REPROVADA (843949c): 40/45; C08 0/3 → 2/3, mas C02 3/3 → 1/3 e C09 2/3 → 1/3 (o agente inventou o pagamento quando recebeu a categoria).
- Simulação: trava "registro sem palavra de pagamento na mensagem → perguntar o pagamento" daria v12 41 → 41 e v13 40 → 44.

## Onde paramos
- Base oficial = v12, MAS o código do agente ainda está na v13: a dica está ligada (`TEXTO_DICA` preenchido em agente.py) e `VERSAO_AGENTE` = "v13" em benchmark.py. Rodar o benchmark agora repete a v13.
- Tudo commitado, exceto este encerramento (RETOMADA, DIARIO e o arquivo em .plano/historico).

## Próxima ação (a primeira coisa de amanhã)
1. Perguntar ao usuário se segue o plano: v14 = v12 + trava do pagamento inventado (régua neutra); depois v15 = v14 + a dica da v13 (régua dirigida, alvo C08). Ele disse que decide depois.
2. Se sim: primeiro voltar o agente oficial à v12 (dica desligada, sem apagar `TEXTO_DICA` nem `mensagem_com_dica()`, que a v15 reutiliza); só então implementar a trava.

## Decisões tomadas que não estão em outro arquivo
- A trava da v14 reaproveita `pagamento_na_mensagem()` (v9). "cartão" sozinho não conta como pagamento, então o C09 vira pergunta do pagamento, como o gabarito pede.
- Ela implementa "valor e pagamento nunca são deduzidos", regra explícita do prompt, e por isso cabe na régua neutra.
- Na v13, o C08 na ordem original passou a registrar certo (era o "pergunta o valor"); só a invertida ainda pergunta a categoria, mesmo com a dica.
- Lição: com o modelo de 4B, a frase de limite no texto da dica não impediu a gangorra; uma trava em Python, sim (pela simulação).
- `testar_dashboard.py` tem a lista fixa `OFICIAIS`: acrescente cada versão nova, senão 1 verificação falha.

## Aguardando o usuário
- Decidir a v14 (plano acima) ou outro caminho (ex.: ir à validação final no conjunto oculto).

## Ler se necessário
- `CLAUDE.md`, seção 4: item "v13 reprovada" e a régua dirigida.
- `agente.py`: seções da v9 (`pagamento_na_mensagem`) e da v13 (`TEXTO_DICA`, `mensagem_com_dica`, início de `interpretar`).
- `resultados/brutos_v13_2026-10-23_1916.json`.

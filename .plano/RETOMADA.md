# Retomada — 2026-10-17
## Feito hoje
- Branch `lote-noturno-2026-10-15` juntado ao `main` (fast-forward); o trabalho continua no `main`.
- v6 (regra de categoria da v5 restrita: deduzir só a categoria) testada: 38/45, mas perdeu o C10 -> reprovada (7617401).
- Régua neutra criada em `comparar_versoes.py` (`--neutra`): trava de segurança aprovada com 0 perdas e total que não cai (11e8126).
- v7 = v4 + trava "valor 0 -> perguntar o valor" (`valor_invalido()` em agente.py): 34/45, igual à v4; aprovada pela régua neutra, **nova base** (9e15bfe).
- Ideia do harness de agentes (pesquisador, analista, juiz, construtor) registrada na seção 8 de contexto-benchmark-agentes.md (53437a4) e documentada em 2 PDFs na pasta `docs/`.
## Onde paramos
- Base oficial = v7. Nada rodando. Só a pasta `docs/` (os 2 PDFs) pode estar sem commit.
## Próxima ação (a primeira coisa de amanhã)
1. Montar a v8 = v7 + a regra de categoria da v6 (o texto está na mensagem do commit 7617401) e rodar o benchmark (régua normal: `comparar_versoes.py v7 v8`).
2. Expectativa (simulação): cerca de 40/45, mas o C10 pode ficar 2/3, porque na ordem invertida pergunta o pagamento que já foi dado; isso ainda reprovaria a v8. Analisar antes de decidir.
## Decisões tomadas que não estão em outro arquivo
- O usuário prefere que eu escreva o código quando ele pedir; ele analisa depois.
- O C08 ("abasteci") não deve ser consertado acrescentando "abastecer" ao prompt (sobreajuste); só com uma revisão geral do vocabulário das categorias, mais tarde.
- Os tokens (+15% na v6) ficam para depois; o foco agora é a assertividade.
## Aguardando o usuário
- Decidir se a pasta `docs/` (PDFs do laboratório) entra no repositório.
## Ler se necessário
- `git show 7617401` (texto da regra de categoria) e `CLAUDE.md`, seção 4 (v6, v7 e régua neutra).

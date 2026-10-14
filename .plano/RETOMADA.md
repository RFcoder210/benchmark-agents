# Retomada — 2026-10-14

## Feito hoje
- Ambiente commitado (`.venv`, `requirements.txt`, Ollama 0.40.4) — `ecd2ff1`.
- Agente mínimo `agente.py` com prompt escrito em conjunto e ferramentas simuladas; `perguntar_usuario` ganhou `campos_faltantes` (especificação atualizada) — `1a3b98e`.
- Benchmark completo `benchmark.py` (ler → executar 3× → comparar → CSV) e `testar_comparar.py` — `3fe84dc`, `c8b913f`, `c9f4c3a`.
- Linha de base v1: 25/45 (56%). v2 (bloco de 8 exemplos resolvidos): **30/45 (67%)**, base atual — `9a96d64`.
- Rotina de uma sessão por dia: hook `iniciar-sessao.ps1` e skill `/encerrar-dia` adaptados a este projeto.

## Onde paramos
- v3 **planejada, não implementada**. Nada pendente de commit além desta adaptação (ver git status).

## Próxima ação (a primeira coisa de amanhã)
1. Implementar a v3: acrescentar ao bloco "Exemplos resolvidos" do `PROMPT_SISTEMA` 3 exemplos de registrar com categoria deduzida — "pedágio 12,40 no crédito" → transporte; "netflix 55 no crédito" → lazer; "remédio pra gripe 28 em dinheiro" → saude. Nada mais muda.
2. Mudar `VERSAO_AGENTE` para "v3" (e o comentário de histórico) em `benchmark.py`; rodar `.venv\Scripts\python benchmark.py`.
3. Comparar v2 × v3 caso a caso a partir de `resultados/resultados.csv`. Meta: recuperar C07, C08, C14 sem perder C02, C09, C15.

## Decisões tomadas que não estão em outro arquivo
- Uma mudança por vez: a troca do exemplo "transferi 500 pra poupança" (suspeito no C10, que passou a ser ignorado) fica para a v4, se o C10 continuar errando.
- C13 ("loja" registrada como mercado) é outro tipo de erro; tratar depois, possivelmente com validação em Python.
- O usuário pode preferir que eu implemente a lógica e ele analise os resultados caso a caso (tabelas por caso).

## Aguardando o usuário
- Aprovar (ou trocar) os 3 exemplos da v3 antes de rodar.

## Ler se necessário
- `CLAUDE.md` (seção 4, resultados v1/v2) | `agente.py` (PROMPT_SISTEMA) | `resultados/resultados.csv`

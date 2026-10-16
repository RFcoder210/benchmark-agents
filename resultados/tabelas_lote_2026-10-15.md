# Tabelas do lote de calibração (geradas por analisar_lote.py)

## Visão geral

| Rótulo | Data | Execuções/caso | Acerto (execuções) | Casos ✓ por maioria | Tempo médio (s) | Tokens médios |
|---|---|---|---|---|---|---|
| v1 | 2026-10-14 19:47 | 3 | 25/45 (56%) | 8/15 | 3.06 (mediana 3.06) | 1513 |
| v2 | 2026-10-14 19:58 | 3 | 30/45 (67%) | 10/15 | 3.21 (mediana 3.19) | 1804 |
| v2-loteA | 2026-10-15 22:24 | 3 | 31/45 (69%) | 10/15 | 2.50 (mediana 2.81) | 1804 |
| v2-t0.7 | 2026-10-15 22:26 | 10 | 108/150 (72%) | 11/15 | 2.41 (mediana 2.80) | 1804 |
| v2-ordemB | 2026-10-15 22:32 | 3 | 30/45 (67%) | 10/15 | 2.65 (mediana 2.93) | 1804 |
| v2-ordemC | 2026-10-15 22:34 | 3 | 25/45 (56%) | 8/15 | 2.50 (mediana 2.64) | 1802 |
| v2-ordemD | 2026-10-15 22:36 | 3 | 30/45 (67%) | 10/15 | 2.70 (mediana 3.00) | 1805 |
| v3-candidato | 2026-10-15 22:38 | 3 | 30/45 (67%) | 10/15 | 2.64 (mediana 2.83) | 1920 |

## A. Determinismo com temperatura 0

- Casos em que as 3 respostas do loteA não são idênticas entre si: ['C14']
- Casos em que as respostas do loteA diferem das da v2 de 14/10 (ação+argumentos): ['C08', 'C14']
- Casos com taxa de acerto diferente da v2 de 14/10: ['C14']
- Total loteA: 31/45 (69%) | v2 de 14/10: 30/45 (67%)
  - C08: loteA ['["perguntar", {"campos_faltantes": ["categoria"], "pergunta": "Qual foi a categoria desse gasto?"}, 1]'] | v2 ['["perguntar", {"campos_faltantes": ["categoria"], "pergunta": "Qual foi a categoria desse gasto (ex: transporte)?"}, 1]']
  - C14: loteA ['["perguntar", {"campos_faltantes": ["categoria"], "pergunta": "Em que foi o presente de aniversário pra sua mãe?"}, 1]', '["registrar", {"categoria": "outros", "data": "2026-10-11", "pagamento": "credito", "valor": 80}, 1]'] | v2 ['["perguntar", {"campos_faltantes": ["categoria"], "pergunta": "Em que foi o presente de aniversário pra sua mãe?"}, 1]']

## B. Temperatura 0.7, 10 execuções

| Caso | v2 (t=0, 3×) | v2-t0.7 (10×) | Respostas distintas | Situação |
|---|---|---|---|---|
| C01 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C02 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C03 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C04 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C05 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C06 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C07 | 0/3 | 0/10 (0%) | 1 | estável ✗ |
| C08 | 0/3 | 0/10 (0%) | 3 | estável ✗ |
| C09 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C10 | 0/3 | 6/10 (60%) | 2 | INSTÁVEL |
| C11 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C12 | 3/3 | 10/10 (100%) | 1 | estável ✓ |
| C13 | 0/3 | 0/10 (0%) | 1 | estável ✗ |
| C14 | 0/3 | 2/10 (20%) | 2 | INSTÁVEL |
| C15 | 3/3 | 10/10 (100%) | 1 | estável ✓ |

Casos instáveis (0 < acertos < 10): ['C10', 'C14']

Chance de a maioria de k execuções concordar com o veredito das 10 (casos instáveis):

| Caso | p (10×) | k=1 | k=3 | k=5 | k=7 | k=9 |
|---|---|---|---|---|---|---|
| C10 | 60% | 60% | 65% | 68% | 71% | 73% |
| C14 | 20% | 80% | 90% | 94% | 97% | 98% |

Desvio-padrão esperado da taxa de acerto geral (pontos percentuais), por k:

| k | 1 | 3 | 5 | 10 | 20 |
|---|---|---|---|---|---|
| desvio (p.p.) | 4.2 | 2.4 | 1.9 | 1.3 | 0.9 |

## C. Reordenação dos exemplos (temperatura 0)

- v2-ordemB: ordem [3, 4, 6, 7, 2, 5, 0, 1]
- v2-ordemC: ordem [3, 7, 2, 0, 4, 6, 5, 1]
- v2-ordemD: ordem [3, 5, 2, 4, 1, 6, 7, 0]

| Caso | v2 | v2-loteA | v2-ordemB | v2-ordemC | v2-ordemD |
|---|---|---|---|---|---|
| C01 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C02 | ✓ 3/3 | ✓ 3/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| C03 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C04 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C05 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✗ 1/3 | ✓ 3/3 |
| C06 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✗ 0/3 | ✓ 3/3 |
| C07 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| C08 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| C09 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C10 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |
| C11 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C12 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| C13 | ✗ 0/3 | ✗ 0/3 | ✓ 3/3 | ✗ 0/3 | ✗ 0/3 |
| C14 | ✗ 0/3 | ✗ 1/3 | ✗ 0/3 | ✓ 3/3 | ✓ 3/3 |
| C15 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |
| **Total ✓** | 10/15 | 10/15 | 10/15 | 8/15 | 10/15 |

- v2-ordemB: 2 caso(s) viraram em relação à v2: ['C02', 'C13'] | total 30/45 (67%)

- v2-ordemC: 4 caso(s) viraram em relação à v2: ['C02', 'C05', 'C06', 'C14'] | total 25/45 (56%)

- v2-ordemD: 2 caso(s) viraram em relação à v2: ['C02', 'C14'] | total 30/45 (67%)

- Casos sensíveis à ordem (viraram em pelo menos uma): ['C02', 'C05', 'C06', 'C13', 'C14']
- Viradas por reordenação: mínimo 2, máximo 4, média 2.7
- Para comparação, v1 → v2: 4 caso(s) viraram: ['C02', 'C07', 'C09', 'C15']
  - C02: v1 ✗ → v2 ✓
  - C07: v1 ✓ → v2 ✗
  - C09: v1 ✗ → v2 ✓
  - C15: v1 ✗ → v2 ✓
- Acertos (de 45) nas reordenações: [30, 25, 30]; v2 = 30; v1 = 25

## D. v2 × v3-candidato (temperatura 0)

| Caso | Papel | v2 (14/10) | v2-loteA | v3-candidato | Mudou? |
|---|---|---|---|---|---|
| C01 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C02 | protegido | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C03 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C04 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C05 |  | ✓ 3/3 | ✓ 3/3 | ✗ 0/3 | **sim** |
| C06 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C07 | meta | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |  |
| C08 | meta | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |  |
| C09 | protegido | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C10 |  | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |  |
| C11 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C12 |  | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |
| C13 |  | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 |  |
| C14 | meta | ✗ 0/3 | ✗ 1/3 | ✓ 3/3 | **sim** |
| C15 | protegido | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 |  |

- Viradas v2 → v3-candidato: 2 (ganhos ['C14'], perdas ['C05']); saldo +0 | total 30/45 (67%)
- Meta ['C07', 'C08', 'C14']: C07 ✗, C08 ✗, C14 ✓
- Protegidos ['C02', 'C09', 'C15']: C02 ✓, C09 ✓, C15 ✓

Erros da v3-candidato (coluna observacao do CSV):

- C05: ignorou; texto: "registrar_gasto: valor 187.3, categoria moradia, pagamento debito, data 2026-10-"
- C07: perguntou ['categoria']: "Em que categoria foi esse gasto? (lazer ou outros)"
- C08: perguntou ['categoria']: "Qual foi a categoria desse gasto?"
- C10: ignorou; texto: "registrar_gasto: valor 0.0, categoria educacao, pagamento pix, data de referênci"
- C13: registrou: valor=50, categoria=mercado, pagamento=debito, data=2026-10-11

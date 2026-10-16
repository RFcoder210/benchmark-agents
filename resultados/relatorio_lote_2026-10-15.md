# Relatório do lote de calibração — noite de 15/10/2026

Branch: `lote-noturno-2026-10-15` · Modelo: `qwen3:4b-instruct` (Ollama local, custo R$ 0) · Casos: só `casos/casos.json` (15). O conjunto oculto não foi aberto.
Tabelas completas, geradas por `analisar_lote.py`: [tabelas_lote_2026-10-15.md](tabelas_lote_2026-10-15.md).

## Resumo (5 linhas)

1. **Temperatura 0 é quase determinística, mas não totalmente:** na repetição da v2, 14 dos 15 casos deram exatamente o mesmo resultado; o C14 variou (1 acerto em 3 hoje, 0 em 3 ontem).
2. **Reordenar os exemplos, sem mudar o conteúdo, virou de 2 a 4 casos** (média 2,7) e moveu o total entre 25/45 e 30/45. Esse é o **limiar de ruído** do benchmark atual.
3. **A melhora v1 → v2 (25/45 → 30/45) está dentro desse limiar:** só a reordenação da v2 já produz 25/45. Os ganhos C09 e C15 parecem sólidos (resistiram a todas as ordens); o C02 não (caiu nas 3 reordenações).
4. **A v3 candidata ficou empatada com a v2 (30/45):** recuperou o C14, não recuperou C07 nem C08, manteve C02, C09 e C15 e **perdeu o C05**. A diferença (2 viradas, saldo 0) não supera o limiar de ruído.
5. **Achado inesperado:** todos os erros "ignorou" de casos que eram gastos (C10 sempre; C05 e C06 em algumas variantes) são o modelo **escrevendo a chamada de ferramenta como texto**, imitando o formato dos exemplos (`registrar_gasto: valor ...`). Na v1 isso nunca ocorreu.

## O que foi feito e por quê

Antes de pesar ingredientes, um cozinheiro cuidadoso coloca na balança um peso conhecido: se a balança marca 1 kg ora como 1,00, ora como 1,05, ele sabe que diferenças menores que 50 g não significam nada. O benchmark é a nossa balança. Até aqui, comparamos v1 e v2 sem saber quanto ele "oscila sozinho". Este lote mede essa oscilação de três formas:

| Rodada | Rótulo no CSV | O que muda | Pergunta |
|---|---|---|---|
| A | `v2-loteA` | nada (repete a v2, temperatura 0, 3×) | O resultado se repete? |
| B | `v2-t0.7` | temperatura 0,7, 10× | Quais casos oscilam quando há aleatoriedade? Quantas repetições bastam? |
| C | `v2-ordemB/C/D` | só a **ordem** dos 8 exemplos (temperatura 0, 3×) | Quanto o resultado muda sem mudar o conteúdo? |
| D | `v3-candidato` | v2 + 3 exemplos de registrar (temperatura 0, 3×) | Exploratório: os exemplos propostos ajudam? |

Ordens sorteadas com `random.Random(42)` (índices dos exemplos originais, 0 = "pizza 45 no débito" … 7 = "transferi 500 pra poupança"):

- `v2-ordemB`: [3, 4, 6, 7, 2, 5, 0, 1]
- `v2-ordemC`: [3, 7, 2, 0, 4, 6, 5, 1]
- `v2-ordemD`: [3, 5, 2, 4, 1, 6, 7, 0]

Exemplos acrescentados na rodada D (ao fim do bloco, no mesmo formato dos existentes):
`"pedágio 12,40 no crédito"` → transporte, 12.4, credito · `"netflix 55 no crédito"` → lazer, 55.0, credito · `"remédio pra gripe 28 em dinheiro"` → saude, 28.0, dinheiro (todos com a data de referência).

**Mudanças no código** (a versão oficial continua v2, idêntica):
- `agente.py`: `interpretar()` ganhou `temperatura=0` e `prompt_sistema=None` (com os padrões, o comportamento é o de antes). Novas funções `separar_exemplos()` e `montar_prompt(ordem, extras)`. Um `assert` garante que `montar_prompt()` sem argumentos reproduz o `PROMPT_SISTEMA` caractere por caractere; também conferi que o prompt e as ferramentas são idênticos aos do commit anterior.
- `benchmark.py`: `executar_casos`, `salvar_brutos` e `avaliar` ganharam parâmetros opcionais (temperatura, prompt, rótulo) cujos padrões são os valores antigos. `VERSAO_AGENTE` continua `"v2"`.
- Novos: `lote.py`, `analisar_lote.py`, `resultados/lote_2026-10-15_config.json` (configuração exata de cada rodada) e `resultados/lote_2026-10-15.log` (saída da execução).

Todas as rodadas terminaram sem erro (≈16 min no total).

## A. Repetição da v2 com temperatura 0

| | Acertos | Casos ✓ (maioria) |
|---|---|---|
| v2 de 14/10 | 30/45 | 10/15 |
| v2-loteA (15/10) | 31/45 | 10/15 |

- 14 de 15 casos tiveram exatamente a mesma taxa de acerto. Exceção: **C14**, que hoje acertou 1 de 3 (registrou "outros"), contra 0 de 3 ontem.
- Comparando as respostas cruas (ação + argumentos), além do C14 só o texto da pergunta do C08 mudou ("Qual foi a categoria desse gasto (ex: transporte)?" → "... desse gasto?"). O texto da pergunta não é avaliado.
- **Conclusão:** com temperatura 0 o modelo é *quase* determinístico. Pequenas variações numéricas no cálculo (a GPU nem sempre soma na mesma ordem) podem mudar a resposta quando o modelo está "em cima do muro", como no C14.
- **Implicação:** repetir 3× com temperatura 0 quase não traz informação nova (as 3 execuções costumam ser cópias), mas é barato (≈2 min) e detecta casos "em cima do muro" como o C14. Sugestão: manter 3 execuções, sabendo que **elas não medem o ruído principal** (ver C).

## B. Temperatura 0,7, 10 execuções

| Caso | v2 (t=0, 3×) | v2-t0.7 (10×) | Respostas distintas | Situação |
|---|---|---|---|---|
| C01 | 3/3 | 10/10 | 1 | estável ✓ |
| C02 | 3/3 | 10/10 | 1 | estável ✓ |
| C03 | 3/3 | 10/10 | 1 | estável ✓ |
| C04 | 3/3 | 10/10 | 1 | estável ✓ |
| C05 | 3/3 | 10/10 | 1 | estável ✓ |
| C06 | 3/3 | 10/10 | 1 | estável ✓ |
| C07 | 0/3 | 0/10 | 1 | estável ✗ |
| C08 | 0/3 | 0/10 | 3 | estável ✗ (erra de formas diferentes) |
| C09 | 3/3 | 10/10 | 1 | estável ✓ |
| C10 | 0/3 | **6/10** | 2 | **instável** |
| C11 | 3/3 | 10/10 | 1 | estável ✓ |
| C12 | 3/3 | 10/10 | 1 | estável ✓ |
| C13 | 0/3 | 0/10 | 1 | estável ✗ |
| C14 | 0/3 | **2/10** | 2 | **instável** |
| C15 | 3/3 | 10/10 | 1 | estável ✓ |

Total: 108/150 (72%), um pouco **acima** da temperatura 0 (67–69%), por causa do C10: com aleatoriedade, às vezes o modelo "escapa" de escrever a ferramenta como texto.

**Quantas repetições?** Chance de o voto da maioria de *k* execuções dar o mesmo veredito que as 10 execuções (modelo binomial):

| Caso | taxa | k=1 | k=3 | k=5 | k=7 | k=9 |
|---|---|---|---|---|---|---|
| C10 | 60% | 60% | 65% | 68% | 71% | 73% |
| C14 | 20% | 80% | 90% | 94% | 97% | 98% |

Oscilação esperada (desvio-padrão) da taxa de acerto geral: k=1 → 4,2 p.p.; k=3 → 2,4; k=5 → 1,9; k=10 → 1,3; k=20 → 0,9.

**Recomendação para agentes com temperatura > 0:** pelo menos **5 execuções por caso** (desvio de ~2 p.p. no total, e ~94% de acerto no veredito de um caso com taxa 20% ou 80%), e **10** quando se quer comparar versões caso a caso. Para casos perto de 50% (como o C10), nenhum número razoável de repetições dá um veredito ✓/✗ confiável: nesses casos deve-se **relatar a taxa** (ex.: 6/10), não a maioria.

## C. Reordenação dos exemplos (o "limiar de ruído")

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
| **Casos ✓** | 10 | 10 | 10 | 8 | 10 |
| **Acertos** | 30/45 | 31/45 | 30/45 | 25/45 | 30/45 |

Casos que viraram em relação à v2, **só por reordenar**: ordemB 2 (C02, C13) · ordemC 4 (C02, C05, C06, C14) · ordemD 2 (C02, C14). Casos sensíveis à ordem: C02, C05, C06, C13, C14.

O total quase não muda (as viradas se compensam), mas **quais** casos acertam muda bastante. Por isso a comparação caso a caso é mais sensível ao ruído do que o total.

**Definição proposta do limiar de ruído:** o número máximo de casos que viraram só por reordenar = **4 casos** (de 15), ou, em acertos, uma faixa de **25 a 30 de 45**. Uma mudança no agente só deve ser considerada "real" se virar mais casos do que isso, ou se as viradas se repetirem em várias ordens.

**A melhora v1 → v2 à luz do limiar:** v1 → v2 virou 4 casos (ganhou C02, C09, C15; perdeu C07) e foi de 25 para 30 acertos. Isso **não supera** o limiar: a própria v2, só reordenada, faz 25/45. Olhando caso a caso, porém, há evidência mista:
- **C09 e C15** passaram em todas as 5 medições da v2 (inclusive nas 3 ordens): ganho provavelmente real.
- **C02** só passa na ordem original; nas 3 reordenações ele pergunta categoria **e** pagamento (a categoria "almoço" era conhecida). Ganho frágil.
- **C07** falhou em todas: a perda parece real e consistente ("lazer ou outros?").

## D. v2 × v3-candidato (exploratório; temperatura 0, 3×)

| Caso | Papel | v2 (14/10) | v2-loteA | v3-candidato | Mudou? |
|---|---|---|---|---|---|
| C01 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C02 | **não pode cair** | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C03 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C04 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C05 | | ✓ 3/3 | ✓ 3/3 | ✗ 0/3 | **sim (perdeu)** |
| C06 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C07 | **meta** | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | |
| C08 | **meta** | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | |
| C09 | **não pode cair** | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C10 | | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | |
| C11 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C12 | | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| C13 | | ✗ 0/3 | ✗ 0/3 | ✗ 0/3 | |
| C14 | **meta** | ✗ 0/3 | ✗ 1/3 | ✓ 3/3 | **sim (ganhou)** |
| C15 | **não pode cair** | ✓ 3/3 | ✓ 3/3 | ✓ 3/3 | |
| **Total** | | 30/45 | 31/45 | 30/45 | |

- Meta: **C14 ✓**, C07 ✗ (ainda pergunta "lazer ou outros?"), C08 ✗ (ainda pergunta a categoria de "abasteci o carro").
- Protegidos: C02, C09 e C15 mantidos.
- Nova perda: **C05** ("conta de luz, 187,30 no débito"): o modelo escreveu `registrar_gasto: valor 187.3, categoria moradia, ...` **como texto**, sem chamar a ferramenta. A interpretação estava certa; o formato, não.
- **Comparação com o limiar:** 2 viradas (1 ganho, 1 perda, saldo 0) — **abaixo** do limiar de 4. Além disso, o C14 é justamente um dos casos sensíveis à ordem (virou em ordemC e ordemD, e oscilou no loteA e na temperatura 0,7). Os dados de hoje **não permitem afirmar** que a v3 candidata é melhor ou pior que a v2. A decisão é sua.

## Achado extra: chamadas de ferramenta escritas como texto

Contei, em todos os arquivos de brutos, os casos que deveriam ser gasto mas foram "ignorados" com o texto contendo `registrar_gasto` ou `perguntar_usuario`:

| Execução | Casos afetados (execuções) |
|---|---|
| v1 (2 execuções) | nenhum |
| v2, v2-loteA, ordemB, ordemD | C10 (3/3) |
| v2-t0.7 | C10 (4/10) |
| v2-ordemC | C10 (3), C06 (3), C05 (2) |
| v3-candidato | C10 (3), C05 (3) |

No C10 de 14/10, o texto era `perguntar_usuario: campos_faltantes ["valor"], pergunta "Qual foi o valor do cur...` — ou seja, **a interpretação estava certa**. Isso enfraquece a hipótese registrada ontem de que o exemplo "transferi 500 pra poupança" faria o C10 ser ignorado. Hipótese alternativa (a verificar por você): o formato `-> registrar_gasto: ...` dos exemplos ensina o modelo a *escrever* a chamada em vez de *fazê-la*, e quanto mais exemplos nesse formato, mais isso acontece (a v3 tem 11 e piorou o C05). Isso se encaixa em dois degraus da escada: mudar o formato dos exemplos, ou "validação em Python" (reconhecer esse texto e convertê-lo em chamada).

## Tempo e tokens médios por lote

| Rótulo | Tempo médio (s) | Mediana (s) | Tokens médios |
|---|---|---|---|
| v1 (14/10) | 3,06 | 3,06 | 1513 |
| v2 (14/10) | 3,21 | 3,19 | 1804 |
| v2-loteA | 2,50 | 2,81 | 1804 |
| v2-t0.7 | 2,41 | 2,80 | 1804 |
| v2-ordemB | 2,65 | 2,93 | 1804 |
| v2-ordemC | 2,50 | 2,64 | 1802 |
| v2-ordemD | 2,70 | 3,00 | 1805 |
| v3-candidato | 2,64 | 2,83 | 1920 |

A v3 custa ~116 tokens a mais por resposta (+6%), por causa dos 3 exemplos. Custo financeiro: zero em todos (modelo local). A primeira chamada de cada execução pode demorar mais (carregamento do modelo), por isso incluí a mediana.

## Limitações

- **Só 15 casos:** uma virada vale 6,7 p.p. Qualquer conclusão sobre um caso isolado é frágil.
- **Só 3 ordens sorteadas**, e por acaso todas começam pelo exemplo 3 ("ingresso do show, 120 no cartão"). Não é possível separar "ordem diferente" de "esse exemplo em primeiro lugar" (isso pode explicar o C02 cair nas 3).
- Com temperatura 0, as 3 repetições são quase cópias: as taxas 0/3 e 3/3 não significam "100% de certeza".
- A recomendação de repetições (B) usa as taxas de 10 execuções como se fossem a verdade; com 10 execuções, a própria taxa ainda tem incerteza (6/10 pode ser 40% ou 80%).
- O texto da pergunta não é avaliado (só `campos_faltantes`).
- O lote mediu um único modelo (`qwen3:4b-instruct`) num único computador; GPU e versão do Ollama podem mudar o determinismo.
- Não rodei `benchmark.py` sozinho depois das mudanças (isso acrescentaria 45 linhas "v2" ao CSV). Conferi por leitura de código e pelo teste do prompt que os padrões são os antigos.
- `testar_comparar.py` (Parte B) usa o brutos "mais recente" pela **ordem alfabética do nome**; com os novos rótulos, ele agora pega `brutos_v3-candidato_...`. Não é erro, mas vale saber.

## Perguntas guiadas (para você responder)

1. O C14 acertou 0/3 ontem, 1/3 hoje com o mesmo prompt, 3/3 em duas reordenações e 3/3 na v3. Se fosse um exame médico, você confiaria nesse "ganho" da v3? O que precisaria ver para confiar?
2. Reordenar os exemplos levou o total de 30 para 25 sem mudar nenhuma palavra. Com isso em mente, você ainda descreveria a v2 como "melhor que a v1"? Que parte dessa melhora (C02, C09, C15) você considera real, e por quê?
3. Olhe os textos do C10 e do C05 na coluna `observacao`. O agente entendeu a mensagem? Esse erro é de *interpretação* ou de *formato*? Em qual degrau da escada ele deveria ser tratado?
4. Para as próximas comparações, o que é mais útil: repetir cada caso 3× com a mesma ordem, ou rodar 1× em 3 ordens diferentes? Por quê?
5. Com base no limiar de 4 casos, qual regra você escreveria para "aprovar" uma nova versão do agente?

## Conceitos de Python usados

- **Funções com parâmetros padrão** (`def interpretar(mensagem, data_referencia, temperatura=0, prompt_sistema=None)`): quem não passa o argumento recebe o valor padrão. É assim que o benchmark antigo continua igual e o lote consegue variar as coisas.
- **`None` e `is None`**: "nada foi informado". Usamos para dizer "use o prompt oficial".
- **Fatiamento de textos e listas** (`prompt[:inicio]`, `linhas[i:i + 2]`, `lista[:]`): pegar pedaços, como cortar uma fita métrica em trechos.
- **`str.index`, `split` e `join`**: achar a posição de um trecho, quebrar um texto em linhas e juntá-las de novo.
- **`assert`**: uma verificação que interrompe o programa se for falsa. Garante que a "montagem" reproduz o prompt original.
- **Compreensão de lista** (`[EXEMPLOS_V2[i] for i in ordem]`): cria uma lista nova em uma linha.
- **`random.Random(42)`**: um sorteador com semente fixa; o mesmo número gera sempre o mesmo sorteio, o que torna o experimento repetível.
- **Laço `while`**: repete até a condição ficar falsa (sortear até ter 3 ordens diferentes).
- **Dicionários** e **`setdefault`**: agrupar linhas por rótulo ou por caso (`{"C01": (3, 3), ...}`); `{**a, **b}` junta dois dicionários.
- **Tuplas e desempacotamento** (`acertos, total = taxas[c]`; `maioria(*taxas[c])`): várias informações num pacote só, abertas em variáveis.
- **`try / except`**: se uma rodada der erro, anota e segue para a próxima, em vez de perder o lote.
- **`sys.argv`**: os argumentos digitados depois do nome do script (`lote.py --teste`).
- **Módulos `csv` e `json`**: ler o CSV (`DictReader`, com `;`) e os brutos; `json.dumps(..., sort_keys=True)` transforma uma resposta num texto comparável.
- **`math.comb` e `math.sqrt`**: combinações (para a conta binomial) e raiz quadrada (desvio-padrão).
- **`set`**: conjunto sem repetição; `len(set(respostas))` conta quantas respostas *diferentes* houve.

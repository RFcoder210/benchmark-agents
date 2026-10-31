# Teste de mutação do benchmark (30/10)

Objetivo: verificar se o benchmark percebe falhas colocadas de propósito. Script: `testar_mutacao.py`. Respostas da Parte C: `resultados/mutacao/`, com uma pasta por versão do Ollama. Nada foi gravado em `resultados/resultados.csv`, e o conjunto oculto não foi usado.

## Conclusões

1. **A comparação com o gabarito funciona.** Das 15 corrupções, 12 foram detectadas em 100% das respostas. As outras 3 são pontos cegos previstos.
2. **Os testes do benchmark tinham lacunas, agora corrigidas.** Dos 23 mutantes de código, 8 não foram detectados na 1ª rodada, além de 1 equivalente. Com os novos exemplos, só o equivalente sobrevive.
3. **Na 0.40.4, o benchmark é estável e detecta 5 de 8 falhas do agente.** A v15 sem mudança deu 44/45 nas 3 repetições, com o mesmo erro de 27/10.
4. **O Ollama 0.40.13 muda o resultado.** A versão instalada automaticamente em 30/10, às 16:49, fez a mesma v15 variar de 41 a 44/45. A régua neutra chegou a reprovar a v15 contra ela mesma. Por isso, a versão do Ollama faz parte do experimento.

## Parte A: respostas certas da v15 corrompidas

| Corrupção | Detectadas |
|---|---|
| valor + 1; valor x 10; categoria trocada; pagamento trocado; data um dia antes; pagamento esquecido; registro virou ignorar | 23/23 cada |
| pergunta virou registro; pergunta com campo a menos; pergunta com campo a mais | 15/15 cada |
| ignorar virou registro | 6/6 |
| 2 chamadas de ferramenta | 38/38 |
| **texto da pergunta sem sentido** | **0/15** |
| **campo inventado no registro** | **0/23** |
| **conversou em vez de ignorar** | **0/6** |

Os 3 pontos cegos ficam como limites conhecidos. Mudar a comparação alteraria a régua usada em todas as versões anteriores.

## Parte B: código do benchmark mutado

| Mutante que não foi detectado na 1ª rodada | Situação após os novos exemplos |
|---|---|
| valor errado nunca conta | detectado |
| valor com tolerância de R$ 1 | detectado |
| data só é conferida se ausente | detectado |
| pergunta aceita campo a menos | detectado |
| régua: exige só 1 ganho | detectado |
| régua: o total pode cair | detectado |
| régua: alvo precisa subir só 1 | detectado |
| régua: dirigida ignora perdas | detectado |
| sem o teste de campo ausente | sobrevive: é equivalente, pois não muda o comportamento |

Foram acrescentados 5 exemplos em `testar_comparar.py` e criado `testar_regua.py`, com 11 exemplos. A régua original reproduz as 13 decisões históricas.

Nas 1.185 respostas salvas (sem o conjunto oculto), nenhum veredito depende da conferência de valor, categoria, pagamento ou data de um campo presente: todos os erros do CSV são de ação ou de `campos_faltantes`. Essa conferência só foi acionada de verdade neste teste, no mutante `prompt-sem-datas`.

## Parte C: a mesma v15 nas duas versões do Ollama

O modelo tem o mesmo ID (`0edcdef34593`) nas duas versões, e o `agente.py` não mudou desde a v15.

| Execução da v15, sem mudança | 0.40.4 | 0.40.13 |
|---|---|---|
| Modelo recém-carregado, 1ª vez | 44/45 (C08 2/3) | 41/45 (C08 1/3, C13 1/3) |
| Modelo já carregado | 44/45 (C08 2/3) | 44/45 (C13 2/3) |
| Modelo recém-carregado, 2ª vez | 44/45 (C08 2/3) | 41/45 (C08 1/3, C13 1/3) |
| Classificador no C13 | `nao_identificavel` | `mercado` |
| Trava da v12 age no C13 | sim | não |
| Régua neutra, v15 x v15 | aprova | **reprova** (falso alarme) |

Na 0.40.4, as duas execuções recém-carregadas repetiram exatamente as respostas de 27/10. A execução com o modelo já carregado difere só no C15 da ordem original, sem mudar o placar.

## Parte C: agente mutado, na 0.40.4

Critério: um mutante é detectado se algum caso cair abaixo do pior controle.

| Mutante | Total | Resultado | Abaixo da faixa | Previsão |
|---|---|---|---|---|
| sem trava do valor (v7) | 43/45 | detectado | C10 3→2 | certa |
| sem trava da categoria (v12) | 43/45 | detectado | C13 3→2 | certa |
| sem trava do pagamento inventado (v14) | 40/45 | detectado | C02 3→1, C09 3→1 | certa |
| sem a dica (v15) | 42/45 | detectado | C08 2→0 | em parte: previa também o C09 |
| prompt sem a seção de datas | 40/45 | detectado | C08 2→0, C12 3→1 | certa |
| sem recuperação do texto (v4) | 44/45 | sobreviveu | nenhum | certa |
| sem trava do pagamento informado (v9) | 44/45 | sobreviveu | nenhum | certa |
| prompt sem "o que não é gasto" | 44/45 | sobreviveu | nenhum | **errada**: previa o C11 |

Leituras:

- **v4 e v9:** os 15 casos não acionam essas travas na v15, então desligá-las não muda nada. Elas agem quando o prompt muda: sem "o que não é gasto", a v4 recuperou 5 chamadas e a v9 agiu 1 vez.
- **"O que não é gasto":** C04 e C11 seguiram 3/3 sem a seção. Os casos atuais não medem essa regra.
- **Dica:** sem ela, o C09 ficou 3/3. A previsão vinha da v14, em que o erro do C09 já tinha sido tratado como ruído.
- **Prompt sem datas:** gerou os primeiros erros reais só de campo: a data errada no C08 (3 ordens) e no C12 (2 ordens).

## Decisão: benchmark fixado na 0.40.4

A versão portátil fica em `%LOCALAPPDATA%\Programs\Ollama-0.40.4`, na porta 11500, e é ligada com `.\iniciar_ollama.bat`. `ambiente.py` aponta o agente para ela, e `benchmark.py` para com um aviso se o servidor estiver desligado ou em outra versão. A trava foi testada nesses dois casos. Depois, a v15 pelo caminho novo deu 44/45, com as mesmas respostas de 27/10, sem gravar no CSV (`controle-v15-apos-fixar`).

## Limites

- A estabilidade da 0.40.4 vem de 3 repetições no mesmo dia. O ruído do C09 visto na v12 também ocorreu nessa versão, então ela não é livre de ruído.
- O 15/15 do conjunto oculto foi medido na 0.40.4 e não foi repetido. Ele continua válido só para essa versão.
- A causa interna da mudança na 0.40.13 não foi investigada; o teste mostra o efeito da versão, não o mecanismo.

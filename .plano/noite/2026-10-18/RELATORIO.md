# Relatório da noite — 2026-10-18 (benchmark-agents)

## 1. Resumo
- 1 tarefa no lote (V8): **concluída** e aprovada na revisão individual. Nenhuma reprovada nem bloqueada.
- Resultado da v8: **40/45 (89%)**, contra 34/45 da v7. Mesmo assim foi **reprovada pela régua normal**, porque o C10 caiu de 3/3 para 2/3. Pela sua decisão ("Seguir o padrão de sempre"), o `agente.py` voltou à v7 e os dados da v8 ficaram guardados.
- Revisão geral: **COM_RESSALVAS** (nenhum problema grave; integridade ok; testes passando).
- Primeira coisa a fazer: restaurar as notificações (seção 6, item 1) e depois ler a [análise da v8](../../../resultados/analise_v8_2026-10-18.md), seção 8.

## 2. Tabela
| Tarefa | Status final | Modelo | Veredito | Ressalva |
|---|---|---|---|---|
| V8: v8 = v7 + regra de categoria da v6 | concluída (v8 reprovada pela régua) | opus | APROVADA | o critério (b) do lote contradizia a seção 6; o executor seguiu a seção 6, que é a correta |

## 3. O que foi feito
- **V8.** O bloco de regra do commit `d40483e` entrou na seção Categorias do prompt. O benchmark rodou uma vez (45 respostas) e depois veio `comparar_versoes.py v7 v8`. Ganhos: C02, C07 e C14 viraram estáveis ✓, e o C13 foi de 1/3 para 2/3. Perda: o C10 caiu de 3/3 para 2/3. Decisão da régua: MANTER v7. A simulação da retomada acertou o resultado (40/45, com o C10 falhando na ordem invertida).
- Arquivos: [analise_v8_2026-10-18.md](../../../resultados/analise_v8_2026-10-18.md) (novo), `resultados/brutos_v8_2026-10-18_2032.json` (novo), `resultados/resultados.csv` (+45 linhas, 0 removidas), [benchmark.py](../../../benchmark.py) (histórico), [dashboard.py](../../../dashboard.py) (`HISTORICO` com "v8": "reprovada"), [testar_dashboard.py](../../../testar_dashboard.py) (`OFICIAIS` com a v8) e [CLAUDE.md](../../../CLAUDE.md) (seção 4).
- O `agente.py` termina idêntico ao do `main` (v7).

## 4. Decisões conservadoras
- **Execução nesta sessão, logo após a preparação** (você escolheu "Agora"), sem tarefa agendada.
- **`VERSAO_AGENTE` voltou a "v7"**, como no commit da v6 (que voltou a "v4"), seguindo a seção 6 do lote e não a letra do critério (b).
- **As 2 ressalvas da revisão geral no CLAUDE.md não foram corrigidas à noite**: só registro aqui (seção 6), porque não faziam parte da tarefa aprovada.
- **A régua não foi tocada**, embora a análise mostre que a única perda é por "perguntar demais" e não por inventar dado. Mudar a régua é decisão sua.

## 5. O que não funcionou ou não foi verificado
- **A v8 não passou.** Ela não virou base, apesar dos +6 acertos.
- **A regra continua puxando o valor para 0 no C10.** Em 2 das 3 ordens, o modelo escreveu `registrar_gasto: valor 0.0`. Foi a trava da v7 (acionada pela primeira vez) que salvou essas respostas, não o modelo.
- **C08 continua 0/3 e ganhou um modo de falha novo.** Na ordem original, a v8 perguntou o **valor** (o 150 estava na mensagem). Na ordem girada, a pergunta ("forma de pagamento?") não bate com `campos_faltantes ['categoria']`.
- **O texto exato que rodou só pode ser provado pelos dados.** O `agente.py` foi revertido e nenhum diff da v8 ficou guardado. A prova indireta: os tokens de entrada da v8 são iguais aos da v6 nas 45 respostas, e as respostas também são iguais, exceto as 2 travadas.
- **`testar_comparar.py` lê o `brutos_*.json` mais recente.** Por isso agora reproduz 40/45 (v8), e não 34/45 (v7). Ele continua passando, mas o número mostrado mudou.
- **`comparar_versoes.py` quebra ao gravar o ✓ em arquivo no console do Windows (cp1252).** Contorno usado: `PYTHONIOENCODING=utf-8`. O defeito é antigo e não foi corrigido (o arquivo é protegido).

## 6. Para o usuário
1. **Restaurar as notificações** para os valores da seção 10 do [LOTE.md](LOTE.md): som `system` e os três avisos em `banner`.
2. **Decidir o próximo passo após a v8.** Ver a [análise](../../../resultados/analise_v8_2026-10-18.md), seção 8, e o CLAUDE.md, linha 46. Uma opção que só você pode decidir: a régua distinguir perda por "perguntar demais" de perda por inventar dado.
3. **Corrigir o CLAUDE.md.** A linha 45 (item da v7) ainda diz "Próximo passo: v8 = …", o que está desatualizado. Se quiser, registre no item da v8 a falha nova do C08 (pergunta o valor que foi dado).
4. **Decidir se o branch `noite/2026-10-18` entra no `main`.**
5. **Fechar a linha do Dia 4** em `.plano/DIARIO.md` no `/encerrar-dia`.
6. Para os próximos lotes: o critério de pronto não deve fixar um valor que a decisão do usuário pode mudar (o caso do critério (b)).

## 7. Git
- Branch `noite/2026-10-18`, criado a partir de `main` (90bca0f). Commits: `e5304ba` (v8 reprovada) e o commit de encerramento (relatório, revisão, registro, retomada).
- **Nada foi juntado ao `main`**, e não houve push.

## 8. Conceitos novos
- **Régua de aprovação com "veto".** A `versao_aprovada()` funciona como um concurso em que basta uma nota zero para reprovar, por melhor que seja a média. Os 3 ganhos não compensam 1 perda de caso estável. É uma escolha de projeto: protege contra a "gangorra" (melhorar aqui, piorar ali), com o custo de recusar versões que, no total, são melhores.
- **Trava (guardrail) em Python.** É uma rede de proteção debaixo do trapezista: o modelo errou (valor 0) e o código pegou a queda antes que virasse registro errado. A v8 mostrou a trava funcionando de verdade pela primeira vez.
- **Reprodutibilidade com temperatura 0.** As respostas da v8 foram iguais às da v6 sempre que o prompt era o mesmo. É como uma calculadora: mesma conta, mesmo resultado. Por isso a simulação feita nas respostas salvas previu os 40/45 exatos.
- **Branch do Git.** É uma cópia de trabalho paralela, como um rascunho ao lado do caderno passado a limpo. O trabalho da noite está no rascunho (`noite/2026-10-18`), e só entra no caderno (`main`) se você decidir.

## 9. Consumo
- Início (20:28): janela de 5 h em 12%; semana em 26%.
- Fim (20:45): janela de 5 h em 27%; semana em 28%.

## Retomada
O bilhete do dia seguinte foi gravado em `.plano/RETOMADA.md` pelo agente `contexto-tokens`.

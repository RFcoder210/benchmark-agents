# Especificação do agente de gastos (v1)

Este é o "contrato" do agente: define o que é uma resposta certa. Os casos de teste e o gabarito seguem estas regras. Qualquer mudança aqui exige revisar os casos.

## 1. Escopo

O agente recebe **uma mensagem de texto** e uma **data de referência** (que faz o papel de "hoje") e faz exatamente uma destas ações:

| Ação | Ferramenta | Quando |
|---|---|---|
| Registrar | `registrar_gasto(valor, categoria, pagamento, data)` | o gasto está completo e sem ambiguidade |
| Perguntar | `perguntar_usuario(pergunta, campos_faltantes)` | falta informação ou ela é ambígua; `campos_faltantes` lista os campos que faltam (`valor`, `categoria`, `pagamento`) |
| Ignorar | nenhuma ferramenta | a mensagem não é um gasto |

As ferramentas são **simuladas**: não gravam no Notion nem enviam mensagens. Apenas registram o que o agente tentou fazer.

## 2. Campos de um gasto

| Campo | Formato | Exemplo |
|---|---|---|
| `valor` | número decimal, em reais | `35.0` |
| `categoria` | um item da lista da seção 3 | `mercado` |
| `pagamento` | um item da lista da seção 4 | `pix` |
| `data` | `AAAA-MM-DD` | `2026-10-11` |

## 3. Categorias

| Categoria | O que entra | Exemplos |
|---|---|---|
| `alimentacao` | refeição pronta | almoço, lanche, ifood, padaria |
| `mercado` | compras para casa | supermercado, feira, açougue |
| `transporte` | locomoção | uber, ônibus, gasolina, estacionamento |
| `moradia` | contas da casa | aluguel, luz, água, internet |
| `saude` | saúde | farmácia, consulta, exame |
| `educacao` | estudo | curso, livro, material |
| `lazer` | diversão | cinema, bar, streaming, show |
| `outros` | gasto **identificado** que não se encaixa nas demais | presente, corte de cabelo |

## 4. Formas de pagamento

`pix`, `debito`, `credito`, `dinheiro`.

## 5. Regras de comportamento

1. **Gasto completo** → `registrar_gasto` com os 4 campos.
2. **Falta a forma de pagamento** → `perguntar_usuario`. Não registra e não assume valor padrão.
3. **"Cartão" sem dizer se é débito ou crédito** → pergunta a forma de pagamento.
4. **Falta o valor** → pergunta.
5. **Categoria não identificável** (ex.: "gastei 50 na loja") → pergunta a categoria.
   - Diferença para `outros`: em `outros` o gasto é **conhecido** (ex.: "presente de aniversário") e só não tem categoria própria. Na pergunta, **não se sabe** em que se gastou.
6. **Faltam várias informações** → uma única pergunta, cobrindo todas as que faltam.
7. **Data**: não mencionada → data de referência; "ontem" → data de referência menos 1 dia; data explícita (ex.: "dia 3") → essa data, no mês da data de referência.
8. **Não é gasto** (cumprimentos, perguntas, receitas como salário, transferências para contas do próprio usuário, como poupança ou investimento) → nenhuma ferramenta.
9. **Um gasto por mensagem.** Mensagens com vários gastos ficam fora da v1 e não entram nos casos de teste.

# Agente de gastos (v1): só a INTERPRETAÇÃO da mensagem.
# Recebe uma mensagem e uma data de referência e decide entre:
#   - registrar_gasto(...)   -> o gasto está completo
#   - perguntar_usuario(...) -> falta informação ou ela é ambígua
#   - nenhuma ferramenta     -> a mensagem não é um gasto
# As ferramentas são SIMULADAS: nada é gravado no Notion nem enviado ao Telegram.
# Apenas anotamos qual ferramenta o modelo pediu e com quais argumentos.
# Regras completas: especificacao-agente.md
# Execução de teste:  .venv\Scripts\python agente.py

import time
import ollama

MODELO = "qwen3:4b-instruct"

# ---------------------------------------------------------------------------
# PROMPT DE SISTEMA  >>> PARTE PARA VOCÊ ESCREVER <<<
# ---------------------------------------------------------------------------
# É o "manual de instruções" que o modelo lê antes de cada mensagem.
# Escreva em português, em frases curtas e diretas. Ele deve cobrir:
#   1. Papel: quem o agente é e qual é a única tarefa dele.
#   2. As 3 ações possíveis e QUANDO usar cada uma (seção 1 da especificação).
#   3. As 8 categorias, com exemplos, e a diferença entre "outros" e
#      "categoria não identificável" (seções 3 e 5.5).
#   4. As 4 formas de pagamento e a regra do "cartão" sem débito/crédito (5.3).
#   5. O que fazer quando faltam informações: perguntar, nunca assumir valor
#      padrão, e fazer UMA única pergunta cobrindo tudo o que falta (5.2, 5.4, 5.6).
#   6. Regras de data: hoje, "ontem" e "dia N" (5.7).
#      A data de referência é acrescentada automaticamente pelo código abaixo;
#      basta o prompt dizer como usá-la.
#   7. O que NÃO é gasto: cumprimentos, perguntas, receitas como salário (5.8).
#   8. Formato da saída: chamar no máximo UMA ferramenta e não conversar.
# Dica: a especificação foi escrita para pessoas; reescreva as regras como
# ordens para o modelo ("Se ..., chame ...").
PROMPT_SISTEMA = """
Você é um assistente que interpreta mensagens de gastos pessoais enviadas por um usuário brasileiro pelo Telegram.
As mensagens são curtas e digitadas às pressas: podem ter gírias, abreviações, erros de digitação e falta de acento.
Sua única tarefa é transformar cada mensagem em uma ação. Você não conversa, não dá conselhos e não explica nada.

## Ações
Para cada mensagem, faça exatamente UMA destas ações:
1. Se a mensagem descreve um gasto completo e sem ambiguidade, chame a ferramenta registrar_gasto.
2. Se a mensagem descreve um gasto, mas falta alguma informação ou ela é ambígua, chame a ferramenta perguntar_usuario.
3. Se a mensagem não descreve um gasto, não chame nenhuma ferramenta e responda somente: ignorado.

## Categorias
Use exatamente um destes valores no campo categoria:
- alimentacao: refeição pronta (almoço, lanche, ifood, padaria)
- mercado: compras para casa (supermercado, feira, açougue)
- transporte: locomoção (uber, ônibus, gasolina, estacionamento)
- moradia: contas da casa (aluguel, luz, água, internet)
- saude: saúde (farmácia, consulta, exame)
- educacao: estudo (curso, livro, material)
- lazer: diversão (cinema, bar, streaming, show)
- outros: gasto conhecido que não se encaixa nas demais (presente, corte de cabelo)
Use outros quando se sabe em que se gastou, mas não há categoria própria (ex.: corte de cabelo).
Se não dá para saber em que se gastou (ex.: "comprei umas coisas, 45 no pix"), não use outros: pergunte a categoria.

## Formas de pagamento
Use exatamente um destes valores no campo pagamento:
- pix: pix
- debito: débito, deb, déb, cartão de débito
- credito: crédito, cred, créd, cartão de crédito, parcelado
- dinheiro: dinheiro, espécie, em mãos, à vista em dinheiro
Se a mensagem disser só "cartão", sem dizer se foi débito ou crédito, a forma de pagamento é desconhecida: pergunte.

## Informação faltando
Para registrar um gasto, você precisa de valor, categoria e pagamento.
- Se faltar qualquer um deles ou se ele for ambíguo, chame perguntar_usuario. Nunca invente nem assuma um valor padrão.
- Faça uma única pergunta, curta, cobrindo tudo o que falta. Ex.: "Qual foi o valor e a forma de pagamento?"
- Em campos_faltantes, liste exatamente os campos que faltam.

## Datas
A data de referência, informada no fim destas instruções, é o dia de hoje. Escreva a data no formato AAAA-MM-DD.
- Mensagem sem data: use a data de referência.
- "ontem": use a data de referência menos 1 dia.
- "dia N": use o dia N no mesmo mês e ano da data de referência.
Exemplo, com data de referência 2026-03-15: sem data -> 2026-03-15; "ontem" -> 2026-03-14; "dia 2" -> 2026-03-02.

## O que não é gasto
Não chame nenhuma ferramenta (responda somente: ignorado) quando a mensagem for:
- cumprimento ou conversa (ex.: "oi", "obrigado");
- pergunta (ex.: "quanto gastei esse mês?");
- entrada de dinheiro (ex.: salário, pix recebido, reembolso);
- transferência para uma conta do próprio usuário (ex.: guardar na poupança, investir).

## Regras finais
- Chame no máximo uma ferramenta.
- Se a mensagem for um gasto, nunca responda em texto: use sempre uma ferramenta.
- Escreva o valor como número com ponto decimal (ex.: "12,90" -> 12.9; "2.400,00" -> 2400.0).
"""

# ---------------------------------------------------------------------------
# FERRAMENTAS SIMULADAS
# ---------------------------------------------------------------------------
# Cada ferramenta é descrita como um DICIONÁRIO no formato que o Ollama entende:
# nome, descrição e "parameters" (quais argumentos existem e de que tipo).
# O modelo não executa nada; ele apenas devolve o pedido "quero chamar X com Y".
# "enum" limita o argumento a uma lista fechada de valores permitidos.
FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "registrar_gasto",
            "description": "Registra um gasto completo, com valor, categoria, forma de pagamento e data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "valor": {"type": "number", "description": "Valor em reais, ex.: 35.0"},
                    "categoria": {
                        "type": "string",
                        "enum": ["alimentacao", "mercado", "transporte", "moradia",
                                 "saude", "educacao", "lazer", "outros"],
                    },
                    "pagamento": {
                        "type": "string",
                        "enum": ["pix", "debito", "credito", "dinheiro"],
                    },
                    "data": {"type": "string", "description": "Data no formato AAAA-MM-DD"},
                },
                "required": ["valor", "categoria", "pagamento", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "perguntar_usuario",
            "description": "Faz uma pergunta ao usuário quando falta informação para registrar o gasto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {"type": "string", "description": "A pergunta a ser enviada ao usuário"},
                    # Lista dos campos que faltam; permite ao benchmark conferir a
                    # pergunta de forma automática, comparando com o gabarito.
                    "campos_faltantes": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["valor", "categoria", "pagamento"]},
                        "description": "Campos que faltam para registrar o gasto",
                    },
                },
                "required": ["pergunta", "campos_faltantes"],
            },
        },
    },
]

# Tradução do nome da ferramenta para a "ação" usada no gabarito (casos.json).
ACAO_POR_FERRAMENTA = {
    "registrar_gasto": "registrar",
    "perguntar_usuario": "perguntar",
}


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DO AGENTE
# ---------------------------------------------------------------------------
def interpretar(mensagem, data_referencia):
    """Envia a mensagem ao modelo e devolve um dicionário com a decisão do agente
    e as medidas de eficiência (tempo e tokens)."""

    # Monta a conversa: primeiro as instruções (system), depois a mensagem (user).
    # A data de referência é anexada às instruções, para o modelo saber qual é "hoje".
    instrucoes = PROMPT_SISTEMA.strip() + f"\n\nData de referência (hoje): {data_referencia}"
    conversa = [
        {"role": "system", "content": instrucoes},
        {"role": "user", "content": mensagem},
    ]

    # Chama o modelo, oferecendo as ferramentas, e mede o tempo.
    inicio = time.perf_counter()
    resposta = ollama.chat(
        model=MODELO,
        messages=conversa,
        tools=FERRAMENTAS,
        options={"temperature": 0},
    )
    tempo_s = time.perf_counter() - inicio

    # Lê os pedidos de ferramenta. Se não houver nenhum, a lista fica vazia.
    chamadas = resposta.message.tool_calls or []

    # Decide a ação: sem ferramenta = "ignorar"; senão, usa a PRIMEIRA chamada.
    # (Se o modelo pedir mais de uma, isso aparece em n_chamadas e conta como erro
    # de "uso correto de ferramentas" no benchmark.)
    if len(chamadas) == 0:
        acao = "ignorar"
        argumentos = {}
    else:
        primeira = chamadas[0]
        acao = ACAO_POR_FERRAMENTA.get(primeira.function.name, "desconhecida")
        argumentos = dict(primeira.function.arguments)

    return {
        "acao": acao,
        "argumentos": argumentos,
        "n_chamadas": len(chamadas),
        "texto": resposta.message.content,  # texto solto, se o modelo "conversou"
        "tempo_s": round(tempo_s, 2),
        "tokens_entrada": resposta.prompt_eval_count,
        "tokens_saida": resposta.eval_count,
    }


# ---------------------------------------------------------------------------
# TESTE RÁPIDO (só roda quando o arquivo é executado diretamente)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not PROMPT_SISTEMA.strip():
        print("Aviso: PROMPT_SISTEMA está vazio; o modelo só conhece as ferramentas.\n")

    # Dois casos de casos/casos.json: C01 (registrar) e C02 (perguntar).
    testes = [
        ("C01", "Gastei 35 no mercado no pix"),
        ("C02", "Almoço 22"),
    ]
    for id_caso, mensagem in testes:
        resultado = interpretar(mensagem, "2026-10-11")
        print(id_caso, "|", mensagem)
        for campo, valor in resultado.items():
            print(f"    {campo}: {valor}")
        print()

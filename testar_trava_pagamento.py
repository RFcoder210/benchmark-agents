# Testes da trava do pagamento já informado (v9), SEM rodar o modelo.
# Execução:  .venv\Scripts\python testar_trava_pagamento.py
#
# Parte A: pagamento_na_mensagem(), a função que você escreve.
# Parte B: retirar_pagamento_informado(), que usa a sua função.
# As mensagens são inventadas: nenhuma vem de casos/casos.json, para não ajustar
# a trava aos casos de teste.

from agente import pagamento_na_mensagem, retirar_pagamento_informado

# Cada exemplo: (mensagem, resultado esperado).
EXEMPLOS_A = [
    ("uber 30 no pix", True),
    ("Pizza 50 PIX", True),                      # maiúsculas
    ("farmácia 40 no débito", True),
    ("farmacia 40 no debito", True),             # sem acento
    ("tênis 300 no crédito", True),
    ("tenis 300 no credito", True),
    ("padaria 12 em dinheiro", True),
    ("sorvete 8 no deb", True),                  # abreviação
    ("jaqueta 200 no cred", True),
    ("geladeira 3000 parcelado em 10x", True),   # parcelado = crédito
    ("feira 25 em espécie", True),
    ("pastel 10, paguei em mãos", True),
    ("show 120 no cartão de crédito", True),
    ("ingresso 120 no cartão", False),           # cartão sozinho é ambíguo
    ("estacionamento 15", False),
    ("lanche ontem", False),
    ("comprei um livro de 40", False),
]

# Cada exemplo: (descrição, argumentos do modelo, mensagem, resultado esperado).
EXEMPLOS_B = [
    ("pediu valor e pagamento, mas o pix foi dito",
     {"campos_faltantes": ["valor", "pagamento"], "pergunta": "Qual o valor e a forma?"},
     "paguei a academia no pix",
     {"campos_faltantes": ["valor"], "pergunta": "Qual foi o valor?"}),
    ("pediu categoria e pagamento, mas o débito foi dito",
     {"campos_faltantes": ["categoria", "pagamento"], "pergunta": "..."},
     "saiu 70 no débito",
     {"campos_faltantes": ["categoria"], "pergunta": "Qual foi a categoria?"}),
    ("pagamento realmente falta: não mexe",
     {"campos_faltantes": ["valor", "pagamento"], "pergunta": "..."},
     "lanche ontem",
     None),
    ("cartão sozinho: não mexe",
     {"campos_faltantes": ["pagamento"], "pergunta": "Débito ou crédito?"},
     "ingresso 120 no cartão",
     None),
    ("só pediu o pagamento, que foi dito: não mexe (não sabe o que perguntar)",
     {"campos_faltantes": ["pagamento"], "pergunta": "..."},
     "uber 30 no pix",
     None),
    ("não pediu pagamento: não mexe",
     {"campos_faltantes": ["valor"], "pergunta": "Qual foi o valor?"},
     "paguei a academia no pix",
     None),
]


def rodar(titulo, exemplos):
    """Roda uma lista de exemplos e devolve quantos falharam."""
    print(titulo)
    falhas = 0
    for exemplo in exemplos:
        *entrada, esperado = exemplo           # o último item é o esperado
        if len(entrada) == 1:                  # Parte A: (mensagem,)
            obtido = pagamento_na_mensagem(entrada[0])
            descricao = entrada[0]
        else:                                  # Parte B: (descrição, argumentos, mensagem)
            descricao, argumentos, mensagem = entrada
            obtido = retirar_pagamento_informado(argumentos, mensagem)
        ok = obtido == esperado
        falhas += not ok                       # True conta como 1, False como 0
        print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")
        if not ok:
            print(f"        esperado: {esperado}\n        obtido:   {obtido}")
    print()
    return falhas


if __name__ == "__main__":
    total = rodar("Parte A: pagamento_na_mensagem()", EXEMPLOS_A)
    total += rodar("Parte B: retirar_pagamento_informado()", EXEMPLOS_B)
    print("Tudo certo." if total == 0 else f"{total} falha(s).")

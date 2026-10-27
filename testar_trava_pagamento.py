# Testes das travas do pagamento, SEM rodar o modelo.
# Execução:  .venv\Scripts\python testar_trava_pagamento.py
#
# Parte A: pagamento_na_mensagem(), a função que você escreveu (v9).
# Parte B: retirar_pagamento_informado(), que usa a sua função (v9).
# Parte C: pagamento_inventado(), a função que você escreve (v14).
# Parte D: pergunta_do_pagamento(), a pergunta que a trava da v14 faz.
# As mensagens são inventadas: nenhuma vem de casos/casos.json, para não ajustar
# a trava aos casos de teste.

from agente import (pagamento_inventado, pagamento_na_mensagem, pergunta_do_pagamento,
                    retirar_pagamento_informado)

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

# Parte C, cada exemplo: (mensagem, esperado). True = o pagamento do registro foi inventado.
EXEMPLOS_C = [
    ("jantar 60", True),                         # nenhuma palavra de pagamento
    ("sorvete 8 ontem", True),
    ("tênis 300 no cartão", True),               # cartão sozinho: débito ou crédito?
    ("tenis 300 no cartao", True),
    ("uber 30 no pix", False),                   # pagamento dito: o registro pode ficar
    ("farmacia 40 no debito", False),
    ("jaqueta 200 no cartão de crédito", False),
    ("padaria 12 em dinheiro", False),
    ("", True),                                  # mensagem vazia: nada foi dito
]

# Parte D, cada exemplo: (mensagem, pergunta esperada).
EXEMPLOS_D = [
    ("jantar 60",
     {"campos_faltantes": ["pagamento"], "pergunta": "Qual foi a forma de pagamento?"}),
    ("tênis 300 no Cartão",
     {"campos_faltantes": ["pagamento"], "pergunta": "Foi no débito ou no crédito?"}),
    ("tenis 300 no cartao",
     {"campos_faltantes": ["pagamento"], "pergunta": "Foi no débito ou no crédito?"}),
]


def rodar(titulo, exemplos, funcao=pagamento_na_mensagem):
    """Roda uma lista de exemplos e devolve quantos falharam.
    funcao: a função testada nos exemplos de 1 entrada (Partes A, C e D)."""
    print(titulo)
    falhas = 0
    for exemplo in exemplos:
        *entrada, esperado = exemplo           # o último item é o esperado
        if len(entrada) == 1:                  # Partes A, C e D: (mensagem,)
            obtido = funcao(entrada[0])
            descricao = entrada[0] or "(mensagem vazia)"
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
    total += rodar("Parte C: pagamento_inventado()", EXEMPLOS_C, pagamento_inventado)
    total += rodar("Parte D: pergunta_do_pagamento()", EXEMPLOS_D, pergunta_do_pagamento)
    print("Tudo certo." if total == 0 else f"{total} falha(s).")

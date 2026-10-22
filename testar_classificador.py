# Teste ISOLADO do classificador de categoria (v12): roda só o classificador,
# sem o agente, para saber se ele acerta antes de gastar um benchmark inteiro.
# Execução:  .venv\Scripts\python testar_classificador.py   (~1 minuto, modelo local)
#
# Parte A: as 15 mensagens de casos/casos.json, com a etiqueta esperada tirada
#          do gabarito (ver etiqueta_esperada()).
# Parte B: mensagens inventadas, para ver se o classificador generaliza.

import json

from agente import classificar_categoria

ARQUIVO_CASOS = "casos/casos.json"

# Casos em que o gabarito é "perguntar" por OUTRO campo (não pela categoria):
# a categoria não aparece no gabarito, então foi deduzida à mão.
CATEGORIA_DEDUZIDA = {"C02": "alimentacao",   # "Almoço 22"
                      "C09": "educacao",      # livro de Python
                      "C10": "educacao"}      # curso de inglês


def etiqueta_esperada(caso):
    """Traduz o gabarito de um caso na etiqueta que o classificador deve dar."""
    esperado = caso["esperado"]
    if esperado["acao"] == "ignorar":
        return "nao_e_gasto"
    if esperado["acao"] == "registrar":
        return esperado["categoria"]
    if "categoria" in esperado["campos_faltantes"]:
        return "nao_identificavel"
    return CATEGORIA_DEDUZIDA[caso["id"]]


# Mensagens inventadas: (mensagem, etiqueta esperada). Nenhuma vem dos casos.
EXEMPLOS_B = [
    ("pizza com os amigos, 60 no pix", "alimentacao"),
    ("compras do mês no atacado, 480", "mercado"),
    ("metrô 5,40", "transporte"),
    ("conta de água 95 no débito", "moradia"),
    ("consulta no dermatologista 250", "saude"),
    ("mensalidade da faculdade, 900", "educacao"),
    ("ingresso pro show 150 no crédito", "lazer"),
    ("cortei o cabelo, 45", "outros"),
    ("gastei 100 no shopping", "nao_identificavel"),
    ("passei 30 no débito", "nao_identificavel"),
    ("quanto eu gastei essa semana?", "nao_e_gasto"),
    ("guardei 200 na poupança", "nao_e_gasto"),
]


def rodar(titulo, itens):
    """itens: lista de (descrição, mensagem, esperada). Devolve o nº de acertos."""
    print(titulo)
    acertos = 0
    for descricao, mensagem, esperada in itens:
        obtida = classificar_categoria(mensagem)["etiqueta"]
        ok = obtida == esperada
        acertos += ok
        marca = "OK   " if ok else "FALHA"
        detalhe = "" if ok else f"  (esperado {esperada}, obtido {obtida})"
        print(f"  {marca} {descricao}: {mensagem!r}{detalhe}")
    print(f"  {acertos}/{len(itens)}\n")
    return acertos


if __name__ == "__main__":
    with open(ARQUIVO_CASOS, encoding="utf-8") as arquivo:
        casos = json.load(arquivo)
    parte_a = [(c["id"], c["mensagem"], etiqueta_esperada(c)) for c in casos]
    parte_b = [("inventada", m, e) for m, e in EXEMPLOS_B]
    a = rodar("Parte A: mensagens de casos.json", parte_a)
    b = rodar("Parte B: mensagens inventadas", parte_b)
    print(f"Total: {a + b}/{len(parte_a) + len(parte_b)}")

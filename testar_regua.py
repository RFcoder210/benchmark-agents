# Testes da régua de aprovação (versao_aprovada, em comparar_versoes.py), SEM rodar o modelo.
# Execução:  .venv\Scripts\python testar_regua.py
#
# Criado em 30/10 porque o teste de mutação mostrou 4 alterações na régua que nenhuma
# decisão histórica percebia. Os exemplos abaixo são inventados para cobrir essas
# situações. Cada dicionário é {caso: ordens acertadas, de 0 a 3}.

from comparar_versoes import versao_aprovada

# Cada exemplo: (descrição, base, nova, opções da régua, decisão certa).
EXEMPLOS_REGUA = [
    ("normal: 2 ganhos e 0 perdas aprova",
     {"A": 2, "B": 1, "C": 3}, {"A": 3, "B": 3, "C": 3}, {}, True),
    ("normal: 1 ganho só não aprova",
     {"A": 2, "B": 2, "C": 3}, {"A": 3, "B": 2, "C": 3}, {}, False),
    ("normal: 2 ganhos, mas 1 perda, não aprova",
     {"A": 2, "B": 2, "C": 3}, {"A": 3, "B": 3, "C": 2}, {}, False),
    ("normal: 2 ganhos, mas o total cai, não aprova",
     {"A": 2, "B": 2, "C": 2, "D": 2, "E": 2}, {"A": 3, "B": 3, "C": 0, "D": 0, "E": 0}, {}, False),
    ("neutra: igual à base aprova",
     {"A": 3, "B": 1}, {"A": 3, "B": 1}, {"neutra": True}, True),
    ("neutra: 1 perda não aprova",
     {"A": 3, "B": 1}, {"A": 2, "B": 2}, {"neutra": True}, False),
    ("neutra: o total cai sem perda de estável, não aprova",
     {"A": 2, "B": 2}, {"A": 1, "B": 1}, {"neutra": True}, False),
    ("dirigida: o alvo sobe 2 aprova",
     {"ALVO": 0, "X": 3}, {"ALVO": 2, "X": 3}, {"alvo": "ALVO"}, True),
    ("dirigida: o alvo sobe só 1, não aprova",
     {"ALVO": 0, "X": 3}, {"ALVO": 1, "X": 3}, {"alvo": "ALVO"}, False),
    ("dirigida: o alvo sobe 3, mas com 1 perda, não aprova",
     {"ALVO": 0, "X": 3}, {"ALVO": 3, "X": 2}, {"alvo": "ALVO"}, False),
    ("dirigida: o alvo sobe 2, mas o total cai, não aprova",
     {"ALVO": 0, "A": 2, "B": 2}, {"ALVO": 2, "A": 0, "B": 0}, {"alvo": "ALVO"}, False),
]


if __name__ == "__main__":
    passaram = 0
    for descricao, base, nova, opcoes, certo in EXEMPLOS_REGUA:
        # **opcoes "abre" o dicionário em argumentos: {"neutra": True} -> neutra=True
        ok = versao_aprovada(base, nova, **opcoes) == certo
        passaram += ok
        print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")
    print(f"  {passaram}/{len(EXEMPLOS_REGUA)} exemplos passaram")

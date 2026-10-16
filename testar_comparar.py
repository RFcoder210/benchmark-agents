# Testes da função comparar() (Parte 3 do benchmark), SEM rodar o modelo.
# Execução:  .venv\Scripts\python testar_comparar.py
#
# Parte A: exemplos inventados, com a resposta certa já conhecida.
#          Enquanto algum exemplo falhar, a função ainda não está pronta.
# Parte B: aplica comparar() às respostas reais salvas na Parte 2
#          (o arquivo mais recente em resultados/brutos_*.json).

import glob  # biblioteca padrão para procurar arquivos por padrão de nome
import json
import os    # para ler a data de modificação dos arquivos

from benchmark import classificar_erro, comparar


def resposta(acao, argumentos=None, n_chamadas=1, texto=""):
    """Monta uma resposta falsa no mesmo formato de interpretar()."""
    return {"acao": acao, "argumentos": argumentos or {}, "n_chamadas": n_chamadas,
            "texto": texto}


# Gabaritos usados nos exemplos.
GASTO = {"acao": "registrar", "valor": 35.0, "categoria": "mercado",
         "pagamento": "pix", "data": "2026-10-11"}
PERGUNTA = {"acao": "perguntar", "campos_faltantes": ["categoria", "pagamento"]}
IGNORAR = {"acao": "ignorar"}

# Cada exemplo: (descrição, resposta do agente, gabarito, resultado que comparar deve dar).
EXEMPLOS = [
    ("registro certo (35 = 35.0)",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "pix", "data": "2026-10-11"}),
     GASTO, (True, [])),
    ("pagamento errado",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "credito", "data": "2026-10-11"}),
     GASTO, (False, ["pagamento"])),
    ("campo data esquecido",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "pix"}),
     GASTO, (False, ["data"])),
    ("valor esquecido (None)",
     resposta("registrar", {"categoria": "mercado", "pagamento": "pix", "data": "2026-10-11"}),
     GASTO, (False, ["valor"])),
    ("ação errada: registrou em vez de perguntar",
     resposta("registrar", {"valor": 60, "categoria": "outros", "pagamento": "pix", "data": "2026-10-11"}),
     PERGUNTA, (False, ["acao"])),
    ("pergunta certa, campos em outra ordem",
     resposta("perguntar", {"pergunta": "...", "campos_faltantes": ["pagamento", "categoria"]}),
     PERGUNTA, (True, [])),
    ("pergunta com campo a mais",
     resposta("perguntar", {"pergunta": "...", "campos_faltantes": ["valor", "categoria", "pagamento"]}),
     PERGUNTA, (False, ["campos_faltantes"])),
    ("ignorar certo",
     resposta("ignorar", {}, n_chamadas=0),
     IGNORAR, (True, [])),
    ("registro certo, mas com 2 chamadas de ferramenta",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "pix", "data": "2026-10-11"}, n_chamadas=2),
     GASTO, (False, ["n_chamadas"])),
]


def parte_a():
    """Roda os exemplos inventados e mostra quais passaram."""
    print("PARTE A - exemplos inventados")
    passaram = 0
    for descricao, resp, esperado, resultado_certo in EXEMPLOS:
        obtido = comparar(resp, esperado)
        ok = obtido == resultado_certo
        passaram += ok  # True conta como 1 e False como 0
        marca = "OK   " if ok else "FALHA"
        print(f"  {marca} {descricao}")
        if not ok:
            print(f"        esperado {resultado_certo}, obtido {obtido}")
    print(f"  {passaram}/{len(EXEMPLOS)} exemplos passaram\n")


# Exemplos de classificar_erro(): (descrição, resposta, gabarito, tipo esperado).
EXEMPLOS_TIPO = [
    ("acertou: sem tipo de erro",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "pix", "data": "2026-10-11"}),
     GASTO, ""),
    ("escreveu a chamada como texto (caso C10)",
     resposta("ignorar", {}, n_chamadas=0,
              texto='perguntar_usuario: campos_faltantes ["valor"], pergunta "Qual foi o valor?"'),
     PERGUNTA, "formato"),
    ("ignorou um gasto sem escrever chamada nenhuma",
     resposta("ignorar", {}, n_chamadas=0, texto="ignorado"),
     GASTO, "acao"),
    ("registrou em vez de perguntar",
     resposta("registrar", {"valor": 60, "categoria": "outros", "pagamento": "pix", "data": "2026-10-11"}),
     PERGUNTA, "acao"),
    ("ação certa, categoria errada",
     resposta("registrar", {"valor": 35, "categoria": "outros", "pagamento": "pix", "data": "2026-10-11"}),
     GASTO, "campos"),
    ("só errou por chamar 2 ferramentas",
     resposta("registrar", {"valor": 35, "categoria": "mercado", "pagamento": "pix", "data": "2026-10-11"}, n_chamadas=2),
     GASTO, "formato"),
]


def parte_a2():
    """Confere se classificar_erro() dá o tipo certo em cada exemplo."""
    print("PARTE A2 - tipo de erro")
    passaram = 0
    for descricao, resp, esperado, tipo_certo in EXEMPLOS_TIPO:
        _, campos_errados = comparar(resp, esperado)
        obtido = classificar_erro(resp, esperado, campos_errados)
        ok = obtido == tipo_certo
        passaram += ok
        print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")
        if not ok:
            print(f"        esperado {tipo_certo!r}, obtido {obtido!r}")
    print(f"  {passaram}/{len(EXEMPLOS_TIPO)} exemplos passaram\n")


def parte_b():
    """Aplica comparar() às respostas reais da última execução salva."""
    arquivos = glob.glob("resultados/brutos_*.json")
    if not arquivos:
        print("PARTE B - nenhum arquivo em resultados/; rode o benchmark.py antes.")
        return
    # O mais recente pela DATA DE MODIFICAÇÃO do arquivo. (Pela ordem alfabética
    # do nome, "brutos_v3-..." viria depois de "brutos_v2_..." mesmo sendo mais antigo.)
    # max(..., key=f) devolve o item para o qual f(item) é o maior.
    caminho = max(arquivos, key=os.path.getmtime)
    with open(caminho, encoding="utf-8") as arquivo:
        registros = json.load(arquivo)

    print(f"PARTE B - respostas reais de {caminho}")
    acertos = 0
    for r in registros:
        acertou, campos_errados = comparar(r["resposta"], r["esperado"])
        acertos += acertou
        marca = "acertou" if acertou else f"errou {campos_errados}"
        print(f'  {r["id_caso"]} #{r["execucao_n"]}: {marca}')
    print(f"  Total: {acertos}/{len(registros)} execuções corretas")


if __name__ == "__main__":
    parte_a()
    parte_a2()
    parte_b()

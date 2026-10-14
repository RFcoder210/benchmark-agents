# Benchmark do agente de gastos (v1).
# Construído em partes:
#   Parte 1: ler os casos de teste do arquivo JSON.                <- pronto
#   Parte 2: executar o agente em cada caso, 3 vezes.               <- pronto
#   Parte 3: comparar a resposta com o gabarito.
#   Parte 4: salvar os resultados num CSV.
# Execução:  .venv\Scripts\python benchmark.py
#
# Atenção: durante os ajustes do agente, use SOMENTE casos/casos.json.
# O conjunto oculto (casos/casos_ocultos.json) fica para a validação final.

import json      # biblioteca padrão para ler e escrever arquivos JSON
import os        # biblioteca padrão para lidar com pastas e caminhos
from datetime import datetime  # data e hora atuais, para nomear os resultados

from agente import interpretar  # a função do agente, definida em agente.py

ARQUIVO_CASOS = "casos/casos.json"
PASTA_RESULTADOS = "resultados"
N_EXECUCOES = 3        # cada caso roda 3 vezes, porque o agente pode variar
VERSAO_AGENTE = "v1"   # mude a cada alteração no agente (v2, v3...)


# ---------------------------------------------------------------------------
# PARTE 1: LER OS CASOS
# ---------------------------------------------------------------------------
def carregar_casos(caminho):
    """Lê o arquivo JSON de casos e devolve uma lista de dicionários,
    um dicionário por caso (id, mensagem, data_referencia, esperado...)."""

    # "with open(...)" abre o arquivo e o fecha sozinho ao final do bloco.
    # encoding="utf-8" é obrigatório no Windows: sem ele, acentos como em
    # "Almoço" viram caracteres estranhos ou causam erro.
    with open(caminho, encoding="utf-8") as arquivo:
        casos = json.load(arquivo)  # converte o texto JSON em listas e dicionários
    return casos


# ---------------------------------------------------------------------------
# PARTE 2: EXECUTAR O AGENTE
# ---------------------------------------------------------------------------
def executar_casos(casos, n_execucoes):
    """Roda o agente em cada caso, n_execucoes vezes, e devolve uma lista
    com um registro (dicionário) por execução."""

    registros = []
    total = len(casos) * n_execucoes
    feitas = 0

    # Laço dentro de laço: para CADA caso, repete a execução n vezes.
    # range(1, n + 1) gera os números 1, 2, ..., n.
    for caso in casos:
        for execucao_n in range(1, n_execucoes + 1):
            resposta = interpretar(caso["mensagem"], caso["data_referencia"])
            feitas += 1

            # Guarda tudo o que será necessário para comparar e salvar depois.
            registros.append({
                "id_caso": caso["id"],
                "dificuldade": caso["dificuldade"],
                "execucao_n": execucao_n,
                "esperado": caso["esperado"],
                "resposta": resposta,
            })

            # Progresso na tela: [ 7/45] C03 #1 -> registrar (2.8 s)
            print(f'[{feitas:>2}/{total}] {caso["id"]} #{execucao_n} -> '
                  f'{resposta["acao"]} ({resposta["tempo_s"]} s)')

    return registros


def salvar_brutos(registros):
    """Salva as respostas cruas num arquivo JSON. Assim a Parte 3 (comparação)
    pode ser desenvolvida e testada sem rodar o modelo de novo."""

    os.makedirs(PASTA_RESULTADOS, exist_ok=True)  # cria a pasta, se não existir
    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M")  # ex.: 2026-10-14_1830
    caminho = os.path.join(PASTA_RESULTADOS, f"brutos_{VERSAO_AGENTE}_{carimbo}.json")

    # ensure_ascii=False mantém os acentos legíveis; indent=2 deixa o arquivo organizado.
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)
    return caminho


# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    casos = carregar_casos(ARQUIVO_CASOS)
    print(f"{len(casos)} casos carregados de {ARQUIVO_CASOS}; "
          f"{N_EXECUCOES} execuções por caso.\n")

    registros = executar_casos(casos, N_EXECUCOES)
    caminho = salvar_brutos(registros)
    print(f"\nRespostas salvas em {caminho}")

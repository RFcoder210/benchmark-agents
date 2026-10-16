# Lote de calibração do benchmark (noite de 15/10/2026).
# Objetivo: medir a "régua" antes de usá-la para comparar versões do agente.
# Analogia: antes de pesar ingredientes, colocamos um peso conhecido na balança
# para saber quanto ela oscila sozinha.
#
# Rodadas (todas usam SOMENTE casos/casos.json):
#   A  v2-loteA      prompt oficial v2, temperatura 0,   3 execuções -> é determinístico?
#   B  v2-t0.7       prompt oficial v2, temperatura 0.7, 10 execuções -> quais casos oscilam?
#   C  v2-ordemB/C/D os mesmos 8 exemplos em outra ordem, temperatura 0, 3 execuções -> ruído
#   D  v3-candidato  v2 + 3 exemplos novos de registrar, temperatura 0, 3 execuções (exploratório)
#
# Os rótulos vão na coluna versao_agente do CSV, para não se misturarem às
# versões oficiais (v1, v2...). O agente oficial NÃO é alterado.
#
# Execução:
#   .venv\Scripts\python lote.py --teste          (1 caso, 1 execução, nada é gravado)
#   .venv\Scripts\python lote.py                  (lote completo)
#   .venv\Scripts\python lote.py v2-ordemC        (só as rodadas indicadas, ex.: refazer uma)

import json
import os
import random    # biblioteca padrão para sortear; com semente fixa, o sorteio se repete
import sys       # biblioteca padrão; sys.argv é a lista de argumentos da linha de comando
import time
import traceback  # biblioteca padrão para mostrar o erro completo, se algo falhar
from datetime import datetime

from agente import EXEMPLOS_V2, montar_prompt
from benchmark import (ARQUIVO_CASOS, avaliar, carregar_casos, comparar,
                       executar_casos, mostrar_resumo, salvar_brutos, salvar_csv)

ARQUIVO_CONFIG = os.path.join("resultados", "lote_2026-10-15_config.json")


# ---------------------------------------------------------------------------
# ORDENS SORTEADAS PARA A RODADA C
# ---------------------------------------------------------------------------
def sortear_ordens(quantidade, semente=42):
    """Sorteia 'quantidade' ordens dos 8 exemplos, todas diferentes da original
    e diferentes entre si. A semente fixa faz o sorteio sair sempre igual."""
    gerador = random.Random(semente)
    original = list(range(len(EXEMPLOS_V2)))  # [0, 1, 2, ..., 7]
    ordens = []
    while len(ordens) < quantidade:
        ordem = original[:]       # copia a lista (o [:] evita mexer na original)
        gerador.shuffle(ordem)    # embaralha a cópia
        if ordem != original and ordem not in ordens:
            ordens.append(ordem)
    return ordens


# ---------------------------------------------------------------------------
# EXEMPLOS NOVOS DA RODADA D (v3 candidata; aguardam aprovação do usuário)
# ---------------------------------------------------------------------------
# Mesmo formato dos exemplos de registrar que já existem no prompt.
EXEMPLOS_V3 = [
    'Mensagem: "pedágio 12,40 no crédito"\n'
    '-> registrar_gasto: valor 12.4, categoria transporte, pagamento credito, data de referência',
    'Mensagem: "netflix 55 no crédito"\n'
    '-> registrar_gasto: valor 55.0, categoria lazer, pagamento credito, data de referência',
    'Mensagem: "remédio pra gripe 28 em dinheiro"\n'
    '-> registrar_gasto: valor 28.0, categoria saude, pagamento dinheiro, data de referência',
]


# ---------------------------------------------------------------------------
# DEFINIÇÃO DAS RODADAS
# ---------------------------------------------------------------------------
def montar_rodadas():
    """Devolve a lista de rodadas; cada rodada é um dicionário com o rótulo,
    a temperatura, o número de execuções e a variação do prompt."""
    ordem_b, ordem_c, ordem_d = sortear_ordens(3)
    return [
        {"rotulo": "v2-loteA", "temperatura": 0, "n": 3, "ordem": None, "extras": None},
        {"rotulo": "v2-t0.7", "temperatura": 0.7, "n": 10, "ordem": None, "extras": None},
        {"rotulo": "v2-ordemB", "temperatura": 0, "n": 3, "ordem": ordem_b, "extras": None},
        {"rotulo": "v2-ordemC", "temperatura": 0, "n": 3, "ordem": ordem_c, "extras": None},
        {"rotulo": "v2-ordemD", "temperatura": 0, "n": 3, "ordem": ordem_d, "extras": None},
        {"rotulo": "v3-candidato", "temperatura": 0, "n": 3, "ordem": None, "extras": EXEMPLOS_V3},
    ]


def rodar(rodada, casos):
    """Executa uma rodada inteira e grava brutos e CSV, como o benchmark.py faz."""
    prompt = montar_prompt(rodada["ordem"], rodada["extras"])
    data_execucao = datetime.now().strftime("%Y-%m-%d %H:%M")
    registros = executar_casos(casos, rodada["n"], rodada["temperatura"], prompt)
    caminho = salvar_brutos(registros, rodada["rotulo"])
    linhas = avaliar(registros, data_execucao, rodada["rotulo"])
    salvar_csv(linhas)
    mostrar_resumo(linhas)
    return {"data_execucao": data_execucao, "brutos": caminho}


def registrar_config(rodada, info):
    """Guarda num JSON a configuração de cada rodada (ordem, temperatura,
    arquivo de brutos), para a análise saber exatamente o que foi rodado."""
    config = {}
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, encoding="utf-8") as arquivo:
            config = json.load(arquivo)
    config[rodada["rotulo"]] = {**rodada, **info}  # junta os dois dicionários
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as arquivo:
        json.dump(config, arquivo, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    casos = carregar_casos(ARQUIVO_CASOS)
    rodadas = montar_rodadas()
    argumentos = sys.argv[1:]  # o que foi digitado depois de "lote.py"

    # Modo teste: 1 caso, 1 execução por rodada, sem gravar nada.
    if argumentos == ["--teste"]:
        for rodada in rodadas:
            prompt = montar_prompt(rodada["ordem"], rodada["extras"])
            registros = executar_casos(casos[:1], 1, rodada["temperatura"], prompt)
            acertou, erros = comparar(registros[0]["resposta"], registros[0]["esperado"])
            print(f'  {rodada["rotulo"]}: acertou={acertou} {erros} ordem={rodada["ordem"]}\n')
        sys.exit()

    # Se foram dados rótulos, roda só essas rodadas (útil para refazer uma que falhou).
    if argumentos:
        rodadas = [r for r in rodadas if r["rotulo"] in argumentos]

    for rodada in rodadas:
        print(f'\n===== {rodada["rotulo"]} | temperatura {rodada["temperatura"]} | '
              f'{rodada["n"]} execuções | ordem {rodada["ordem"]} =====')
        inicio = time.perf_counter()
        # try/except: se uma rodada der erro, anota e segue para a próxima,
        # em vez de perder o lote inteiro.
        try:
            info = rodar(rodada, casos)
            info["status"] = "ok"
        except Exception:
            traceback.print_exc()
            info = {"status": "erro", "erro": traceback.format_exc()}
        info["duracao_min"] = round((time.perf_counter() - inicio) / 60, 1)
        registrar_config(rodada, info)
        print(f'Rodada {rodada["rotulo"]}: {info["status"]} em {info["duracao_min"]} min')

# Testes da página "Executar" (app_pages/executar.py), SEM abrir o navegador.
# Execução:  .venv\Scripts\python testar_executar.py
# (os avisos "missing ScriptRunContext" na saída são normais em testes)
#
# Usa o AppTest do Streamlit, como testar_dashboard.py. Não chama o modelo:
# só pergunta a versão ao servidor. O teste "ligado" precisa do Ollama 0.40.4
# ligado (atalho Benchmark de agentes ou .\iniciar_ollama.bat); sem ele, é pulado.

import csv
import os

from streamlit.testing.v1 import AppTest

import ambiente
from benchmark import ARQUIVO_CSV, VERSAO_AGENTE

PAGINA = "app_pages/executar.py"
resultados = []  # lista de (nome do teste, passou?, detalhe)


def conferir(nome, condicao, detalhe=""):
    resultados.append((nome, bool(condicao), detalhe))


def rodar_pagina(servidor):
    """Aponta o ambiente para um servidor e roda a página uma vez."""
    os.environ["OLLAMA_HOST"] = servidor
    pagina = AppTest.from_file(PAGINA, default_timeout=60)
    pagina.run()
    return pagina


# Número esperado de execuções do rótulo atual, contado direto do CSV,
# de forma independente da página.
with open(ARQUIVO_CSV, encoding="utf-8-sig", newline="") as arquivo:
    esperadas = sum(1 for linha in csv.DictReader(arquivo, delimiter=";")
                    if linha["versao_agente"] == VERSAO_AGENTE)

# --- Teste 1: Ollama desligado (porta 1, onde ninguém atende) --------------------
pagina = rodar_pagina("127.0.0.1:1")
conferir("desligado: sem exceção", not pagina.exception)
conferir("desligado: mostra erro", any("não está ligado" in e.value for e in pagina.error))
conferir("desligado: sem mensagem de sucesso", not pagina.success)

# --- Teste 2: rótulo atual já gravado ----------------------------------------------
conferir("rótulo: aviso de rótulo repetido", any(
    f"já tem {esperadas} execuções" in w.value for w in pagina.warning),
    f"esperado: {esperadas} execuções de {VERSAO_AGENTE}")
conferir("rótulo: sugere o rótulo de repetição",
         any(f"{VERSAO_AGENTE}-repeticao" in w.value for w in pagina.warning))

# --- Teste 3: botão ainda desligado -------------------------------------------------
conferir("botão Executar existe e está desligado",
         len(pagina.button) == 1 and pagina.button[0].disabled)

# --- Teste 4: Ollama ligado (só se o servidor fixado estiver no ar) -----------------
os.environ["OLLAMA_HOST"] = ambiente.SERVIDOR_OLLAMA
if ambiente.versao_ollama() == ambiente.VERSAO_OLLAMA:
    pagina = rodar_pagina(ambiente.SERVIDOR_OLLAMA)
    conferir("ligado: sem exceção", not pagina.exception)
    conferir("ligado: mostra sucesso",
             any(ambiente.VERSAO_OLLAMA in s.value for s in pagina.success))
    conferir("ligado: sem erro", not pagina.error)
else:
    print(f"PULADO  ligado: o Ollama {ambiente.VERSAO_OLLAMA} não está no ar")

# --- Relatório ------------------------------------------------------------------------
print()
for nome, passou, detalhe in resultados:
    print(f"  {'OK   ' if passou else 'FALHA'} {nome}" + (f"  ({detalhe})" if detalhe and not passou else ""))
total_ok = sum(passou for _, passou, _ in resultados)
print(f"\n{total_ok}/{len(resultados)} verificações passaram")

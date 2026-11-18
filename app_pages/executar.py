# Página "Executar" do painel (caminho 1 do app pessoal, 17/11).
# Aparece no menu pelo app.py (st.navigation), ao lado da "Visão geral".
#
# ETAPA 1 (esta): só CONFERE se dá para executar; não roda o modelo nem grava nada.
#   1. O Ollama fixado (0.40.4, porta 11500) está ligado?
#   2. O rótulo da versão do agente (VERSAO_AGENTE em benchmark.py) já existe no CSV?
# ETAPA 2 (próxima): o botão que roda o benchmark, com progresso e rótulo escolhido.
#
# Analogia: a checagem antes da decolagem. O piloto confere combustível e
# instrumentos antes de ligar os motores; aqui, o servidor e o rótulo.

import csv
import os

import streamlit as st

import ambiente                                  # versão exigida e pergunta ao servidor
from benchmark import ARQUIVO_CSV, VERSAO_AGENTE  # rótulo atual e caminho do CSV

st.set_page_config(page_title="Executar o benchmark", layout="wide")


# ---------------------------------------------------------------------------
# FUNÇÕES DE CONFERÊNCIA (sem tela: devolvem dados, a tela vem depois)
# ---------------------------------------------------------------------------
def contar_execucoes(rotulo, caminho=ARQUIVO_CSV):
    """Quantas linhas do CSV têm este rótulo na coluna versao_agente.
    Devolve 0 se o CSV ainda não existir."""
    if not os.path.exists(caminho):
        return 0
    # utf-8-sig: o CSV começa com um BOM (marca invisível que o Excel usa).
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        # DictReader lê cada linha como um dicionário {nome da coluna: valor}.
        # sum(1 for ...) conta quantas linhas passam no filtro.
        return sum(1 for linha in csv.DictReader(arquivo, delimiter=";")
                   if linha["versao_agente"] == rotulo)


# ---------------------------------------------------------------------------
# TELA
# ---------------------------------------------------------------------------
st.title("Executar o benchmark")
st.caption("Etapa 1: só a conferência. Nada é executado nem gravado nesta página por enquanto.")

# --- 1. Ambiente --------------------------------------------------------------
st.subheader("1. Ollama fixado")
versao = ambiente.versao_ollama()   # texto da versão, ou None se ninguém responder
servidor = os.environ["OLLAMA_HOST"]

if versao is None:
    st.error(f"O Ollama {ambiente.VERSAO_OLLAMA} não está ligado em {servidor}. "
             "Abra o painel pelo atalho **Benchmark de agentes**, que liga o servidor, "
             "ou rode `.\\iniciar_ollama.bat` num terminal.")
elif versao != ambiente.VERSAO_OLLAMA:
    st.error(f"O servidor em {servidor} está na versão {versao}, mas o benchmark exige a "
             f"{ambiente.VERSAO_OLLAMA}. Outra versão muda as respostas e quebra a comparação "
             "com o histórico.")
else:
    st.success(f"Ollama {versao} ligado em {servidor}.")

# --- 2. Rótulo da versão ----------------------------------------------------------
st.subheader("2. Versão do agente")
ja_gravadas = contar_execucoes(VERSAO_AGENTE)

if ja_gravadas:
    st.warning(f"O rótulo **{VERSAO_AGENTE}** já tem {ja_gravadas} execuções no CSV. "
               "Rodar de novo com ele misturaria duas execuções na mesma versão. "
               f"Para repetir a base, use o rótulo **{VERSAO_AGENTE}-repeticao** "
               "(lote de calibração); para uma mudança no agente, atualize `VERSAO_AGENTE` "
               "em `benchmark.py`.")
else:
    st.info(f"O rótulo **{VERSAO_AGENTE}** ainda não existe no CSV: é uma versão nova.")

# --- 3. O que vem a seguir ---------------------------------------------------------
st.subheader("3. Execução")
st.button("Executar", disabled=True,
          help="Chega na próxima etapa, junto com a escolha do rótulo.")
st.markdown(
    "- Cada execução roda os 15 casos de ajuste nas 3 ordens dos exemplos (45 respostas, "
    "cerca de 4 a 5 minutos).\n"
    "- O conjunto oculto não terá botão: ele já foi usado na validação final da v15."
)

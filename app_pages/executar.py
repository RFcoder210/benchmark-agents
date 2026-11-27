# Página "Executar" do painel (caminho 1 do app pessoal, 17/11).
# Aparece no menu pelo app.py (st.navigation), ao lado da "Visão geral".
#
# ETAPA 2 (esta): escolhe o rótulo, pede confirmação e lança o benchmark em segundo plano.
#   1. O Ollama fixado (0.40.4, porta 11500) está ligado?
#   2. O rótulo escolhido é válido e ainda não existe no CSV?
#   3. Com a caixa de confirmação marcada, o botão chama execucao.iniciar().
# ETAPA 3 (próxima, T09): barra de progresso e resultado final.
#
# Analogia: a checagem antes da decolagem. O piloto confere combustível e
# instrumentos antes de ligar os motores; aqui, o servidor e o rótulo.

import csv
import os

import streamlit as st

import ambiente                                  # versão exigida e pergunta ao servidor
import execucao                                  # regras e lançamento em segundo plano
from benchmark import (ARQUIVO_CASOS, ARQUIVO_CSV, N_EXECUCOES, ORDENS_EXEMPLOS,
                       VERSAO_AGENTE, carregar_casos)

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


def rotulo_livre(base, caminho=ARQUIVO_CSV):
    """Primeiro rótulo ainda sem linhas no CSV: base, base2, base3...
    Ex.: se v15-repeticao já existe, devolve v15-repeticao2."""
    candidato, numero = base, 1
    # Laço while: repete enquanto o candidato já estiver no CSV.
    while contar_execucoes(candidato, caminho):
        numero += 1
        candidato = f"{base}{numero}"
    return candidato


@st.cache_resource
def registro_execucao():
    """Dicionário compartilhado que guarda a execução lançada.
    O cache_resource devolve sempre o MESMO objeto, então a execução não se perde
    quando a página recarrega (analogia: um quadro de avisos fixo na parede)."""
    return {"execucao": None}


# ---------------------------------------------------------------------------
# TELA
# ---------------------------------------------------------------------------
st.title("Executar o benchmark")
st.caption("Etapa 2: o botão grava no CSV oficial, depois de uma confirmação explícita.")

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

# --- 2. Rótulo da execução ---------------------------------------------------------
st.subheader("2. Rótulo da execução")
st.write(f"Agente em uso: **{VERSAO_AGENTE}** (definido em `benchmark.py`).")
# Sugestão de rótulo de repetição que ainda não existe no CSV (v15-repeticao, -repeticao2...).
sugestao = rotulo_livre(f"{VERSAO_AGENTE}-repeticao")
rotulo = st.text_input(
    "Rótulo da execução", value=sugestao,
    help="Nome que identifica estas linhas no CSV. Com hífen (ex.: v15-repeticao), "
         "vira lote de calibração no painel; sem hífen, conta como versão oficial.")
ja_gravadas = contar_execucoes(rotulo)

if ja_gravadas:
    st.warning(f"O rótulo **{rotulo}** já tem {ja_gravadas} execuções no CSV. "
               "Rodar de novo com ele misturaria duas execuções no mesmo rótulo. "
               f"Para repetir a base, use um rótulo novo, como **{sugestao}** "
               "(lote de calibração); para uma mudança no agente, atualize `VERSAO_AGENTE` "
               "em `benchmark.py`.")
else:
    st.info(f"O rótulo **{rotulo}** ainda não existe no CSV: é um rótulo novo.")

if "-" not in rotulo:
    st.warning(f"Sem hífen, **{rotulo}** aparecerá no painel como **versão oficial**. "
               "Com hífen (ex.: `-repeticao`), vira lote de calibração.")

# --- 3. Execução ---------------------------------------------------------------------
st.subheader("3. Execução")
registro = registro_execucao()
atual = registro["execucao"]
em_andamento = atual is not None and execucao.situacao(atual)["rodando"]

# Quantas linhas esta execução vai acrescentar: casos x ordens x repetições.
n_linhas = len(carregar_casos(ARQUIVO_CASOS)) * len(ORDENS_EXEMPLOS) * N_EXECUCOES

motivo = execucao.pode_executar(versao, rotulo, ja_gravadas, em_andamento)
if motivo:
    st.warning(motivo)
    st.button("Executar", disabled=True)
else:
    confirmado = st.checkbox(
        f"Confirmo: acrescentar {n_linhas} linhas a `resultados/resultados.csv` "
        f"com o rótulo **{rotulo}**")
    if st.button("Executar", type="primary", disabled=not confirmado):
        registro["execucao"] = execucao.iniciar(rotulo)
        st.rerun()

def formatar_tempo(segundos):
    """Converte segundos em 'mm:ss' (ex.: 125 -> '02:05')."""
    minutos, resto = divmod(int(segundos), 60)
    return f"{minutos:02d}:{resto:02d}"


# FRAGMENTO: um pedaço da página que se atualiza sozinho, sem recarregar o resto.
# Analogia: só o placar do jogo muda a cada 2 segundos; o estádio inteiro fica parado.
@st.fragment(run_every="2s")
def painel_progresso(lancada):
    """Barra de progresso da execução em andamento; ao terminar, recarrega a página."""
    estado = execucao.situacao(lancada)
    if not estado["rodando"]:
        # Recarrega a página inteira: ela sai do modo de atualização automática
        # e passa a mostrar o resultado final.
        st.rerun()
    feitas, total = estado["feitas"], estado["total"]
    tempo = formatar_tempo(estado["segundos"])
    if total == 0:
        # Antes da 1ª resposta o log ainda não tem progresso: o modelo está sendo
        # carregado na memória (cerca de 30 s a frio). Mostrar "0 de 0" confundia.
        st.progress(0, text=f"Carregando o modelo (a 1ª resposta leva cerca de 30 s) · {tempo}")
    else:
        st.progress(feitas / total, text=f"{feitas} de {total} respostas · {tempo}")
    if estado["ultimas_linhas"]:
        st.caption(estado["ultimas_linhas"][-1])


if registro["execucao"] is not None:
    lancada = registro["execucao"]
    st.info(f"Execução iniciada com o rótulo **{lancada['rotulo']}** em "
            f"{lancada['inicio'].strftime('%H:%M:%S')}. Log: `{lancada['log']}`")
    estado = execucao.situacao(lancada)

    if estado["rodando"]:
        painel_progresso(lancada)
    else:
        if estado["codigo_saida"] == 0:
            st.success(f"Execução **{lancada['rotulo']}** concluída. "
                       f"{estado['acerto'] or 'Sem linha de acerto no log.'}")
            try:
                st.page_link("dashboard.py", label="Ver na Visão geral",
                             icon=":material/monitoring:")
            except st.errors.StreamlitPageNotFoundError:
                # Fora do menu do app.py (ex.: página testada sozinha) o atalho não existe.
                st.write("Abra **Visão geral** no menu à esquerda.")
            if "-" in lancada["rotulo"]:
                st.caption("Na Visão geral, marque **Incluir lotes de calibração** "
                           "para ver este rótulo.")
        else:
            st.error(f"A execução terminou com erro (código {estado['codigo_saida']}).")
            st.code("\n".join(estado["ultimas_linhas"]))
            gravadas = contar_execucoes(lancada["rotulo"])
            if gravadas == 0:
                st.write("Nada foi gravado no CSV.")
            else:
                st.write(f"{gravadas} linhas com este rótulo estão no CSV; "
                         "confira antes de rodar de novo.")
        if st.button("Nova execução"):
            registro["execucao"] = None
            st.rerun()

st.markdown(
    f"- Cada execução roda os casos de ajuste nas {len(ORDENS_EXEMPLOS)} ordens dos exemplos "
    f"({n_linhas} respostas, cerca de 4 a 5 minutos).\n"
    "- O conjunto oculto não tem botão nesta página: ele já foi usado na validação final da v15."
)

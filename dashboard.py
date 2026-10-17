# Dashboard das métricas do benchmark (etapa 8 do plano).
# Lê resultados/resultados.csv e mostra cada métrica no gráfico mais adequado.
# NUNCA roda o modelo: só lê o que o benchmark.py já gravou.
#
# Execução:  .venv\Scripts\streamlit run dashboard.py
# (abre sozinho no navegador, em http://localhost:8501)
#
# Ferramentas:
#   pandas    -> lê e resume a tabela (como uma planilha programável)
#   altair    -> desenha os gráficos a partir de uma "descrição" (eixo x = tal coluna...)
#   streamlit -> transforma este script numa página com filtros
# A cada clique num filtro, o Streamlit roda o script de novo, de cima a baixo.

import os
import re

import altair as alt
import pandas as pd
import streamlit as st

ARQUIVO_PADRAO = "resultados/resultados.csv"

# Limiar de ruído medido no lote de 15/10: só reordenar os exemplos moveu o total
# entre 25 e 30 de 45 acertos, ou seja, cerca de 11 pontos percentuais.
RUIDO_PP = 11

# Situação de cada versão oficial (ver o histórico em benchmark.py).
HISTORICO = {
    "v1": "linha de base",
    "v2": "aprovada",
    "v3": "reprovada",
    "v4": "aprovada",
    "v5": "reprovada",
    "v6": "reprovada",
    "v7": "aprovada (base atual)",
}

# Paleta categórica (ordem fixa, validada para daltonismo). A cor segue a VERSÃO:
# a v2 tem sempre a mesma cor, em qualquer gráfico e com qualquer filtro.
CORES_SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#6250d6", "#e34948"]
# Tipos de erro: 3 cores fixas, as 3 primeiras da paleta.
CORES_ERRO = {"formato": "#2a78d6", "acao": "#eb6834", "campos": "#1baf7a"}
# Mapa de calor: um só tom (azul), do claro (pouco acerto) ao escuro (muito acerto).
ESCALA_CALOR = ["#cde2fb", "#6da7ec", "#256abf", "#0d366b"]
ORDENS = ["original", "invertida", "girada"]
# Cinza médio para textos sobre o gráfico: legível no tema claro e no escuro.
COR_TEXTO = "#8a8984"

st.set_page_config(page_title="Benchmark de agentes", layout="wide")


# ---------------------------------------------------------------------------
# PREPARAÇÃO DOS DADOS
# ---------------------------------------------------------------------------
@st.cache_data  # guarda o resultado: o CSV só é relido se o arquivo mudar
def carregar_dados(caminho, _modificado):
    """Lê o CSV (separador ";" e vírgula decimal, como o benchmark grava) e
    acrescenta colunas auxiliares. _modificado (a data do arquivo) só serve para
    o cache perceber que o CSV mudou depois de uma nova execução."""
    dados = pd.read_csv(caminho, sep=";", decimal=",", encoding="utf-8-sig")
    dados["tipo_erro"] = dados["tipo_erro"].fillna("")      # vazio = acertou
    dados["observacao"] = dados["observacao"].fillna("")
    # Rótulos com hífen (v2-loteA, v3-candidato...) são lotes de calibração.
    dados["calibracao"] = dados["versao_agente"].str.contains("-")
    # Uma mesma versão pode ter rodado mais de uma vez; marca a mais recente.
    # transform("max") devolve, para cada linha, a maior data da sua versão.
    ultima = dados.groupby("versao_agente")["data"].transform("max")
    dados["mais_recente"] = dados["data"] == ultima
    return dados


def chave_versao(rotulo):
    """Chave de ordenação: oficiais primeiro (v1, v2, ..., v10), depois os lotes."""
    numero = re.match(r"v(\d+)", rotulo)
    return ("-" in rotulo, int(numero.group(1)) if numero else 999, rotulo)


def resumo_por_versao(dados):
    """Uma linha por versão: taxa de acerto, tempo, tokens e número de execuções."""
    resumo = dados.groupby("versao_agente").agg(
        taxa=("acertou", "mean"),            # média de 0/1 = proporção de acertos
        acertos=("acertou", "sum"),
        execucoes=("acertou", "size"),
        tempo_mediano=("tempo_s", "median"),
        tokens_medios=("tokens", "mean"),
    ).reset_index()
    resumo["situacao"] = resumo["versao_agente"].map(HISTORICO).fillna("calibração")
    resumo["taxa_pct"] = resumo["taxa"] * 100
    return resumo


def por_caso(dados):
    """Uma linha por (caso, versão): quantas execuções acertaram, de quantas."""
    tabela = dados.groupby(["id_caso", "versao_agente"]).agg(
        acertos=("acertou", "sum"), execucoes=("acertou", "size")).reset_index()
    tabela["taxa"] = tabela["acertos"] / tabela["execucoes"]
    tabela["rotulo"] = tabela["acertos"].astype(str) + "/" + tabela["execucoes"].astype(str)
    return tabela


# ---------------------------------------------------------------------------
# EXIBIÇÃO DOS GRÁFICOS (computador e celular)
# ---------------------------------------------------------------------------
def mostrar(grafico):
    """Mostra um gráfico ocupando a largura disponível, sem passar da tela.
    No celular a tela tem ~375 px: por isso a legenda vai para BAIXO do gráfico
    (ao lado, ela empurraria o desenho para fora da tela) e o tamanho total
    (autosize "fit") já inclui eixos e legenda."""
    grafico = (grafico
               .properties(width="container",
                           autosize=alt.AutoSizeParams(type="fit", contains="padding"))
               .configure_legend(orient="bottom", direction="horizontal", titleOrient="left"))
    st.altair_chart(grafico, width="stretch")


# ---------------------------------------------------------------------------
# FILTROS (barra lateral)
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros")
caminho = st.sidebar.text_input("Arquivo de resultados", ARQUIVO_PADRAO,
                                help="Para outro agente do kit, aponte para o CSV dele.")
try:
    todos = carregar_dados(caminho, os.path.getmtime(caminho))
except FileNotFoundError:
    st.error(f"Arquivo não encontrado: {caminho}")
    st.stop()

incluir_calibracao = st.sidebar.checkbox(
    "Incluir lotes de calibração", value=False,
    help="Rótulos como v2-ordemB e v2-t0.7, do lote de 15/10.")
so_recente = st.sidebar.checkbox(
    "Só a execução mais recente de cada versão", value=True,
    help="Desmarque para juntar todas as execuções de uma mesma versão.")

base_filtrada = todos if incluir_calibracao else todos[~todos["calibracao"]]
if so_recente:
    base_filtrada = base_filtrada[base_filtrada["mais_recente"]]

# A ordem das versões e as cores são calculadas com TODOS os rótulos, para a
# cor de uma versão não mudar quando outra some do filtro.
ordem_versoes = sorted(todos["versao_agente"].unique(), key=chave_versao)
cor_por_versao = {v: CORES_SERIES[i % len(CORES_SERIES)] for i, v in enumerate(ordem_versoes)}

disponiveis = [v for v in ordem_versoes if v in set(base_filtrada["versao_agente"])]
versoes = st.sidebar.multiselect("Versões", disponiveis, default=disponiveis)
acoes = st.sidebar.multiselect("Ação esperada", ["registrar", "perguntar", "ignorar"],
                               default=["registrar", "perguntar", "ignorar"])
dificuldades = st.sidebar.multiselect("Dificuldade", ["facil", "medio", "dificil"],
                                      default=["facil", "medio", "dificil"])
oficiais = [v for v in versoes if "-" not in v]
base = st.sidebar.selectbox("Versão de referência (faixa de ruído)", oficiais or versoes,
                            index=(oficiais.index("v4") if "v4" in oficiais else 0))

dados = base_filtrada[base_filtrada["versao_agente"].isin(versoes)
                      & base_filtrada["categoria"].isin(acoes)
                      & base_filtrada["dificuldade"].isin(dificuldades)]
if dados.empty:
    st.warning("Nenhuma execução com esses filtros.")
    st.stop()

versoes_presentes = [v for v in ordem_versoes if v in set(dados["versao_agente"])]
escala_cor = alt.Scale(domain=versoes_presentes,
                       range=[cor_por_versao[v] for v in versoes_presentes])
eixo_versao = alt.X("versao_agente:N", title="Versão", sort=versoes_presentes,
                     axis=alt.Axis(labelAngle=0))
resumo = resumo_por_versao(dados)


# ---------------------------------------------------------------------------
# CABEÇALHO: números principais da versão de referência
# ---------------------------------------------------------------------------
st.title("Benchmark do agente de gastos")
st.caption("Cada caso roda 1 vez em cada ordem dos exemplos (original, invertida, girada). "
           "Os dados vêm só do CSV; o modelo não é executado aqui.")

linha_base = resumo[resumo["versao_agente"] == base].iloc[0]
casos_base = por_caso(dados[dados["versao_agente"] == base])
# Contêiner horizontal com quebra de linha: 4 números lado a lado no computador
# e 2 por linha no celular (cada número tem largura fixa de 160 px).
numeros = st.container(horizontal=True, gap="small")
numeros.metric(f"Acerto ({base})", f"{linha_base['taxa_pct']:.0f}%",
               help=f"{int(linha_base['acertos'])} de {int(linha_base['execucoes'])} execuções", width=160)
numeros.metric("Casos estáveis ✓", f"{(casos_base['taxa'] == 1).sum()} de {len(casos_base)}",
               help="Casos que acertaram em todas as execuções.", width=160)
numeros.metric("Tempo mediano", f"{linha_base['tempo_mediano']:.1f} s", width=160)
numeros.metric("Tokens por resposta", f"{linha_base['tokens_medios']:.0f}", width=160)


# ---------------------------------------------------------------------------
# EFICÁCIA
# ---------------------------------------------------------------------------
st.header("Eficácia")
esquerda, direita = st.columns(2)

with esquerda:
    st.subheader("Acerto geral por versão")
    st.caption(f"A faixa sombreada é a versão de referência ± {RUIDO_PP} p.p. (limiar de ruído): "
               "uma versão dentro dela não é diferente da referência só pelo total.")
    centro = linha_base["taxa_pct"]
    faixa = alt.Chart(pd.DataFrame({"y1": [centro - RUIDO_PP], "y2": [centro + RUIDO_PP]})
                      ).mark_rect(opacity=0.12, color="#2a78d6").encode(y="y1:Q", y2="y2:Q")
    linha = alt.Chart(resumo).mark_line(strokeWidth=2, color="#2a78d6", point=alt.OverlayMarkDef(
        size=80, filled=True, color="#2a78d6")).encode(
        x=eixo_versao,
        y=alt.Y("taxa_pct:Q", title="Acerto (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                 alt.Tooltip("taxa_pct:Q", title="Acerto (%)", format=".0f"),
                 alt.Tooltip("acertos:Q", title="Acertos"),
                 alt.Tooltip("execucoes:Q", title="Execuções"),
                 alt.Tooltip("situacao:N", title="Situação")])
    rotulos = alt.Chart(resumo).mark_text(dy=-14, fontSize=12, color=COR_TEXTO).encode(
        x=eixo_versao, y="taxa_pct:Q", text=alt.Text("taxa_pct:Q", format=".0f"))
    mostrar(faixa + linha + rotulos)

with direita:
    st.subheader("Acerto por grupo")
    dimensao = st.radio("Agrupar por", ["categoria", "dificuldade"], horizontal=True,
                        format_func=lambda d: "ação esperada" if d == "categoria" else d)
    grupos = (dados.groupby([dimensao, "versao_agente"])["acertou"].mean()
              .mul(100).rename("taxa_pct").reset_index())
    barras = alt.Chart(grupos).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(f"{dimensao}:N", title=None, axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("versao_agente:N", sort=versoes_presentes),
        y=alt.Y("taxa_pct:Q", title="Acerto (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("versao_agente:N", title="Versão", scale=escala_cor),
        tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                 alt.Tooltip(f"{dimensao}:N", title="Grupo"),
                 alt.Tooltip("taxa_pct:Q", title="Acerto (%)", format=".0f")])
    mostrar(barras)


# ---------------------------------------------------------------------------
# CASO A CASO E TIPOS DE ERRO
# ---------------------------------------------------------------------------
st.header("Caso a caso")
esquerda, direita = st.columns([3, 2])

with esquerda:
    st.subheader("Mapa de calor: acertos por caso e versão")
    st.caption("Cor escura = acertou em todas as execuções (estável ✓); clara = errou em todas.")
    tabela = por_caso(dados)
    celulas = alt.Chart(tabela).mark_rect(stroke="white", strokeWidth=2).encode(
        x=alt.X("versao_agente:N", title="Versão", sort=versoes_presentes, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("id_caso:N", title="Caso"),
        color=alt.Color("taxa:Q", title="Acerto", scale=alt.Scale(domain=[0, 1], range=ESCALA_CALOR),
                        legend=alt.Legend(format=".0%")),
        tooltip=[alt.Tooltip("id_caso:N", title="Caso"),
                 alt.Tooltip("versao_agente:N", title="Versão"),
                 alt.Tooltip("rotulo:N", title="Acertos")])
    # Texto branco nas células escuras e escuro nas claras, para ser sempre legível.
    textos = alt.Chart(tabela).mark_text(fontSize=11).encode(
        x=alt.X("versao_agente:N", sort=versoes_presentes), y="id_caso:N", text="rotulo:N",
        color=alt.condition("datum.taxa > 0.5", alt.value("white"), alt.value("#0b0b0b")))
    altura = 26 * tabela["id_caso"].nunique()
    mostrar((celulas + textos).properties(height=altura))

with direita:
    st.subheader("Tipos de erro por versão")
    st.caption("formato = entendeu, mas respondeu no formato errado; "
               "acao = escolheu a ação errada; campos = ação certa, campo errado.")
    erros = (dados[dados["tipo_erro"] != ""].groupby(["versao_agente", "tipo_erro"])
             .size().rename("quantidade").reset_index())
    if erros.empty:
        st.info("Nenhum erro com esses filtros.")
    else:
        empilhado = alt.Chart(erros).mark_bar(stroke="white", strokeWidth=2).encode(
            x=eixo_versao,
            y=alt.Y("quantidade:Q", title="Execuções com erro"),
            color=alt.Color("tipo_erro:N", title="Tipo de erro",
                            scale=alt.Scale(domain=list(CORES_ERRO), range=list(CORES_ERRO.values()))),
            tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                     alt.Tooltip("tipo_erro:N", title="Tipo"),
                     alt.Tooltip("quantidade:Q", title="Quantidade")])
        mostrar(empilhado)

    st.subheader("Sensibilidade à ordem dos exemplos")
    st.caption("Mesma versão, só com os exemplos do prompt em outra ordem.")
    com_ordem = dados[dados["ordem"].isin(ORDENS)]
    por_ordem = (com_ordem.groupby(["versao_agente", "ordem"])["acertou"].mean()
                 .mul(100).rename("taxa_pct").reset_index())
    # Só versões que rodaram nas 3 ordens (as antigas rodaram só na original).
    completas = por_ordem.groupby("versao_agente")["ordem"].nunique()
    por_ordem = por_ordem[por_ordem["versao_agente"].isin(completas[completas == 3].index)]
    if por_ordem.empty:
        st.info("Nenhuma versão com as 3 ordens nesses filtros.")
    else:
        barras_ordem = alt.Chart(por_ordem).mark_bar(
            cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("versao_agente:N", title="Versão", sort=versoes_presentes, axis=alt.Axis(labelAngle=0)),
            xOffset=alt.XOffset("ordem:N", sort=ORDENS),
            y=alt.Y("taxa_pct:Q", title="Acerto (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("ordem:N", title="Ordem", sort=ORDENS,
                            scale=alt.Scale(domain=ORDENS, range=CORES_SERIES[:3])),
            tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                     alt.Tooltip("ordem:N", title="Ordem"),
                     alt.Tooltip("taxa_pct:Q", title="Acerto (%)", format=".0f")])
        mostrar(barras_ordem)


# ---------------------------------------------------------------------------
# EFICIÊNCIA
# ---------------------------------------------------------------------------
st.header("Eficiência")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Tempo por resposta")
    st.caption("A caixa vai do 1º ao 3º quartil; o traço é a mediana; os pontos são respostas fora "
               "do padrão. Os pontos acima de ~8 s costumam ser a 1ª chamada, que carrega o modelo.")
    caixas = alt.Chart(dados).mark_boxplot(extent=1.5, size=28).encode(
        x=eixo_versao,
        y=alt.Y("tempo_s:Q", title="Tempo (s)"),
        color=alt.Color("versao_agente:N", scale=escala_cor, legend=None))
    mostrar(caixas)

with col2:
    st.subheader("Tokens por resposta")
    st.caption("Média de tokens (entrada + saída). Custo: R$ 0, modelo local.")
    tokens = alt.Chart(resumo).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=eixo_versao,
        y=alt.Y("tokens_medios:Q", title="Tokens"),
        color=alt.Color("versao_agente:N", scale=escala_cor, legend=None),
        tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                 alt.Tooltip("tokens_medios:Q", title="Tokens", format=".0f")])
    mostrar(tokens)

with col3:
    st.subheader("Eficácia × eficiência")
    st.caption("Para cima = acerta mais; para a esquerda = gasta menos tokens.")
    pontos = alt.Chart(resumo).mark_circle(size=140, opacity=1, stroke="white", strokeWidth=2).encode(
        x=alt.X("tokens_medios:Q", title="Tokens por resposta", scale=alt.Scale(zero=False)),
        y=alt.Y("taxa_pct:Q", title="Acerto (%)", scale=alt.Scale(zero=False)),
        color=alt.Color("versao_agente:N", scale=escala_cor, legend=None),
        tooltip=[alt.Tooltip("versao_agente:N", title="Versão"),
                 alt.Tooltip("taxa_pct:Q", title="Acerto (%)", format=".0f"),
                 alt.Tooltip("tokens_medios:Q", title="Tokens", format=".0f"),
                 alt.Tooltip("situacao:N", title="Situação")])
    nomes = alt.Chart(resumo).mark_text(dx=12, align="left", fontSize=12, color=COR_TEXTO).encode(
        x="tokens_medios:Q", y="taxa_pct:Q", text="versao_agente:N")
    mostrar(pontos + nomes)


# ---------------------------------------------------------------------------
# CALIBRAÇÃO: INSTABILIDADE COM TEMPERATURA
# ---------------------------------------------------------------------------
temperatura = todos[todos["versao_agente"] == "v2-t0.7"]
if not temperatura.empty:
    st.header("Calibração: instabilidade com temperatura 0,7")
    st.caption("Lote de 15/10, v2 com 10 execuções por caso. Casos longe de 0% e de 100% são instáveis.")
    instab = por_caso(temperatura)
    instab["taxa_pct"] = instab["taxa"] * 100
    horizontais = alt.Chart(instab).mark_bar(
        cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#2a78d6").encode(
        y=alt.Y("id_caso:N", title="Caso"),
        x=alt.X("taxa_pct:Q", title="Acerto (%)", scale=alt.Scale(domain=[0, 100])),
        tooltip=[alt.Tooltip("id_caso:N", title="Caso"), alt.Tooltip("rotulo:N", title="Acertos")])
    mostrar(horizontais.properties(height=26 * len(instab)))


# ---------------------------------------------------------------------------
# TABELAS (a mesma informação dos gráficos, em texto)
# ---------------------------------------------------------------------------
with st.expander("Resumo por versão (tabela)"):
    st.dataframe(resumo, hide_index=True)
with st.expander("Execuções filtradas (dados brutos do CSV)"):
    st.dataframe(dados.drop(columns=["calibracao", "mais_recente"]), hide_index=True)

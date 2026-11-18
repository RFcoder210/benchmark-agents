# Ponto de entrada do painel: só monta a NAVEGAÇÃO entre as páginas.
# Execução:  .venv\Scripts\streamlit run app.py   (ou o atalho "Benchmark de agentes")
#
# Analogia: a recepção de um prédio. Ela não tem conteúdo próprio; só indica
# as salas (páginas) e leva você até a escolhida.
#   - Visão geral -> dashboard.py (os gráficos; só lê o CSV)
#   - Executar    -> app_pages/executar.py (conferência antes de rodar o benchmark)
# O visual (tema Grafite) fica em .streamlit/config.toml.

import streamlit as st

st.set_page_config(page_title="Benchmark de agentes", layout="wide")

# st.Page descreve cada página: o arquivo, o nome no menu e um ícone.
# st.navigation monta o menu na barra lateral e devolve a página escolhida.
pagina = st.navigation([
    st.Page("dashboard.py", title="Visão geral", icon=":material/monitoring:", default=True),
    st.Page("app_pages/executar.py", title="Executar", icon=":material/play_arrow:"),
])
pagina.run()

# Testes do dashboard, SEM abrir o navegador.
# Execução:  .venv\Scripts\python testar_dashboard.py
# (os avisos "missing ScriptRunContext" na saída são normais em testes e podem ser ignorados)
#
# Usa o AppTest do próprio Streamlit: ele "roda" a página por dentro, como se
# alguém clicasse nos filtros, e permite conferir o que apareceu na tela.
# Analogia: um robô que clica em todos os botões e anota se algo quebrou.
#
# Cada teste: (1) ajusta os filtros, (2) roda a página, (3) confere o resultado.
# Os números esperados são calculados direto do CSV, de forma independente do
# dashboard, para pegar erros de cálculo e não só erros de execução.

import csv
from collections import defaultdict

from streamlit.testing.v1 import AppTest

from benchmark import ARQUIVO_CSV
from comparar_versoes import acertos_por_caso

OFICIAIS = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8"]
resultados = []  # lista de (nome do teste, passou?, detalhe)


def nova_pagina():
    """Abre o dashboard do zero e roda uma vez (estado padrão dos filtros)."""
    pagina = AppTest.from_file("dashboard.py", default_timeout=60)
    pagina.run()
    return pagina


def widget(pagina, tipo, rotulo):
    """Acha um filtro da barra lateral pelo rótulo (ex.: "Versões")."""
    for elemento in getattr(pagina.sidebar, tipo):
        if elemento.label == rotulo:
            return elemento
    raise LookupError(f"{tipo} {rotulo!r} não encontrado")


def checar(nome, condicao, detalhe=""):
    """Anota o resultado de uma verificação."""
    resultados.append((nome, bool(condicao), detalhe))


def sem_erro(pagina):
    """True se a página rodou sem exceção do Python."""
    return len(pagina.exception) == 0


def tabela_resumo(pagina):
    """A tabela 'Resumo por versão' (primeiro dataframe da página)."""
    return pagina.dataframe[0].value.set_index("versao_agente")


# ---------------------------------------------------------------------------
# Números esperados, calculados direto do CSV (sem passar pelo dashboard)
# ---------------------------------------------------------------------------
with open(ARQUIVO_CSV, encoding="utf-8-sig", newline="") as arquivo:
    linhas = list(csv.DictReader(arquivo, delimiter=";"))
ultima_data = {}
for l in linhas:
    ultima_data[l["versao_agente"]] = max(ultima_data.get(l["versao_agente"], ""), l["data"])
acertos_recente = defaultdict(int)
execucoes_recente = defaultdict(int)
execucoes_todas = defaultdict(int)
for l in linhas:
    execucoes_todas[l["versao_agente"]] += 1
    if l["data"] == ultima_data[l["versao_agente"]]:
        acertos_recente[l["versao_agente"]] += int(l["acertou"])
        execucoes_recente[l["versao_agente"]] += 1


# ---------------------------------------------------------------------------
# 1. Estado padrão
# ---------------------------------------------------------------------------
p = nova_pagina()
checar("padrão: roda sem erro", sem_erro(p), p.exception)
checar("padrão: 4 números no topo", len(p.metric) == 4)
checar("padrão: 9 gráficos", len(p.get("vega_lite_chart")) == 9, len(p.get("vega_lite_chart")))
checar("padrão: versões = todas as oficiais",
       widget(p, "multiselect", "Versões").value == OFICIAIS,
       widget(p, "multiselect", "Versões").value)
checar("padrão: referência = v4", widget(p, "selectbox", "Versão de referência (faixa de ruído)").value == "v4")

# 2. Os números batem com o CSV?
resumo = tabela_resumo(p)
for v in OFICIAIS:
    esperado = (acertos_recente[v], execucoes_recente[v])
    obtido = (int(resumo.loc[v, "acertos"]), int(resumo.loc[v, "execucoes"]))
    checar(f"números: {v} = {esperado[0]}/{esperado[1]} como no CSV", obtido == esperado, obtido)
taxa_v4 = round(100 * acertos_recente["v4"] / execucoes_recente["v4"])
checar("números: cartão 'Acerto (v4)'", p.metric[0].value == f"{taxa_v4}%", p.metric[0].value)
estaveis_v4 = sum(1 for a in acertos_por_caso("v4").values() if a == 3)
checar("números: cartão 'Casos estáveis' igual ao comparar_versoes.py",
       p.metric[1].value.startswith(f"{estaveis_v4} de"), p.metric[1].value)

# 3. Agrupar por dificuldade
p = nova_pagina()
p.radio[0].set_value("dificuldade").run()
checar("agrupar por dificuldade: sem erro", sem_erro(p), p.exception)

# 4. Trocar a versão de referência
p = nova_pagina()
widget(p, "selectbox", "Versão de referência (faixa de ruído)").set_value("v2").run()
taxa_v2 = round(100 * acertos_recente["v2"] / execucoes_recente["v2"])
checar("referência v2: cartão muda para v2",
       p.metric[0].label == "Acerto (v2)" and p.metric[0].value == f"{taxa_v2}%",
       (p.metric[0].label, p.metric[0].value))

# 5. Incluir os lotes de calibração
p = nova_pagina()
widget(p, "checkbox", "Incluir lotes de calibração").check().run()
opcoes = widget(p, "multiselect", "Versões").options
checar("calibração: sem erro", sem_erro(p), p.exception)
checar("calibração: rótulos do lote aparecem", "v2-t0.7" in opcoes and "v2-ordemB" in opcoes, opcoes)
checar("calibração: oficiais vêm antes dos lotes", opcoes[:len(OFICIAIS)] == OFICIAIS, opcoes[:len(OFICIAIS) + 1])

# 6. Todas as execuções (não só a mais recente)
p = nova_pagina()
widget(p, "checkbox", "Só a execução mais recente de cada versão").uncheck().run()
resumo = tabela_resumo(p)
checar("todas as execuções: sem erro", sem_erro(p), p.exception)
for v in ["v2", "v4"]:
    checar(f"todas as execuções: {v} soma todas as rodadas ({execucoes_todas[v]})",
           int(resumo.loc[v, "execucoes"]) == execucoes_todas[v], int(resumo.loc[v, "execucoes"]))

# 7. Só a ação "ignorar" (ninguém erra: o gráfico de erros vira aviso)
p = nova_pagina()
widget(p, "multiselect", "Ação esperada").set_value(["ignorar"]).run()
checar("só ignorar: sem erro", sem_erro(p), p.exception)
checar("só ignorar: aviso 'Nenhum erro'", any("Nenhum erro" in i.value for i in p.info),
       [i.value for i in p.info])

# 8. Só a dificuldade "facil"
p = nova_pagina()
widget(p, "multiselect", "Dificuldade").set_value(["facil"]).run()
checar("só fácil: sem erro", sem_erro(p), p.exception)

# 9. Só a v1 (rodou só na ordem original: o gráfico de ordens vira aviso)
p = nova_pagina()
widget(p, "multiselect", "Versões").set_value(["v1"]).run()
checar("só v1: sem erro", sem_erro(p), p.exception)
checar("só v1: referência passa a ser v1", p.metric[0].label == "Acerto (v1)", p.metric[0].label)
checar("só v1: aviso das 3 ordens", any("3 ordens" in i.value for i in p.info), [i.value for i in p.info])

# 10. Só um lote de calibração (nenhuma versão oficial selecionada)
p = nova_pagina()
widget(p, "checkbox", "Incluir lotes de calibração").check().run()
widget(p, "multiselect", "Versões").set_value(["v2-t0.7"]).run()
checar("só v2-t0.7: sem erro", sem_erro(p), p.exception)
checar("só v2-t0.7: vira a referência", p.metric[0].label == "Acerto (v2-t0.7)", p.metric[0].label)

# 11. Filtros vazios: deve avisar, não quebrar
p = nova_pagina()
widget(p, "multiselect", "Versões").set_value([]).run()
checar("nenhuma versão: sem erro", sem_erro(p), p.exception)
checar("nenhuma versão: aviso na tela", len(p.warning) == 1, [w.value for w in p.warning])
p = nova_pagina()
widget(p, "multiselect", "Ação esperada").set_value([]).run()
checar("nenhuma ação: aviso na tela", sem_erro(p) and len(p.warning) == 1, p.exception)

# 12. Arquivo inexistente: mensagem de erro amigável
p = nova_pagina()
widget(p, "text_input", "Arquivo de resultados").input("nao_existe.csv").run()
checar("arquivo inexistente: sem exceção", sem_erro(p), p.exception)
checar("arquivo inexistente: mensagem de erro", any("não encontrado" in e.value for e in p.error),
       [e.value for e in p.error])


# ---------------------------------------------------------------------------
# RESULTADO
# ---------------------------------------------------------------------------
passaram = sum(ok for _, ok, _ in resultados)
for nome, ok, detalhe in resultados:
    print(f"  {'OK   ' if ok else 'FALHA'} {nome}" + ("" if ok else f"  -> {detalhe}"))
print(f"\n{passaram}/{len(resultados)} verificações passaram")

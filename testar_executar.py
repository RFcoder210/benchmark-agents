# Testes da página "Executar" (app_pages/executar.py), SEM abrir o navegador.
# Execução:  .venv\Scripts\python testar_executar.py
# (os avisos "missing ScriptRunContext" na saída são normais em testes)
#
# Usa o AppTest do Streamlit, como testar_dashboard.py. NUNCA roda o modelo:
#   - a versão do Ollama é simulada (ambiente.versao_ollama trocada de forma temporária);
#   - todo clique em "Executar" usa um COMANDO FALSO (execucao.montar_comando trocado).
# Só o cenário "ligado de verdade" precisa do Ollama 0.40.4 no ar; sem ele, é pulado.

import csv
import glob
import os
import sys
import time

from streamlit.testing.v1 import AppTest

import ambiente
import execucao
from benchmark import ARQUIVO_CSV, VERSAO_AGENTE

PAGINA = "app_pages/executar.py"
resultados = []  # lista de (nome do teste, passou?, detalhe)


def conferir(nome, condicao, detalhe=""):
    resultados.append((nome, bool(condicao), detalhe))


def rodar_pagina(servidor, rotulo=None):
    """Zera o registro da execução, aponta para um servidor e roda a página uma vez.
    Se `rotulo` for dado, digita-o no campo de texto e roda de novo."""
    st_cache_limpar()
    os.environ["OLLAMA_HOST"] = servidor
    pagina = AppTest.from_file(PAGINA, default_timeout=60)
    pagina.run()
    if rotulo is not None:
        pagina.text_input[0].set_value(rotulo).run()
    return pagina


def st_cache_limpar():
    import streamlit as st
    st.cache_resource.clear()


def botao_executar(pagina):
    achados = [b for b in pagina.button if b.label == "Executar"]
    return achados[0] if achados else None


# Original das funções que serão trocadas temporariamente (restauradas no fim).
versao_real = ambiente.versao_ollama
comando_real = execucao.montar_comando


def ollama_simulado():
    return ambiente.VERSAO_OLLAMA


def comando_falso(rotulo):
    return [sys.executable, "-c",
            "print('[ 1/1] C01 #1 (original) -> registrar (0.1 s)')"]


# Número esperado de execuções do rótulo atual, contado direto do CSV,
# de forma independente da página.
with open(ARQUIVO_CSV, encoding="utf-8-sig", newline="") as arquivo:
    esperadas = sum(1 for linha in csv.DictReader(arquivo, delimiter=";")
                    if linha["versao_agente"] == VERSAO_AGENTE)

# Estado do CSV e dos brutos antes de qualquer teste (para provar que nada foi gravado).
stat_antes = os.stat(ARQUIVO_CSV)
brutos_antes = set(glob.glob("resultados/brutos_teste-pagina-*"))
carimbo = time.strftime("%Y%m%d%H%M%S")
rotulo_novo = f"teste-pagina-{carimbo}"
oculto_visto = []  # rótulos de widgets que contêm "oculto"

try:
    # --- Cenário 1: Ollama desligado (porta 1, onde ninguém atende), sem troca ---------
    pagina = rodar_pagina("127.0.0.1:1")
    conferir("desligado: sem exceção", not pagina.exception)
    conferir("desligado: mostra erro", any("não está ligado" in e.value for e in pagina.error))
    conferir("desligado: sem mensagem de sucesso", not pagina.success)
    botao = botao_executar(pagina)
    conferir("desligado: botão Executar existe e está desligado", botao is not None and botao.disabled)
    conferir("desligado: nenhuma caixa de confirmação", len(pagina.checkbox) == 0)

    # --- Cenário 2: rótulo padrão e rótulo já gravado ----------------------------------
    conferir("rótulo: campo começa com o rótulo de repetição",
             pagina.text_input[0].value == f"{VERSAO_AGENTE}-repeticao")
    pagina = rodar_pagina("127.0.0.1:1", VERSAO_AGENTE)
    conferir("rótulo atual: aviso de rótulo já gravado", any(
        f"já tem {esperadas} execuções" in w.value for w in pagina.warning),
        f"esperado: {esperadas} execuções de {VERSAO_AGENTE}")

    # --- Cenário 3: Ollama simulado, rótulos barrados ----------------------------------
    ambiente.versao_ollama = ollama_simulado
    pagina = rodar_pagina("127.0.0.1:1", VERSAO_AGENTE)
    botao = botao_executar(pagina)
    conferir("simulado, rótulo repetido: botão desligado", botao is not None and botao.disabled)
    conferir("simulado, rótulo repetido: aviso com 'outro'",
             any("outro" in w.value for w in pagina.warning))

    pagina = rodar_pagina("127.0.0.1:1", "a b")
    botao = botao_executar(pagina)
    conferir("simulado, rótulo 'a b': botão desligado", botao is not None and botao.disabled)

    pagina = rodar_pagina("127.0.0.1:1", f"{VERSAO_AGENTE}-oculto")
    botao = botao_executar(pagina)
    conferir("simulado, rótulo reservado: botão desligado", botao is not None and botao.disabled)

    pagina = rodar_pagina("127.0.0.1:1", "v99")
    conferir("simulado, rótulo sem hífen: aviso de versão oficial",
             any("versão oficial" in w.value for w in pagina.warning))

    # --- Cenário 4: rótulo novo, confirmação e clique com COMANDO FALSO ---------------
    pagina = rodar_pagina("127.0.0.1:1", rotulo_novo)
    conferir("novo: sem exceção", not pagina.exception)
    conferir("novo: caixa de confirmação presente", len(pagina.checkbox) == 1)
    botao = botao_executar(pagina)
    conferir("novo: botão desligado antes de marcar", botao is not None and botao.disabled)
    pagina.checkbox[0].check().run()
    botao = botao_executar(pagina)
    conferir("novo: botão ligado depois de marcar", botao is not None and not botao.disabled)

    # Widgets com "oculto" no rótulo (checagem feita com a página completa).
    for grupo in (pagina.button, pagina.checkbox, pagina.text_input, pagina.selectbox, pagina.radio):
        for w in grupo:
            if "oculto" in (w.label or "").lower():
                oculto_visto.append(w.label)
    conferir("nenhum widget com 'oculto' no rótulo", not oculto_visto, str(oculto_visto))

    # Clique: só com o comando falso instalado (confere a troca antes de clicar).
    execucao.montar_comando = comando_falso
    seguro = execucao.montar_comando is comando_falso and ambiente.versao_ollama is ollama_simulado
    conferir("clique: comando falso instalado antes de clicar", seguro)
    if seguro:
        botao_executar(pagina).click().run()
        conferir("clique: sem exceção", not pagina.exception, str(pagina.exception))
        conferir("clique: mensagem de execução iniciada com o rótulo",
                 any("Execução iniciada" in i.value and rotulo_novo in i.value for i in pagina.info))
        # Espera o processo falso terminar (até 10 s) e apaga o log que ele criou.
        import streamlit as st
        registro = st.cache_resource  # só para manter o import em uso
        fim = time.time() + 10
        while time.time() < fim:
            logs = glob.glob(f"resultados/logs/execucao_{rotulo_novo}_*.log")
            if logs:
                break
            time.sleep(0.2)
        time.sleep(1.5)  # dá tempo de o processo falso encerrar e soltar o arquivo
        for log in glob.glob(f"resultados/logs/execucao_{rotulo_novo}_*.log"):
            for _ in range(20):
                try:
                    os.remove(log)
                    break
                except PermissionError:
                    time.sleep(0.5)
    else:
        print("PULADO  clique: a troca do comando não valeu; nenhum clique foi feito")
finally:
    # Restaura sempre as funções originais, mesmo se um teste quebrar.
    ambiente.versao_ollama = versao_real
    execucao.montar_comando = comando_real

# --- Cenário 5: nada foi gravado --------------------------------------------------------
stat_depois = os.stat(ARQUIVO_CSV)
conferir("CSV intacto: mesmo tamanho", stat_depois.st_size == stat_antes.st_size)
conferir("CSV intacto: mesma data de modificação", stat_depois.st_mtime_ns == stat_antes.st_mtime_ns)
conferir("nenhum brutos_teste-pagina-* novo",
         set(glob.glob("resultados/brutos_teste-pagina-*")) == brutos_antes)
conferir("nenhum log execucao_teste-pagina-* sobrando",
         not glob.glob("resultados/logs/execucao_teste-pagina-*"))

# --- Cenário 6: Ollama ligado de verdade (sem clicar em Executar) -----------------------
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
sys.exit(0 if total_ok == len(resultados) else 1)

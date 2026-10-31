# Teste de mutação: quem está sendo testado aqui é o BENCHMARK, não o agente.
# Analogia: para saber se a balança funciona, colocamos nela um peso conhecido.
# Cada "mutante" é uma falha colocada de propósito. Se o benchmark perceber, o
# mutante foi DETECTADO; se não perceber, ele SOBREVIVEU, o que indica um ponto cego.
#
# Parte A: respostas certas da v15 corrompidas de propósito. comparar() percebe?
# Parte B: o código do benchmark mutado (comparar, classificar_erro e a régua de
#          aprovação). Os testes existentes percebem?
# Parte C: o agente mutado (uma trava desligada ou uma seção do prompt retirada).
#          Algum caso cai abaixo da faixa de ruído? Usa o modelo local: cerca de 4
#          minutos por execução (8 mutantes + 3 controles); reaproveita o que já rodou.
#
# Execução:  .venv\Scripts\python testar_mutacao.py            (Partes A e B, sem modelo)
#            .venv\Scripts\python testar_mutacao.py --modelo   (acrescenta a Parte C)
#
# Nada aqui altera agente.py ou benchmark.py, nem grava em resultados/resultados.csv:
# as falhas existem só na memória, durante a execução. As respostas da Parte C ficam
# em resultados/mutacao/ollama-<versão>/. Usa somente casos/casos.json, nunca o
# conjunto oculto. Sem a variável OLLAMA_HOST, a Parte C usa o Ollama fixado em
# ambiente.py; ligue-o antes com iniciar_ollama.bat.

import copy      # deepcopy: cópia independente, para corromper sem estragar o original
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

import ambiente  # aponta para o Ollama fixado; precisa vir antes de "import ollama"
import ollama

import agente
from benchmark import ARQUIVO_CASOS, ORDENS_EXEMPLOS, carregar_casos, comparar, executar_casos
from comparar_versoes import versao_aprovada
from testar_comparar import EXEMPLOS, EXEMPLOS_TIPO
from testar_regua import EXEMPLOS_REGUA

BRUTOS_V15 = "resultados/brutos_v15_2026-10-27_1920.json"


def pasta_mutacao():
    """Uma pasta por versão do Ollama, pois a versão muda as respostas (30/10: a 0.40.13
    tirou a v15 de 44/45). Para usar outro servidor: defina a variável OLLAMA_HOST."""
    return f"resultados/mutacao/ollama-{ambiente.versao_ollama()}"


def marca(previsto, obtido):
    """Avisa quando o resultado contraria a previsão declarada antes de rodar."""
    return "" if previsto == obtido else "  <- contrariou a previsão"


# ---------------------------------------------------------------------------
# PARTE A: RESPOSTAS CORROMPIDAS
# ---------------------------------------------------------------------------
# Cada corrupção é uma função pequena que estraga uma resposta certa. Funções
# também podem ser guardadas numa lista, como qualquer outro valor.
def somar_um(r, e):
    r["argumentos"]["valor"] = float(e["valor"]) + 1


def vezes_dez(r, e):
    r["argumentos"]["valor"] = float(e["valor"]) * 10


def trocar_categoria(r, e):
    r["argumentos"]["categoria"] = "lazer" if e["categoria"] != "lazer" else "saude"


def trocar_pagamento(r, e):
    r["argumentos"]["pagamento"] = "pix" if e["pagamento"] != "pix" else "dinheiro"


def data_anterior(r, e):
    dia = date.fromisoformat(e["data"]) - timedelta(days=1)
    r["argumentos"]["data"] = dia.isoformat()


def esquecer_pagamento(r, e):
    del r["argumentos"]["pagamento"]


def virar_ignorar(r, e):
    r["acao"], r["argumentos"], r["n_chamadas"] = "ignorar", {}, 0


def virar_registrar(r, e):
    r["acao"], r["n_chamadas"] = "registrar", 1
    r["argumentos"] = {"valor": 10.0, "categoria": "outros", "pagamento": "pix",
                       "data": "2026-10-11"}


def tirar_campo_da_pergunta(r, e):
    r["argumentos"]["campos_faltantes"] = e["campos_faltantes"][:-1]   # sem o último


def pedir_campo_a_mais(r, e):
    todos = ["valor", "categoria", "pagamento"]
    a_mais = [c for c in todos if c not in e["campos_faltantes"]][0]
    r["argumentos"]["campos_faltantes"] = e["campos_faltantes"] + [a_mais]


def duas_chamadas(r, e):
    r["n_chamadas"] = 2


def pergunta_sem_sentido(r, e):
    r["argumentos"]["pergunta"] = "Qual é a sua cor favorita?"


def campo_inventado(r, e):
    r["argumentos"]["loja"] = "inventada pelo agente"


def conversar_em_vez_de_ignorar(r, e):
    r["texto"] = "Olá! Como posso ajudar você hoje?"


# (descrição, ações a que se aplica, função, previsão: detecta?)
# As 3 últimas são pontos cegos já esperados: comparar() não olha o texto da
# pergunta, nem argumentos a mais, nem o texto de quem deveria só ignorar.
CORRUPCOES = [
    ("valor + 1", ["registrar"], somar_um, True),
    ("valor x 10", ["registrar"], vezes_dez, True),
    ("categoria trocada", ["registrar"], trocar_categoria, True),
    ("pagamento trocado", ["registrar"], trocar_pagamento, True),
    ("data um dia antes", ["registrar"], data_anterior, True),
    ("pagamento esquecido", ["registrar"], esquecer_pagamento, True),
    ("registro virou ignorar", ["registrar"], virar_ignorar, True),
    ("pergunta virou registro", ["perguntar"], virar_registrar, True),
    ("ignorar virou registro", ["ignorar"], virar_registrar, True),
    ("pergunta com campo a menos", ["perguntar"], tirar_campo_da_pergunta, True),
    ("pergunta com campo a mais", ["perguntar"], pedir_campo_a_mais, True),
    ("2 chamadas de ferramenta", ["registrar", "perguntar"], duas_chamadas, True),
    ("texto da pergunta sem sentido", ["perguntar"], pergunta_sem_sentido, False),
    ("campo inventado no registro", ["registrar"], campo_inventado, False),
    ("conversou em vez de ignorar", ["ignorar"], conversar_em_vez_de_ignorar, False),
]


def parte_a():
    """Corrompe cada resposta certa da v15 e conta quantas comparar() percebe."""
    with open(BRUTOS_V15, encoding="utf-8") as arquivo:
        registros = json.load(arquivo)
    certos = [r for r in registros if comparar(r["resposta"], r["esperado"])[0]]

    print(f"PARTE A - {len(certos)} respostas certas da v15, corrompidas de propósito")
    print(f"  {'Corrupção':<32}{'detectadas':>12}")
    for nome, acoes, corromper, previsto in CORRUPCOES:
        alvos = [r for r in certos if r["esperado"]["acao"] in acoes]
        detectadas = 0
        for r in alvos:
            resposta = copy.deepcopy(r["resposta"])
            corromper(resposta, r["esperado"])
            acertou, _ = comparar(resposta, r["esperado"])
            detectadas += not acertou
        detectou_tudo = detectadas == len(alvos)
        fracao = f"{detectadas}/{len(alvos)}"
        print(f"  {nome:<32}{fracao:>12}{marca(previsto, detectou_tudo)}")
    print()


# ---------------------------------------------------------------------------
# PARTE B: O CÓDIGO DO BENCHMARK MUTADO
# ---------------------------------------------------------------------------
def carregar_mutado(arquivo, trocas):
    """Lê o código de um .py como TEXTO, aplica as trocas e o executa na memória,
    devolvendo um dicionário com as funções mutadas. O arquivo não é alterado.
    O assert protege contra um mutante que não muda nada porque o trecho sumiu."""
    with open(arquivo, encoding="utf-8") as origem:
        fonte = origem.read()
    for antigo, novo in trocas:
        assert antigo in fonte, f"trecho não encontrado em {arquivo}: {antigo!r}"
        fonte = fonte.replace(antigo, novo)
    modulo = {"__name__": "mutante"}   # outro nome: o bloco __main__ não roda
    exec(compile(fonte, arquivo, "exec"), modulo)
    return modulo


# (descrição, [(trecho original, trecho mutado)], previsão: os testes detectam?)
# Na 1ª rodada (30/10), sem os exemplos novos de testar_comparar.py e testar_regua.py,
# 4 destes e 4 dos MUTANTES_REGUA sobreviveram. Com os exemplos, a previsão é detectar.
MUTANTES_COMPARAR = [
    ("valor errado nunca conta",
     [("if float(obtido) != float(certo):", "if False:")], True),
    ("valor com tolerância de R$ 1",
     [("if float(obtido) != float(certo):", "if abs(float(obtido) - float(certo)) > 1:")], True),
    ("categoria não é conferida",
     [('CAMPOS_GASTO = ["valor", "categoria", "pagamento", "data"]',
       'CAMPOS_GASTO = ["valor", "pagamento", "data"]')], True),
    ("pagamento não é conferido",
     [('CAMPOS_GASTO = ["valor", "categoria", "pagamento", "data"]',
       'CAMPOS_GASTO = ["valor", "categoria", "data"]')], True),
    ("data só é conferida se ausente",
     [("elif obtido != certo:", 'elif campo != "data" and obtido != certo:')], True),
    ("pergunta aceita campo a mais",
     [('if set(obtidos) != set(esperado["campos_faltantes"]):',
       'if not set(esperado["campos_faltantes"]).issubset(obtidos):')], True),
    ("pergunta aceita campo a menos",
     [('if set(obtidos) != set(esperado["campos_faltantes"]):',
       'if not set(obtidos).issubset(esperado["campos_faltantes"]):')], True),
    ("ordem dos campos passa a importar",
     [('if set(obtidos) != set(esperado["campos_faltantes"]):',
       'if list(obtidos) != list(esperado["campos_faltantes"]):')], True),
    ("ação não é conferida",
     [('if resposta["acao"] != esperado["acao"]:', "if False:")], True),
    ("aceita 2 chamadas de ferramenta",
     [('if resposta["n_chamadas"] > 1:', 'if resposta["n_chamadas"] > 2:')], True),
    # Mutante EQUIVALENTE: sem esse teste, None ainda cai como erro nas linhas
    # seguintes. O código muda, mas o comportamento não; sobreviver aqui é normal.
    ("sem o teste de campo ausente (equivalente)",
     [("if obtido is None:", "if False:")], False),
    ("erro de formato não reconhece o texto",
     [("and escreveu_chamada:", "and False:")], True),
    ("2 chamadas deixam de ser erro de formato",
     [('if campos_errados == ["n_chamadas"]:', "if False:")], True),
]


def testes_detectam(modulo):
    """Roda os exemplos de testar_comparar.py com as funções mutadas. Devolve True
    se algum exemplo falhar (ou o código quebrar), isto é, se o mutante foi pego."""
    try:
        for _, resp, esperado, certo in EXEMPLOS:
            if modulo["comparar"](resp, esperado) != certo:
                return True
        for _, resp, esperado, tipo in EXEMPLOS_TIPO:
            _, erros = modulo["comparar"](resp, esperado)
            if modulo["classificar_erro"](resp, esperado, erros) != tipo:
                return True
    except Exception:
        return True
    return False


def ler_historico():
    """Todas as respostas já salvas, menos as do conjunto oculto."""
    registros = []
    for caminho in glob.glob("resultados/brutos_*.json"):
        if "oculto" not in caminho:
            with open(caminho, encoding="utf-8") as arquivo:
                registros += json.load(arquivo)
    return registros


def veredito(modulo, r):
    """O que o benchmark (mutado ou não) conclui de uma resposta salva."""
    acertou, erros = modulo["comparar"](r["resposta"], r["esperado"])
    return acertou, erros, modulo["classificar_erro"](r["resposta"], r["esperado"], erros)


def diferencas_no_historico(modulo, original, historico):
    """Em quantas respostas já salvas o veredito do mutante difere do original?
    Mostra se a falha teria mudado algum resultado real do projeto."""
    diferentes = 0
    for r in historico:
        try:
            if veredito(modulo, r) != veredito(original, r):
                diferentes += 1
        except Exception:
            diferentes += 1
    return diferentes


# As decisões que a régua tomou ao longo do projeto: (base, nova, opções, resultado).
# O conjunto v10 -> v12 é MANTER de propósito: a régua apontou a perda, e a aprovação
# veio depois, do usuário, com a evidência do ruído. Aqui importa o que a régua disse.
DECISOES_HISTORICAS = [
    ("v2", "v3", {}, False),
    ("v2", "v4", {}, True),
    ("v4", "v5", {}, False),
    ("v4", "v6", {}, False),
    ("v4", "v7", {"neutra": True}, True),
    ("v7", "v8", {}, False),
    ("v7", "v9", {"neutra": True}, True),
    ("v9", "v10", {}, True),
    ("v10", "v11", {}, False),
    ("v10", "v12", {"neutra": True}, False),
    ("v12", "v13", {"alvo": "C08"}, False),
    ("v12", "v14", {"neutra": True}, True),
    ("v14", "v15", {"alvo": "C08"}, True),
]

MUTANTES_REGUA = [
    ("tolera 1 perda de estável", [("MAXIMO_PERDAS = 0", "MAXIMO_PERDAS = 1")], True),
    ("exige só 1 ganho", [("MINIMO_GANHOS = 2", "MINIMO_GANHOS = 1")], True),
    ("não exige ganhos", [("MINIMO_GANHOS = 2", "MINIMO_GANHOS = 0")], True),
    ("total pode cair", [("total_nova >= total_base,", "True,")], True),
    ("perda só se cair a 0/3",
     [("elif antes == 3 and depois < 3:", "elif antes == 3 and depois == 0:")], True),
    ("alvo precisa subir só 1", [("MINIMO_SUBIDA_ALVO = 2", "MINIMO_SUBIDA_ALVO = 1")], True),
    ("alvo precisa subir 3", [("MINIMO_SUBIDA_ALVO = 2", "MINIMO_SUBIDA_ALVO = 3")], True),
    ("usa a execução mais antiga da versão",
     [('ultima = max(l["data"] for l in linhas)', 'ultima = min(l["data"] for l in linhas)')], True),
    ("régua neutra ignora perdas",
     [("elif neutra:\n        condicoes = [\n            len(perdas) <= MAXIMO_PERDAS,",
       "elif neutra:\n        condicoes = [\n            True,")], True),
    ("régua dirigida ignora perdas",
     [("if alvo is not None:\n        subida = acertos_nova.get(alvo, 0) - acertos_base.get(alvo, 0)\n"
       "        condicoes = [\n            len(perdas) <= MAXIMO_PERDAS,",
       "if alvo is not None:\n        subida = acertos_nova.get(alvo, 0) - acertos_base.get(alvo, 0)\n"
       "        condicoes = [\n            True,")], True),
]


def decisoes_que_mudam(modulo):
    """Lista as decisões históricas que a régua (mutada ou não) teria tomado diferente."""
    mudaram = []
    for base, nova, opcoes, certo in DECISOES_HISTORICAS:
        obtido = modulo["versao_aprovada"](modulo["acertos_por_caso"](base),
                                           modulo["acertos_por_caso"](nova), **opcoes)
        if obtido != certo:
            mudaram.append(f"{base}->{nova}")
    return mudaram


def exemplos_que_falham(modulo):
    """Quantos exemplos de testar_regua.py a régua (mutada ou não) erra."""
    return sum(modulo["versao_aprovada"](base, nova, **opcoes) != certo
               for _, base, nova, opcoes, certo in EXEMPLOS_REGUA)


def parte_b():
    """Muta o código de comparar() e da régua e vê se alguém percebe."""
    historico = ler_historico()
    print(f"PARTE B1 - comparar() e classificar_erro() mutados "
          f"(histórico: {len(historico)} respostas salvas)")
    print(f"  {'Mutante':<44}{'testes':>12}{'histórico':>12}")
    sem_mutacao = carregar_mutado("benchmark.py", [])
    assert not testes_detectam(sem_mutacao), "os testes falham mesmo sem mutação"
    vivos = 0
    for nome, trocas, previsto in MUTANTES_COMPARAR:
        modulo = carregar_mutado("benchmark.py", trocas)
        detectou = testes_detectam(modulo)
        vivos += not detectou
        testes = "detectou" if detectou else "SOBREVIVEU"
        print(f"  {nome:<44}{testes:>12}{diferencas_no_historico(modulo, sem_mutacao, historico):>12}"
              f"{marca(previsto, detectou)}")
    print(f"  Sobreviveram aos testes: {vivos}/{len(MUTANTES_COMPARAR)}\n")

    print(f"PARTE B2 - régua mutada, contra as {len(DECISOES_HISTORICAS)} decisões históricas "
          f"e os {len(EXEMPLOS_REGUA)} exemplos de testar_regua.py")
    original = carregar_mutado("comparar_versoes.py", [])
    assert decisoes_que_mudam(original) == [], "a régua original não reproduz o histórico"
    assert exemplos_que_falham(original) == 0, "a régua original erra os exemplos"
    print("  Régua original: reproduz todas as decisões e acerta todos os exemplos.")
    print(f"  {'Mutante':<44}{'resultado':>12}{'exemplos':>10}   decisões que mudam")
    vivos = 0
    for nome, trocas, previsto in MUTANTES_REGUA:
        modulo = carregar_mutado("comparar_versoes.py", trocas)
        mudaram = decisoes_que_mudam(modulo)
        falhas = exemplos_que_falham(modulo)
        detectou = bool(mudaram) or falhas > 0
        vivos += not detectou
        resultado = "detectou" if detectou else "SOBREVIVEU"
        print(f"  {nome:<44}{resultado:>12}{falhas:>10}   {', '.join(mudaram)}{marca(previsto, detectou)}")
    print(f"  Sobreviveram: {vivos}/{len(MUTANTES_REGUA)}\n")


# ---------------------------------------------------------------------------
# PARTE C: O AGENTE MUTADO (USA O MODELO LOCAL)
# ---------------------------------------------------------------------------
def sem_secao(titulo, proximo):
    """Devolve o início do prompt sem uma seção, para desligar uma regra."""
    return re.sub(rf"{titulo}\n.*?(?={proximo}\n)", "", agente._ANTES, flags=re.DOTALL)


# interpretar() procura as funções no módulo agente na hora da chamada. Por isso
# dá para trocar uma delas temporariamente, sem editar o arquivo agente.py.
# (nome, {atributo do agente: substituto}, casos que devem cair: a previsão, tirada
# de onde cada trava agiu na v15. v4 e v9 não agiram: a previsão é sobreviverem.)
MUTANTES_AGENTE = [
    ("sem-recuperacao-v4", {"recuperar_chamada_em_texto": lambda texto, data: None}, []),
    ("sem-trava-valor-v7", {"valor_invalido": lambda argumentos: False}, ["C10"]),
    ("sem-trava-pagamento-v9", {"retirar_pagamento_informado": lambda argumentos, mensagem: None}, []),
    ("sem-trava-categoria-v12",
     {"conciliar_categoria": lambda acao, argumentos, etiqueta: (acao, argumentos, False)}, ["C13"]),
    ("sem-trava-inventado-v14", {"pagamento_inventado": lambda mensagem: False}, ["C02", "C09"]),
    ("sem-dica-v15", {"USAR_DICA": False}, ["C08", "C09"]),
    ("prompt-sem-datas", {"_ANTES": sem_secao("## Datas", "## O que não é gasto")}, ["C08", "C12"]),
    ("prompt-sem-nao-gasto", {"_ANTES": sem_secao("## O que não é gasto", "## Exemplos resolvidos")}, ["C11"]),
]


def rodar_com_mutacao(rotulo, substitutos, casos, frio=False):
    """Roda o benchmark com as trocas e sempre restaura o agente, mesmo se houver
    erro (bloco try/finally). Se o arquivo já existe, reaproveita: assim uma
    execução interrompida continua de onde parou.
    frio=True descarrega o modelo antes, para a execução começar sem cache."""
    caminho = os.path.join(pasta_mutacao(), f"{rotulo}.json")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)

    if frio:
        ollama.generate(model=agente.MODELO, keep_alive=0)   # keep_alive=0 = descarregar
    print(f"\n=== {rotulo} ({datetime.now():%H:%M}) ===")
    originais = {nome: getattr(agente, nome) for nome in substitutos}
    try:
        for nome, valor in substitutos.items():
            setattr(agente, nome, valor)
        registros = executar_casos(casos, 1, ordens=ORDENS_EXEMPLOS)
    finally:
        for nome, valor in originais.items():
            setattr(agente, nome, valor)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)
    return registros


def acertos_dos_registros(registros):
    """Como acertos_por_caso() de comparar_versoes.py, mas lendo as respostas salvas."""
    acertos = {}
    for r in registros:
        certo, _ = comparar(r["resposta"], r["esperado"])
        acertos[r["id_caso"]] = acertos.get(r["id_caso"], 0) + int(certo)
    return acertos


def parte_c():
    """Roda cada mutante do agente e o compara com a FAIXA DE RUÍDO: os controles são
    a v15 sem mudança nenhuma, repetida, e o que varia entre eles é só acaso. Um
    mutante é detectado se algum caso cair ABAIXO do pior controle. Analogia: uma
    balança que oscila entre 70 e 72 kg não mostra que você engordou ao marcar 71."""
    os.makedirs(pasta_mutacao(), exist_ok=True)
    casos = carregar_casos(ARQUIVO_CASOS)

    # A ordem importa: o estado do cache muda as respostas. O 1º controle e o último
    # começam com o modelo descarregado; o do meio, logo depois de outra execução.
    primeiro = rodar_com_mutacao("controle-v15", {}, casos, frio=True)
    resultados = []
    for rotulo, substitutos, previstos in MUTANTES_AGENTE:
        acertos = acertos_dos_registros(rodar_com_mutacao(rotulo, substitutos, casos))
        resultados.append((rotulo, acertos, previstos))
    quente = rodar_com_mutacao("controle-v15-quente", {}, casos)
    frio = rodar_com_mutacao("controle-v15-frio", {}, casos, frio=True)

    with open(BRUTOS_V15, encoding="utf-8") as arquivo:
        v15 = acertos_dos_registros(json.load(arquivo))
    controles = {"frio, 1º": acertos_dos_registros(primeiro),
                 "quente": acertos_dos_registros(quente),
                 "frio, 2º": acertos_dos_registros(frio)}

    print(f"\nPARTE C - agente mutado, comparado à faixa de ruído dos controles (v15 sem mudança); "
          f"respostas em {pasta_mutacao()}")
    print(f"  v15 de 27/10 (Ollama 0.40.4): {sum(v15.values())}/45")
    for nome, acertos in controles.items():
        print(f"  Controle {nome:<9}: {sum(acertos.values())}/45  "
              f"{ {c: n for c, n in acertos.items() if n < 3} }")

    # O teste de "falso alarme": a régua reprova o agente comparado com ele mesmo?
    aprova = versao_aprovada(controles["quente"], controles["frio, 2º"], neutra=True)
    print(f"  Régua neutra, v15 quente x v15 fria: {'APROVA' if aprova else 'REPROVA (falso alarme)'}")

    pior = {c: min(a[c] for a in controles.values()) for c in v15}
    print(f"  {'Mutante':<26}{'total':>7}{'resultado':>12}   abaixo da faixa (previstos)")
    for rotulo, acertos, previstos in resultados:
        abaixo = [c for c in pior if acertos[c] < pior[c]]
        total = f"{sum(acertos.values())}/45"
        resultado = "detectou" if abaixo else "SOBREVIVEU"
        quedas = ", ".join(f"{c} {pior[c]}->{acertos[c]}" for c in abaixo) or "-"
        print(f"  {rotulo:<26}{total:>7}{resultado:>12}   {quedas} "
              f"({', '.join(previstos) or 'nenhum'}){marca(sorted(previstos), abaixo)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")   # o símbolo ✓ e os acentos no Windows
    parte_a()
    parte_b()
    if "--modelo" in sys.argv:
        parte_c()

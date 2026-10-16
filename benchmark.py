# Benchmark do agente de gastos (v1).
# Construído em partes:
#   Parte 1: ler os casos de teste do arquivo JSON.                <- pronto
#   Parte 2: executar o agente em cada caso, em 3 ordens dos exemplos. <- pronto
#   Parte 3: comparar a resposta com o gabarito.                     <- pronto
#   Parte 4: salvar os resultados num CSV.                           <- pronto
# Execução:  .venv\Scripts\python benchmark.py
#
# Atenção: durante os ajustes do agente, use SOMENTE casos/casos.json.
# O conjunto oculto (casos/casos_ocultos.json) fica para a validação final.

import csv       # biblioteca padrão para escrever planilhas CSV
import json      # biblioteca padrão para ler e escrever arquivos JSON
import os        # biblioteca padrão para lidar com pastas e caminhos
from datetime import datetime  # data e hora atuais, para nomear os resultados

from agente import ACAO_POR_FERRAMENTA, EXEMPLOS_V2, interpretar, montar_prompt

ARQUIVO_CASOS = "casos/casos.json"
PASTA_RESULTADOS = "resultados"
VERSAO_AGENTE = "v2"   # mude a cada alteração no agente (v2, v3...)
# Histórico: v1 = linha de base (instruções); v2 = + bloco de exemplos resolvidos no prompt
ARQUIVO_CSV = os.path.join(PASTA_RESULTADOS, "resultados.csv")  # um só arquivo para todas as versões


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
def ordens_padrao(n_exemplos):
    """Devolve as 3 ordens dos exemplos usadas pelo benchmark, como uma lista de
    pares (nome, lista de índices). Com 8 exemplos:
        original  -> [0, 1, 2, 3, 4, 5, 6, 7]
        invertida -> [7, 6, 5, 4, 3, 2, 1, 0]
        girada    -> [4, 5, 6, 7, 0, 1, 2, 3]  (começa do meio)
    Cada ordem começa e termina com um exemplo diferente, o que evita o problema
    do lote de 15/10 (as 3 ordens sorteadas começavam pelo mesmo exemplo)."""
    original = list(range(n_exemplos))
    meio = n_exemplos // 2
    return [
        ("original", original),
        ("invertida", original[::-1]),             # [::-1] = a lista de trás para a frente
        ("girada", original[meio:] + original[:meio]),
    ]


# Cada caso roda 1 vez em CADA uma das 3 ordens (3 execuções no total).
# Por quê: o lote de 15/10 mostrou que, com temperatura 0, repetir na mesma
# ordem quase sempre dá cópias, enquanto só reordenar os exemplos virou de
# 2 a 4 casos. Variar a ordem mede o ruído que realmente importa.
ORDENS_EXEMPLOS = ordens_padrao(len(EXEMPLOS_V2))
N_EXECUCOES = 1  # execuções por ordem (3 ordens x 1 = 3 execuções por caso)


def executar_casos(casos, n_execucoes, temperatura=0, prompt_sistema=None, ordens=None):
    """Roda o agente em cada caso e devolve uma lista com um registro
    (dicionário) por execução.

    ordens: lista de pares (nome, ordem) de ordens_padrao(). Cada caso roda
        n_execucoes vezes em CADA ordem. Sem ordens, roda n_execucoes vezes
        com prompt_sistema (ou o prompt oficial), como no lote de 15/10.
    temperatura e prompt_sistema são repassados ao agente; os valores padrão
    correspondem ao agente oficial."""

    # Monta as "variantes" do prompt: pares (nome da ordem, texto do prompt).
    if ordens is None:
        variantes = [("original", prompt_sistema)]
    else:
        variantes = [(nome, montar_prompt(ordem)) for nome, ordem in ordens]

    registros = []
    total = len(casos) * len(variantes) * n_execucoes
    feitas = 0

    # Três laços, um dentro do outro: para CADA ordem, para CADA caso,
    # repete a execução n vezes. A ordem fica no laço de FORA de propósito:
    # o Ollama reaproveita o início do prompt já processado na chamada anterior
    # (cache), desde que ele não mude. Alternar a ordem a cada chamada destruía
    # esse cache e triplicava o tempo (de ~3 s para ~9 s por resposta).
    # execucao_n conta 1, 2, 3... dentro de cada caso.
    for i_ordem, (nome_ordem, prompt) in enumerate(variantes):
        for caso in casos:
            for volta in range(n_execucoes):
                execucao_n = i_ordem * n_execucoes + volta + 1
                resposta = interpretar(caso["mensagem"], caso["data_referencia"],
                                       temperatura=temperatura, prompt_sistema=prompt)
                feitas += 1

                # Guarda tudo o que será necessário para comparar e salvar depois.
                registros.append({
                    "id_caso": caso["id"],
                    "dificuldade": caso["dificuldade"],
                    "execucao_n": execucao_n,
                    "ordem": nome_ordem,
                    "esperado": caso["esperado"],
                    "resposta": resposta,
                })

                # Progresso na tela: [ 7/45] C03 #1 (original) -> registrar (2.8 s)
                print(f'[{feitas:>2}/{total}] {caso["id"]} #{execucao_n} ({nome_ordem}) -> '
                      f'{resposta["acao"]} ({resposta["tempo_s"]} s)')

    return registros


def salvar_brutos(registros, rotulo=VERSAO_AGENTE):
    """Salva as respostas cruas num arquivo JSON. Assim a Parte 3 (comparação)
    pode ser desenvolvida e testada sem rodar o modelo de novo.
    rotulo entra no nome do arquivo (padrão: a versão oficial do agente)."""

    os.makedirs(PASTA_RESULTADOS, exist_ok=True)  # cria a pasta, se não existir
    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M")  # ex.: 2026-10-14_1830
    caminho = os.path.join(PASTA_RESULTADOS, f"brutos_{rotulo}_{carimbo}.json")

    # ensure_ascii=False mantém os acentos legíveis; indent=2 deixa o arquivo organizado.
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)
    return caminho


# ---------------------------------------------------------------------------
# PARTE 3: COMPARAR COM O GABARITO
# ---------------------------------------------------------------------------
CAMPOS_GASTO = ["valor", "categoria", "pagamento", "data"]


def comparar(resposta, esperado):
    """Compara a resposta do agente com o gabarito de um caso.

    resposta: dicionário devolvido por interpretar(), por exemplo
        {"acao": "registrar", "argumentos": {"valor": 35, ...}, "n_chamadas": 1, ...}
    esperado: o campo "esperado" do caso em casos.json, por exemplo
        {"acao": "registrar", "valor": 35.0, "categoria": "mercado", ...}

    Devolve DOIS valores:
        acertou        -> True ou False
        campos_errados -> lista com o nome do que deu errado (vazia se acertou)
    """
    campos_errados = []
    argumentos = resposta["argumentos"]

    # PASSO 1 - A ação está certa? Se não estiver, para aqui: não faz sentido
    # comparar os campos de uma ação errada.
    if resposta["acao"] != esperado["acao"]:
        return False, ["acao"]

    # PASSO 2 - "registrar": confere os 4 campos, um por um.
    if esperado["acao"] == "registrar":
        for campo in CAMPOS_GASTO:
            obtido = argumentos.get(campo)  # None se o modelo esqueceu o campo
            certo = esperado[campo]
            if obtido is None:
                campos_errados.append(campo)
            elif campo == "valor":
                # Compara como número: 35 e 35.0 são o mesmo valor.
                # Se o modelo mandou um texto que não é número, conta como erro.
                try:
                    if float(obtido) != float(certo):
                        campos_errados.append(campo)
                except (TypeError, ValueError):
                    campos_errados.append(campo)
            elif obtido != certo:
                campos_errados.append(campo)

    # PASSO 3 - "perguntar": confere os campos faltantes, sem ligar para a ordem.
    # O texto da pergunta não é conferido na v1.
    elif esperado["acao"] == "perguntar":
        obtidos = argumentos.get("campos_faltantes") or []
        if set(obtidos) != set(esperado["campos_faltantes"]):
            campos_errados.append("campos_faltantes")

    # PASSO 4 - "ignorar" não tem campos: não há nada a fazer.

    # PASSO 5 - Uso correto de ferramentas: mais de uma chamada é erro.
    if resposta["n_chamadas"] > 1:
        campos_errados.append("n_chamadas")

    acertou = len(campos_errados) == 0
    return acertou, campos_errados


# Nomes das ferramentas simuladas (registrar_gasto, perguntar_usuario), para
# reconhecer quando o modelo ESCREVE a chamada como texto em vez de fazê-la.
NOMES_FERRAMENTAS = list(ACAO_POR_FERRAMENTA)


def classificar_erro(resposta, esperado, campos_errados):
    """Diz de que TIPO é o erro, para separar "não entendeu" de "entendeu,
    mas respondeu no formato errado". Devolve um destes textos:
        ""        -> acertou (não há erro)
        "formato" -> a interpretação pode estar certa, mas a forma de responder
                     falhou: escreveu a chamada da ferramenta como texto, ou
                     chamou mais de uma ferramenta
        "acao"    -> escolheu a ação errada (registrar, perguntar ou ignorar)
        "campos"  -> ação certa, mas algum campo errado (valor, categoria...)
    Analogia: numa prova, "formato" é a resposta certa escrita fora do
    gabarito; "acao" e "campos" são respostas erradas de fato."""

    if not campos_errados:
        return ""

    # Formato 1: deveria chamar uma ferramenta, não chamou, mas o texto da
    # resposta contém o nome de uma ferramenta (ex.: "registrar_gasto: valor 45...").
    texto = resposta.get("texto") or ""
    escreveu_chamada = any(nome in texto for nome in NOMES_FERRAMENTAS)
    if resposta["acao"] == "ignorar" and esperado["acao"] != "ignorar" and escreveu_chamada:
        return "formato"

    # Formato 2: o único erro foi chamar mais de uma ferramenta.
    if campos_errados == ["n_chamadas"]:
        return "formato"

    if "acao" in campos_errados:
        return "acao"
    return "campos"


# ---------------------------------------------------------------------------
# PARTE 4: SALVAR OS RESULTADOS NO CSV
# ---------------------------------------------------------------------------
# Ordem das colunas do CSV (definida em contexto-benchmark-agentes.md).
#   categoria -> a ação esperada do caso (registrar, perguntar ou ignorar)
#   tokens    -> tokens de entrada + tokens de saída
#   custo     -> sempre 0, pois o modelo roda localmente
#   n_passos  -> número de chamadas de ferramenta feitas pelo agente
#   ordem     -> em que ordem estavam os exemplos do prompt nessa execução
#   tipo_erro -> formato, acao ou campos (ver classificar_erro); vazio se acertou
COLUNAS = ["data", "versao_agente", "id_caso", "categoria", "dificuldade",
           "execucao_n", "ordem", "acertou", "campos_errados", "tipo_erro",
           "tempo_s", "tokens", "custo", "n_passos", "observacao"]


def descrever_erro(resposta, esperado, campos_errados):
    """Escreve, em texto curto, o que o agente fez de errado (coluna observacao).
    Devolve texto vazio quando o agente acertou."""

    if not campos_errados:
        return ""
    argumentos = resposta["argumentos"]

    # Ação errada: descreve a ação que o agente tomou no lugar da certa.
    if "acao" in campos_errados:
        if resposta["acao"] == "registrar":
            # Junta os 4 campos num texto só: "valor=89.9, categoria=educacao, ..."
            campos = [f"{campo}={argumentos.get(campo)}" for campo in CAMPOS_GASTO]
            return "registrou: " + ", ".join(campos)
        if resposta["acao"] == "perguntar":
            return f'perguntou {argumentos.get("campos_faltantes")}: "{argumentos.get("pergunta")}"'
        if resposta["acao"] == "ignorar":
            return f'ignorou; texto: "{(resposta["texto"] or "").strip()[:80]}"'
        return f'ação desconhecida: {resposta["acao"]}'

    # Ação certa, mas com campos errados: mostra obtido x esperado em cada um.
    partes = []
    for campo in campos_errados:
        if campo == "campos_faltantes":
            partes.append(f'campos_faltantes={argumentos.get("campos_faltantes")} '
                          f'(esperado {esperado["campos_faltantes"]})')
        elif campo == "n_chamadas":
            partes.append(f'{resposta["n_chamadas"]} chamadas de ferramenta')
        else:
            partes.append(f"{campo}={argumentos.get(campo)} (esperado {esperado[campo]})")
    return "; ".join(partes)


def avaliar(registros, data_execucao, rotulo=VERSAO_AGENTE):
    """Compara cada execução com o gabarito e monta as linhas do CSV
    (um dicionário por linha, com as chaves de COLUNAS).
    rotulo vai na coluna versao_agente (padrão: a versão oficial do agente)."""

    linhas = []
    for r in registros:
        resposta = r["resposta"]
        acertou, campos_errados = comparar(resposta, r["esperado"])
        linhas.append({
            "data": data_execucao,
            "versao_agente": rotulo,
            "id_caso": r["id_caso"],
            "categoria": r["esperado"]["acao"],
            "dificuldade": r["dificuldade"],
            "execucao_n": r["execucao_n"],
            "ordem": r.get("ordem", "original"),  # brutos antigos não têm ordem
            "acertou": 1 if acertou else 0,  # 1/0 permite tirar a média na planilha
            "campos_errados": ",".join(campos_errados),
            "tipo_erro": classificar_erro(resposta, r["esperado"], campos_errados),
            "tempo_s": resposta["tempo_s"],
            "tokens": (resposta["tokens_entrada"] or 0) + (resposta["tokens_saida"] or 0),
            "custo": 0.0,
            "n_passos": resposta["n_chamadas"],
            "observacao": descrever_erro(resposta, r["esperado"], campos_errados),
        })
    return linhas


def salvar_csv(linhas):
    """Acrescenta as linhas ao fim de resultados/resultados.csv.
    Formato pensado para o Excel em português: separador ";" e vírgula decimal."""

    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    arquivo_novo = not os.path.exists(ARQUIVO_CSV)

    # "utf-8-sig" grava uma marca no início do arquivo que faz o Excel exibir os
    # acentos corretamente; ela só pode ser gravada uma vez, na criação do arquivo.
    codificacao = "utf-8-sig" if arquivo_novo else "utf-8"

    # Modo "a" (append) = acrescentar ao fim, sem apagar as execuções anteriores.
    # newline="" é obrigatório com o módulo csv no Windows (evita linhas em branco).
    with open(ARQUIVO_CSV, "a", encoding=codificacao, newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS, delimiter=";")
        if arquivo_novo:
            escritor.writeheader()  # o cabeçalho só entra na primeira vez
        for linha in linhas:
            # Copia a linha trocando o ponto decimal por vírgula nos números com casas.
            linha = dict(linha)
            for coluna in ["tempo_s", "custo"]:
                linha[coluna] = str(linha[coluna]).replace(".", ",")
            escritor.writerow(linha)


def mostrar_resumo(linhas):
    """Mostra na tela a taxa de acerto geral, por ação esperada e por dificuldade."""

    def taxa(grupo):
        acertos = sum(linha["acertou"] for linha in grupo)
        return f"{acertos}/{len(grupo)} ({acertos / len(grupo):.0%})"

    print(f"\nAcerto geral: {taxa(linhas)}")
    for coluna in ["categoria", "dificuldade", "ordem"]:
        # Agrupa as linhas pelo valor da coluna: {"registrar": [...], "perguntar": [...]}
        grupos = {}
        for linha in linhas:
            grupos.setdefault(linha[coluna], []).append(linha)
        for valor, grupo in grupos.items():
            print(f"  {coluna} = {valor:<10} {taxa(grupo)}")

    # Quantos erros de cada tipo: separa "não entendeu" de "errou o formato".
    erros = [linha["tipo_erro"] for linha in linhas if linha["tipo_erro"]]
    contagem = {tipo: erros.count(tipo) for tipo in ["formato", "acao", "campos"]}
    print(f"Erros por tipo: {contagem}")

    tempo_medio = sum(linha["tempo_s"] for linha in linhas) / len(linhas)
    tokens_medio = sum(linha["tokens"] for linha in linhas) / len(linhas)
    print(f"Tempo médio: {tempo_medio:.2f} s | Tokens médios: {tokens_medio:.0f} | Custo: R$ 0,00")


# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    casos = carregar_casos(ARQUIVO_CASOS)
    nomes = ", ".join(nome for nome, _ in ORDENS_EXEMPLOS)
    print(f"{len(casos)} casos carregados de {ARQUIVO_CASOS}; "
          f"{N_EXECUCOES} execução por ordem dos exemplos ({nomes}).\n")

    data_execucao = datetime.now().strftime("%Y-%m-%d %H:%M")
    registros = executar_casos(casos, N_EXECUCOES, ordens=ORDENS_EXEMPLOS)
    caminho = salvar_brutos(registros)
    print(f"\nRespostas salvas em {caminho}")

    linhas = avaliar(registros, data_execucao)
    salvar_csv(linhas)
    print(f"Resultados acrescentados em {ARQUIVO_CSV}")
    mostrar_resumo(linhas)

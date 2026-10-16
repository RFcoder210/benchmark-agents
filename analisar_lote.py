# Análise do lote de calibração de 15/10/2026 (ver lote.py).
# Lê resultados/resultados.csv e os brutos_*.json do lote e gera as tabelas
# usadas no relatório: resultados/tabelas_lote_2026-10-15.md
# Execução:  .venv\Scripts\python analisar_lote.py
#
# Termos usados:
#   taxa      -> acertos / execuções de um caso (ex.: 2/3)
#   maioria   -> o caso "passa" (✓) se acertou em mais da metade das execuções
#   virada    -> caso cuja maioria (✓/✗) mudou em relação à v2 de 14/10

import csv
import json
import math   # biblioteca padrão de matemática (usaremos a raiz quadrada)

ARQUIVO_CSV = "resultados/resultados.csv"
ARQUIVO_CONFIG = "resultados/lote_2026-10-15_config.json"
ARQUIVO_SAIDA = "resultados/tabelas_lote_2026-10-15.md"
BRUTOS_V2_OFICIAL = "resultados/brutos_v2_2026-10-14_2001.json"

ORDENS = ["v2-ordemB", "v2-ordemC", "v2-ordemD"]
META_V3 = ["C07", "C08", "C14"]      # casos que a v3 quer recuperar
PROTEGIDOS = ["C02", "C09", "C15"]   # casos que a v3 não pode perder


# ---------------------------------------------------------------------------
# LEITURA DOS DADOS
# ---------------------------------------------------------------------------
def ler_csv():
    """Lê o CSV e devolve {rotulo: [linhas]}, guardando só a execução MAIS
    RECENTE de cada rótulo (a v1, por exemplo, foi rodada duas vezes)."""
    # "utf-8-sig" descarta a marca invisível que o benchmark grava para o Excel.
    with open(ARQUIVO_CSV, encoding="utf-8-sig", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo, delimiter=";"))

    por_rotulo = {}
    for linha in linhas:
        # Converte os textos do CSV em números (vírgula decimal -> ponto).
        linha["acertou"] = int(linha["acertou"])
        linha["tempo_s"] = float(linha["tempo_s"].replace(",", "."))
        linha["tokens"] = int(linha["tokens"])
        por_rotulo.setdefault(linha["versao_agente"], []).append(linha)

    for rotulo, grupo in por_rotulo.items():
        ultima = max(linha["data"] for linha in grupo)  # datas no formato AAAA-MM-DD HH:MM
        por_rotulo[rotulo] = [linha for linha in grupo if linha["data"] == ultima]
    return por_rotulo


def taxas_por_caso(linhas):
    """Devolve {id_caso: (acertos, execucoes)}."""
    taxas = {}
    for linha in linhas:
        acertos, total = taxas.get(linha["id_caso"], (0, 0))
        taxas[linha["id_caso"]] = (acertos + linha["acertou"], total + 1)
    return taxas


def maioria(acertos, total):
    """True se o caso acertou em mais da metade das execuções."""
    return acertos > total / 2


def marca(acertos, total):
    return "✓" if maioria(acertos, total) else "✗"


def assinatura(resposta):
    """Resume uma resposta crua num texto comparável (ação + argumentos).
    Duas respostas com a mesma assinatura são, na prática, idênticas."""
    return json.dumps([resposta["acao"], resposta["argumentos"], resposta["n_chamadas"]],
                      ensure_ascii=False, sort_keys=True)


def ler_brutos(caminho):
    """Devolve {id_caso: [assinatura da execução 1, 2, ...]}."""
    with open(caminho, encoding="utf-8") as arquivo:
        registros = json.load(arquivo)
    respostas = {}
    for r in registros:
        respostas.setdefault(r["id_caso"], []).append(assinatura(r["resposta"]))
    return respostas


# ---------------------------------------------------------------------------
# ANÁLISE
# ---------------------------------------------------------------------------
def main():
    dados = ler_csv()
    with open(ARQUIVO_CONFIG, encoding="utf-8") as arquivo:
        config = json.load(arquivo)
    casos = sorted(taxas_por_caso(dados["v2"]))  # ["C01", ..., "C15"]
    taxas = {rotulo: taxas_por_caso(linhas) for rotulo, linhas in dados.items()}
    saida = []  # lista de linhas de texto; no fim vira o arquivo .md

    def total(rotulo):
        acertos = sum(linha["acertou"] for linha in dados[rotulo])
        return f"{acertos}/{len(dados[rotulo])} ({acertos / len(dados[rotulo]):.0%})"

    def n_maioria(rotulo):
        return sum(maioria(*taxas[rotulo][c]) for c in casos)

    def viradas(rotulo_a, rotulo_b):
        return [c for c in casos if maioria(*taxas[rotulo_a][c]) != maioria(*taxas[rotulo_b][c])]

    # --- Visão geral -------------------------------------------------------
    saida.append("## Visão geral\n")
    saida.append("| Rótulo | Data | Execuções/caso | Acerto (execuções) | Casos ✓ por maioria | Tempo médio (s) | Tokens médios |")
    saida.append("|---|---|---|---|---|---|---|")
    for rotulo in ["v1", "v2", "v2-loteA", "v2-t0.7"] + ORDENS + ["v3-candidato"]:
        if rotulo not in dados:
            saida.append(f"| {rotulo} | (sem dados) | | | | | |")
            continue
        linhas = dados[rotulo]
        n = len(linhas) // len(casos)
        tempo = sum(l["tempo_s"] for l in linhas) / len(linhas)
        # Mediana do tempo: a 1ª chamada carrega o modelo e distorce a média.
        tempos = sorted(l["tempo_s"] for l in linhas)
        mediana = tempos[len(tempos) // 2]
        tokens = sum(l["tokens"] for l in linhas) / len(linhas)
        saida.append(f"| {rotulo} | {linhas[0]['data']} | {n} | {total(rotulo)} | "
                     f"{n_maioria(rotulo)}/15 | {tempo:.2f} (mediana {mediana:.2f}) | {tokens:.0f} |")

    # --- A: determinismo ---------------------------------------------------
    saida.append("\n## A. Determinismo com temperatura 0\n")
    brutos_a = ler_brutos(config["v2-loteA"]["brutos"])
    brutos_v2 = ler_brutos(BRUTOS_V2_OFICIAL)
    variam_dentro = [c for c in casos if len(set(brutos_a[c])) > 1]
    diferem_v2 = [c for c in casos if set(brutos_a[c]) != set(brutos_v2[c])]
    resultado_difere = [c for c in casos if taxas["v2-loteA"][c] != taxas["v2"][c]]
    saida.append(f"- Casos em que as 3 respostas do loteA não são idênticas entre si: {variam_dentro or 'nenhum'}")
    saida.append(f"- Casos em que as respostas do loteA diferem das da v2 de 14/10 (ação+argumentos): {diferem_v2 or 'nenhum'}")
    saida.append(f"- Casos com taxa de acerto diferente da v2 de 14/10: {resultado_difere or 'nenhum'}")
    saida.append(f"- Total loteA: {total('v2-loteA')} | v2 de 14/10: {total('v2')}")
    for c in diferem_v2:
        saida.append(f"  - {c}: loteA {sorted(set(brutos_a[c]))} | v2 {sorted(set(brutos_v2[c]))}")

    # --- B: temperatura 0.7 ------------------------------------------------
    saida.append("\n## B. Temperatura 0.7, 10 execuções\n")
    saida.append("| Caso | v2 (t=0, 3×) | v2-t0.7 (10×) | Respostas distintas | Situação |")
    saida.append("|---|---|---|---|---|")
    brutos_b = ler_brutos(config["v2-t0.7"]["brutos"])
    instaveis = []
    for c in casos:
        a, n = taxas["v2-t0.7"][c]
        situacao = "estável ✓" if a == n else ("estável ✗" if a == 0 else "INSTÁVEL")
        if 0 < a < n:
            instaveis.append(c)
        a0, n0 = taxas["v2"][c]
        saida.append(f"| {c} | {a0}/{n0} | {a}/{n} ({a / n:.0%}) | {len(set(brutos_b[c]))} | {situacao} |")
    saida.append(f"\nCasos instáveis (0 < acertos < 10): {instaveis or 'nenhum'}")

    # Quantas repetições bastam? Para cada caso instável com taxa p, calcula a
    # chance de o voto da maioria de k execuções dar o mesmo veredito que a
    # "taxa verdadeira" (estimada pelas 10 execuções). Usa a distribuição binomial:
    # P(exatamente j acertos em k) = C(k, j) * p^j * (1-p)^(k-j).
    saida.append("\nChance de a maioria de k execuções concordar com o veredito das 10 (casos instáveis):\n")
    ks = [1, 3, 5, 7, 9]
    saida.append("| Caso | p (10×) | " + " | ".join(f"k={k}" for k in ks) + " |")
    saida.append("|---|---|" + "---|" * len(ks))
    for c in instaveis:
        a, n = taxas["v2-t0.7"][c]
        p = a / n
        celulas = []
        for k in ks:
            p_maioria_acerta = sum(math.comb(k, j) * p ** j * (1 - p) ** (k - j)
                                   for j in range(k // 2 + 1, k + 1))
            concorda = p_maioria_acerta if p > 0.5 else 1 - p_maioria_acerta
            celulas.append(f"{concorda:.0%}")
        saida.append(f"| {c} | {p:.0%} | " + " | ".join(celulas) + " |")

    # Oscilação esperada da taxa geral (desvio-padrão) com k execuções por caso:
    # variância da média = soma de p(1-p)/k de cada caso, dividida por 15².
    saida.append("\nDesvio-padrão esperado da taxa de acerto geral (pontos percentuais), por k:\n")
    saida.append("| k | " + " | ".join(str(k) for k in [1, 3, 5, 10, 20]) + " |")
    saida.append("|---|" + "---|" * 5)
    ps = [taxas["v2-t0.7"][c][0] / taxas["v2-t0.7"][c][1] for c in casos]
    desvios = [100 * math.sqrt(sum(p * (1 - p) / k for p in ps)) / len(casos) for k in [1, 3, 5, 10, 20]]
    saida.append("| desvio (p.p.) | " + " | ".join(f"{d:.1f}" for d in desvios) + " |")

    # --- C: reordenação ----------------------------------------------------
    saida.append("\n## C. Reordenação dos exemplos (temperatura 0)\n")
    for rotulo in ORDENS:
        saida.append(f"- {rotulo}: ordem {config[rotulo]['ordem']}")
    colunas = ["v2", "v2-loteA"] + ORDENS
    saida.append("\n| Caso | " + " | ".join(colunas) + " |")
    saida.append("|---|" + "---|" * len(colunas))
    for c in casos:
        celulas = [f"{marca(*taxas[r][c])} {taxas[r][c][0]}/{taxas[r][c][1]}" for r in colunas]
        saida.append(f"| {c} | " + " | ".join(celulas) + " |")
    saida.append("| **Total ✓** | " + " | ".join(f"{n_maioria(r)}/15" for r in colunas) + " |")
    n_viradas = []
    for rotulo in ORDENS:
        v = viradas("v2", rotulo)
        n_viradas.append(len(v))
        saida.append(f"\n- {rotulo}: {len(v)} caso(s) viraram em relação à v2: {v or 'nenhum'} | total {total(rotulo)}")
    # Casos que viraram em pelo menos uma reordenação.
    sensiveis = sorted({c for r in ORDENS for c in viradas("v2", r)})
    saida.append(f"\n- Casos sensíveis à ordem (viraram em pelo menos uma): {sensiveis or 'nenhum'}")
    saida.append(f"- Viradas por reordenação: mínimo {min(n_viradas)}, máximo {max(n_viradas)}, "
                 f"média {sum(n_viradas) / len(n_viradas):.1f}")
    v12 = viradas("v1", "v2")
    saida.append(f"- Para comparação, v1 → v2: {len(v12)} caso(s) viraram: {v12}")
    for c in v12:
        saida.append(f"  - {c}: v1 {marca(*taxas['v1'][c])} → v2 {marca(*taxas['v2'][c])}")
    acertos_ordens = [sum(l["acertou"] for l in dados[r]) for r in ORDENS]
    saida.append(f"- Acertos (de 45) nas reordenações: {acertos_ordens}; v2 = "
                 f"{sum(l['acertou'] for l in dados['v2'])}; v1 = {sum(l['acertou'] for l in dados['v1'])}")

    # --- D: v3 candidata ---------------------------------------------------
    saida.append("\n## D. v2 × v3-candidato (temperatura 0)\n")
    saida.append("| Caso | Papel | v2 (14/10) | v2-loteA | v3-candidato | Mudou? |")
    saida.append("|---|---|---|---|---|---|")
    for c in casos:
        papel = "meta" if c in META_V3 else ("protegido" if c in PROTEGIDOS else "")
        mudou = "**sim**" if maioria(*taxas["v2"][c]) != maioria(*taxas["v3-candidato"][c]) else ""
        celulas = [f"{marca(*taxas[r][c])} {taxas[r][c][0]}/{taxas[r][c][1]}"
                   for r in ["v2", "v2-loteA", "v3-candidato"]]
        saida.append(f"| {c} | {papel} | " + " | ".join(celulas) + f" | {mudou} |")
    v23 = viradas("v2", "v3-candidato")
    ganhos = [c for c in v23 if maioria(*taxas["v3-candidato"][c])]
    perdas = [c for c in v23 if not maioria(*taxas["v3-candidato"][c])]
    saida.append(f"\n- Viradas v2 → v3-candidato: {len(v23)} (ganhos {ganhos}, perdas {perdas}); "
                 f"saldo {len(ganhos) - len(perdas):+d} | total {total('v3-candidato')}")
    saida.append(f"- Meta {META_V3}: " + ", ".join(f"{c} {marca(*taxas['v3-candidato'][c])}" for c in META_V3))
    saida.append(f"- Protegidos {PROTEGIDOS}: " + ", ".join(f"{c} {marca(*taxas['v3-candidato'][c])}" for c in PROTEGIDOS))

    # Observações dos erros da v3 candidata (o que ela fez de errado).
    saida.append("\nErros da v3-candidato (coluna observacao do CSV):\n")
    for linha in dados["v3-candidato"]:
        if not linha["acertou"] and linha["execucao_n"] == "1":
            saida.append(f"- {linha['id_caso']}: {linha['observacao']}")

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as arquivo:
        arquivo.write("# Tabelas do lote de calibração (geradas por analisar_lote.py)\n\n")
        arquivo.write("\n".join(saida) + "\n")
    print("\n".join(saida))
    print(f"\nTabelas gravadas em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()

# Compara duas versões do agente caso a caso e decide se a nova pode ser aprovada.
# Execução:  .venv\Scripts\python comparar_versoes.py v2 v3
#
# Usa só as execuções no protocolo de 3 ordens (original, invertida, girada)
# e, de cada versão, a execução MAIS RECENTE gravada em resultados/resultados.csv.
#
# A função versao_aprovada() (no fim do arquivo) é SUA para escrever: ela é a
# regra que transforma os números em decisão. O resto do arquivo já funciona.

import csv
import sys

from benchmark import ARQUIVO_CSV, ORDENS_EXEMPLOS

NOMES_ORDENS = [nome for nome, _ in ORDENS_EXEMPLOS]  # ["original", "invertida", "girada"]


def acertos_por_caso(versao):
    """Devolve um dicionário {id_caso: acertos}, em que acertos vai de 0 a 3
    (um ponto por ordem em que o caso passou). Ex.: {"C01": 3, "C02": 1, ...}"""

    with open(ARQUIVO_CSV, encoding="utf-8-sig", newline="") as arquivo:
        linhas = [l for l in csv.DictReader(arquivo, delimiter=";")
                  if l["versao_agente"] == versao and l["ordem"] in NOMES_ORDENS]
    if not linhas:
        sys.exit(f"Nenhuma execução da versão {versao!r} no protocolo de 3 ordens.")

    # Fica só com a execução mais recente da versão (a maior data).
    ultima = max(l["data"] for l in linhas)
    acertos = {}
    for l in linhas:
        if l["data"] == ultima:
            # setdefault cria a chave com 0 na primeira vez; depois só soma.
            acertos[l["id_caso"]] = acertos.setdefault(l["id_caso"], 0) + int(l["acertou"])
    return acertos


def situacao(acertos):
    """Traduz 0 a 3 acertos em palavras."""
    if acertos == 3:
        return "estável ✓"
    if acertos == 0:
        return "estável ✗"
    return "sensível"   # passou em algumas ordens e falhou em outras


def mostrar_tabela(base, nova, acertos_base, acertos_nova):
    """Mostra, caso a caso, quantas ordens cada versão acertou."""
    print(f"{'Caso':<6}{base:>8}{nova:>8}   situação ({base} -> {nova})")
    for caso in sorted(acertos_base):
        a, b = acertos_base[caso], acertos_nova.get(caso, 0)
        seta = "  <- mudou" if situacao(a) != situacao(b) else ""
        print(f"{caso:<6}{a:>6}/3{b:>6}/3   {situacao(a)} -> {situacao(b)}{seta}")
    print(f"{'Total':<6}{sum(acertos_base.values()):>5}/45{sum(acertos_nova.values()):>5}/45")


# ---------------------------------------------------------------------------
# A REGRA DE APROVAÇÃO (para você escrever)
# ---------------------------------------------------------------------------
def versao_aprovada(acertos_base, acertos_nova):
    """Recebe os dois dicionários {id_caso: acertos de 0 a 3} e devolve True
    (aprovar a versão nova) ou False (manter a base).

    Dados do lote de 15/10 para orientar a sua regra:
      - Só reordenar os exemplos virou de 2 a 4 casos (o "limiar de ruído").
      - Um caso "estável ✓" (3/3) é um acerto em que dá para confiar;
        um caso "sensível" (1/3 ou 2/3) pode virar por acaso.

    Perguntas que a regra deve responder:
      1. O que conta como um caso GANHO? (ex.: passar de sensível/✗ para estável ✓?)
      2. O que conta como um caso PERDIDO? Uma perda pesa igual a um ganho?
      3. Quantos ganhos líquidos são necessários para superar o ruído?
      4. Existe algum caso que, se perdido, reprova a versão de qualquer jeito?

    Dica de Python: percorra os casos com
        for caso in acertos_base:
            antes = acertos_base[caso]
            depois = acertos_nova.get(caso, 0)
    e conte os ganhos e as perdas em duas variáveis.
    """
    return None  # substitua por sua regra; None = "regra ainda não escrita"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: .venv\\Scripts\\python comparar_versoes.py VERSAO_BASE VERSAO_NOVA")
    base, nova = sys.argv[1], sys.argv[2]  # sys.argv = palavras digitadas no terminal

    acertos_base = acertos_por_caso(base)
    acertos_nova = acertos_por_caso(nova)
    mostrar_tabela(base, nova, acertos_base, acertos_nova)

    decisao = versao_aprovada(acertos_base, acertos_nova)
    if decisao is None:
        print("\nRegra de aprovação ainda não escrita (versao_aprovada devolve None).")
    else:
        print(f"\nDecisão: {'APROVAR ' + nova if decisao else 'MANTER ' + base}")

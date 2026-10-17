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
# A REGRA DE APROVAÇÃO
# ---------------------------------------------------------------------------
# Base nos dados do lote de 15/10:
#   - Só reordenar os exemplos virou de 2 a 4 casos (o "limiar de ruído").
#   - Um caso "estável ✓" (3/3) é um acerto em que dá para confiar;
#     um caso "sensível" (1/3 ou 2/3) pode virar por acaso.
# Por isso a regra só dá valor às mudanças que CHEGAM ou SAEM do estável ✓.
# Oscilar entre 0/3, 1/3 e 2/3 é tratado como ruído e não conta.
#
# Analogia: um aluno só "aprendeu" a matéria se acerta a questão nas três
# versões da prova; acertar em uma e errar em outra ainda é sorte.
MINIMO_GANHOS = 2   # ganhos necessários para aprovar (1 só pode ser acaso)
MAXIMO_PERDAS = 0   # um acerto estável que quebra é regressão real: reprova


def contar_mudancas(acertos_base, acertos_nova):
    """Devolve duas listas de casos:
        ganhos -> não era estável ✓ na base e passou a ser na nova (3/3)
        perdas -> era estável ✓ na base e deixou de ser na nova"""
    ganhos, perdas = [], []
    for caso in acertos_base:
        antes = acertos_base[caso]
        depois = acertos_nova.get(caso, 0)   # caso ausente na nova conta como 0
        if antes < 3 and depois == 3:
            ganhos.append(caso)
        elif antes == 3 and depois < 3:
            perdas.append(caso)
    return ganhos, perdas


def versao_aprovada(acertos_base, acertos_nova, neutra=False):
    """Recebe os dois dicionários {id_caso: acertos de 0 a 3} e devolve True
    (aprovar a versão nova) ou False (manter a base).

    Régua normal (neutra=False): a nova versão é aprovada só se cumprir as
    TRÊS condições:
      1. nenhum caso estável ✓ foi perdido (perdas <= MAXIMO_PERDAS);
      2. pelo menos MINIMO_GANHOS casos viraram estável ✓;
      3. o total de acertos não caiu (protege contra perdas espalhadas
         entre casos sensíveis, que a condição 1 não enxerga).

    Régua neutra (neutra=True, regra de 17/10): para uma trava de segurança
    que implementa uma regra explícita da especificação (ex.: "nunca invente
    um valor"). O valor dela é impedir erros futuros, não ganhar casos agora,
    então a condição 2 não é exigida; valem só a 1 e a 3. O tipo da mudança
    é decidido ANTES de rodar o benchmark, nunca depois de ver o resultado."""
    ganhos, perdas = contar_mudancas(acertos_base, acertos_nova)
    total_base = sum(acertos_base.values())
    total_nova = sum(acertos_nova.values())

    if neutra:
        condicoes = [
            len(perdas) <= MAXIMO_PERDAS,
            total_nova >= total_base,
        ]
    else:
        condicoes = [
            len(perdas) <= MAXIMO_PERDAS,
            len(ganhos) >= MINIMO_GANHOS,
            total_nova >= total_base,
        ]
    return all(condicoes)   # all() = True só se todas as condições forem True


if __name__ == "__main__":
    # sys.argv = palavras digitadas no terminal. Ex.: comparar_versoes.py v4 v7 --neutra
    #   -> ["comparar_versoes.py", "v4", "v7", "--neutra"]
    neutra = "--neutra" in sys.argv          # True se a palavra foi digitada
    versoes = [a for a in sys.argv[1:] if a != "--neutra"]
    if len(versoes) != 2:
        sys.exit("Uso: .venv\\Scripts\\python comparar_versoes.py VERSAO_BASE VERSAO_NOVA [--neutra]")
    base, nova = versoes

    acertos_base = acertos_por_caso(base)
    acertos_nova = acertos_por_caso(nova)
    mostrar_tabela(base, nova, acertos_base, acertos_nova)

    # Mostra os números que levaram à decisão, para ela nunca ser uma "caixa-preta".
    ganhos, perdas = contar_mudancas(acertos_base, acertos_nova)
    minimo = "não exigido" if neutra else MINIMO_GANHOS
    print(f"\nRégua: {'neutra (trava de segurança)' if neutra else 'normal'}")
    print(f"Ganhos (viraram estável ✓): {len(ganhos)} {ganhos}  | mínimo {minimo}")
    print(f"Perdas (deixaram de ser estável ✓): {len(perdas)} {perdas}  | máximo {MAXIMO_PERDAS}")

    decisao = versao_aprovada(acertos_base, acertos_nova, neutra=neutra)
    print(f"Decisão: {'APROVAR ' + nova if decisao else 'MANTER ' + base}")

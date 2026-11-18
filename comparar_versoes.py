# Compara duas versões do agente caso a caso e decide se a nova pode ser aprovada.
# Execução:  .venv\Scripts\python comparar_versoes.py v2 v3
#
# Usa só as execuções no protocolo de 3 ordens (original, invertida, girada)
# e, de cada versão, a execução MAIS RECENTE gravada em resultados/resultados.csv.
#
# A função versao_aprovada() é a regra que transforma os números em decisão
# (escrita em 16/10 e ampliada com a régua neutra, 17/10, e a dirigida, 23/10).
# Uso: comparar_versoes.py BASE NOVA [--neutra | --alvo CASO]

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
    # Máximo possível = 3 ordens por caso (45 nos 15 casos de ajuste; 15 nos 5 ocultos).
    maximo = 3 * len(acertos_base)
    print(f"{'Total':<6}{sum(acertos_base.values()):>5}/{maximo}"
          f"{sum(acertos_nova.values()):>5}/{maximo}")


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
MINIMO_SUBIDA_ALVO = 2   # régua dirigida: ordens que o caso-alvo precisa ganhar


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


def versao_aprovada(acertos_base, acertos_nova, neutra=False, alvo=None):
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
    é decidido ANTES de rodar o benchmark, nunca depois de ver o resultado.

    Régua dirigida (alvo="C08", regra de 23/10): para uma mudança que mira UM
    caso, declarado antes de rodar. Um caso só dificilmente chega a 3/3, então
    a condição 2 vira "o caso-alvo subiu pelo menos MINIMO_SUBIDA_ALVO ordens";
    a 1 e a 3 continuam valendo."""
    ganhos, perdas = contar_mudancas(acertos_base, acertos_nova)
    total_base = sum(acertos_base.values())
    total_nova = sum(acertos_nova.values())

    if alvo is not None:
        subida = acertos_nova.get(alvo, 0) - acertos_base.get(alvo, 0)
        condicoes = [
            len(perdas) <= MAXIMO_PERDAS,
            subida >= MINIMO_SUBIDA_ALVO,
            total_nova >= total_base,
        ]
    elif neutra:
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
    # Força a saída em UTF-8. Sem isto, ao gravar a saída num arquivo
    # (ex.: comparar_versoes.py v7 v8 > saida.txt), o Windows usa a codificação
    # antiga cp1252, que não tem o símbolo ✓, e o script para com UnicodeEncodeError.
    sys.stdout.reconfigure(encoding="utf-8")

    # sys.argv = palavras digitadas no terminal. Ex.: comparar_versoes.py v4 v7 --neutra
    #   -> ["comparar_versoes.py", "v4", "v7", "--neutra"]
    uso = ("Uso: .venv\\Scripts\\python comparar_versoes.py VERSAO_BASE VERSAO_NOVA "
           "[--neutra | --alvo CASO]")
    argumentos = sys.argv[1:]
    neutra = "--neutra" in argumentos        # True se a palavra foi digitada
    alvo = None
    if "--alvo" in argumentos:
        posicao = argumentos.index("--alvo")
        if posicao + 1 >= len(argumentos):   # "--alvo" sem o caso depois
            sys.exit(uso)
        alvo = argumentos.pop(posicao + 1)   # tira o caso da lista e guarda
    versoes = [a for a in argumentos if a not in ("--neutra", "--alvo")]
    if len(versoes) != 2 or (neutra and alvo):
        sys.exit(uso)
    base, nova = versoes

    acertos_base = acertos_por_caso(base)
    acertos_nova = acertos_por_caso(nova)
    if alvo is not None and alvo not in acertos_base:
        sys.exit(f"Caso-alvo {alvo!r} não existe nos resultados da versão {base!r}.")
    mostrar_tabela(base, nova, acertos_base, acertos_nova)

    # Mostra os números que levaram à decisão, para ela nunca ser uma "caixa-preta".
    ganhos, perdas = contar_mudancas(acertos_base, acertos_nova)
    if alvo is not None:
        nome_regua = f"dirigida (caso-alvo {alvo})"
    elif neutra:
        nome_regua = "neutra (trava de segurança)"
    else:
        nome_regua = "normal"
    minimo = "não exigido" if (neutra or alvo) else MINIMO_GANHOS
    print(f"\nRégua: {nome_regua}")
    print(f"Ganhos (viraram estável ✓): {len(ganhos)} {ganhos}  | mínimo {minimo}")
    print(f"Perdas (deixaram de ser estável ✓): {len(perdas)} {perdas}  | máximo {MAXIMO_PERDAS}")
    if alvo is not None:
        subida = acertos_nova.get(alvo, 0) - acertos_base[alvo]
        print(f"Caso-alvo {alvo}: {acertos_base[alvo]}/3 -> {acertos_nova.get(alvo, 0)}/3 "
              f"(subiu {subida})  | mínimo {MINIMO_SUBIDA_ALVO}")

    decisao = versao_aprovada(acertos_base, acertos_nova, neutra=neutra, alvo=alvo)
    print(f"Decisão: {'APROVAR ' + nova if decisao else 'MANTER ' + base}")

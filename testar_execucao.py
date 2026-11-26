# Testes das regras da execução (execucao.py), SEM rodar o modelo, SEM Ollama e
# SEM gravar no CSV.
# Execução:  .venv\Scripts\python testar_execucao.py
#
# Testa duas funções de execucao.py: ler_progresso() e pode_executar().
# Cada verificação roda dentro de try/except: se a função ainda não foi escrita
# (NotImplementedError), a verificação vira FALHA e o teste segue adiante.

import sys

import ambiente
from benchmark import rotulo_invalido
from execucao import ler_progresso, pode_executar

resultados = []   # lista de (descrição, passou)


def verificar(descricao, funcao):
    """Roda `funcao` (que devolve True/False); qualquer exceção conta como FALHA."""
    try:
        ok = bool(funcao())
    except Exception:
        ok = False
    resultados.append((descricao, ok))
    print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")


def motivo_contem(motivo, *trechos):
    """True se o motivo é um texto que contém todos os trechos."""
    return isinstance(motivo, str) and all(t in motivo for t in trechos)


CABECALHO = "15 casos carregados de casos/casos.json; 3 ordens; 45 execuções\n"
L1 = "[ 1/45] C01 #1 (original) -> registrar (2.8 s)"
L2 = "[ 2/45] C02 #1 (original) -> perguntar (3.1 s)"
L3 = "[ 3/45] C03 #1 (original) -> registrar (2.5 s)"
L7 = "[ 7/45] C07 #1 (original) -> ignorar (1.9 s)"

# --- ler_progresso ---
verificar("ler_progresso('') == (0, 0)",
          lambda: ler_progresso("") == (0, 0))
verificar("só o cabeçalho, sem progresso, == (0, 0)",
          lambda: ler_progresso(CABECALHO) == (0, 0))
verificar("3 linhas de progresso == (3, 45)",
          lambda: ler_progresso(CABECALHO + "\n".join([L1, L2, L3]) + "\n") == (3, 45))
verificar("fim do benchmark (45/45 e linhas finais) == (45, 45)",
          lambda: ler_progresso(
              CABECALHO + L1 + "\n[45/45] C15 #3 (girada) -> registrar (2.7 s)\n"
              "Respostas salvas em resultados/brutos_v15.json\n"
              "Resultados acrescentados em resultados/resultados.csv\n"
              "Acerto geral: 44/45 (98%)\n") == (45, 45))
verificar("última linha cortada '[ 8/4' é ignorada == (7, 45)",
          lambda: ler_progresso(L1 + "\n" + L7 + "\n[ 8/4") == (7, 45))
verificar("acentos e quebras \\r\\n do Windows",
          lambda: ler_progresso(
              "Execução iniciada: ação, não, coração\r\n" + L1 + "\r\n" + L2 + "\r\n")
          == (2, 45))

# --- pode_executar ---
V = ambiente.VERSAO_OLLAMA
verificar("tudo certo devolve None",
          lambda: pode_executar(V, "v15-repeticao", 0) is None)
verificar("em_andamento=True bloqueia (motivo com 'andamento')",
          lambda: motivo_contem(
              pode_executar(V, "v15-repeticao", 0, em_andamento=True), "andamento"))
verificar("Ollama desligado (None): 'não está ligado'",
          lambda: motivo_contem(
              pode_executar(None, "v15-repeticao", 0), "não está ligado"))
verificar("Ollama desligado: o motivo cita a versão exigida",
          lambda: motivo_contem(pode_executar(None, "v15-repeticao", 0), V))
verificar("versão errada: cita a encontrada e a exigida",
          lambda: motivo_contem(
              pode_executar("0.40.13", "v15-repeticao", 0), "0.40.13", V))
verificar("rótulo 'a b': motivo igual ao de rotulo_invalido",
          lambda: pode_executar(V, "a b", 0) == rotulo_invalido("a b"))
verificar("rótulo 'v15-oculto' é recusado",
          lambda: pode_executar(V, "v15-oculto", 0) is not None)
verificar("rótulo já gravado (45 linhas): cita rótulo, 45 e 'outro'",
          lambda: motivo_contem(pode_executar(V, "v15", 45), "v15", "45", "outro"))
verificar("ordem: Ollama desligado e rótulo inválido -> motivo do Ollama",
          lambda: motivo_contem(pode_executar(None, "a b", 0), "não está ligado"))

# --- relatório ---
passaram = sum(1 for _, ok in resultados if ok)
print(f"\n{passaram}/{len(resultados)} verificações passaram")
sys.exit(0 if passaram == len(resultados) else 1)

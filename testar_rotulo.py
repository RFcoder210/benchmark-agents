# Testes das opções da linha de comando do benchmark (--rotulo e --ocultos),
# SEM rodar o modelo, SEM Ollama e SEM gravar no CSV.
# Execução:  .venv\Scripts\python testar_rotulo.py
#
# Testa duas funções de benchmark.py: rotulo_invalido() e escolher_execucao().
# Cada verificação roda dentro de try/except: se a função ainda não foi escrita
# (NotImplementedError), a verificação vira FALHA e o teste segue adiante.

import contextlib
import io
import sys

from benchmark import (ARQUIVO_CASOS, ARQUIVO_CASOS_OCULTOS, VERSAO_AGENTE,
                       escolher_execucao, rotulo_invalido)

resultados = []   # lista de (descrição, passou)


def verificar(descricao, funcao):
    """Roda `funcao` (que devolve True/False); qualquer exceção conta como FALHA."""
    try:
        ok = bool(funcao())
    except Exception:
        ok = False
    resultados.append((descricao, ok))
    print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")


def sai_com_codigo_2(argv):
    """True se escolher_execucao(argv) termina com SystemExit de código 2."""
    try:
        # O argparse escreve a mensagem de erro em stderr; aqui ela é silenciada.
        with contextlib.redirect_stderr(io.StringIO()):
            escolher_execucao(argv)
    except SystemExit as erro:
        return erro.code == 2
    return False


# --- rotulo_invalido: rótulos que servem ---
for rotulo in ["v15-repeticao", "v2-t0.7", "v16", "v15_teste", "a" * 40]:
    verificar(f"rotulo_invalido({rotulo[:20]!r}) é None",
              lambda r=rotulo: rotulo_invalido(r) is None)

# --- rotulo_invalido: rótulos que não servem (devolve um texto não vazio) ---
for rotulo in ["", " ", " v15", "v15 repeticao", "v15;x", "v15/x", "v15\\x",
               "versão", "v15-oculto", "a" * 41]:
    def confere(r=rotulo):
        motivo = rotulo_invalido(r)
        return isinstance(motivo, str) and motivo != ""
    verificar(f"rotulo_invalido({rotulo[:20]!r}) devolve o motivo", confere)

# --- escolher_execucao: caminhos felizes ---
verificar("sem opções: casos de ajuste e a versão do agente",
          lambda: escolher_execucao([]) == (ARQUIVO_CASOS, VERSAO_AGENTE))
verificar("--rotulo X (dois argumentos)",
          lambda: escolher_execucao(["--rotulo", "v15-repeticao"])
          == (ARQUIVO_CASOS, "v15-repeticao"))
verificar("--rotulo=X (um argumento)",
          lambda: escolher_execucao(["--rotulo=v15-repeticao"])
          == (ARQUIVO_CASOS, "v15-repeticao"))
verificar("--ocultos: conjunto oculto com rótulo fixo",
          lambda: escolher_execucao(["--ocultos"])
          == (ARQUIVO_CASOS_OCULTOS, VERSAO_AGENTE + "-oculto"))

# --- escolher_execucao: erros do argparse (SystemExit 2) ---
for argv in [["--rotulo"], ["--rotulo", "a b"], ["--rotulo", "v15-oculto"],
             ["--ocultos", "--rotulo", "x"], ["--desconhecida"]]:
    verificar(f"{' '.join(argv)} termina com erro (código 2)",
              lambda a=argv: sai_com_codigo_2(a))


# --- escolher_execucao() sem argumentos lê sys.argv ---
def le_sys_argv():
    original = sys.argv
    sys.argv = ["benchmark.py"]
    try:
        return escolher_execucao() == (ARQUIVO_CASOS, VERSAO_AGENTE)
    finally:
        sys.argv = original   # sempre devolve o sys.argv original


verificar("argv=None usa sys.argv", le_sys_argv)

if __name__ == "__main__":
    passaram = sum(1 for _, ok in resultados if ok)
    print(f"\n{passaram}/{len(resultados)} verificações passaram")
    sys.exit(0 if passaram == len(resultados) else 1)

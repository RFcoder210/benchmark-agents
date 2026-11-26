# Testes do lançamento em segundo plano (execucao.py), SEM modelo, SEM Ollama e
# SEM CSV: usam comandos falsos. Execução:  .venv\Scripts\python testar_processo.py

import os
import sys
import tempfile
import time

from execucao import iniciar, montar_comando, situacao

resultados = []   # lista de (descrição, passou)


def verificar(descricao, funcao):
    """Roda `funcao` (devolve True/False); qualquer exceção conta como FALHA."""
    try:
        ok = bool(funcao())
    except Exception:
        ok = False
    resultados.append((descricao, ok))
    print(f"  {'OK   ' if ok else 'FALHA'} {descricao}")


# Comando falso (sem "-u" de propósito): imprime acento, 3 linhas de progresso
# com pausa entre elas e a linha final.
SCRIPT_OK = (
    "import time\n"
    "print('1 execução por ordem')\n"
    "for i in (1, 2, 3):\n"
    "    print(f'[ {i}/3] C01 #1 (original) -> registrar (0.1 s)')\n"
    "    time.sleep(0.5)\n"
    "print('Acerto geral: 3/3 (100%)')\n"
)
SCRIPT_FALHA = (
    "print('[ 1/3] C01 #1 (original) -> registrar (0.1 s)')\n"
    "raise RuntimeError('falha simulada')\n"
)
FALSO_OK = [sys.executable, "-c", SCRIPT_OK]
FALSO_FALHA = [sys.executable, "-c", SCRIPT_FALHA]


def esperar(execucao, limite=30):
    """Consulta a cada 0,1 s até terminar; devolve todas as situações vistas."""
    vistas = []
    fim = time.time() + limite
    while time.time() < fim:
        s = situacao(execucao)
        vistas.append(s)
        if not s["rodando"]:
            break
        time.sleep(0.1)
    execucao["processo"].wait(timeout=10)
    return vistas


with tempfile.TemporaryDirectory() as pasta:
    # --- execução bem-sucedida ---
    exe = iniciar("teste-ok", comando=FALSO_OK, pasta_logs=pasta)
    rodando_logo = situacao(exe)["rodando"]
    vistas = esperar(exe)
    final = situacao(exe)
    verificar("logo após iniciar(), rodando é True", lambda: rodando_logo is True)
    verificar("progresso parcial visto durante a execução (0 < feitas < 3)",
              lambda: any(s["rodando"] and 0 < s["feitas"] < 3 for s in vistas))
    verificar("no fim: rodando falso e código de saída 0",
              lambda: final["rodando"] is False and final["codigo_saida"] == 0)
    verificar("no fim: (feitas, total) == (3, 3)",
              lambda: (final["feitas"], final["total"]) == (3, 3))
    verificar("acerto == 'Acerto geral: 3/3 (100%)'",
              lambda: final["acerto"] == "Acerto geral: 3/3 (100%)")
    verificar("log contém 'execução' com acento correto",
              lambda: "execução" in open(exe["log"], encoding="utf-8").read())

    # --- execução que falha ---
    exe2 = iniciar("teste-falha", comando=FALSO_FALHA, pasta_logs=pasta)
    esperar(exe2)
    s2 = situacao(exe2)
    verificar("comando que falha: código de saída diferente de 0",
              lambda: s2["codigo_saida"] != 0)
    verificar("'falha simulada' aparece em ultimas_linhas",
              lambda: any("falha simulada" in l for l in s2["ultimas_linhas"]))

    # --- rótulo inválido ---
    antes = set(os.listdir(pasta))

    def rotulo_ruim():
        try:
            iniciar("a b", comando=FALSO_OK, pasta_logs=pasta)
        except ValueError:
            return True
        return False

    verificar("iniciar('a b') levanta ValueError", rotulo_ruim)
    verificar("rótulo inválido não cria log", lambda: set(os.listdir(pasta)) == antes)

# --- montar_comando ---
cmd = montar_comando("v15-repeticao")
verificar("montar_comando: começa com sys.executable e tem '-u'",
          lambda: cmd[0] == sys.executable and "-u" in cmd)
verificar("montar_comando: benchmark.py antes de '--rotulo' e do rótulo",
          lambda: cmd[cmd.index("-u") + 1].endswith("benchmark.py")
          and cmd[-2:] == ["--rotulo", "v15-repeticao"])
verificar("montar_comando: não contém '--ocultos'",
          lambda: "--ocultos" not in cmd)

total = len(resultados)
passou = sum(1 for _, ok in resultados if ok)
print(f"\n{passou}/{total} verificações passaram")
sys.exit(0 if passou == total else 1)

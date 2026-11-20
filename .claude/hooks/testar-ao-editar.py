"""testar-ao-editar.py — "Inspetor de linha de montagem" (hook PostToolUse).

Quando roda: logo depois de o Claude editar ou criar um arquivo (Edit e Write).

O que faz (em linguagem simples):
    Olha qual arquivo mudou e roda só os testes ligados a ele, todos SEM o
    modelo (não precisam do Ollama ligado e não gravam no CSV):

        agente.py            -> testar_trava_pagamento.py
        benchmark.py         -> testar_comparar.py, testar_mutacao.py, testar_executar.py
        comparar_versoes.py  -> testar_regua.py, testar_dashboard.py
        dashboard.py         -> testar_dashboard.py
        app.py               -> testar_dashboard.py, testar_executar.py
        app_pages/*.py       -> testar_executar.py
        testar_*.py          -> o próprio teste (menos o testar_classificador.py,
                                que chama o modelo)

    Se algum teste falhar, o Claude recebe o final da saída do teste na hora,
    em vez de descobrir o erro só ao rodar o benchmark. Se todos passarem,
    recebe uma linha curta dizendo quais rodaram.

Analogia: o inspetor confere cada peça assim que ela sai da máquina, em vez de
esperar o carro inteiro ficar pronto para descobrir o defeito.

Custo: zero de cota (são scripts locais); de 1 a 20 segundos por edição.
Observação: numa etapa em que o teste é escrito ANTES do código (teste
"vermelho" de propósito), a falha avisada aqui é a esperada.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Testes que chamam o modelo: nunca rodam aqui.
COM_MODELO = {"testar_classificador.py"}

# Arquivo editado -> testes ligados a ele.
MAPA = {
    "agente.py": ["testar_trava_pagamento.py"],
    "benchmark.py": ["testar_comparar.py", "testar_mutacao.py", "testar_executar.py"],
    "comparar_versoes.py": ["testar_regua.py", "testar_dashboard.py"],
    "dashboard.py": ["testar_dashboard.py"],
    "app.py": ["testar_dashboard.py", "testar_executar.py"],
}

LIMITE_SEGUNDOS = 120
LINHAS_DO_ERRO = 40


def raiz_do_projeto(entrada):
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    if entrada.get("cwd"):
        return Path(entrada["cwd"])
    return Path(__file__).resolve().parent.parent.parent


def testes_para(caminho, raiz):
    """Descobre quais testes rodar para o arquivo editado."""
    try:
        relativo = Path(caminho).resolve().relative_to(raiz.resolve())
    except ValueError:
        return []  # arquivo fora do projeto
    partes = relativo.parts
    nome = relativo.name

    if len(partes) == 1 and nome in MAPA:
        return MAPA[nome]
    if len(partes) == 2 and partes[0] == "app_pages" and nome.endswith(".py"):
        return ["testar_executar.py"]
    if len(partes) == 1 and nome.startswith("testar_") and nome.endswith(".py") and nome not in COM_MODELO:
        return [nome]
    return []


def rodar(teste, raiz):
    """Roda um teste com o Python do .venv e devolve (passou, saída)."""
    python = raiz / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        return True, "(sem .venv: teste não rodado)"
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run(
            [str(python), teste],
            cwd=raiz,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=ambiente,
            timeout=LIMITE_SEGUNDOS,
        )
    except subprocess.TimeoutExpired:
        return False, f"passou de {LIMITE_SEGUNDOS} s e foi interrompido"
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def main():
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return 0
    caminho = (entrada.get("tool_input") or {}).get("file_path")
    if not caminho:
        return 0

    raiz = raiz_do_projeto(entrada)
    testes = testes_para(caminho, raiz)
    if not testes:
        return 0

    falhas = []
    for teste in testes:
        passou, saida = rodar(teste, raiz)
        if not passou:
            final = "\n".join(saida.splitlines()[-LINHAS_DO_ERRO:])
            falhas.append(f"--- {teste} FALHOU ---\n{final}")

    if falhas:
        sys.stderr.reconfigure(encoding="utf-8")
        print(
            f"Testes sem modelo após editar {Path(caminho).name}:\n" + "\n\n".join(falhas),
            file=sys.stderr,
        )
        return 2

    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": f"Testes sem modelo passaram após editar {Path(caminho).name}: {', '.join(testes)}.",
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""fiscal-executor.py — "Fiscal da obra" sem custo de cota (hook SubagentStop).

Quando roda: quando o subagente executor-tarefa tenta encerrar (matcher no settings.json).

O que faz (em linguagem simples):
    Só olha relatórios "STATUS: CONCLUIDA". Pendências passam direto.
    1. Confere se o campo VERIFICACAO está preenchido (laudo assinado).
    2. Abre a ordem de serviço (TAREFA: Txx), lê a seção "## Não alterar" e, se o
       projeto usa git, confere se algum desses arquivos foi modificado
       (régua de medição adulterada).
    Se achar problema, impede o encerramento e devolve ao executor o motivo.
    Bloqueia no máximo UMA vez por encerramento (stop_hook_active), para nunca
    virar um loop que consome a cota.

Analogia: o fiscal fica na porta da obra. Não confere cada tijolo, mas ninguém
sai sem laudo nem com a régua de medição mexida.

Custo: zero de cota. Limite: sem git, só o item 1 é conferido.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def arquivos_protegidos(arq_tarefa):
    protegidos, na_secao = [], False
    for linha in arq_tarefa.read_text(encoding="utf-8-sig").splitlines():
        if linha.startswith("## "):
            na_secao = bool(re.match(r"##\s+N[ãa]o alterar", linha, re.IGNORECASE))
            continue
        m = re.match(r"\s*[-*]\s+(.+)$", linha)
        if na_secao and m:
            item = m.group(1).strip().strip("`").strip()
            if item and not item.startswith("(") and not item.lower().startswith("nenhum"):
                protegidos.append(item)
    return protegidos


def alterados_no_git(raiz, arquivos):
    try:
        dentro = subprocess.run(["git", "-C", raiz, "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True)
    except OSError:
        return None  # git não instalado
    if dentro.returncode != 0:
        return None  # projeto sem git
    alterados = []
    for arq in arquivos:
        r = subprocess.run(["git", "-C", raiz, "status", "--porcelain", "--", arq],
                           capture_output=True, text=True)
        if r.stdout.strip():
            alterados.append(arq)
    return alterados


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return 0

    if entrada.get("stop_hook_active"):
        return 0  # segunda passagem depois de um bloqueio: deixa sair
    tipo = entrada.get("agent_type")
    if tipo and "executor-tarefa" not in tipo:
        return 0  # segurança extra, caso o matcher seja removido
    msg = str(entrada.get("last_assistant_message") or "")
    if not re.search(r"STATUS:\s*CONCLUIDA", msg):
        return 0  # só fiscaliza quem declara conclusão

    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or entrada.get("cwd")
    problemas = []

    m = re.search(r"^\s*VERIFICACAO:[ \t]*(.*)$", msg, re.MULTILINE)
    verif = m.group(1).strip() if m else ""
    if not verif or verif.startswith("(") or len(verif) < 5:
        problemas.append(
            "O campo VERIFICACAO está vazio. Rode a verificação do critério de pronto da tarefa e "
            "informe o comando executado e o resultado obtido."
        )

    m = re.search(r"TAREFA:\s*(T[0-9]+[A-Za-z]?)", msg)
    if raiz and m:
        pasta = Path(raiz) / ".plano" / "tarefas"
        candidatos = sorted(pasta.glob(f"{m.group(1)}-*.md")) or sorted(pasta.glob(f"{m.group(1)}.md"))
        if candidatos:
            protegidos = arquivos_protegidos(candidatos[0])
            if protegidos:
                alterados = alterados_no_git(raiz, protegidos)
                if alterados:
                    problemas.append(
                        f'Arquivos da seção "Não alterar" foram modificados: {", ".join(alterados)}. '
                        "Reverta a alteração ou declare PENDENTE explicando por que eles precisam mudar. "
                        "Se a alteração já existia antes desta tarefa, diga isso no campo FEITO."
                    )

    if problemas:
        print(json.dumps({"decision": "block", "reason": "Fiscal automático: " + " ".join(problemas)},
                         ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

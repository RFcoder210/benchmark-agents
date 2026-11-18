"""arquivar-retomada.py — Guarda o bilhete de retomada anterior (sem tokens).

Quando roda: chamado pelo orquestrador no início do Checkpoint (seção Checkpoint
de .claude/skills/encerrar-dia/SKILL.md), ANTES de escrever a nova RETOMADA.md.

O que faz:
    Copia .plano/RETOMADA.md para .plano/historico/, com a data e a hora em que
    ela foi escrita no nome, e mantém só as 10 mais recentes. O histórico de
    retomadas é o diário do projeto.

Por que é um script e não um agente: copiar e apagar arquivos não exige
raciocínio. Trabalho mecânico não deve gastar cota.

Uso: py -3 .claude/hooks/arquivar-retomada.py
"""
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

MANTER = 10


def raiz_do_projeto():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent.parent


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    plano = raiz_do_projeto() / ".plano"
    retomada = plano / "RETOMADA.md"
    if not retomada.exists():
        print("Sem RETOMADA.md anterior: nada a arquivar.")
        return 0

    hist = plano / "historico"
    hist.mkdir(parents=True, exist_ok=True)
    quando = datetime.fromtimestamp(retomada.stat().st_mtime).strftime("%Y-%m-%d-%H%M")
    shutil.copy2(retomada, hist / f"RETOMADA-{quando}.md")

    # Mantém só as mais recentes (apaga apenas dentro de .plano/historico)
    antigas = sorted(hist.glob("RETOMADA-*.md"), key=lambda a: a.name, reverse=True)[MANTER:]
    for a in antigas:
        a.unlink()

    print(f"Retomada anterior arquivada em .plano/historico/RETOMADA-{quando}.md "
          f"({len(antigas)} removida(s) por excesso).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

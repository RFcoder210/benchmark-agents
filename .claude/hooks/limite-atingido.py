"""limite-atingido.py — "Caixa-preta" da interrupção por limite (hook StopFailure).

Quando roda: quando uma resposta é interrompida porque o limite de uso acabou
(evento StopFailure, tipo rate_limit).

Por que é um script e não um agente: com o limite esgotado, nenhum agente
consegue trabalhar. Um script, que não gasta tokens, ainda consegue anotar.

O que faz:
    Acrescenta ao final de .plano/RETOMADA.md um aviso com data, hora e a
    previsão de renovação, e registra a interrupção em .plano/estado/interrupcoes.log.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
    except (ValueError, UnicodeDecodeError):
        entrada = {}
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or entrada.get("cwd")
    if not raiz:
        return 0
    plano = Path(raiz) / ".plano"
    if not plano.is_dir():
        return 0

    renovacao = "desconhecida"
    try:
        uso = json.loads((plano / "estado" / "uso.json").read_text(encoding="utf-8-sig"))
        p5, ps = uso.get("janela_5h_pct"), uso.get("semanal_pct")
        if ps is None or (p5 is not None and float(p5) >= float(ps)):
            if uso.get("janela_5h_renova_hora"):
                renovacao = "janela de 5 h renova às " + uso["janela_5h_renova_hora"]
        elif uso.get("semanal_renova_data"):
            renovacao = "cota semanal renova em " + uso["semanal_renova_data"]
    except (OSError, ValueError):
        pass

    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    bloco = (
        "\n## ⚠ Interrupção por limite de uso\n"
        f"- Momento: {agora}\n"
        f"- Renovação prevista: {renovacao}\n"
        "- A sessão parou no meio do trabalho. Tarefas marcadas como EM_ANDAMENTO em\n"
        "  .plano/ESTADO.md podem estar incompletas: conferir antes de retomar.\n"
    )
    try:
        with open(plano / "RETOMADA.md", "a", encoding="utf-8") as f:
            f.write(bloco)
    except OSError:
        pass
    try:
        (plano / "estado").mkdir(parents=True, exist_ok=True)
        with open(plano / "estado" / "interrupcoes.log", "a", encoding="utf-8") as f:
            f.write(f"{agora} | limite de uso | {renovacao}\n")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

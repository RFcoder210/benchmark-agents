"""verificar-uso.py — "Sentinela" de consumo (hook).

Quando roda:
    - UserPromptSubmit: toda vez que você envia uma mensagem;
    - PostToolUse (Agent|SendMessage): toda vez que o orquestrador aciona ou
      retoma um subagente.

O que faz:
    Lê .plano/estado/uso.json e, se algum limite passou do nível de alerta,
    entrega ao orquestrador um aviso de contexto. Cada aviso é dado UMA vez por
    nível e por janela, para não repetir (estado em .plano/estado/alertas.json).

Níveis (ajuste nas constantes abaixo):
    janela de 5 h : 80% = checkpoint preventivo | 85% = encerrar o dia (reserva para o relatório semanal)
    semana        : 85% = reduzir o ritmo       | 93% = encerrar o dia (reserva para o relatório semanal)
    contexto      : 70% do orçamento de 200 mil tokens = checkpoint + compactar
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ALERTA_5H = 80
CRITICO_5H = 85      # era 90; reserva cota para o relatório semanal em PDF (27/11/2026)
ALERTA_SEMANA = 85
CRITICO_SEMANA = 93  # era 95; mesma reserva
ALERTA_CTX = 70
REARME_CTX = 45     # abaixo disto (ex.: após compactar) o alerta de contexto é rearmado
VALIDADE_MIN = 360  # medições com mais de 6 h são ignoradas

SKILL = ".claude/skills/encerrar-dia/SKILL.md"


def ler_json(caminho):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return 0
    evento = entrada.get("hook_event_name")
    if not evento:
        return 0
    # Hooks disparados DENTRO de um subagente trazem agent_id: o aviso é só do orquestrador
    if entrada.get("agent_id"):
        return 0

    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or entrada.get("cwd")
    if not raiz:
        return 0
    pasta = Path(raiz) / ".plano" / "estado"
    uso = ler_json(pasta / "uso.json")
    if not uso:
        return 0

    try:
        idade = (datetime.now() - datetime.fromisoformat(uso["atualizado_em"])).total_seconds() / 60
    except (KeyError, TypeError, ValueError):
        return 0
    if idade > VALIDADE_MIN:
        return 0

    lido = ler_json(pasta / "alertas.json") or {}
    estado = {
        "janela5h": str(lido.get("janela5h", "")),
        "niveis5h": list(lido.get("niveis5h") or []),
        "janelaSem": str(lido.get("janelaSem", "")),
        "niveisSem": list(lido.get("niveisSem") or []),
        "ctxAlertado": bool(lido.get("ctxAlertado", False)),
    }

    # Nova janela de uso = zera os alertas daquela janela
    if str(uso.get("janela_5h_renova_epoch")) != estado["janela5h"]:
        estado["janela5h"] = str(uso.get("janela_5h_renova_epoch"))
        estado["niveis5h"] = []
    if str(uso.get("semanal_renova_epoch")) != estado["janelaSem"]:
        estado["janelaSem"] = str(uso.get("semanal_renova_epoch"))
        estado["niveisSem"] = []

    avisos = []

    p = uso.get("janela_5h_pct")
    if p is not None:
        p = float(p)
        renova = uso.get("janela_5h_renova_hora")
        if p >= CRITICO_5H and "critico" not in estado["niveis5h"]:
            avisos.append(
                f"Medidor de uso do projeto: a janela de 5 horas está em {p:.0f}% (renova às {renova}). "
                f"Nível CRÍTICO: pelo protocolo /orquestrar, a próxima ação é o encerramento do dia "
                f"(ler e seguir {SKILL}), sem iniciar novas tarefas."
            )
            estado["niveis5h"] += ["critico", "alerta"]
        elif p >= ALERTA_5H and "alerta" not in estado["niveis5h"]:
            avisos.append(
                f"Medidor de uso do projeto: a janela de 5 horas está em {p:.0f}% (renova às {renova}). "
                f"Nível de ALERTA: pelo protocolo /orquestrar, cabe um checkpoint preventivo "
                f"(seção Checkpoint de {SKILL}) antes da próxima tarefa, e apenas tarefas pequenas até a renovação."
            )
            estado["niveis5h"].append("alerta")

    s = uso.get("semanal_pct")
    if s is not None:
        s = float(s)
        renova = uso.get("semanal_renova_data")
        if s >= CRITICO_SEMANA and "critico" not in estado["niveisSem"]:
            avisos.append(
                f"Medidor de uso do projeto: a cota semanal está em {s:.0f}% (renova em {renova}). "
                f"Nível CRÍTICO: pelo protocolo, encerra-se o dia (ler e seguir {SKILL}) "
                f"e o cronograma é refeito até a renovação."
            )
            estado["niveisSem"] += ["critico", "alerta"]
        elif s >= ALERTA_SEMANA and "alerta" not in estado["niveisSem"]:
            avisos.append(
                f"Medidor de uso do projeto: a cota semanal está em {s:.0f}% (renova em {renova}). "
                f"Pelo protocolo, o agente cronograma redistribui as tarefas restantes considerando a cota."
            )
            estado["niveisSem"].append("alerta")

    c = uso.get("contexto_pct")
    if c is not None:
        c = float(c)
        if c < REARME_CTX:
            estado["ctxAlertado"] = False
        if c >= ALERTA_CTX and not estado["ctxAlertado"]:
            avisos.append(
                f"Medidor de uso do projeto: o contexto desta conversa está em {c:.0f}% do orçamento de "
                f"200 mil tokens. Pelo protocolo, faça a seção Checkpoint de {SKILL} (motivo \"antes de "
                f"compactar\") e oriente o usuário a executar /compact; a retomada é recarregada sozinha."
            )
            estado["ctxAlertado"] = True

    try:
        (pasta / "alertas.json").write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    if avisos:
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": evento, "additionalContext": "\n".join(avisos)}
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

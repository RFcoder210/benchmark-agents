"""iniciar-sessao.py — Carrega SOMENTE o contexto de retomada (hook SessionStart).
Versão própria do benchmark-agents (porte para Python, em 17/11/2026, do iniciar-sessao.ps1 do projeto).

Neste projeto não se usa a orquestração (/orquestrar): o estado duradouro fica na seção
"Estado atual" do CLAUDE.md e o bilhete do dia em .plano/RETOMADA.md, gravado pela skill
/encerrar-dia. A rotina é uma sessão por dia, nomeada "Dia N · DD/MM · foco", com o
registro dos dias em .plano/DIARIO.md.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

LIMITE_CARACTERES = 7000  # o Claude Code aceita até 10.000 por hook
DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def numero_do_dia(diario, hoje):
    """N vem da última linha de .plano/DIARIO.md: mesma data = mesmo dia; senão, o próximo."""
    if not diario.exists():
        return 1, False
    linhas = [l for l in diario.read_text(encoding="utf-8-sig").splitlines()
              if l.startswith("|") and l.split("|")[1].strip().isdigit()]
    if not linhas:
        return 1, False
    partes = linhas[-1].split("|")
    ultimo, data = int(partes[1].strip()), partes[2].strip()
    return (ultimo, True) if data == hoje else (ultimo + 1, False)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
    except (ValueError, UnicodeDecodeError):
        entrada = {}
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or entrada.get("cwd")
    if not raiz:
        return 0
    origem = str(entrada.get("source") or "")
    agora = datetime.now()
    plano = Path(raiz) / ".plano"
    linhas = [f"Data atual: {agora:%Y-%m-%d} ({DIAS[agora.weekday()]}), {agora:%H:%M}."]

    if origem == "compact":
        linhas.append("A conversa acabou de ser compactada. O estado duradouro do projeto está na seção 'Estado atual' do CLAUDE.md.")

    retomada = plano / "RETOMADA.md"
    if retomada.exists():
        texto = retomada.read_text(encoding="utf-8-sig").strip() or "(arquivo vazio)"
        if len(texto) > LIMITE_CARACTERES:
            texto = texto[:LIMITE_CARACTERES] + "\n[... RETOMADA.md truncado; ler o arquivo completo se necessário ...]"
        linhas += ["Contexto de retomada do projeto (conteúdo de .plano/RETOMADA.md):", "-----", texto, "-----"]
    else:
        linhas.append("Não há .plano/RETOMADA.md; o estado do projeto está na seção 'Estado atual' do CLAUDE.md.")

    try:
        uso = json.loads((plano / "estado" / "uso.json").read_text(encoding="utf-8-sig"))
        quando = uso.get("atualizado_em", "")
        try:
            quando = datetime.fromisoformat(quando).strftime("%d/%m %H:%M")
        except (TypeError, ValueError):
            pass
        p5 = f"{uso['janela_5h_pct']}%" if uso.get("janela_5h_pct") is not None else "n/d"
        ps = f"{uso['semanal_pct']}%" if uso.get("semanal_pct") is not None else "n/d"
        linhas.append(f"Última medição de uso registrada ({quando}): janela 5h {p5}, semana {ps}.")
    except (OSError, ValueError):
        pass

    n, ja = numero_do_dia(plano / "DIARIO.md", f"{agora:%Y-%m-%d}")
    sufixo = " (2)" if ja else ""
    linhas.append(
        f"Nome da sessão: se o título atual não segue o padrão, renomeie-a logo no início com set_session_title "
        f"(session_id 'self') para 'Dia {n} · {agora:%d/%m} · <foco em 2 a 5 palavras>{sufixo}', com o foco tirado "
        f"da 'Próxima ação'. Se for um dia novo, acrescente a linha do Dia {n} em .plano/DIARIO.md."
    )
    linhas.append("Rotina: uma sessão por dia. Comece pela 'Próxima ação' da retomada; ao terminar o dia, o usuário digita /encerrar-dia.")
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""gravar-uso.py — Grava o medidor de uso quando o projeto roda no app desktop.

Por que existe (em linguagem simples):
    No app desktop a barra de status (statusline-uso.py) não roda, então
    .plano/estado/uso.json não se atualiza sozinho. O orquestrador lê o uso com a
    ferramenta get_usage e chama ESTE script, que grava o mesmo arquivo, no mesmo
    formato. Assim o sentinela (verificar-uso.py) funciona sem mudança.

Analogia: o marcador do painel não acende; alguém lê o nível na bomba e anota
no mesmo caderno de bordo.

Uso (exemplo):
    py -3 .claude/hooks/gravar-uso.py --cinco 44 --cinco-renova 2026-11-06T21:30:00Z \
        --semana 14 --semana-renova 2026-11-12T17:00:00Z --contexto 23
--contexto é a porcentagem de um orçamento de 200 mil tokens (tokens usados ÷ 2000).
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def para_epoch(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


def raiz_do_projeto():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    # .claude/hooks/gravar-uso.py -> raiz do projeto
    return Path(__file__).resolve().parent.parent.parent


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Grava .plano/estado/uso.json a partir do get_usage.")
    p.add_argument("--cinco", type=float, required=True, help="%% usado da janela de 5 horas")
    p.add_argument("--cinco-renova", required=True, help="resetsAt da janela de 5 horas (ISO 8601)")
    p.add_argument("--semana", type=float, required=True, help="%% usado da janela semanal")
    p.add_argument("--semana-renova", required=True, help="resetsAt da janela semanal (ISO 8601)")
    p.add_argument("--contexto", type=float, default=None, help="%% do orçamento de 200 mil tokens")
    p.add_argument("--sessao", default="app")
    a = p.parse_args(argv)

    e5 = para_epoch(a.cinco_renova)
    es = para_epoch(a.semana_renova)
    agora = datetime.now()
    registro = {
        "atualizado_em": agora.strftime("%Y-%m-%dT%H:%M:%S"),
        "sessao": a.sessao,
        "contexto_pct": a.contexto,
        "janela_5h_pct": a.cinco,
        "janela_5h_renova_epoch": e5,
        "janela_5h_renova_hora": datetime.fromtimestamp(e5).strftime("%H:%M"),
        "semanal_pct": a.semana,
        "semanal_renova_epoch": es,
        "semanal_renova_data": datetime.fromtimestamp(es).strftime("%d/%m %H:%M"),
        "fonte": "app desktop (get_usage) via gravar-uso.py",
    }

    pasta = raiz_do_projeto() / ".plano" / "estado"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "uso.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")

    # Histórico: uma linha por leitura, para calibrar o cronograma no benchmark
    linha = f"{registro['atualizado_em']};5h={a.cinco}%;semana={a.semana}%;contexto={a.contexto}\n"
    with open(pasta / "uso_historico.txt", "a", encoding="utf-8") as f:
        f.write(linha)

    print(
        f"medidor gravado: 5h {a.cinco:g}% (renova {registro['janela_5h_renova_hora']}) | "
        f"semana {a.semana:g}% (renova {registro['semanal_renova_data']}) | contexto {a.contexto}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

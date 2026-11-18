"""statusline-uso.py — Barra de status + "medidor de uso" do projeto (terminal).

O que faz (em linguagem simples):
    O Claude Code chama este script várias vezes durante a sessão e entrega a ele,
    em JSON, o uso do contexto, da janela de 5 horas e da janela semanal.
    O script:
      1) grava esses números em .plano/estado/uso.json, para os outros hooks;
      2) imprime uma linha curta que aparece no rodapé do Claude Code.

Analogia: é o marcador de combustível. Não dirige; mostra quanto resta e anota.

Contexto: medido contra um orçamento fixo de 200 mil tokens (e não contra o
tamanho da janela), porque o custo de cada turno cresce com a quantidade de
tokens. Se o Claude Code não informar o tamanho da janela, usa a porcentagem dele.

Só funciona no terminal: no app desktop a barra de status não roda e quem grava
o medidor é o gravar-uso.py, chamado pelo orquestrador.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ORCAMENTO_CONTEXTO = 200_000


def hora_local(epoch, formato):
    if epoch is None:
        return None
    try:
        return datetime.fromtimestamp(float(epoch)).strftime(formato)
    except (TypeError, ValueError, OSError):
        return None


def pegar(dados, *chaves):
    atual = dados
    for chave in chaves:
        if not isinstance(atual, dict):
            return None
        atual = atual.get(chave)
    return atual


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        dados = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        print("[uso indisponível]")
        return 0

    ctx_pct = pegar(dados, "context_window", "used_percentage")
    tamanho = pegar(dados, "context_window", "context_window_size")
    if ctx_pct is not None and tamanho:
        ctx = round(float(ctx_pct) * float(tamanho) / 100 / ORCAMENTO_CONTEXTO * 100, 1)
    else:
        ctx = ctx_pct
    cinco = pegar(dados, "rate_limits", "five_hour", "used_percentage")
    cinco_rst = pegar(dados, "rate_limits", "five_hour", "resets_at")
    semana = pegar(dados, "rate_limits", "seven_day", "used_percentage")
    sem_rst = pegar(dados, "rate_limits", "seven_day", "resets_at")
    modelo = pegar(dados, "model", "display_name")

    cinco_hora = hora_local(cinco_rst, "%H:%M")
    sem_data = hora_local(sem_rst, "%d/%m %H:%M")

    raiz = pegar(dados, "workspace", "project_dir") or dados.get("cwd")
    if raiz and (Path(raiz) / ".plano").is_dir():
        pasta = Path(raiz) / ".plano" / "estado"
        pasta.mkdir(parents=True, exist_ok=True)
        registro = {
            "atualizado_em": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "sessao": dados.get("session_id"),
            "contexto_pct": ctx,
            "janela_5h_pct": cinco,
            "janela_5h_renova_epoch": cinco_rst,
            "janela_5h_renova_hora": cinco_hora,
            "semanal_pct": semana,
            "semanal_renova_epoch": sem_rst,
            "semanal_renova_data": sem_data,
            "fonte": "barra de status (terminal)",
        }
        try:
            (pasta / "uso.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    partes = []
    if modelo:
        partes.append(f"[{modelo}]")
    if ctx is not None:
        partes.append(f"ctx {float(ctx):.0f}%")
    if cinco is not None:
        texto = f"5h {float(cinco):.0f}%"
        if cinco_hora:
            texto += f" (renova {cinco_hora})"
        partes.append(texto)
    if semana is not None:
        partes.append(f"semana {float(semana):.0f}%")
    print(" | ".join(partes) if partes else "[aguardando primeira resposta]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

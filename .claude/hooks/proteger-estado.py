"""proteger-estado.py — "Cadeado" da pasta .plano/estado/ (hook PreToolUse).

Quando roda: antes de o Claude editar ou criar um arquivo (ferramentas Edit e Write).

O que faz:
    Recusa a edição se o arquivo estiver dentro de .plano/estado/. Essa pasta é
    gerada pelos scripts do medidor de uso e só eles escrevem nela (um dono por
    pasta). O .gitkeep é a única exceção. Os scripts continuam gravando
    normalmente, porque o cadeado vale apenas para as ferramentas do Claude.
"""
import json
import re
import sys


def main():
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return 0
    caminho = (entrada.get("tool_input") or {}).get("file_path")
    if not caminho:
        return 0
    norm = caminho.replace("\\", "/").lower()
    if re.search(r"/\.plano/estado/", norm) and not norm.endswith("/.gitkeep"):
        sys.stderr.reconfigure(encoding="utf-8")
        print(
            "Bloqueado: .plano/estado/ é gerado por scripts (medidor de uso) e não deve ser editado "
            "manualmente. Se o conteúdo estiver errado, corrija o script que o gera, em .claude/hooks/.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""proteger-oculto.py — "Lacre" do conjunto oculto (hook PreToolUse).

Quando roda: antes de o Claude ler, buscar, editar ou criar arquivos e antes de
rodar comandos no terminal (Read, Grep, Edit, Write, NotebookEdit, Bash,
PowerShell).

O que faz (em linguagem simples):
    A regra do CLAUDE.md diz: casos/casos_ocultos.json não é aberto durante os
    ajustes do agente. Até agora a regra dependia só de memória. Este script a
    transforma em trava: se a ferramenta for ABRIR o conjunto oculto (o arquivo
    de casos ou as respostas cruas da validação oculta, brutos_*-oculto_*.json),
    a ação é recusada e o Claude recebe o motivo.

    Olha só o caminho que a ferramenta abre, nunca o texto que ela escreve:
    citar o nome do arquivo num documento (como no CLAUDE.md) continua livre.

    Continua permitido:
    - rodar a validação final (benchmark.py --ocultos): quem lê o arquivo é o
      Python, não o Claude;
    - procurar o NOME do arquivo no código (ex.: grep casos_ocultos benchmark.py);
    - comandos git que só movem o arquivo sem mostrar o conteúdo (add, rm, mv,
      ls-files, status, commit).

Analogia: é o lacre do envelope da prova. O professor pode guardar, levar e
entregar o envelope; só não pode abrir antes do dia da prova.

Limite: um Grep sem caminho que varre a pasta casos/ inteira não cita o arquivo.
Para isso existe a segunda camada, a regra "deny" em .claude/settings.json.
"""
import json
import re
import sys

# Num caminho: qualquer citação do conjunto oculto.
OCULTO_NO_CAMINHO = re.compile(r"casos_ocultos|brutos_[^\s\"'\\/]*-oculto", re.IGNORECASE)

# Num comando: só o ARQUIVO (com .json ou curinga), não o nome solto no meio do código.
OCULTO_NO_COMANDO = re.compile(
    r"casos_ocultos(\.json|\*)|brutos_[^\s\"']*-oculto[^\s\"']*(\.json|\*)",
    re.IGNORECASE,
)

# Comandos git que não mostram o conteúdo do arquivo.
GIT_SEM_CONTEUDO = re.compile(r"^\s*git\s+(add|rm|mv|ls-files|status|commit)\b", re.IGNORECASE)

# Para cada ferramenta, os campos que dizem QUAL arquivo ela abre.
CAMPOS_DE_CAMINHO = {
    "Read": ["file_path"],
    "Edit": ["file_path"],
    "Write": ["file_path"],
    "NotebookEdit": ["notebook_path"],
    "Grep": ["path", "glob"],
}

FERRAMENTAS_DE_COMANDO = {"Bash", "PowerShell"}


def comando_permitido(comando):
    """Um comando git que só move o arquivo passa, desde que não use pipe nem encadeie outro comando."""
    sem_encadeamento = not re.search(r"[|;&]", comando)
    return sem_encadeamento and bool(GIT_SEM_CONTEUDO.match(comando))


def abre_o_oculto(ferramenta, dados):
    """Diz se a ferramenta vai abrir o conjunto oculto."""
    if ferramenta in FERRAMENTAS_DE_COMANDO:
        comando = str(dados.get("command", ""))
        return bool(OCULTO_NO_COMANDO.search(comando)) and not comando_permitido(comando)
    for campo in CAMPOS_DE_CAMINHO.get(ferramenta, []):
        if OCULTO_NO_CAMINHO.search(str(dados.get(campo) or "")):
            return True
    return False


def main():
    try:
        entrada = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return 0

    ferramenta = entrada.get("tool_name", "")
    dados = entrada.get("tool_input") or {}

    if not abre_o_oculto(ferramenta, dados):
        return 0

    sys.stderr.reconfigure(encoding="utf-8")
    print(
        "Bloqueado: o conjunto oculto (casos/casos_ocultos.json e as respostas brutos_*-oculto_*.json) "
        "não pode ser aberto durante os ajustes do agente (CLAUDE.md, seção 2). Use só casos/casos.json. "
        "A validação final roda pelo Python, com: .venv\\Scripts\\python benchmark.py --ocultos. "
        "Novos casos ocultos são escritos pelo usuário, sem o Claude ver.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())

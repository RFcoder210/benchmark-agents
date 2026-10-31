# Fixa o ambiente do benchmark: qual versão do Ollama responde às perguntas do agente.
# Em 30/10, a atualização automática do Ollama (0.40.4 -> 0.40.13) mudou as respostas
# da v15 sem nenhuma mudança no código. Analogia: uma balança trocada no meio do
# experimento; o peso muda, e a pessoa é a mesma.
#
# A 0.40.4 fica numa pasta própria e atende em outra porta, separada do Ollama
# instalado, que pode continuar se atualizando sem afetar o benchmark.
# Para ligar o servidor:  .\iniciar_ollama.bat
#
# Este arquivo precisa ser importado ANTES de "import ollama": a biblioteca lê a
# variável OLLAMA_HOST uma única vez, no momento em que é importada.

import os
import sys

import httpx   # faz a pergunta da versão ao servidor (já vem com a biblioteca ollama)

VERSAO_OLLAMA = "0.40.4"
SERVIDOR_OLLAMA = "127.0.0.1:11500"

# setdefault só define a variável se ela não existir. Assim, um experimento ainda
# pode apontar de propósito para outro servidor, como fez o teste de mutação.
os.environ.setdefault("OLLAMA_HOST", SERVIDOR_OLLAMA)


def versao_ollama():
    """Pergunta a versão ao servidor. Devolve o texto da versão ou, se o servidor
    não responder, None."""
    try:
        return httpx.get(f"http://{os.environ['OLLAMA_HOST']}/api/version", timeout=5).json()["version"]
    except httpx.HTTPError:
        return None


def conferir_ollama():
    """A trava: encerra o programa, com uma explicação, se o servidor estiver
    desligado ou em outra versão. Roda antes de qualquer resposta do modelo."""
    versao = versao_ollama()
    if versao is None:
        sys.exit(f"O Ollama {VERSAO_OLLAMA} não está ligado em {os.environ['OLLAMA_HOST']}.\n"
                 "Abra outro terminal, rode .\\iniciar_ollama.bat e tente de novo.")
    if versao != VERSAO_OLLAMA:
        sys.exit(f"O servidor em {os.environ['OLLAMA_HOST']} está na versão {versao}, mas o "
                 f"benchmark exige a {VERSAO_OLLAMA}: outra versão muda as respostas e\n"
                 "quebra a comparação com o histórico. Nada foi executado nem gravado.")

# Teste de conexão: Python -> Ollama -> modelo local.
# Objetivo: confirmar que conseguimos enviar UMA mensagem ao modelo e ler a resposta,
# antes de construir o agente de verdade (ferramentas simuladas, regras etc.).
# Execução:  .venv\Scripts\python teste_conexao.py

import time    # biblioteca padrão do Python, usada aqui para medir o tempo
import ollama  # biblioteca que conversa com o Ollama rodando no computador

# Nome do modelo do agente (definido no CLAUDE.md).
MODELO = "qwen3:4b-instruct"

# Mensagem do caso C01 (casos/casos.json), escrita direto aqui só para o teste.
mensagem = "Gastei 35 no mercado no pix"

# A conversa é uma LISTA de mensagens; cada mensagem é um DICIONÁRIO
# com o papel de quem fala ("role") e o texto ("content").
conversa = [
    {"role": "user", "content": mensagem},
]

# Envia a conversa ao modelo e mede quanto tempo a resposta levou.
# "temperature": 0 deixa o modelo o mais previsível possível (1º degrau da escada).
inicio = time.perf_counter()
resposta = ollama.chat(model=MODELO, messages=conversa, options={"temperature": 0})
tempo_s = time.perf_counter() - inicio

# Mostra o texto da resposta e os números que, no futuro, irão para o CSV.
print("Mensagem enviada:", mensagem)
print("Resposta do modelo:", resposta.message.content)
print(f"Tempo: {tempo_s:.1f} s")
print("Tokens de entrada:", resposta.prompt_eval_count)
print("Tokens de saída:", resposta.eval_count)

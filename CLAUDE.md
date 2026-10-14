# Benchmark próprio de agentes

Conjunto de avaliações, em Python, para medir a **eficácia** e a **eficiência** dos meus agentes de IA e compará-los entre versões **com dados**, e não por impressão.

A especificação completa (escopo da v1, métricas, formato do CSV, plano em etapas e evoluções futuras) está em [contexto-benchmark-agentes.md](contexto-benchmark-agentes.md). Leia esse arquivo antes de propor arquitetura ou mudanças de escopo.

## 1. Como trabalhar comigo

- Sou estudante de IA, **aprendendo Python**, e quero me tornar engenheiro de agentes. Este projeto é para aprendizado e portfólio.
- **Explique como para iniciante**, com analogias. Ao surgir um conceito básico de Python (lista, dicionário, função, laço, leitura de arquivos), pare e revise-o brevemente.
- **Construa em etapas pequenas.** Nunca escreva o projeto inteiro de uma vez. Ao final de cada etapa, explique o que foi feito e por quê, e indique os conceitos de Python usados.
- **Deixe as partes centrais para eu escrever ou alterar**, com orientação. O objetivo é que eu aprenda, não apenas que o script funcione.
- **Comente o código em português**, explicando o propósito de cada bloco.
- Linguagem **formal e objetiva**; soluções **realistas** para o meu nível.
- Tudo deve ser feito **em casa, sozinho e com ferramentas gratuitas**.

## 2. Regras que não podem ser quebradas

- **Custo:** antes de qualquer ação que gere custo (chamada de API paga), **avise e estime o custo** e aguarde minha confirmação.
- **Isolamento:** o benchmark **nunca** grava no Notion real nem envia mensagens reais pelo Telegram. Ele testa apenas a interpretação do agente (mensagem → dados estruturados ou pergunta de volta), com ferramentas simuladas.
- **Conjunto oculto:** `casos/casos_ocultos.json` não é usado durante os ajustes do agente, apenas na validação final. **Não abra esse arquivo** ao ajustar prompts, regras ou código do agente; use só `casos/casos.json`.
- **Uma mudança por vez** no agente entre execuções do benchmark.
- Cada caso é executado **mais de uma vez** (padrão: 3), porque agentes não respondem sempre igual.

## 3. Ambiente

- Windows 11. Comandos e caminhos compatíveis com Windows.
- Python 3.14 pelo comando **`py`** (o comando `python` abre a Microsoft Store e não deve ser usado).
- Git instalado; o repositório é local.
- Ambiente virtual em `.venv` (bibliotecas em `requirements.txt`). Execute os scripts com `.venv\Scripts\python arquivo.py`, não com `py`.
- Ollama 0.40.4 instalado (`%LOCALAPPDATA%\Programs\Ollama\ollama.exe`). Modelo do agente: **`qwen3:4b-instruct`** (sem raciocínio). Também está baixado `qwen3:4b`, que é a versão "thinking" (sempre raciocina; ~35 s por resposta curta), reservado para um experimento futuro.

## 4. Estado atual

- O agente de gastos está em [agente.py](agente.py), em versão mínima: só a interpretação (mensagem → ferramenta simulada `registrar_gasto` ou `perguntar_usuario(pergunta, campos_faltantes)`), sem Telegram nem Notion. A função `interpretar(mensagem, data_referencia)` é o ponto de entrada do benchmark. O `PROMPT_SISTEMA` foi escrito em conjunto com o usuário (14/10).
- Modelo decidido: **local, pelo Ollama** (gratuito, sem chave de API). Hardware: 16 GB de RAM e GTX 1650 de 4 GB, adequado para modelos de cerca de 3B.
- Melhorias no agente seguem a "escada": temperatura 0 → saída estruturada → instruções → exemplos no prompt → validação em Python → modelo maior → fine-tuning (último recurso, fora da v1). Cada degrau é medido pelo benchmark.
- Ordem das etapas: 1. casos de teste com gabarito (concluída) → 2. agente mínimo (concluída) → 3. script do benchmark (concluída) → 4. linha de base (concluída) → **melhorias pela escada, uma por versão (atual: planejar a v3)**.
- Benchmark: [benchmark.py](benchmark.py) (lê casos → executa 3× → compara → acrescenta em `resultados/resultados.csv`, com `;` e vírgula decimal, e grava as respostas cruas em `resultados/brutos_*.json`). [testar_comparar.py](testar_comparar.py) testa `comparar()` sem rodar o modelo.
- Linha de base v1 (14/10, 2 execuções completas, resultado idêntico): **25/45 (56%)**; registrar 75%, **perguntar 7%**, ignorar 100%; ~3 s e ~1515 tokens por resposta. Principal falha: o agente assume dados em vez de perguntar (C09, C10, C13, C15).
- **v2 = base atual** (14/10): troca do exemplo único de pergunta por um bloco "Exemplos resolvidos" (8 exemplos: 2 registrar, 5 perguntar, 1 ignorar). Resultado: **30/45 (67%)**; registrar 62% ⬇, **perguntar 60%** ⬆, ignorar 100%; ~1804 tokens por resposta. Ganhou C02, C09, C15; perdeu C07 (pergunta "lazer ou outros?") e C10 (passou a ignorar). Ainda erram C08 e C14 (pergunta a categoria que já tinha) e C13 (registra como mercado). Hipótese: exemplos desequilibrados levam o agente a perguntar demais.
- Histórico de versões: comentário junto de `VERSAO_AGENTE` em [benchmark.py](benchmark.py); ao mudar o agente, atualize a versão e o histórico.
- Regras do agente: [especificacao-agente.md](especificacao-agente.md). Casos: `casos/casos.json` (15 de ajuste) e `casos/casos_ocultos.json` (5 ocultos).
- [teste_conexao.py](teste_conexao.py) é só o teste inicial Python → Ollama (sem prompt nem ferramentas).
- A pasta `.claude/` traz, do projeto CRM, o medidor de uso e o sistema de orquestração (`/orquestrar`, agentes em `.claude/agents/`). Na v1 trabalhamos diretamente, etapa por etapa, sem a orquestração. O hook `testar-ao-parar.ps1` ainda é do CRM (roda `npm test` apenas se houver `index.html`) e não faz nada aqui até ser adaptado para Python.

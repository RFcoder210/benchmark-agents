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
- **Conjunto oculto:** os casos marcados como ocultos não são usados durante os ajustes do agente, apenas na validação final. Não os leia nem os mostre ao ajustar o agente.
- **Uma mudança por vez** no agente entre execuções do benchmark.
- Cada caso é executado **mais de uma vez** (padrão: 3), porque agentes não respondem sempre igual.

## 3. Ambiente

- Windows 11. Comandos e caminhos compatíveis com Windows.
- Python 3.14 pelo comando **`py`** (o comando `python` abre a Microsoft Store e não deve ser usado).
- Git instalado; o repositório é local.

## 4. Estado atual

- Etapa atual: **1 — entender como o agente de gastos é chamado**. Ainda falta saber onde está o código do agente, qual modelo ele usa, se há custo por chamada e como ele devolve o resultado.
- Ainda não há código do benchmark.
- A pasta `.claude/` traz, do projeto CRM, o medidor de uso e o sistema de orquestração (`/orquestrar`, agentes em `.claude/agents/`). Na v1 trabalhamos diretamente, etapa por etapa, sem a orquestração. O hook `testar-ao-parar.ps1` ainda é do CRM (roda `npm test` apenas se houver `index.html`) e não faz nada aqui até ser adaptado para Python.

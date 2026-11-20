# Objetivo do projeto

> Preencha os campos marcados com **(obrigatório)** antes de executar `/orquestrar`.
> Escreva como se estivesse explicando a um colega que nunca viu o projeto.
> Preenchido em 2026-11-20 com as respostas do usuário (objetivo, prazo e disponibilidade).

## Objetivo final (obrigatório)
Concluir o **app pessoal do benchmark**: o painel Streamlit (`app.py`, páginas
"Visão geral" e "Executar"), aberto pelo lançador `abrir_benchmark.bat`, deve
permitir rodar o benchmark do agente de gastos **sem precisar da sessão do
Claude**: escolher o rótulo da execução, rodar em segundo plano com barra de
progresso, ser avisado antes de gravar no CSV oficial e ver o resultado no painel.
A v1 do benchmark (casos, agente, script, linha de base, melhorias até a v15 e
validação no conjunto oculto) já está concluída e não faz parte deste objetivo.

## Critérios de conclusão (obrigatório)
- `benchmark.py` aceita a opção `--rotulo` (por exemplo, `v15-repeticao`) sem
  editar o código, com teste automático; sem rótulo, o comportamento atual não muda.
- A página "Executar" tem o botão ligado: confere o Ollama 0.40.4 (porta 11500) e
  o rótulo, pede confirmação antes de gravar em `resultados/resultados.csv`,
  roda em segundo plano e mostra o progresso (a execução leva de 4 a 5 minutos).
- Não existe botão nem opção na página para o conjunto oculto (`casos_ocultos.json`).
- Um rótulo que já existe no CSV é recusado ou exige confirmação explícita.
- `testar_executar.py`, `testar_dashboard.py` e os demais testes sem modelo passam.
- Uma execução real pelo botão (por exemplo, `v15-repeticao`) foi feita pelo
  usuário, gravou no CSV e aparece no painel como lote de calibração.
- README e CLAUDE.md atualizados com o uso da página Executar.

## Prazo final (obrigatório)
- Prazo final: sem prazo fixo.
- Entregas intermediárias (sem datas): 1. opção `--rotulo` com teste;
  2. botão ligado com progresso e aviso; 3. execução real pelo botão e documentação.

## Disponibilidade (obrigatório)
- Dias da semana em que vou trabalhar no projeto: sem dias fixos (sessões soltas,
  uma por dia de trabalho, conforme a rotina do CLAUDE.md).
- Horas por dia, em média: 2
- Commits: aprovação permanente do usuário (20/11): "sempre commite tudo quando
  for coerente" (tarefa, fase, planejamento em `.plano/`), para aproveitar o
  aprendizado como portfólio. Trabalho direto na `main`; todo commit é seguido de
  `git push` (CLAUDE.md, seção 3). Nunca `push --force` sem pedido explícito.
- Plano do Claude: Pro

## Situação atual
Benchmark v1 concluído: base v15 com 44/45 nos casos de ajuste e 15/15 no
conjunto oculto (28/10). Painel com tema Grafite, menu `app.py` e página
"Executar" na etapa 1 (só confere o Ollama e se o rótulo de `VERSAO_AGENTE` já
existe no CSV; botão desligado; 9 verificações em `testar_executar.py`).
Lançador `.bat` com atalho na área de trabalho. Repositório público no GitHub
(MIT). O rótulo da execução ainda é definido dentro de `benchmark.py`
(`VERSAO_AGENTE`).

## Restrições
- Somente ferramentas gratuitas; tudo feito em casa, sozinho.
- Nenhuma chamada de API paga sem estimativa de custo e confirmação.
- O benchmark nunca grava no Notion nem envia mensagens pelo Telegram.
- O conjunto oculto não é aberto nem exposto no app.
- O CSV é o histórico oficial: nada é gravado nele sem aviso e rótulo escolhido.
- O benchmark roda só no Ollama 0.40.4 portátil (porta 11500), ligado pelo
  usuário com `iniciar_ollama.bat` ou pelo lançador.
- O agente não muda neste objetivo (a v15 segue como base).
- Painel sem CSS próprio: só as opções do tema.
- Etapas pequenas; as partes centrais ficam para o usuário escrever, com orientação.
- Passos que dependem do usuário (ligar o Ollama, rodar a execução real, aprovar
  commit) constam como AGUARDA USUÁRIO, nunca são assumidos.

## Recursos disponíveis
Windows 11; Python 3.14 (`py`) e ambiente virtual `.venv` (Streamlit, Altair,
cliente do Ollama); Ollama 0.40.4 portátil com `qwen3:4b-instruct`; Git com
repositório público no GitHub; navegador embutido do app para testar o painel.
Hardware: 16 GB de RAM e GTX 1650 de 4 GB. Nenhuma senha ou chave neste arquivo.

## Meu nível técnico
Estudante de IA, aprendendo Python, quer se tornar engenheiro de agentes.
Explicar cada conceito novo com analogia, de forma formal e objetiva
(CLAUDE.md, seção 1).

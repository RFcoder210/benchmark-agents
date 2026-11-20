# T10 — AGUARDA USUÁRIO: execução real v15-repeticao pelo botão

**Fase:** 3 — Execução real e documentação (entrega 3)
**Porte:** P
**Depende de:** T09
**Executor:** AGUARDA USUÁRIO (só o usuário liga o Ollama, roda o modelo e autoriza a gravação no CSV oficial)
**Revisão:** nenhuma

## Contexto mínimo
Critério de conclusão do objetivo: uma execução real feita pelo botão, gravada no CSV e visível no painel como lote de calibração. O rótulo `v15-repeticao` repete a base v15 (44/45 em 27/10) no Ollama 0.40.4; serve também como evidência de estabilidade. Custo: R$ 0,00 (modelo local); tempo: 4 a 5 minutos.

## Arquivos para ler
- Nenhum. O orquestrador lembra os passos abaixo.

## O que fazer (o usuário)
1. Fechar painéis abertos antes e abrir pelo atalho **Benchmark de agentes** (liga o Ollama 0.40.4 na porta 11500 e o painel na 8501).
2. Ir à página **Executar** e conferir: "Ollama 0.40.4 ligado"; rótulo `v15-repeticao` sem aviso de repetido.
3. Marcar a confirmação de gravação no CSV e clicar em **Executar**. Acompanhar a barra até 45 de 45.
4. Anotar a linha "Acerto geral" e o horário. Se terminar com erro (já houve "CUDA error" passageiro em 27/10), anotar a mensagem e rodar de novo com o mesmo rótulo só se a página disser "Nada foi gravado no CSV.".
5. Clicar em **Ver na Visão geral**, marcar **Incluir lotes de calibração** e conferir que `v15-repeticao` aparece.
6. Informar ao orquestrador: acerto geral, se houve erro, e se o rótulo apareceu no painel.

## Arquivos a criar ou alterar
- `resultados/resultados.csv` (45 linhas novas, gravadas pelo benchmark)
- `resultados/brutos_v15-repeticao_<carimbo>.json` (novo, gravado pelo benchmark)

## Critério de pronto (verificável)
- [ ] O usuário informou o acerto geral da execução e que `v15-repeticao` aparece no painel com os lotes de calibração.
- [ ] Existe `resultados/brutos_v15-repeticao_*.json`.

## Não alterar
- `casos/casos.json`
- `casos/casos_ocultos.json`
- `agente.py`

## Cuidados
- Não usar o conjunto oculto (não há botão para ele).
- Um acerto diferente de 44/45 não reprova esta tarefa: é um dado (a T11 compara com a v15 caso a caso).
- Não fechar a janela minimizada do painel durante a execução (o processo pode seguir sozinho, mas a página perde o acompanhamento).

## Resultado
(preenchido ao terminar: acerto geral, horário, ocorrências)

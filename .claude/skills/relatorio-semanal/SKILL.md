---
name: relatorio-semanal
description: Atualiza o relatório semanal do projeto em PDF (docs/relatorios-semanais/), escrito para o usuário ler e entender o raciocínio da semana. Roda no fim de toda sessão, como passo do /encerrar-dia; também pode ser pedido à parte.
disable-model-invocation: true
---

# Relatório semanal em PDF

Pedido do usuário (27/11/2026): **um PDF por semana**, atualizado **no fim de toda sessão**,
para ele ler e entender o raciocínio do que foi feito, enquanto a parte técnica fica nas
sessões. Ele é o leitor: estudante de IA aprendendo Python. O relatório explica o porquê,
não lista comandos.

## 1. Qual arquivo

- A semana vai de **segunda a domingo**. Arquivos em `docs/relatorios-semanais/`:
  `semana-AAAA-MM-DD.json` (conteúdo) e `semana-AAAA-MM-DD.pdf` (gerado), com a data da segunda-feira.
- Se o JSON da semana já existe, **acrescente a sessão de hoje** a ele e suba a versão
  em 0.1 (1.0 → 1.1). Se não existe, crie-o na versão 1.0.
- A primeira edição de cada semana repete o modelo de `semana-2026-11-23.json`.

## 2. De onde vem o conteúdo (só fatos confirmados)

Leia, nesta ordem, só o necessário: `.plano/DIARIO.md` (linhas da semana),
`.plano/RETOMADA.md` (a de hoje e as de `.plano/historico/` da semana),
`git log --since=<segunda> --format="%ad %s" --date=format:%d/%m/%Y`, `.plano/ESTADO.md`
e, se houve versão nova do agente, `docs/historico-versoes.md`.
Nunca invente motivo, número ou decisão. O que não está confirmado vai para
"Próximos passos" como item a verificar.

## 3. Datas (regra do usuário: tudo datado corretamente)

1. A data de hoje vem do sistema (hook do início da sessão ou `Get-Date`), nunca de memória.
2. Toda data no formato **DD/MM/AAAA**, com o ano.
3. Cada decisão leva a data **do dia em que foi tomada** (confira no diário, na retomada ou
   na data do commit), não a data em que o relatório foi escrito.
4. Itens da linha de raciocínio começam com a data entre parênteses: `(27/11) <b>Constatação</b>; por isso, decisão.`
5. O gerador confere as datas e calcula o dia da semana sozinho; se ele recusar, corrija a data
   em vez de contornar a conferência.

## 4. Como escrever

- **situacao:** um parágrafo, onde o projeto estava ao começar a semana (base do agente,
  etapa, o que já existia). O leitor deve entender a semana sem ter lido a anterior.
- **foco:** um parágrafo, o que a semana buscava e por quê.
- **raciocinio:** de 3 a 7 itens, "constatação; por isso, decisão", do mais fundamental ao mais específico.
- **sessoes:** uma por sessão, com `feito` (2 a 5 itens), `por_que`, `resultado` e, opcional,
  `tecnico` (uma frase com arquivos e comandos; é o único lugar para eles).
- **decisoes:** data, quem decidiu (usuário, sessão, usuário e sessão) e o texto.
- **aprendizados:** problemas encontrados e o que ensinaram, inclusive erros.
- **proximos:** de 3 a 5 itens, começando com verbo em negrito.
- Português formal e didático; termo técnico em negrito com explicação curta na primeira vez.
  Só a tag `<b>`. Sem tabelas, cores nem marcadores. Alvo: 2 a 4 páginas.

## 5. Gerar, conferir e entregar

1. `.venv\Scripts\python .claude\skills\relatorio-semanal\gerar_relatorio.py docs\relatorios-semanais\semana-AAAA-MM-DD.json`
2. Abra o PDF com a ferramenta Read e confira acentos, datas e quebras de página
   (título de seção sozinho no fim da página, página quase vazia).
3. Entregue com SendUserFile (`display: "render"`). Os dois arquivos entram no commit do encerramento.

## 6. Custo e reserva de cota

- Meça `get_usage` antes e depois de gerar e registre abaixo (data, % da janela de 5 h).
- **Reserva:** o medidor (`.claude/hooks/verificar-uso.py`) passa ao nível CRÍTICO em 85% da janela
  de 5 h (antes, 90%) e em 93% da semana (antes, 95%). Assim, o encerramento com o PDF ainda cabe.
  Se as medições mostrarem outro tamanho, ajuste esses limites.

Medições:
- 27/11/2026, 1ª edição (v1.0, 2 sessões, 3 páginas): janela de 5 h de 14% para 15% (~1 p.p.); semana de 4% para 5%.
  Medida no meio da sessão, com o contexto em ~150 mil tokens; no fim de uma sessão longa deve custar mais.
  A reserva de 5 p.p. (85% → 90%) cobre com folga; reavaliar após 3 medições.

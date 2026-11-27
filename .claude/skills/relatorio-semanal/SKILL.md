---
name: relatorio-semanal
description: Atualiza o relatório semanal de aprendizado do projeto em PDF (docs/relatorios-semanais/), que ensina ao usuário o que foi construído na semana, com mapa da arquitetura, fluxogramas, trechos reais do código, glossário e perguntas de revisão. Roda no fim de toda sessão, como passo do /encerrar-dia; também pode ser pedido à parte.
disable-model-invocation: true
---

# Relatório semanal de aprendizado em PDF

## Para que serve (pedido do usuário em 27/11/2026)

O usuário é estudante de IA, aprendendo Python, e quer **entender de verdade o que está
construindo**, sem deixar tudo nas mãos do Claude Code e sem atrasar o desenvolvimento.
Este PDF é o material de estudo da semana: o desenvolvimento técnico acontece nas
sessões, e o relatório **ensina** o que foi feito, como e por quê.

Não confundir com o **doc-projeto-pdf**, que é o registro de ideias de projeto (um PDF
conceitual por ideia). Os dois convivem; este não substitui aquele.

## 1. Qual arquivo

- A semana vai de **segunda a domingo**. Arquivos em `docs/relatorios-semanais/`:
  `semana-AAAA-MM-DD.json` (conteúdo, com a data da segunda-feira) e o `.pdf` gerado.
- Se o JSON da semana já existe, **acrescente** o que a sessão de hoje fez e suba a
  versão em 0.1 (2.0 → 2.1). Se não existe, crie-o na versão 1.0, copiando a estrutura
  de `semana-2026-11-23.json` (primeiro exemplo completo do padrão).
- O mapa (seção 2) passa de uma semana para a outra: copie-o, atualize-o e marque como
  `"novo"` só o que mudou na semana.

## 2. De onde vem o conteúdo (só fatos confirmados)

Leia só o necessário: `.plano/DIARIO.md` (linhas da semana), `.plano/RETOMADA.md` e as de
`.plano/historico/` da semana, `git log --since=<segunda> --format="%ad %s" --date=format:%d/%m/%Y`,
`git show --stat` dos commits que viram lição e **o próprio código** dos trechos explicados.
Nunca invente motivo, número, alternativa ou decisão. O que não está confirmado aparece
como "a conferir" ou vai para os próximos passos.

## 3. Datas (regra do usuário: tudo datado corretamente)

1. A data de hoje vem do sistema (hook do início da sessão ou `Get-Date`), nunca de memória.
2. Toda data em **DD/MM/AAAA**; nas listas, `(DD/MM)` no início do item.
3. Cada decisão leva a data **do dia em que foi tomada** (diário, retomada ou data do commit).
4. O gerador confere as datas e calcula o dia da semana sozinho. Se ele recusar, corrija a
   data; nunca contorne a conferência.

## 4. O que escrever (campos do JSON)

| Campo | Conteúdo |
|---|---|
| `como_ler` | um parágrafo fixo, que orienta a leitura (pode repetir o do exemplo) |
| `resumo` | 3 a 6 frases: o que mudou no projeto, em linguagem simples |
| `mapa.texto` | as camadas do projeto e onde a novidade da semana se encaixa |
| `mapa.diagrama` | o projeto inteiro em caixas e setas (ver seção 5) |
| `mapa.componentes` | cada peça: `nome`, `o_que_e`, `analogia` opcional, `novo: true` se mudou |
| `licoes` | **uma por mudança relevante**, a parte principal (ver abaixo) |
| `glossario` | todo termo técnico usado na semana: `termo`, `definicao`, `no_projeto` |
| `decisoes` | `data`, `quem` (usuário, sessão, usuário e sessão), `texto` |
| `aprendizados` | problemas e o que ensinaram, inclusive erros |
| `proximos` | 3 a 5 itens com verbo em negrito **e o que ele vai aprender com cada um** |
| `perguntas` | 4 a 8 `pergunta`/`resposta` sobre o porquê das coisas, não sobre decoreba |

**Cada lição** (`licoes[]`) tem: `titulo`, `data`, `sessao`, `em_uma_frase`, `problema`
(o que precisávamos resolver), `ideia` (o conceito de engenharia, nomeado e explicado),
e, quando ajudam: `como_funciona` (passos), `diagrama`, `codigo`, `python` (conceitos de
Python do trecho), `alternativas` ("Descartado: X, porque Y", só se confirmadas),
`como_sabemos` (os testes ou a evidência).

Regras de escrita:
- **Explicar, não listar.** Cada lição responde: que problema havia, que ideia resolveu,
  como funciona por dentro e como sabemos que funciona.
- **Todo termo técnico** em negrito com explicação curta entre parênteses na primeira vez,
  e também no glossário. Prefira o termo real (processo filho, condição de corrida) a
  um eufemismo: ele precisa aprender o vocabulário.
- **Analogias** curtas quando esclarecem; nunca forçadas.
- **Diagrama** sempre que houver arquitetura (quem chama quem), fluxo (passo a passo com
  decisões) ou laço. O mapa do projeto é obrigatório.
- **Código**: escolha o trecho central da mudança (até ~35 linhas) e explique linha a linha
  em `explicacao`. Não copie o código: informe `arquivo`, `linha_inicial` e `linha_final`,
  e o gerador lê o trecho real e o grava no JSON.
- Só as tags `<b>` e `<i>`. Sem emojis, setas ou símbolos fora do alfabeto latino:
  o gerador recusa caracteres que a fonte não desenha (escreva "para", não uma seta).
- Português formal e didático. Tamanho: o que a semana pedir (a primeira edição teve 14 páginas).

## 5. Diagramas

```json
{"titulo": "...", "colunas": 3, "folga_horizontal": 30,
 "nos": [{"id": "a", "texto": "Título\nexplicação curta", "linha": 0, "coluna": 1,
          "largura": 1, "tipo": "normal|novo|dados|externo|decisao"}],
 "ligacoes": [{"de": "a", "para": "b", "rotulo": "opcional", "tracejada": false,
               "lado": "direita|esquerda (opcional, para laços)"}]}
```

- Caixas numa grade (linha, coluna). Tipos: `novo` (verde, mudou na semana), `normal`,
  `dados` (arquivo), `externo` (fora do projeto, tracejado), `decisao` (losango, sim ou não).
- Evite setas que atravessem caixas: deixe vazia a célula entre dois nós ligados.
- Rótulos curtos (até ~3 palavras). Entre caixas lado a lado só cabe uma palavra; se não
  couber, tire o rótulo e explique no texto.
- Para um laço (repetir até terminar), use `"lado"` na ligação de volta.

## 6. Gerar, conferir e entregar

1. `.venv\Scripts\python .claude\skills\relatorio-semanal\gerar_relatorio.py docs\relatorios-semanais\semana-AAAA-MM-DD.json`
2. Abra o PDF com a ferramenta Read (sem `pages`) e confira **cada página**: rótulos de seta
   visíveis, setas que não cruzam caixas, acentos, datas, meia página vazia antes de figura.
   Corrija o JSON e gere de novo.
3. Entregue com SendUserFile (`display: "render"`). JSON e PDF entram no commit do encerramento.

## 7. Custo e reserva de cota

- Meça `get_usage` antes e depois e registre abaixo (data, edição, % da janela de 5 h).
- **Reserva:** o medidor (`.claude/hooks/verificar-uso.py`) passa ao nível CRÍTICO em 80% da
  janela de 5 h (ver abaixo) e em 93% da semana. Se as medições mostrarem outro tamanho, ajuste os limites.

Medições:
- 27/11/2026, padrão antigo (v1.0, 3 páginas): ~1 p.p. da janela de 5 h.
- 27/11/2026, padrão didático (v2.0, 14 páginas, gerador novo incluído): de 23% para 35% (12 p.p.), mas a maior parte foi construir o gerador e ler o PDF inteiro duas vezes. Estimativa para uma atualização normal: 6 a 8 p.p. Leia o PDF inteiro uma vez só, depois de corrigir tudo o que for possível no JSON.
- 27/11/2026, atualização v2.1 (14 para 19 páginas, 3 lições novas, feita por subagente para poupar o contexto da sessão): de 57% para 65% (8 p.p.), dentro da estimativa.
- Reserva ajustada em 27/11/2026: ALERTA em 75% e CRÍTICO em 80% da janela de 5 h (cerca de 20 p.p. livres para o encerramento com o PDF).

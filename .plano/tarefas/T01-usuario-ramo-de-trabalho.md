# T01 — AGUARDA USUÁRIO: decidir o ramo de trabalho e as permissões pendentes

**Fase:** 0 — Ramo de trabalho
**Porte:** P
**Depende de:** nenhuma
**Executor:** AGUARDA USUÁRIO (decisão do usuário; o orquestrador executa os comandos git que ele aprovar)
**Revisão:** nenhuma

## Contexto mínimo
O repositório está no ramo `config/permissoes-leitura`, com alterações não commitadas em `.claude/settings.json` (permissões de leitura) e `.plano/DIARIO.md`, e com `.plano/OBJETIVO.md` novo. Antes de mexer em código, é preciso decidir onde o trabalho do botão "Executar" será commitado. Todo commit aprovado é seguido de `git push` (CLAUDE.md, seção 3); nunca `push --force`.

## Arquivos para ler
- `git status` e `git diff .claude/settings.json` (o orquestrador mostra ao usuário)

## O que fazer (o usuário decide; o orquestrador executa)
1. Decidir o destino das permissões em `.claude/settings.json`:
   - (a) commitar no ramo `config/permissoes-leitura` e juntar à `main`; ou
   - (b) descartar as alterações.
2. Decidir o ramo do trabalho deste plano:
   - (a) direto na `main`, como no histórico do projeto; ou
   - (b) um ramo novo a partir da `main`, por exemplo `app/botao-executar`, juntado à `main` no fim (T13).
3. Decidir se os arquivos de `.plano/` (OBJETIVO, PLANO, ESTADO, tarefas) entram no commit, como já acontece com `RETOMADA.md` e `DIARIO.md`.
4. O orquestrador executa os comandos git aprovados e confirma com `git status` e `git branch --show-current`.

## Arquivos a criar ou alterar
- Nenhum arquivo de código. Só operações git aprovadas pelo usuário.

## Critério de pronto (verificável)
- [ ] `git branch --show-current` mostra o ramo escolhido pelo usuário.
- [ ] `git status --short -- .claude/settings.json` não lista o arquivo (commitado ou descartado, conforme a decisão).

## Não alterar
- nenhum

## Cuidados
- Nunca `push --force`. Nenhum commit sem a aprovação explícita do usuário.
- Não apagar os ramos locais `lote-noturno-2026-10-15` e `noite/2026-10-18`.

## Resultado
Concluída em 2026-11-20.
- Permissões: já tinham sido commitadas e enviadas na `main` por outra sessão (fb56113, "Permissões: libera comandos e ferramentas só de leitura"); o ramo `config/permissoes-leitura` não existe mais.
- Ramo: trabalho direto na `main`, como no histórico do projeto.
- `.plano/`: entra nos commits. Decisão do usuário (20/11): "sempre commite tudo quando for coerente", para aproveitar o aprendizado como portfólio; cada commit é seguido de `git push`.
- Verificação: `git branch --show-current` → `main`; `git status --short -- .claude/settings.json` → vazio.

# T13 — AGUARDA USUÁRIO: aprovar o commit final e o push

**Fase:** 3 — Execução real e documentação (entrega 3)
**Porte:** P
**Depende de:** T12
**Executor:** AGUARDA USUÁRIO (só o usuário aprova commits; o orquestrador executa os comandos aprovados)
**Revisão:** nenhuma

## Contexto mínimo
Fecha o objetivo. As entregas 1 e 2 já devem ter sido commitadas ao fim das suas fases. Faltam os arquivos da fase 3 (CSV e brutos da `v15-repeticao`, README, CLAUDE.md) e, se o trabalho foi feito num ramo à parte (decisão da T01), juntá-lo à `main`. Rotina do projeto: todo commit aprovado é seguido de `git push`; nunca `push --force`.

## Arquivos para ler
- `git status` e `git log --oneline -10` (o orquestrador mostra ao usuário)
- Mensagens de commit propostas nas seções Resultado da T11 e da T12

## O que fazer (o usuário aprova; o orquestrador executa)
1. Revisar a lista de arquivos alterados e as mensagens propostas.
2. Aprovar o(s) commit(s) da fase 3 e o `git push`.
3. Se houver ramo à parte: aprovar a junção à `main` e o `git push` da `main`.
4. Conferir os critérios de conclusão de `.plano/OBJETIVO.md`, um a um.

## Arquivos a criar ou alterar
- Nenhum arquivo novo; só commits aprovados.

## Critério de pronto (verificável)
- [ ] `git status --short` sem arquivos do projeto pendentes (exceto `.plano/` se o usuário decidiu não versioná-la).
- [ ] `git log origin/main --oneline -5` mostra os commits do objetivo.
- [ ] Os 7 critérios de conclusão do `OBJETIVO.md` conferidos e marcados pelo usuário.

## Não alterar
- nenhum

## Cuidados
- Nunca `push --force`. Commits com o e-mail noreply já configurado no repositório (não mudar `user.email`).
- `resultados/logs/` não entra no commit (está no `.gitignore`).

## Resultado
(preenchido ao terminar: commits feitos e conferência dos critérios)

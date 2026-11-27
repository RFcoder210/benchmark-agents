---
name: encerrar-dia
description: Encerra o dia de trabalho do benchmark gravando o bilhete de retomada (.plano/RETOMADA.md) para a sessão do dia seguinte. Use ao final do dia ou quando o medidor de uso indicar nível crítico.
disable-model-invocation: true
---

# Encerramento do dia (benchmark de agentes)

Rotina do projeto: **uma sessão por dia**. O estado duradouro fica no CLAUDE.md;
o bilhete do dia fica em `.plano/RETOMADA.md`, que o hook `iniciar-sessao.py`
entrega automaticamente à próxima sessão. Não duplique informação entre os dois.

1. **Não inicie nenhuma tarefa nova.** Se algo estiver no meio (ex.: benchmark rodando), aguarde terminar.
2. **Git:** rode `git status`. Se houver alterações sem commit, liste-as ao usuário e pergunte se devem ser commitadas antes de encerrar. Nunca commite sem confirmação.
3. **CLAUDE.md, seção "Estado atual":** atualize apenas fatos duradouros que mudaram hoje (etapa atual, versão base do agente, resultado de uma versão nova). Se nada mudou, não edite.
4. **Arquivar o bilhete anterior:** se existir `.plano/RETOMADA.md`, copie-o para `.plano/historico/RETOMADA-AAAA-MM-DD.md` (data do bilhete antigo). Mantenha só os 10 mais recentes.
5. **Gravar o novo `.plano/RETOMADA.md`** — limite de **40 linhas**, só o que muda a próxima ação; aponte arquivos em vez de copiar conteúdo:

```
# Retomada — AAAA-MM-DD
## Feito hoje
- (3 a 6 itens curtos, com o commit quando houver)
## Onde paramos
- (o passo exato; o que está pronto mas não testado ou não commitado)
## Próxima ação (a primeira coisa de amanhã)
1. ...
## Decisões tomadas que não estão em outro arquivo
- ...
## Aguardando o usuário
- ...
## Ler se necessário
- (arquivos relevantes para a próxima ação)
```

5b. **Diário e nome da sessão:** feche a linha do dia em `.plano/DIARIO.md` (resumo em 1 frase). Se o foco do dia mudou e o nome da sessão ficou desatualizado, acerte-o com `set_session_title` (`session_id: "self"`), mantendo o padrão `Dia N · DD/MM · foco`, e atualize a coluna Sessão do diário.
5c. **Relatório semanal em PDF (toda sessão, desde 27/11/2026):** leia `.claude/skills/relatorio-semanal/SKILL.md` e siga-o: acrescente a sessão de hoje ao relatório da semana, gere o PDF, confira e entregue. Os arquivos do relatório entram no commit do passo 2 (se o commit já foi feito, faça um segundo, com a mesma aprovação). A cota para isto está reservada pelo medidor: não pule este passo por falta de cota, a menos que a janela de 5 h esteja acima de 95%; nesse caso, registre na retomada que o relatório ficou para a próxima sessão.
6. **Responder ao usuário, em no máximo 6 linhas:** o que foi concluído hoje, a primeira ação de amanhã, o que ele precisa providenciar (se algo) e a orientação: "Pode fechar esta sessão. Amanhã, abra uma sessão nova nesta pasta; a retomada será carregada automaticamente."

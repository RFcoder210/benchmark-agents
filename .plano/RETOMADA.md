# Retomada — 2026-11-20
Motivo do checkpoint: antes de compactar (contexto em 72% do orçamento)

## Feito hoje
- Orquestração ligada neste projeto: `.plano/OBJETIVO.md` (concluir o app pessoal, sem prazo, sessões de 2 h), PLANO, ESTADO e 13 tarefas (446c512).
- T01 concluída: trabalho direto na `main`; `.plano/` entra nos commits.
- Ambiente conferido (nada instalado, testes sem modelo passando) e cronograma de hoje: T02 a T06 (612a070).
- Dia 15 renomeado para "Permissões de leitura" (diário e título da sessão).

## Onde paramos
- T02 (teste e esqueleto da opção --rotulo) EM_ANDAMENTO com o `executor-tarefa`.

## Próxima ação
1. Ao receber o relatório da T02: marcar no ESTADO.md, commitar e dar push.
2. T03 é do usuário: escrever `rotulo_invalido()` e `escolher_execucao()` com orientação (ver a tarefa).
3. Seguir o cronograma: T04, T05, T06 (U).

## Decisões tomadas que não estão em outro arquivo
- Aprovação permanente de commits (20/11): "sempre commite tudo quando for coerente", seguido de push (memória `commitar-tudo-coerente`; também no OBJETIVO.md).
- Decisões padrão do PLANO aprovadas: rótulo repetido recusado; confirmação por caixa de seleção; rótulo sem hífen aceito com aviso; logs em `resultados/logs/` fora do git; sem botão de cancelar.

## Aguardando o usuário
- `.claude/hooks/proteger-oculto.py` e `testar-ao-editar.py` (não commitados) são da sessão "Testar skills e melhorar setup"; não mexer.
- Ollama 0.40.4 ligado só na T10.

## Ler se necessário
- `.plano/CRONOGRAMA.md`, `.plano/ESTADO.md` (tabela) e a tarefa da vez em `.plano/tarefas/`.

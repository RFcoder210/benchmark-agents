---
name: orquestrar
description: Conduz o ciclo de trabalho do sistema de agentes do projeto (análise, preparação, cronograma, execução, diagnóstico e checkpoints). Use no início de cada sessão de trabalho.
disable-model-invocation: true
---

# Protocolo do orquestrador

Você (a sessão principal) é o **mestre de obras**. Você não executa tarefas do projeto: você decide quem trabalha, entrega a ordem de serviço certa, lê o relatório curto e registra o andamento. Toda a memória durável vive em `.plano/`; a conversa é descartável.

## Regras de economia (valem o tempo todo)
- Delegue passando **caminhos de arquivo**, nunca o conteúdo dos arquivos.
- Não leia planos, código ou tarefas inteiras você mesmo; os subagentes leem. Você lê apenas os relatórios deles e, quando preciso, `.plano/ESTADO.md`.
- Execute as tarefas **uma por vez**. Paralelismo apenas para tarefas P independentes e com a janela de 5 h abaixo de 50%.
- Mensagens ao usuário: curtas, no fim de cada etapa relevante.
- Nunca use nem sugira `bypassPermissions`. Instalações globais passam pela aprovação do usuário.

## Etapa 0 — Situação
A data e a retomada já chegam no início da sessão (hook). Com base nelas, verifique, **nesta ordem**, apenas a existência e a data dos arquivos:
1. `.plano/OBJETIVO.md` preenchido? Se os campos obrigatórios estiverem vazios → peça ao usuário que o preencha e **pare**.
2. Existe `.plano/PLANO.md`? Se não → Etapa 1.
3. A **primeira linha** de `.plano/AMBIENTE.md` diz `Ambiente pronto: SIM`? (Leia só essa linha.) Se não → Etapa 2.
4. `.plano/CRONOGRAMA.md` tem a data de hoje no título? Se não → Etapa 3.
5. Caso contrário → Etapa 4.

## Etapa 1 — Análise (agente `analise-projeto`)
Delegue: "Analise o projeto a partir de .plano/OBJETIVO.md e gere ESTADO.md, PLANO.md e os arquivos de tarefa." Ao receber o relatório, apresente ao usuário o resumo (quantidade de tarefas, prazo realista ou não, decisões pendentes) e **peça aprovação do plano** antes de prosseguir. Planejar custa pouco; executar um plano errado custa muito.

## Etapa 2 — Preparação (agente `preparacao-terreno`)
Delegue: "Prepare o ambiente conforme a seção Pré-requisitos de .plano/PLANO.md." Itens AGUARDA USUÁRIO → informe o usuário do que ele precisa fazer. Se o relatório disser "pronto: NÃO" por falha técnica, envie o item ao `resolutivo-diagnostico`. Saída parcial (limite de turnos) conta como "pronto: NÃO": acione o agente de novo; os itens já registrados como OK não são refeitos. Quando o diagnóstico devolver destino PREPARACAO, peça **só o item faltante** (modo de item único).

## Etapa 3 — Cronograma (agente `cronograma`)
Delegue: "Gere o cronograma de hoje." Mostre ao usuário a situação do prazo, a lista de hoje e os lembretes antecipados.

## Etapa 4 — Execução (agente `executor-tarefa`)
Para cada tarefa da lista de hoje, em ordem:
1. Marque a tarefa como EM_ANDAMENTO na tabela de `.plano/ESTADO.md` (edição de uma linha).
2. Delegue: "Execute a tarefa descrita em .plano/tarefas/Txx-*.md." Acrescente só o contexto que não está em arquivo (1 a 3 linhas), se houver. **Guarde o ID do agente** retornado.
3. Relatório **CONCLUIDA** → se a coluna `revisão` da tarefa no ESTADO.md for `nenhuma`, marque CONCLUIDA e siga para a próxima. Se indicar um revisor, acione-o antes de marcar:
   - Delegue: "Revise a tarefa Txx. Arquivos alterados: <lista do campo ARQUIVOS do executor>." Não envie diff nem conteúdo de arquivo.
   - Achado **confirmado** e grave → retome o mesmo executor (SendMessage) com os achados e a instrução "Corrija estes pontos e conclua a tarefa". Isso conta como o ciclo de diagnóstico do dia.
   - Só **suspeitas** ou nada encontrado → marque CONCLUIDA; registre as suspeitas em `PENDENCIAS.md` (status ABERTA), sem travar a tarefa.
4. Relatório **PENDENTE** → Etapa 5.
5. Saída **parcial** (o executor atingiu o limite de turnos) ou relatório **sem STATUS** → nunca marque como concluída. Trate como pendência (Etapa 5), avisando ao diagnóstico que o executor foi interrompido e que o histórico das tentativas está na seção Resultado do arquivo da tarefa.

## Etapa 5 — Pendência (agente `resolutivo-diagnostico`)
1. Delegue ao `resolutivo-diagnostico` o relatório de pendência **na íntegra**, mais o caminho do arquivo da tarefa.
   - **Reincidência:** se a tarefa já tem entrada em `.plano/PENDENCIAS.md` (já passou por um diagnóstico antes), acione o diagnóstico com `model: opus` na chamada. Nos demais casos, use o modelo padrão do agente. O modelo forte só é pago quando o problema já provou ser difícil.
   - Ao receber o relatório, copie a linha do campo `PENDENCIA` para `.plano/PENDENCIAS.md` com status ABERTA. Você é o único que escreve nesse arquivo.
2. Conforme o DESTINO do diagnóstico:
   - **EXECUTOR** → retome o **mesmo** executor pelo ID guardado (SendMessage), enviando o diagnóstico completo e a instrução: "Aplique a solução deste diagnóstico e conclua a tarefa." Assim ele continua com todo o contexto que já tinha.
   - **PREPARACAO** → acione o `preparacao-terreno` com o item faltante; depois retome o executor como acima.
   - **REPLANEJAR** → acione o `analise-projeto` no **modo cirúrgico** ("Reescreva somente a tarefa Txx", com o diagnóstico); depois delegue a um executor novo.
   - **USUARIO** → marque BLOQUEADA em ESTADO.md, explique ao usuário exatamente o que é necessário e passe para a próxima tarefa.
3. Quando o executor retomado devolver **CONCLUIDA**: mude a entrada em `PENDENCIAS.md` para RESOLVIDA e, se o campo `OCORRENCIA` do diagnóstico não for "não se aplica", acrescente uma linha em `~/.claude/ocorrencias-agentes.md` no formato `AAAA-MM-DD | projeto | erro → causa → solução`. Só entra no caderno o que foi confirmado.
4. Limite: **um ciclo de diagnóstico por tarefa por dia**. Se a tarefa falhar de novo após a solução, marque BLOQUEADA, registre em PENDENCIAS.md e informe o usuário.

## Leitura do medidor (app desktop)
No app desktop (aba Code) a barra de status não roda, então `.plano/estado/uso.json` não se atualiza sozinho. Leia o uso **somente** nestes três momentos:
1. na Etapa 0;
2. antes de **iniciar** cada tarefa nova (Etapa 4, passo 2);
3. antes de acionar o `resolutivo-diagnostico` (Etapa 5).

Não leia antes de retomar um executor, antes de acionar o `cronograma` nem antes de um checkpoint: o risco está em começar algo grande com a janela no fim, e essas chamadas são curtas.

Como ler: use `mcp__ccd_session_mgmt__get_usage` (se aparecer só como ferramenta adiada, carregue-a uma vez com ToolSearch) e grave com o script, sem editar o arquivo à mão:
`py -3 .claude/hooks/gravar-uso.py --cinco <% 5-hour> --cinco-renova <resetsAt 5-hour> --semana <% Weekly> --semana-renova <resetsAt Weekly> --contexto <tokensUsed ÷ 2000>`
O contexto é medido contra um orçamento fixo de 200 mil tokens, e não contra o tamanho da janela, porque cada turno relê o contexto inteiro e o custo cresce com o tamanho, não com a porcentagem. No terminal, a barra de status já grava o medidor e esta seção não se aplica.

## Avisos do medidor de uso
Os avisos chegam automaticamente (hook), a cada mensagem do usuário e sempre que você aciona ou retoma um subagente.
O checkpoint é feito por você mesmo: leia `.claude/skills/encerrar-dia/SKILL.md` e siga a seção indicada (a skill não pode ser acionada por você, só pelo usuário).
- **ALERTA (5 h ≥ 80%)** → faça a seção **Checkpoint**, motivo "alerta de uso". Depois, continue apenas com tarefas P.
- **CRÍTICO (5 h ≥ 85% ou semana ≥ 93%)** → não inicie nada novo; siga a seção **Encerramento do dia** inteira, que inclui o relatório semanal em PDF (os limites ficam abaixo de 90%/95% para reservar cota para ele).
- **Semana ≥ 85%** → acione o `cronograma` para redistribuir as tarefas.
- **Contexto ≥ 70%** (cerca de 140 mil tokens) → faça a seção **Checkpoint**, motivo "antes de compactar", e oriente o usuário a digitar `/compact`. A retomada é recarregada sozinha depois.

## Fim da lista do dia
Se a lista terminou e ainda há cota (5 h abaixo de 60%), execute as tarefas de "Se sobrar cota hoje". Depois, informe o usuário e sugira `/encerrar-dia`.

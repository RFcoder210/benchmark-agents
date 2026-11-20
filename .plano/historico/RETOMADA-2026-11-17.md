# Retomada — 2026-11-17
Motivo do checkpoint: fim do dia (2º encerramento do mesmo dia; este bilhete substitui o anterior)

## Feito hoje
- README completo, com as seções pessoais (06f1731); lançador com duplo clique (63cfdb0).
- App pessoal: menu `app.py`, página Executar na etapa 1 (só conferência) e tema Grafite (40e3014).
- Revisão de todos os arquivos: 9 correções, entre elas a queda por valor inválido no `agente.py`, a cor única por versão no painel, o README e a LICENSE MIT (f6c224a).
- **Publicado no GitHub**: https://github.com/RFcoder210/benchmark-agents. O histórico foi reescrito com o e-mail noreply, e as 40 citações a códigos de commit foram atualizadas (f784521, ab331b9).

## Onde paramos
- Tudo commitado e enviado: a `main` local é igual à do GitHub.
- A página Executar ainda tem o botão desligado.

## Próxima ação (a primeira coisa de amanhã)
1. Etapa 2 da página Executar: opção `--rotulo` no `benchmark.py` (com teste), para rodar `v15-repeticao` sem editar o código.
2. Depois, ligar o botão: rodar em segundo plano com barra de progresso e aviso antes de gravar no CSV.

## Decisões tomadas que não estão em outro arquivo
- Ideia guardada para o futuro (não iniciar agora): um agente que faz a análise crítica do eval a partir do CSV e dos brutos.
- Sem CSS próprio no painel: só opções do tema. Diferenças aceitas em relação à maquete: etiquetas dos filtros em verde-água cheio e números grandes em Geist.
- Só a `main` foi publicada; os ramos `lote-noturno-2026-10-15` e `noite/2026-10-18` ficam locais (todo o conteúdo deles já está na main).
- Os códigos de commit citados nos bilhetes anteriores a hoje já foram trocados pelos novos.

## Aguardando o usuário
- Apagar, quando quiser, a cópia de segurança `..\benchmark-agents-backup-antes-da-publicacao.bundle`; ela tem o e-mail pessoal e não deve ser publicada.

## Ler se necessário
- `benchmark.py` (bloco `if __name__ == "__main__"`, onde o rótulo é definido).
- `app_pages/executar.py` e `testar_executar.py`.

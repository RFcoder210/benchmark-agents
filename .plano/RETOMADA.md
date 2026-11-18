# Retomada — 2026-11-17
Motivo do checkpoint: fim do dia

## Feito hoje
- README completo: seções "O que aprendi" e "Como este projeto foi construído", conferidas contra o CSV e confirmadas pelo usuário (d0a14e6).
- Lançador com duplo clique (`abrir_benchmark.bat` + atalho "Benchmark de agentes" na área de trabalho) (7a001c4).
- App pessoal (caminho 1): menu `app.py` com "Visão geral" e "Executar"; página Executar na etapa 1, só conferência (a8408d2).
- Tema Grafite aplicado, escolhido entre 3 maquetes; testes 43/43 (painel) e 9/9 (Executar) (a8408d2).
- Porte dos hooks de `.claude/` para Python commitado (06da62c); não foi feito nesta sessão, só conferido.

## Onde paramos
- A página Executar mostra o estado do Ollama e avisa que o rótulo `v15` já tem 45 execuções; o botão "Executar" está desligado.
- Nada sem commit, exceto este encerramento.

## Próxima ação (a primeira coisa de amanhã)
1. Etapa 2 da página Executar: opção `--rotulo` no `benchmark.py` (com teste), para rodar `v15-repeticao` sem editar o código.
2. Depois, ligar o botão: rodar em segundo plano com barra de progresso e aviso antes de gravar no CSV.

## Decisões tomadas que não estão em outro arquivo
- Ideia guardada para o futuro (não iniciar agora): um agente que faz a análise crítica do eval a partir do CSV e dos brutos. Por enquanto, as análises técnicas seguem na sessão.
- Sem CSS próprio no painel: só opções do tema. Diferenças aceitas em relação à maquete: etiquetas dos filtros em verde-água cheio e números grandes em Geist, não em Geist Mono.
- Ao mudar a pasta de páginas ou o `app.py`, é preciso reiniciar o painel: fechar a janela "Painel do benchmark" e abrir o atalho de novo.

## Aguardando o usuário
- Decidir se publica o repositório: licença, link do Ollama 0.40.4 em "Como rodar" e se `casos/casos_ocultos.json` vai junto.

## Ler se necessário
- `benchmark.py` (bloco `if __name__ == "__main__"`, onde o rótulo é definido).
- `app_pages/executar.py` e `testar_executar.py`.

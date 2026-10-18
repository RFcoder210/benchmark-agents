# Revisão geral da noite — 2026-10-18

Veredito: **COM_RESSALVAS** (nenhum problema grave; 3 ressalvas de forma/estado).

## 1. Integridade
- `instantaneo.sh` com os 32 protegidos da seção 7 → `instantaneo_fim.txt` (49 linhas). `diff` contra `instantaneo_inicio.txt`: **sem diferença** (saída 0). `.plano/historico` sem arquivo novo.
- `git diff --numstat main -- resultados/resultados.csv`: `45 0` (só acréscimos, 45 linhas `v8`).
- `git diff main -- agente.py`: vazio (agente idêntico à v7, como manda a decisão de reprovação).
- `casos/casos_ocultos.json` não foi aberto nesta revisão; o benchmark não foi rodado.

## 2. Testes
- `.venv\Scripts\python testar_comparar.py`: saída 0; "Total: 40/45" (o script lê o `brutos_*.json` mais recente por data, agora o da v8; por isso a verificação inicial da noite mostrava 34/45 da v7).
- `.venv\Scripts\python testar_dashboard.py`: **36/36** verificações (eram 35; a nova vem da v8 em `OFICIAIS`).
- `comparar_versoes.py v7 v8` (com `PYTHONIOENCODING=utf-8`; sem isso o console cp1252 quebra no ✓, defeito antigo e não da noite): saída idêntica à copiada na análise; ganhos C02, C07, C14; perda C10; "Decisão: MANTER v7".
- Números recalculados do CSV e conferidos (12): 40/45; registrar 21/24, perguntar 13/15, ignorar 6/6; tokens médios 2075,5 (v8) e 1804,3 (v7); tempo 3,44 s e 3,60 s; erros acao 4/campos 1 (v8) e acao 9/campos 2 (v7); por ordem 14/13/13; C01 2085 tokens (v6 e v8) e 1813 (v7); tokens v6 = v8 nas 45 respostas; C10 2/3 com falha na invertida. Os dois textos `registrar_gasto: valor 0.0, ...` do C10 estão no `brutos_v8_2026-10-18_2032.json`. Citação da RETOMADA ("cerca de 40/45 ... C10 pode ficar 2/3") confere com `.plano/RETOMADA.md`, linha 12. Nenhum número sem origem.

## 3. Coerência entre tarefas
Lote de uma tarefa só (V8). Os números são os mesmos no commit `dc5bc41`, no `benchmark.py`, no `CLAUDE.md`, no `dashboard.py` e na análise. Ressalvas:
1. `CLAUDE.md`, linha 45 (item da v7) ainda termina com "Próximo passo: v8 = v7 + regra de categoria da v6 (régua normal)." — desatualizado; a linha 38 e o novo item da v8 (linha 46) já dizem que o próximo passo está em aberto.
2. `CLAUDE.md`, linha 46, resume "C08 continua 0/3", mas o modo de falha mudou na ordem original: a v8 perguntou o **valor** ("Qual foi o valor do abastecimento?", com 150 na mensagem). A análise registra isso (seção 6); o CLAUDE.md não. Na ordem girada, `campos_faltantes ['categoria']` acompanha a pergunta "Qual foi a forma de pagamento?" (incoerência do próprio modelo, registrada na análise).
3. `LOTE.md`, critério (b) ("`VERSAO_AGENTE = "v8"`") contradiz a seção 6 (reprovada → espelhar a v6). O executor seguiu a seção 6 (`VERSAO_AGENTE = "v7"`, v8 no comentário de histórico), o que é coerente com o padrão da v5/v6. Defeito do lote, não da execução; já anotado pela revisão individual.

## 4. Estado
- `REGISTRO.md`: V8 passou por "em andamento" → "execução concluída" → "revisão individual APROVADA" → "concluida"; nada ficou em andamento.
- Git: `git log main..noite/2026-10-18` = 1 commit (`dc5bc41`, v8 reprovada), que corresponde à única tarefa aprovada; nenhum commit em `main` fora do branch. Fora do commit: só `REGISTRO.md` (linha de cota, do orquestrador) e `instantaneo_fim.txt` (desta revisão).
- `HISTORICO` ("v8": "reprovada"), `OFICIAIS` (com v8), comentário de `VERSAO_AGENTE` e CLAUDE.md seguem o padrão do commit `7617401` (v6).
- `.plano/DIARIO.md`, linha 10: o Dia 4 continua "(em andamento)" (escrito na preparação; deve ser fechado no encerramento do dia).

## 5. Pendências do usuário
1. Decidir o próximo passo após a v8 reprovada — `CLAUDE.md` linhas 38 e 46; `resultados/analise_v8_2026-10-18.md` linha 125.
2. Avaliar se a régua deve distinguir perda por "perguntar demais" (C10 3/3 → 2/3) de perda por inventar dado — só o usuário pode mudar a régua — `resultados/analise_v8_2026-10-18.md` linha 125.
3. Atualizar a linha 45 do `CLAUDE.md` (ressalva 1) e, se quiser, registrar no item da v8 a nova falha do C08 (pergunta o valor dado) — ressalva 2.
4. Fechar a linha do Dia 4 em `.plano/DIARIO.md` (linha 10) no `/encerrar-dia`.
5. Corrigir, para próximos lotes, a contradição entre o critério (b) e a seção 6 do modelo de lote (`LOTE.md`, seções 5 e 6).
6. Restaurar as notificações silenciadas (`LOTE.md`, seção 10) e decidir sobre o merge do branch `noite/2026-10-18` em `main` (seção 11: sem push, sem merge).
7. Adiados pelo usuário (sem ação da noite): vocabulário das categorias/C08, redução de tokens, hook `testar-ao-parar.ps1` — `LOTE.md`, seção 12.

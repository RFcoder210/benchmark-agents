# Retomada — 2026-10-15/16

## Feito na noite de 15/10 (tarefa agendada, sem o usuário)
- Branch **`lote-noturno-2026-10-15`** (não entrou em `main`). Agente oficial continua **v2**, idêntico.
- `agente.py`: `interpretar()` aceita `temperatura` e `prompt_sistema` opcionais; `montar_prompt(ordem, extras)` monta variantes (assert confere que reproduz o prompt v2). `benchmark.py`: parâmetros opcionais de rótulo/temperatura/prompt; padrão inalterado.
- `lote.py` rodou 6 rodadas de calibração (v2-loteA, v2-t0.7, v2-ordemB/C/D, v3-candidato); `analisar_lote.py` gerou as tabelas.
- Principais números: t=0 quase determinístico (só C14 variou); reordenar exemplos vira 2–4 casos (25–30/45) → limiar de ruído; v3-candidato 30/45 (ganhou C14, perdeu C05), dentro do ruído. C10/C05 falham por escrever a ferramenta como texto.

## Próxima ação (a primeira coisa de amanhã, após 13:30)
1. Restaurar as notificações do app (silenciadas em 15/10 a pedido do usuário até 16/10 13:30) com ccd_settings set_setting: notification_sound=system; task_complete_notifications, question_notifications e permission_request_notifications=banner.
2. Ler `resultados/relatorio_lote_2026-10-15.md`, responder às perguntas guiadas e decidir se aprova a v3 e se o branch entra em main.

## Decisões que não estão em outro arquivo
- A hipótese "exemplo da poupança faz o C10 ser ignorado" ficou fraca: o C10 entende certo, mas escreve a chamada como texto (ver relatório).

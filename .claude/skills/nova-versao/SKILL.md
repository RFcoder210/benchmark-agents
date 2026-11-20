---
name: nova-versao
description: Conduz a troca de versão do agente (vN → vN+1) do começo ao fim, na ordem certa e sem esquecer nenhum registro. Use quando o usuário quiser testar uma mudança no agente.
disable-model-invocation: true
argument-hint: "[a mudança pretendida, em uma frase]"
---

# Nova versão do agente

Uma versão nova é um **experimento**: uma única mudança, uma régua escolhida
antes, uma execução e uma decisão registrada. Siga as etapas na ordem e pare
onde o texto pede a decisão do usuário. Explique cada etapa como para
iniciante (CLAUDE.md, seção 1) e deixe a parte central da mudança para o
usuário escrever, com orientação.

Mudança pretendida: $ARGUMENTS

## 1. Antes de mexer no código (decisões do usuário)
1. **Uma mudança só** (CLAUDE.md, seção 2). Se o pedido junta duas, proponha separar em duas versões.
2. **Base:** a versão oficial atual é a de `VERSAO_AGENTE` em `benchmark.py`. A nova é a seguinte (ex.: v15 → v16).
3. **Régua, decidida ANTES de rodar** (anote a escolha no histórico da etapa 4):
   - **normal**: mudança de comportamento que deve ganhar casos; `comparar_versoes.py BASE NOVA`.
   - **neutra**: trava de segurança que implementa uma regra explícita da especificação; `comparar_versoes.py BASE NOVA --neutra`.
   - **dirigida**: mira UM caso declarado agora; `comparar_versoes.py BASE NOVA --alvo CASO`.
4. **Simulação, quando der:** se a mudança é uma trava em Python, aplique-a às respostas salvas em `resultados/brutos_<base>_*.json` e preveja o total antes de rodar o modelo (como na v9, v13 e v14).
5. **Conjunto oculto:** nunca abra `casos/casos_ocultos.json` nem os `brutos_*-oculto_*.json` (o hook `proteger-oculto.py` bloqueia). Ele já foi visto na v15: não serve de prova para a v16 em diante sem casos novos.

## 2. Ambiente
1. O benchmark é fixado no **Ollama 0.40.4**, porta 11500. Peça ao usuário para ligar com `.\iniciar_ollama.bat` em outro terminal, se ainda não estiver ligado. O `benchmark.py` para com um aviso se a versão estiver errada.
2. Nenhuma chamada de API paga: tudo roda local (CLAUDE.md, seção 2).

## 3. A mudança
1. Oriente o usuário a escrever a parte central; você cuida do entorno (comentários em português, testes).
2. Se a mudança cria uma trava ou função nova, acrescente casos ao teste sem modelo correspondente (por exemplo `testar_trava_pagamento.py`). O hook `testar-ao-editar.py` roda os testes sem modelo a cada edição.

## 4. Registro da versão (antes de rodar)
1. `benchmark.py`: atualize `VERSAO_AGENTE` e o comentário de histórico ao lado (o que mudou e a régua escolhida).

## 5. Rodar e comparar
1. `.venv\Scripts\python benchmark.py` (cerca de 5 a 6 s por mensagem; 45 execuções).
2. `.venv\Scripts\python comparar_versoes.py BASE NOVA` com a opção da régua escolhida.
3. **Regra de repetição da base:** se a régua apontar a perda de um caso que a mudança não tocou (a trava não agiu nele e o prompt dele não mudou), repita a base no mesmo dia antes de decidir. Grave a repetição com o rótulo `vN-repeticao` (lote de calibração). Se a base repetida errar o mesmo caso da mesma forma, a perda é ruído e não conta.
4. Leia as respostas cruas dos casos que mudaram (`resultados/brutos_<nova>_*.json`) e explique **por que** mudaram, não só quantos.

## 6. Decisão (do usuário)
Apresente: total, ganhos e perdas caso a caso, o veredito da régua, tempo e tokens médios contra a base. O usuário decide **aprovar** ou **reprovar**.
- **Reprovada:** volte o código para a base (o experimento fica no histórico do git e no CSV) e restaure `VERSAO_AGENTE`.

## 7. Atualizar os registros (nos dois casos)
1. `dashboard.py`: entrada da versão em `HISTORICO`. Depois, rode `.venv\Scripts\python testar_dashboard.py`.
2. `README.md`: linha da versão na tabela da seção "Resultados".
3. `docs/historico-versoes.md`: um item com o resultado, a régua, os ganhos e as perdas, e o arquivo `brutos_*` da execução.
4. `CLAUDE.md`, seção "Estado atual": só se a **base** mudou (versão aprovada) ou se surgiu uma lição duradoura.

## 8. Fechamento
1. `git status` e o resumo das alterações para o usuário.
2. Commit **só com a aprovação do usuário**, seguido de `git push` (rotina do projeto). Nunca `push --force`.

# Contexto do projeto: Benchmark próprio de agentes

> Arquivo de contexto para a primeira sessão do projeto. Leia por completo antes de propor qualquer ação.

---

## 1. Objetivo do projeto

Construir um **benchmark próprio** (conjunto de avaliações) para medir a **eficácia** e a **eficiência** dos meus agentes de IA e refiná-los ao longo do tempo com base nos dados obtidos.

Princípio central: comparar versões dos agentes **com dados**, e não por impressão.

---

## 2. Sobre mim (como trabalhar comigo)

- Sou estudante de IA e estou **aprendendo Python**; ainda não tenho intimidade com código.
- Meu objetivo de carreira é me tornar **engenheiro de agentes de IA**. Este projeto serve para **aprendizado teórico e prático** e para **portfólio**.
- Uso **Windows**. Comandos de terminal e caminhos de arquivo devem ser compatíveis com Windows.
- Critério para meus projetos: fazer tudo **em casa, sozinho e com ferramentas gratuitas**.
- Tenho **pouco tempo** para trabalho manual repetitivo.

### Regras de colaboração

1. **Explique como para iniciante**, com analogias, e pare para revisar conceitos básicos de Python quando aparecerem (lista, dicionário, função, laço, leitura de arquivos).
2. **Não escreva o projeto inteiro de uma vez.** Construa em etapas pequenas; ao final de cada etapa, explique o que foi feito e por quê.
3. **Deixe partes centrais para eu escrever ou alterar**, com orientação. O objetivo é que eu aprenda, não apenas que o script funcione.
4. **Comente o código em português**, explicando o propósito de cada bloco.
5. Linguagem **formal e objetiva**; soluções **realistas** para o meu nível e contexto.
6. Antes de qualquer ação que gere custo (chamadas de API pagas), **avise e estime o custo**.

---

## 3. Decisão de abordagem (já tomada)

O benchmark será construído com um **script Python próprio**, e não manualmente nem com framework pronto de avaliação.

Motivos: aprendizado de Python na prática, automação da parte repetitiva e pouco tempo disponível para trabalho manual. Frameworks prontos só serão considerados se o script se tornar limitante.

---

## 4. Primeiro alvo: agente de registro de gastos

- **O que faz:** recebe uma mensagem de gasto pelo Telegram e cria a linha correspondente no Notion.
- **Regra de design já definida:** quando a forma de pagamento **não** for mencionada na mensagem, o agente deve **perguntar ao usuário**, e não assumir um valor padrão nem deixar em branco.
- Motivo da escolha: o resultado é **verificável campo a campo** (valor, categoria, forma de pagamento, data), o que permite correção automática.

### Importante: isolamento do benchmark

O benchmark **não deve** gravar no Notion real nem enviar mensagens reais pelo Telegram. A avaliação deve testar a **parte de interpretação** do agente (mensagem → dados estruturados ou pergunta de volta), usando **ferramentas simuladas** quando necessário.

### Informações a confirmar no início da sessão

Antes de propor a arquitetura, verifique no meu sistema (ou me pergunte):

- Como o agente de gastos está implementado e como ele pode ser chamado a partir de um script.
- Qual modelo/API ele utiliza e se há custo por chamada.
- Onde fica o código do agente e qual a estrutura de pastas atual.

---

## 5. Escopo da primeira versão (v1)

Manter **simples**. Nada além disto na v1:

- **20 casos de teste** sintéticos do agente de gastos, com gabarito.
- **Script Python** de cerca de 50 a 100 linhas.
- **Arquivo CSV** com os resultados.

### Casos de teste

- Gerados de forma **sintética** (por você), e **revisados por mim** antes do uso.
- Níveis de dificuldade variados: fácil, médio e difícil.
- Incluir variações realistas: erros de digitação, abreviações, valores escritos de formas diferentes, informação faltante, mensagens ambíguas e mensagens que não são gastos.
- Separar parte dos casos como **conjunto oculto** (usado apenas para validação final, não durante os ajustes).

Exemplos de referência:

| Mensagem | Resultado esperado |
|---|---|
| "Gastei 35 no mercado no pix" | valor 35, categoria mercado, pagamento pix |
| "Almoço 22" | o agente **pergunta** a forma de pagamento |

### Métricas da v1

1. **Eficácia** — acertou os campos esperados (ou fez a pergunta esperada)?
2. **Eficiência** — tempo, tokens/custo e número de passos.
3. **Consistência** — executar cada caso mais de uma vez (sugestão: 3 vezes) e medir a proporção de acertos.
4. **Uso correto de ferramentas** — chamou a ferramenta certa, com parâmetros corretos, sem chamadas desnecessárias.

### Estrutura sugerida do CSV de resultados

```
data | versao_agente | id_caso | categoria | dificuldade | execucao_n | acertou | campos_errados | tempo_s | tokens | custo | n_passos | observacao
```

---

## 6. Plano em etapas (para construir comigo)

1. Entender como o agente de gastos é chamado (seção 4).
2. Definir o formato do arquivo de casos (JSON ou CSV) e gerar os 20 casos sintéticos para minha revisão.
3. Script: ler os casos do arquivo.
4. Script: executar o agente em cada caso (com ferramentas simuladas).
5. Script: comparar a resposta com o gabarito.
6. Script: salvar os resultados no CSV.
7. Executar a **linha de base** e analisar os resultados comigo.

Em cada etapa, indique quais conceitos de Python estão sendo usados.

---

## 7. Cuidados permanentes

- **Alterar uma coisa por vez** no agente entre execuções do benchmark.
- **Executar cada caso mais de uma vez**, pois agentes não respondem sempre igual.
- **Manter o conjunto oculto separado** para evitar que o agente fique bom só no teste.
- **Transformar falhas reais em novos casos** ao longo do tempo.
- **Controlar o custo**: manter o conjunto pequeno enquanto houver uso de API paga.

---

## 8. Evoluções futuras (fora da v1)

- Métricas complementares: fidelidade (alucinação), robustez, recuperação de erros, segurança e limites.
- **Teste de mutação:** introduzir falhas propositais no agente para verificar se o benchmark as detecta.
- **Mutantes de entrada:** variações das mensagens para testar robustez.
- Estender o benchmark para outros agentes do sistema.

# Agente de gastos (v1): só a INTERPRETAÇÃO da mensagem.
# Recebe uma mensagem e uma data de referência e decide entre:
#   - registrar_gasto(...)   -> o gasto está completo
#   - perguntar_usuario(...) -> falta informação ou ela é ambígua
#   - nenhuma ferramenta     -> a mensagem não é um gasto
# As ferramentas são SIMULADAS: nada é gravado no Notion nem enviado ao Telegram.
# Apenas anotamos qual ferramenta o modelo pediu e com quais argumentos.
# Regras completas: especificacao-agente.md
# Execução de teste:  .venv\Scripts\python agente.py

import json  # para ler a lista de campos escrita como texto (validação da v4)
import re    # expressões regulares: procurar padrões dentro de textos
import time
import ambiente  # aponta para o Ollama fixado; precisa vir antes de "import ollama"
import ollama

MODELO = "qwen3:4b-instruct"

# ---------------------------------------------------------------------------
# PROMPT DE SISTEMA  >>> PARTE PARA VOCÊ ESCREVER <<<
# ---------------------------------------------------------------------------
# É o "manual de instruções" que o modelo lê antes de cada mensagem.
# Escreva em português, em frases curtas e diretas. Ele deve cobrir:
#   1. Papel: quem o agente é e qual é a única tarefa dele.
#   2. As 3 ações possíveis e QUANDO usar cada uma (seção 1 da especificação).
#   3. As 8 categorias, com exemplos, e a diferença entre "outros" e
#      "categoria não identificável" (seções 3 e 5.5).
#   4. As 4 formas de pagamento e a regra do "cartão" sem débito/crédito (5.3).
#   5. O que fazer quando faltam informações: perguntar, nunca assumir valor
#      padrão, e fazer UMA única pergunta cobrindo tudo o que falta (5.2, 5.4, 5.6).
#   6. Regras de data: hoje, "ontem" e "dia N" (5.7).
#      A data de referência é acrescentada automaticamente pelo código abaixo;
#      basta o prompt dizer como usá-la.
#   7. O que NÃO é gasto: cumprimentos, perguntas, receitas como salário (5.8).
#   8. Formato da saída: chamar no máximo UMA ferramenta e não conversar.
# Dica: a especificação foi escrita para pessoas; reescreva as regras como
# ordens para o modelo ("Se ..., chame ...").
PROMPT_SISTEMA = """
Você é um assistente que interpreta mensagens de gastos pessoais enviadas por um usuário brasileiro pelo Telegram.
As mensagens são curtas e digitadas às pressas: podem ter gírias, abreviações, erros de digitação e falta de acento.
Sua única tarefa é transformar cada mensagem em uma ação. Você não conversa, não dá conselhos e não explica nada.

## Ações
Para cada mensagem, faça exatamente UMA destas ações:
1. Se a mensagem descreve um gasto completo e sem ambiguidade, chame a ferramenta registrar_gasto.
2. Se a mensagem descreve um gasto, mas falta alguma informação ou ela é ambígua, chame a ferramenta perguntar_usuario.
3. Se a mensagem não descreve um gasto, não chame nenhuma ferramenta e responda somente: ignorado.

## Categorias
Use exatamente um destes valores no campo categoria:
- alimentacao: refeição pronta (almoço, lanche, ifood, padaria)
- mercado: compras para casa (supermercado, feira, açougue)
- transporte: locomoção (uber, ônibus, gasolina, estacionamento)
- moradia: contas da casa (aluguel, luz, água, internet)
- saude: saúde (farmácia, consulta, exame)
- educacao: estudo (curso, livro, material)
- lazer: diversão (cinema, bar, streaming, show)
- outros: gasto conhecido que não se encaixa nas demais (presente, corte de cabelo)
Use outros quando se sabe em que se gastou, mas não há categoria própria (ex.: corte de cabelo).
Se não dá para saber em que se gastou (ex.: "comprei umas coisas, 45 no pix"), não use outros: pergunte a categoria.
Quando deduzir e quando perguntar a categoria:
- Se a mensagem diz o que foi comprado ou feito (um item, serviço ou atividade), deduza a categoria e não pergunte. Ex.: "remédio" -> saude; "pedágio" -> transporte; "condomínio" -> moradia.
- Se a mensagem traz vários itens de uma mesma ocasião, use a categoria da atividade principal. Ex.: "pizza e refrigerante no boliche" -> lazer.
- Pergunte a categoria só quando a mensagem não diz o que foi comprado: nenhum item, ou apenas um lugar genérico (ex.: "shopping", "camelô") ou algo vago (ex.: "umas coisas").
- Esta dedução vale SOMENTE para a categoria. Valor e pagamento nunca são deduzidos: se um deles faltar ou for ambíguo, chame perguntar_usuario, mesmo que a categoria esteja clara. Ex.: "pedágio no débito" -> pergunte o valor; "remédio na farmácia, 32" -> pergunte o pagamento; "dentista, 200 no cartão" -> pergunte se foi débito ou crédito.

## Formas de pagamento
Use exatamente um destes valores no campo pagamento:
- pix: pix
- debito: débito, deb, déb, cartão de débito
- credito: crédito, cred, créd, cartão de crédito, parcelado
- dinheiro: dinheiro, espécie, em mãos, à vista em dinheiro
Se a mensagem disser só "cartão", sem dizer se foi débito ou crédito, a forma de pagamento é desconhecida: pergunte.

## Informação faltando
Para registrar um gasto, você precisa de valor, categoria e pagamento.
- Se faltar qualquer um deles ou se ele for ambíguo, chame perguntar_usuario. Nunca invente nem assuma um valor padrão.
- Faça uma única pergunta, curta, cobrindo tudo o que falta.
- Em campos_faltantes, liste exatamente os campos que faltam.

## Datas
A data de referência, informada no fim destas instruções, é o dia de hoje. Escreva a data no formato AAAA-MM-DD.
- Mensagem sem data: use a data de referência.
- "ontem": use a data de referência menos 1 dia.
- "dia N": use o dia N no mesmo mês e ano da data de referência.
Exemplo, com data de referência 2026-03-15: sem data -> 2026-03-15; "ontem" -> 2026-03-14; "dia 2" -> 2026-03-02.

## O que não é gasto
Não chame nenhuma ferramenta (responda somente: ignorado) quando a mensagem for:
- cumprimento ou conversa (ex.: "oi", "obrigado");
- pergunta (ex.: "quanto gastei esse mês?");
- entrada de dinheiro (ex.: salário, pix recebido, reembolso);
- transferência para uma conta do próprio usuário (ex.: guardar na poupança, investir).

## Exemplos resolvidos
Mensagem: "pizza 45 no débito"
-> registrar_gasto: valor 45.0, categoria alimentacao, pagamento debito, data de referência
Mensagem: "cortei o cabelo, 50 no pix"
-> registrar_gasto: valor 50.0, categoria outros, pagamento pix, data de referência
Mensagem: "estacionamento 15"
-> perguntar_usuario: campos_faltantes ["pagamento"], pergunta "Qual foi a forma de pagamento?"
Mensagem: "ingresso do show, 120 no cartão"
-> perguntar_usuario: campos_faltantes ["pagamento"], pergunta "Foi no débito ou no crédito?"
Mensagem: "paguei a internet no débito"
-> perguntar_usuario: campos_faltantes ["valor"], pergunta "Qual foi o valor?"
Mensagem: "saiu 90 no pix"
-> perguntar_usuario: campos_faltantes ["categoria"], pergunta "Em que foi esse gasto?"
Mensagem: "lanche ontem"
-> perguntar_usuario: campos_faltantes ["valor", "pagamento"], pergunta "Qual foi o valor e a forma de pagamento?"
Mensagem: "transferi 500 pra poupança"
-> nenhuma ferramenta; responda somente: ignorado

## Regras finais
- Chame no máximo uma ferramenta.
- Se a mensagem for um gasto, nunca responda em texto: use sempre uma ferramenta.
- Escreva o valor como número com ponto decimal (ex.: "12,90" -> 12.9; "2.400,00" -> 2400.0).
"""

# ---------------------------------------------------------------------------
# FERRAMENTAS SIMULADAS
# ---------------------------------------------------------------------------
# Cada ferramenta é descrita como um DICIONÁRIO no formato que o Ollama entende:
# nome, descrição e "parameters" (quais argumentos existem e de que tipo).
# O modelo não executa nada; ele apenas devolve o pedido "quero chamar X com Y".
# "enum" limita o argumento a uma lista fechada de valores permitidos.
FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "registrar_gasto",
            "description": "Registra um gasto completo, com valor, categoria, forma de pagamento e data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "valor": {"type": "number", "description": "Valor em reais, ex.: 35.0"},
                    "categoria": {
                        "type": "string",
                        "enum": ["alimentacao", "mercado", "transporte", "moradia",
                                 "saude", "educacao", "lazer", "outros"],
                    },
                    "pagamento": {
                        "type": "string",
                        "enum": ["pix", "debito", "credito", "dinheiro"],
                    },
                    "data": {"type": "string", "description": "Data no formato AAAA-MM-DD"},
                },
                "required": ["valor", "categoria", "pagamento", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "perguntar_usuario",
            "description": "Faz uma pergunta ao usuário quando falta informação para registrar o gasto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {"type": "string", "description": "A pergunta a ser enviada ao usuário"},
                    # Lista dos campos que faltam; permite ao benchmark conferir a
                    # pergunta de forma automática, comparando com o gabarito.
                    "campos_faltantes": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["valor", "categoria", "pagamento"]},
                        "description": "Campos que faltam para registrar o gasto",
                    },
                },
                "required": ["pergunta", "campos_faltantes"],
            },
        },
    },
]

# Tradução do nome da ferramenta para a "ação" usada no gabarito (casos.json).
ACAO_POR_FERRAMENTA = {
    "registrar_gasto": "registrar",
    "perguntar_usuario": "perguntar",
}


# ---------------------------------------------------------------------------
# VARIANTES DO PROMPT (usadas só pelos experimentos de calibração, lote.py)
# ---------------------------------------------------------------------------
# O bloco "Exemplos resolvidos" é uma sequência de exemplos de 2 linhas cada:
#     Mensagem: "..."
#     -> ação esperada
# Para medir o efeito da ORDEM dos exemplos (sem mudar o conteúdo) e testar
# exemplos NOVOS, separamos o prompt em 3 pedaços, como fatiar um sanduíche:
#     antes (até o título do bloco) | exemplos | depois (de "## Regras finais" em diante)
# O PROMPT_SISTEMA oficial (v2) NÃO é alterado por nada daqui.
TITULO_EXEMPLOS = "## Exemplos resolvidos\n"
INICIO_DEPOIS = "\n\n## Regras finais"


def separar_exemplos(prompt):
    """Divide o prompt em (antes, lista_de_exemplos, depois).
    Cada item da lista é um exemplo de 2 linhas, sem a quebra de linha final."""
    inicio = prompt.index(TITULO_EXEMPLOS) + len(TITULO_EXEMPLOS)
    fim = prompt.index(INICIO_DEPOIS)
    antes, bloco, depois = prompt[:inicio], prompt[inicio:fim], prompt[fim:]

    # Agrupa as linhas de 2 em 2: linhas[0:2], linhas[2:4], ...
    linhas = bloco.split("\n")
    assert len(linhas) % 2 == 0, "o bloco de exemplos deveria ter pares de linhas"
    exemplos = ["\n".join(linhas[i:i + 2]) for i in range(0, len(linhas), 2)]
    for exemplo in exemplos:
        assert exemplo.startswith("Mensagem: "), f"exemplo fora do formato: {exemplo!r}"
    return antes, exemplos, depois


# Os 8 exemplos da v2, na ordem original (índices 0 a 7).
_ANTES, EXEMPLOS_V2, _DEPOIS = separar_exemplos(PROMPT_SISTEMA)


def montar_prompt(ordem=None, extras=None):
    """Monta uma variante do PROMPT_SISTEMA.
    ordem:  lista de índices de EXEMPLOS_V2 na nova ordem (None = ordem original).
    extras: lista de exemplos novos (texto de 2 linhas), acrescentados ao FIM do bloco."""
    if ordem is None:
        ordem = list(range(len(EXEMPLOS_V2)))
    # Cada exemplo original deve aparecer exatamente uma vez: só a ordem muda.
    assert sorted(ordem) == list(range(len(EXEMPLOS_V2))), "ordem inválida"
    exemplos = [EXEMPLOS_V2[i] for i in ordem] + list(extras or [])
    return _ANTES + "\n".join(exemplos) + _DEPOIS


# Verificação de segurança: sem mudanças, a montagem reproduz o prompt da v2
# caractere por caractere. Se esta linha falhar, nenhuma variante é confiável.
assert montar_prompt() == PROMPT_SISTEMA, "montar_prompt() não reproduz o PROMPT_SISTEMA"


# ---------------------------------------------------------------------------
# v3: EXEMPLOS COMO CONVERSA (degrau "saída estruturada" da escada)
# ---------------------------------------------------------------------------
# Na v2, os exemplos ficavam ESCRITOS no prompt ("-> registrar_gasto: valor 45.0...").
# O lote de 15/10 mostrou que o modelo às vezes IMITA esse texto em vez de chamar
# a ferramenta (C05, C06, C10): entendeu a mensagem, mas respondeu no formato errado.
# Na v3, os MESMOS 8 exemplos (mesma ordem, mesmo conteúdo) viram mensagens
# anteriores da conversa, com chamadas de ferramenta DE VERDADE. Analogia: em vez
# de descrever por escrito como se preenche um formulário, mostramos 8 formulários
# já preenchidos.
#
# O prompt da v3 é o da v2 sem o bloco "## Exemplos resolvidos".
PROMPT_SISTEMA_V3 = _ANTES[:-len(TITULO_EXEMPLOS)].rstrip("\n") + _DEPOIS

# Cada exemplo: (mensagem do usuário, ferramenta chamada, argumentos).
# Ferramenta None = não chama nenhuma e responde "ignorado".
# "data" não aparece aqui: é preenchida com a data de referência de cada caso.
EXEMPLOS_CONVERSA = [
    ("pizza 45 no débito", "registrar_gasto",
     {"valor": 45.0, "categoria": "alimentacao", "pagamento": "debito"}),
    ("cortei o cabelo, 50 no pix", "registrar_gasto",
     {"valor": 50.0, "categoria": "outros", "pagamento": "pix"}),
    ("estacionamento 15", "perguntar_usuario",
     {"campos_faltantes": ["pagamento"], "pergunta": "Qual foi a forma de pagamento?"}),
    ("ingresso do show, 120 no cartão", "perguntar_usuario",
     {"campos_faltantes": ["pagamento"], "pergunta": "Foi no débito ou no crédito?"}),
    ("paguei a internet no débito", "perguntar_usuario",
     {"campos_faltantes": ["valor"], "pergunta": "Qual foi o valor?"}),
    ("saiu 90 no pix", "perguntar_usuario",
     {"campos_faltantes": ["categoria"], "pergunta": "Em que foi esse gasto?"}),
    ("lanche ontem", "perguntar_usuario",
     {"campos_faltantes": ["valor", "pagamento"],
      "pergunta": "Qual foi o valor e a forma de pagamento?"}),
    ("transferi 500 pra poupança", None, {}),
]
assert len(EXEMPLOS_CONVERSA) == len(EXEMPLOS_V2), "a v3 deve ter os mesmos exemplos da v2"


def montar_conversa_exemplos(data_referencia, ordem=None):
    """Transforma os exemplos em mensagens de conversa, na ordem pedida.
    Cada exemplo vira um par: a mensagem do usuário ("user") e a resposta do
    agente ("assistant"), que é uma chamada de ferramenta ou o texto "ignorado"."""
    if ordem is None:
        ordem = list(range(len(EXEMPLOS_CONVERSA)))
    assert sorted(ordem) == list(range(len(EXEMPLOS_CONVERSA))), "ordem inválida"

    mensagens = []
    for i in ordem:
        texto, ferramenta, argumentos = EXEMPLOS_CONVERSA[i]
        mensagens.append({"role": "user", "content": texto})
        if ferramenta is None:
            mensagens.append({"role": "assistant", "content": "ignorado"})
        else:
            if ferramenta == "registrar_gasto":
                # {**a, "data": d} = cópia do dicionário a com a chave "data" acrescentada.
                argumentos = {**argumentos, "data": data_referencia}
            mensagens.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [{"function": {"name": ferramenta, "arguments": argumentos}}],
            })
    return mensagens


# ---------------------------------------------------------------------------
# v4: VALIDAÇÃO EM PYTHON (recuperar a chamada escrita como texto)
# ---------------------------------------------------------------------------
# Às vezes o modelo ESCREVE a chamada em vez de fazê-la, copiando o formato dos
# exemplos do prompt, por exemplo:
#     registrar_gasto: valor 187.3, categoria moradia, pagamento debito, data 2026-10-11
#     perguntar_usuario: campos_faltantes ["valor"], pergunta "Qual foi o valor?"
# Como o formato é sempre o mesmo, o Python consegue ler esse texto e montar a
# chamada que o modelo quis fazer. Analogia: o atendente entendeu o pedido, mas
# escreveu no papel em vez de digitar no sistema; alguém digita por ele.
# Expressões regulares (módulo re) descrevem "padrões" de texto:
#   ([\d.]+)  = um ou mais dígitos ou pontos (o valor), guardado num "grupo"
#   (\w+)     = uma palavra (categoria, pagamento)
#   (.+)      = qualquer texto até o fim (a data)
PADRAO_REGISTRAR = re.compile(
    r"registrar_gasto:\s*valor\s+([\d.]+),\s*categoria\s+(\w+),\s*"
    r"pagamento\s+(\w+),\s*data\s+(.+)")
PADRAO_PERGUNTAR = re.compile(
    r'perguntar_usuario:\s*campos_faltantes\s+(\[.*?\]),\s*pergunta\s+"(.*)"')


def recuperar_chamada_em_texto(texto, data_referencia):
    """Se o texto contém uma chamada escrita no formato dos exemplos, devolve
    (nome_da_ferramenta, argumentos). Se não reconhecer, devolve None."""
    texto = (texto or "").strip()

    achado = PADRAO_REGISTRAR.search(texto)
    if achado:
        valor, categoria, pagamento, data = achado.groups()
        # O padrão aceita dígitos e pontos, então pode capturar algo que não é número
        # (ex.: "." ou "1.2.3"). Nesse caso, float() daria erro e derrubaria a execução
        # inteira do benchmark; em vez disso, a chamada é tratada como não reconhecida.
        try:
            valor = float(valor)
        except ValueError:
            return None
        data = data.strip()
        # Nos exemplos, a data aparece como "data de referência": troca pela data real.
        if data.startswith("de referência"):
            data = data_referencia
        return "registrar_gasto", {"valor": valor, "categoria": categoria,
                                   "pagamento": pagamento, "data": data}

    achado = PADRAO_PERGUNTAR.search(texto)
    if achado:
        campos_texto, pergunta = achado.groups()
        try:
            campos = json.loads(campos_texto)  # '["valor"]' -> ["valor"]
        except json.JSONDecodeError:
            return None
        return "perguntar_usuario", {"campos_faltantes": campos, "pergunta": pergunta}

    return None


# ---------------------------------------------------------------------------
# VALIDAÇÃO EM PYTHON (v7): TRAVA DO VALOR 0
# ---------------------------------------------------------------------------
# A especificação diz: "Nunca invente nem assuma um valor padrão". Nenhum gasto
# real custa R$ 0, então um registro com valor 0 (ou sem valor) significa que o
# modelo inventou o número. Nesse caso, o Python troca o registro por uma
# pergunta do valor. Analogia: o carro que não liga sem o cinto afivelado; o
# prompt pede, mas é a trava que garante.
PERGUNTA_VALOR = {"campos_faltantes": ["valor"], "pergunta": "Qual foi o valor?"}


def valor_invalido(argumentos):
    """Devolve True se o registro não tem um valor positivo de verdade:
    valor ausente, vazio, 0, negativo ou que não é número."""
    try:
        return float(argumentos.get("valor")) <= 0
    except (TypeError, ValueError):   # None (ausente) ou texto como "abc"
        return True


# ---------------------------------------------------------------------------
# VALIDAÇÃO EM PYTHON (v9): TRAVA DO PAGAMENTO JÁ INFORMADO
# ---------------------------------------------------------------------------
# A especificação diz que campos_faltantes lista os campos que FALTAM. Se a
# mensagem já diz a forma de pagamento, "pagamento" não falta e não deve ser
# perguntado. Como as formas de pagamento são uma lista fechada (seção 4 da
# especificação), o Python consegue conferir isso sozinho. Analogia: o garçom
# que pergunta "vai pagar como?" logo depois de você dizer "no pix".
# "cartão" sozinho NÃO conta como pagamento informado: é ambíguo (regra 5.3)
# e deve continuar sendo perguntado.

# Palavras que indicam uma forma de pagamento definida, em minúsculas. A fonte é
# a seção "## Formas de pagamento" do PROMPT_SISTEMA: o Python reconhece as
# mesmas palavras que o modelo foi instruído a reconhecer.
# Como a busca é por PEDAÇO de texto (operador in), um radical cobre várias
# formas: "deb" acha "deb", "debito" e "cartão de debito"; "cred" acha "cred",
# "credito" e "cartão de credito". As versões com acento ("déb", "créd") são
# outros caracteres para o Python, por isso aparecem separadas.
# "cartão" fica de fora de propósito: sozinho, é ambíguo (regra 5.3).
# Limite conhecido: um radical também acha palavras sem relação ("deb" em
# "debate", "cred" em "credencial"); em mensagens de gastos, o risco é pequeno.
PALAVRAS_PAGAMENTO = [
    "pix",
    "deb", "déb",                  # débito
    "cred", "créd", "parcelado",   # crédito
    "dinheiro", "espécie", "especie", "em mãos", "em maos",   # dinheiro
]


def pagamento_na_mensagem(mensagem):
    """Devolve True se a mensagem contém alguma palavra de PALAVRAS_PAGAMENTO,
    sem diferenciar maiúsculas de minúsculas ("PIX" = "pix"). Senão, False."""
    texto = (mensagem or "").lower()   # "or ''" evita erro se a mensagem vier vazia (None)
    for palavra in PALAVRAS_PAGAMENTO:
        if palavra in texto:
            return True    # achou uma: não precisa olhar as outras
    return False           # o laço terminou sem achar nenhuma


# Trecho de pergunta para cada campo, usado para remontar a pergunta sem o pagamento.
TRECHO_PERGUNTA = {"valor": "o valor", "categoria": "a categoria",
                   "pagamento": "a forma de pagamento"}


def retirar_pagamento_informado(argumentos, mensagem):
    """Se a pergunta pede o pagamento, mas a mensagem já o informa, devolve novos
    argumentos sem "pagamento" e com a pergunta remontada. Caso contrário (nada a
    corrigir), devolve None e a resposta do modelo fica como está."""
    campos = argumentos.get("campos_faltantes")
    if not isinstance(campos, list) or "pagamento" not in campos:
        return None
    if not pagamento_na_mensagem(mensagem):
        return None

    # List comprehension: uma lista nova só com os campos diferentes de "pagamento".
    restantes = [campo for campo in campos if campo != "pagamento"]
    # Se só faltava o pagamento, o modelo se enganou sobre o que falta, e o Python
    # não tem como saber o que perguntar no lugar: não mexe.
    if not restantes:
        return None

    trechos = [TRECHO_PERGUNTA.get(campo, campo) for campo in restantes]
    pergunta = "Qual foi " + " e ".join(trechos) + "?"   # ex.: "Qual foi o valor?"
    return {"campos_faltantes": restantes, "pergunta": pergunta}


# ---------------------------------------------------------------------------
# VALIDAÇÃO EM PYTHON (v14): TRAVA DO PAGAMENTO INVENTADO
# ---------------------------------------------------------------------------
# O prompt diz: "Valor e pagamento nunca são deduzidos". Na v13, com a categoria
# dada, o agente registrou "Almoço 22" como dinheiro e "no cartão" como crédito:
# inventou o pagamento. Se a mensagem não tem NENHUMA palavra de pagamento
# (PALAVRAS_PAGAMENTO, da v9), qualquer pagamento no registro foi inventado, e o
# registro vira pergunta do pagamento. Analogia: o caixa que não pode marcar
# "pago no pix" se o cliente não disse como pagou.
# "cartão" sozinho não está em PALAVRAS_PAGAMENTO, então "no cartão" também cai
# na trava, e a pergunta passa a ser "débito ou crédito?" (regra 5.3).
# Limite conhecido: se o registro também tinha a categoria não identificável
# (trava da v12), a pergunta sai só com o pagamento; o ideal seria perguntar os dois.
PERGUNTA_PAGAMENTO = {"campos_faltantes": ["pagamento"],
                      "pergunta": "Qual foi a forma de pagamento?"}
PERGUNTA_DEBITO_CREDITO = {"campos_faltantes": ["pagamento"],
                           "pergunta": "Foi no débito ou no crédito?"}


def pagamento_inventado(mensagem):
    """Parte central da v14. Devolve True se o pagamento de um registro só pode ter
    sido inventado, isto é, se a mensagem NÃO contém nenhuma palavra de pagamento.
    Senão, False. Reaproveita pagamento_na_mensagem() (v9) e inverte a resposta
    com "not". Teste com:  .venv\\Scripts\\python testar_trava_pagamento.py"""
    return not pagamento_na_mensagem(mensagem)


def pergunta_do_pagamento(mensagem):
    """Escolhe a pergunta da trava: se a mensagem fala em cartão, falta só saber
    se foi débito ou crédito; senão, falta a forma de pagamento inteira."""
    texto = (mensagem or "").lower()
    if "cartão" in texto or "cartao" in texto:
        return dict(PERGUNTA_DEBITO_CREDITO)
    return dict(PERGUNTA_PAGAMENTO)


# ---------------------------------------------------------------------------
# v12: CLASSIFICADOR ESPECIALISTA DE CATEGORIA + TRAVA
# ---------------------------------------------------------------------------
# O agente decide tudo de uma vez (ação, valor, categoria, pagamento, data), e é
# na categoria que ele oscila: ora deduz demais ("gastei 50 na loja" -> mercado),
# ora de menos. Modelos pequenos acertam mais em tarefas estreitas. Por isso uma
# SEGUNDA chamada, com uma tarefa só: dizer a categoria, ou que ela não é
# identificável. Analogia: o atendente ganha um colega especialista; quando os
# dois discordam, quem decide é uma regra fixa em Python.
CATEGORIAS = ["alimentacao", "mercado", "transporte", "moradia",
              "saude", "educacao", "lazer", "outros"]
# As 10 etiquetas possíveis: as 8 categorias + 2 situações especiais.
ETIQUETAS_CLASSIFICADOR = CATEGORIAS + ["nao_identificavel", "nao_e_gasto"]

# "Molde" da resposta (saída estruturada do Ollama): um JSON com a chave
# "categoria", cujo valor só pode ser uma das etiquetas. O modelo não consegue
# responder fora da lista.
FORMATO_CLASSIFICADOR = {
    "type": "object",
    "properties": {"categoria": {"type": "string", "enum": ETIQUETAS_CLASSIFICADOR}},
    "required": ["categoria"],
}


def recortar_categorias(prompt):
    """Recorta do prompt do agente a seção "## Categorias" (até "## Formas de
    pagamento"), para o classificador usar EXATAMENTE as mesmas definições.
    Tira a linha sobre valor e pagamento, que não interessa ao classificador."""
    inicio = prompt.index("## Categorias\n")
    fim = prompt.index("\n\n## Formas de pagamento")
    linhas = prompt[inicio:fim].split("\n")
    return "\n".join(linha for linha in linhas
                     if not linha.startswith("- Esta dedução vale SOMENTE"))


# Os exemplos NÃO repetem mensagens de casos/casos.json (nada de "loja" nem
# "abastecer"), para não ensinar a resposta da prova.
PROMPT_CLASSIFICADOR = f"""
Você classifica mensagens de gastos pessoais enviadas por um usuário brasileiro pelo Telegram.
Sua única tarefa é dizer em que categoria o gasto se encaixa. Não registre nada e não converse.
Responda com UMA etiqueta:
- uma das 8 categorias abaixo, se a mensagem diz em que foi gasto;
- nao_identificavel, se a mensagem descreve um gasto, mas não dá para saber em quê (sempre que as regras abaixo mandam perguntar a categoria);
- nao_e_gasto, se a mensagem não descreve um gasto (cumprimento, pergunta, entrada de dinheiro como salário ou reembolso, transferência para uma conta do próprio usuário).
Valor, forma de pagamento e data não importam aqui: classifique só a categoria.

{recortar_categorias(PROMPT_SISTEMA)}

## Exemplos
"remédio 30 no pix" -> saude
"jantar fora ontem, 90" -> alimentacao
"conserto do relógio, 40 no débito" -> outros
"comprei umas coisas, 45 no pix" -> nao_identificavel
"oi, tudo bem?" -> nao_e_gasto
"""


def classificar_categoria(mensagem, temperatura=0):
    """Pergunta ao modelo só a categoria da mensagem. Devolve um dicionário com a
    etiqueta (ou None, se a resposta vier quebrada), o tempo e os tokens gastos."""
    inicio = time.perf_counter()
    resposta = ollama.chat(
        model=MODELO,
        messages=[{"role": "system", "content": PROMPT_CLASSIFICADOR.strip()},
                  {"role": "user", "content": mensagem}],
        format=FORMATO_CLASSIFICADOR,
        options={"temperature": temperatura},
    )
    tempo_s = time.perf_counter() - inicio
    try:
        etiqueta = json.loads(resposta.message.content)["categoria"]
    except (json.JSONDecodeError, KeyError, TypeError):
        etiqueta = None
    if etiqueta not in ETIQUETAS_CLASSIFICADOR:
        etiqueta = None
    return {"etiqueta": etiqueta, "tempo_s": tempo_s,
            "tokens_entrada": resposta.prompt_eval_count or 0,
            "tokens_saida": resposta.eval_count or 0}


PERGUNTA_CATEGORIA = {"campos_faltantes": ["categoria"], "pergunta": "Em que foi esse gasto?"}


def conciliar_categoria(acao, argumentos, etiqueta):
    """Trava da v12 (regra 5.5 da especificação): se o agente registrou, mas o
    classificador diz que a categoria não é identificável, o registro vira pergunta
    da categoria. Em qualquer outra combinação, não mexe.
    Devolve (acao, argumentos, travou)."""
    if acao == "registrar" and etiqueta == "nao_identificavel":
        return "perguntar", dict(PERGUNTA_CATEGORIA), True
    return acao, argumentos, False


def categoria_divergente(acao, argumentos, etiqueta):
    """Só ANOTA (não muda nada) quando o agente e o classificador discordam sobre a
    categoria. Serve de dado para a v13. Exemplos de divergência:
      - o agente registrou "mercado" e o classificador disse "outros";
      - o agente perguntou a categoria, mas o classificador sabe qual é."""
    if etiqueta is None:
        return False
    if acao == "registrar":
        return argumentos.get("categoria") != etiqueta
    if acao == "perguntar":
        campos = argumentos.get("campos_faltantes") or []
        return "categoria" in campos and etiqueta in CATEGORIAS
    return False


# ---------------------------------------------------------------------------
# v13: A ETIQUETA DO CLASSIFICADOR VIRA DICA PARA O AGENTE
# ---------------------------------------------------------------------------
# Na v12 o especialista dava o parecer DEPOIS que o atendente respondia, e só
# podia vetar. Na v13 o atendente recebe o parecer ANTES de responder: a etiqueta
# vai no fim da mensagem do usuário. O prompt de sistema não muda, para preservar
# o cache do Ollama (a dica muda a cada mensagem; o prompt de sistema, não).
#
# TEXTO_DICA é um MOLDE: "{categoria}" é trocado pela etiqueta com .format().
# (Uma f-string não serve aqui, porque ela é preenchida na hora em que a linha é
# lida, e nesse momento ainda não se sabe a categoria.)
# Exemplo: "Categoria: {categoria}".format(categoria="lazer") -> "Categoria: lazer"
#
# >>> ESTE TEXTO É SEU PARA ESCREVER (é a parte central da v13). <<<
# Ele precisa dizer: a categoria provável; e que valor, pagamento e data vêm
# somente da mensagem (proteção contra o efeito gangorra visto na v5).
# Comece com "\n\n" para separar a dica da mensagem.
TEXTO_DICA = ("\n\n(Nota do sistema, não escrita pelo usuário: a categoria deste gasto é "
              "{categoria}. Valor, pagamento e data vêm somente da mensagem acima.)")

# Interruptor da dica. A v13 foi REPROVADA em 23/10 (com a categoria dada, o agente
# inventou o pagamento), e a v14 rodou sem a dica (False). A v15 religa a dica
# (True), agora com a trava do pagamento inventado (v14) protegendo o pagamento.
USAR_DICA = True


def mensagem_com_dica(mensagem, etiqueta):
    """Devolve a mensagem que o agente vai ler: a original + a dica, só quando a
    etiqueta é uma das 8 categorias. Com "nao_identificavel", "nao_e_gasto" ou
    None (resposta quebrada), não há dica e a mensagem segue como na v12."""
    if etiqueta not in CATEGORIAS:
        return mensagem
    if TEXTO_DICA is None:
        raise RuntimeError("Escreva o TEXTO_DICA em agente.py antes de rodar a v13.")
    return mensagem + TEXTO_DICA.format(categoria=etiqueta)


# ---------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DO AGENTE
# ---------------------------------------------------------------------------
def interpretar(mensagem, data_referencia, temperatura=0, prompt_sistema=None,
                ordem_exemplos=None, exemplos_em_conversa=False):
    """Envia a mensagem ao modelo e devolve um dicionário com a decisão do agente
    e as medidas de eficiência (tempo e tokens).

    Modos:
      - prompt_sistema=None (padrão): agente OFICIAL = prompt da v2, com os
        exemplos na ordem ordem_exemplos (None = original), + validação em Python
        que recupera a chamada escrita como texto (v4) + trava do valor 0 (v7)
        + trava do pagamento já informado (v9) + regra de categoria no prompt (v10)
        + classificador especialista de categoria com trava (v12)
        + trava do pagamento inventado (v14) + a dica da v13 religada (v15):
        a etiqueta do classificador entra na mensagem (USAR_DICA = True).
      - exemplos_em_conversa=True: experimento v3 (reprovado em 16/10), com os
        exemplos como conversa. Sem validação.
      - prompt_sistema informado: modo antigo, usado por lote.py para reproduzir
        a v2 exatamente como foi. Sem validação.
    temperatura existe para os experimentos de calibração."""

    oficial = prompt_sistema is None and not exemplos_em_conversa
    exemplos = []
    if exemplos_em_conversa:
        prompt_sistema = PROMPT_SISTEMA_V3
        exemplos = montar_conversa_exemplos(data_referencia, ordem_exemplos)
    elif prompt_sistema is None:
        prompt_sistema = montar_prompt(ordem_exemplos)

    # v12: o classificador especialista roda ANTES do agente. Na v13, a etiqueta
    # dele entrava na mensagem como dica; hoje isso depende de USAR_DICA.
    # Só no agente oficial.
    etiqueta = None
    texto_usuario = mensagem
    if oficial:
        classificacao = classificar_categoria(mensagem, temperatura)
        etiqueta = classificacao["etiqueta"]
        if USAR_DICA:
            texto_usuario = mensagem_com_dica(mensagem, etiqueta)

    # Monta a conversa: instruções (system), exemplos (se houver) e a mensagem (user).
    # A data de referência é anexada às instruções, para o modelo saber qual é "hoje".
    instrucoes = prompt_sistema.strip() + f"\n\nData de referência (hoje): {data_referencia}"
    conversa = ([{"role": "system", "content": instrucoes}]
                + exemplos
                + [{"role": "user", "content": texto_usuario}])

    # Chama o modelo, oferecendo as ferramentas, e mede o tempo.
    inicio = time.perf_counter()
    resposta = ollama.chat(
        model=MODELO,
        messages=conversa,
        tools=FERRAMENTAS,
        options={"temperature": temperatura},
    )
    tempo_s = time.perf_counter() - inicio

    # Lê os pedidos de ferramenta. Se não houver nenhum, a lista fica vazia.
    chamadas = resposta.message.tool_calls or []

    # Decide a ação: sem ferramenta = "ignorar"; senão, usa a PRIMEIRA chamada.
    # (Se o modelo pedir mais de uma, isso aparece em n_chamadas e conta como erro
    # de "uso correto de ferramentas" no benchmark.)
    if len(chamadas) == 0:
        acao = "ignorar"
        argumentos = {}
    else:
        primeira = chamadas[0]
        acao = ACAO_POR_FERRAMENTA.get(primeira.function.name, "desconhecida")
        argumentos = dict(primeira.function.arguments)

    # v4: sem chamada de verdade, tenta recuperar a chamada escrita no texto.
    # Só no agente oficial; os modos de experimento ficam como eram.
    chamada_recuperada = False
    if oficial and len(chamadas) == 0:
        recuperada = recuperar_chamada_em_texto(resposta.message.content, data_referencia)
        if recuperada is not None:
            nome, argumentos = recuperada
            acao = ACAO_POR_FERRAMENTA[nome]
            chamada_recuperada = True

    # v7: um registro sem valor positivo vira pergunta do valor. Vale tanto para a
    # chamada real quanto para a recuperada do texto. Só no agente oficial.
    valor_travado = False
    if oficial and acao == "registrar" and valor_invalido(argumentos):
        acao = "perguntar"
        argumentos = dict(PERGUNTA_VALOR)   # dict() faz uma cópia, para não alterar o original
        valor_travado = True

    # v14: um registro cujo pagamento não aparece na mensagem vira pergunta do
    # pagamento. Vale para a chamada real e para a recuperada do texto. Usa a
    # mensagem ORIGINAL, sem a dica. Só no agente oficial.
    pagamento_travado = False
    if oficial and acao == "registrar" and pagamento_inventado(mensagem):
        acao = "perguntar"
        argumentos = pergunta_do_pagamento(mensagem)
        pagamento_travado = True

    # v9: uma pergunta não pede o pagamento que a mensagem já informou. Vale para a
    # chamada real e para a recuperada do texto. Só no agente oficial.
    # (Usa a mensagem ORIGINAL, sem a dica: a palavra deve vir do usuário.)
    pagamento_retirado = False
    if oficial and acao == "perguntar":
        corrigidos = retirar_pagamento_informado(argumentos, mensagem)
        if corrigidos is not None:
            argumentos = corrigidos
            pagamento_retirado = True

    # v12: com a etiqueta do classificador (obtida no início, na v13), a
    # divergência só é anotada, e a trava age num sentido só (registro sem
    # categoria identificável -> pergunta). Só no agente oficial.
    tokens_entrada = resposta.prompt_eval_count or 0
    tokens_saida = resposta.eval_count or 0
    divergente = categoria_travada = False
    if oficial:
        # Eficiência honesta: a resposta custa as DUAS chamadas.
        tempo_s += classificacao["tempo_s"]
        tokens_entrada += classificacao["tokens_entrada"]
        tokens_saida += classificacao["tokens_saida"]
        divergente = categoria_divergente(acao, argumentos, etiqueta)
        acao, argumentos, categoria_travada = conciliar_categoria(acao, argumentos, etiqueta)

    return {
        "acao": acao,
        "argumentos": argumentos,
        "n_chamadas": len(chamadas),
        "chamada_recuperada": chamada_recuperada,  # True = veio do texto, não do modelo
        "valor_travado": valor_travado,  # True = registro com valor 0 trocado por pergunta
        "pagamento_retirado": pagamento_retirado,  # True = pagamento já informado saiu da pergunta
        "pagamento_travado": pagamento_travado,  # True = registro com pagamento inventado virou pergunta (v14)
        "categoria_classificador": etiqueta,  # etiqueta do classificador (v12)
        "dica_categoria": texto_usuario != mensagem,  # True = a mensagem levou a dica (v13)
        "categoria_divergente": divergente,  # True = agente e classificador discordaram
        "categoria_travada": categoria_travada,  # True = registro sem categoria virou pergunta
        "texto": resposta.message.content,  # texto solto, se o modelo "conversou"
        "tempo_s": round(tempo_s, 2),
        "tokens_entrada": tokens_entrada,
        "tokens_saida": tokens_saida,
    }


# ---------------------------------------------------------------------------
# TESTE RÁPIDO (só roda quando o arquivo é executado diretamente)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not PROMPT_SISTEMA.strip():
        print("Aviso: PROMPT_SISTEMA está vazio; o modelo só conhece as ferramentas.\n")

    # Dois casos de casos/casos.json: C01 (registrar) e C02 (perguntar).
    testes = [
        ("C01", "Gastei 35 no mercado no pix"),
        ("C02", "Almoço 22"),
    ]
    for id_caso, mensagem in testes:
        resultado = interpretar(mensagem, "2026-10-11")
        print(id_caso, "|", mensagem)
        for campo, valor in resultado.items():
            print(f"    {campo}: {valor}")
        print()

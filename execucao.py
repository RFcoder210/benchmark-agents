# Regras da execução do benchmark pela página "Executar" do painel (sem tela).
#
# Analogia: é a "torre de controle". Antes da decolagem, `pode_executar()` confere
# se a pista está livre (Ollama certo, rótulo válido, nada em andamento) e, durante
# o voo, `ler_progresso()` lê o diário de bordo (o log do benchmark) para dizer
# quantas respostas já saíram.
#
# Este módulo não tem tela: assim ele pode ser testado sem navegador
# (ver testar_execucao.py) e importado pela página a cada recarga.
#
# ESQUELETO (T05): as duas funções abaixo serão escritas por você na T06.

import ambiente
from benchmark import rotulo_invalido


# ---------------------------------------------------------------------------
# ROTEIRO de ler_progresso
# ---------------------------------------------------------------------------
# O benchmark escreve uma linha por resposta, neste formato:
#     [ 7/45] C03 #1 (original) -> registrar (2.8 s)
# Outras linhas (avisos, "Respostas salvas em ...", "Acerto geral: ...") não
# são de progresso. A tarefa é achar a ÚLTIMA linha de progresso completa.
#
# Passos sugeridos:
#   1. Separe o texto em linhas com `texto_log.splitlines()` (lida com \r\n).
#   2. Percorra as linhas de trás para a frente com um laço `for` e
#      `reversed(linhas)`: a primeira linha válida encontrada é a última do log.
#   3. Limpe cada linha com `str.strip()` e descarte as que não começam com "["
#      (`str.startswith()`).
#   4. Em uma linha candidata, pegue o trecho entre "[" e "]" e separe em
#      "n" e "total" com `str.split("/")`. Converta com `int()` dentro de
#      `try/except ValueError`: uma linha cortada como "[ 7/4" não tem "]" e
#      deve ser ignorada, assim como qualquer texto que não vire número.
#   5. Devolva `(feitas, total)`. Se nenhuma linha servir, devolva `(0, 0)`.
#
# Alternativa: uma expressão regular com `re.match(r"\[\s*(\d+)/(\d+)\]", linha)`;
# o `match` devolve None quando a linha não tem o formato.
def ler_progresso(texto_log):
    """Devolve (feitas, total) da última linha de progresso completa do log.

    Linhas de outro formato, inclusive uma última linha cortada pela metade
    (ex.: "[ 7/4"), são ignoradas. Sem nenhuma linha de progresso: (0, 0).
    """
    raise NotImplementedError("Sua vez: veja o roteiro nos comentários")


# ---------------------------------------------------------------------------
# ROTEIRO de pode_executar
# ---------------------------------------------------------------------------
# A função decide se o botão "Executar" pode ser liberado. Devolve None quando
# pode e, quando não pode, o MOTIVO em português. A primeira regra que falhar
# decide (devolva cedo com `return`), nesta ordem:
#   1. `em_andamento` verdadeiro  -> motivo com a palavra "andamento".
#   2. `versao_ollama is None`    -> motivo com "não está ligado" e a versão
#                                    exigida (`ambiente.VERSAO_OLLAMA`).
#   3. `versao_ollama` diferente de `ambiente.VERSAO_OLLAMA` -> motivo com a
#                                    versão encontrada e a exigida.
#   4. `rotulo_invalido(rotulo)` não é None -> devolva exatamente esse motivo
#                                    (reaproveite a função já escrita; guarde o
#                                    resultado numa variável para não chamar duas vezes).
#   5. `ja_gravadas > 0`          -> motivo com o rótulo, o número de linhas já
#                                    gravadas e a palavra "outro" (sugere
#                                    escolher outro rótulo).
#   6. Se nenhuma regra falhou, devolva None.
# Dica: use f-strings para montar os textos e `is None` para comparar com None.
def pode_executar(versao_ollama, rotulo, ja_gravadas, em_andamento=False):
    """Devolve None se pode executar; senão, o motivo (texto em português)."""
    raise NotImplementedError("Sua vez: veja o roteiro nos comentários")

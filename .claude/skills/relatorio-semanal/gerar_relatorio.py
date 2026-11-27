# -*- coding: utf-8 -*-
"""Gera o relatório semanal de aprendizado do projeto em PDF, a partir de um JSON.

Uso (sempre pelo ambiente virtual do projeto):
    .venv\\Scripts\\python .claude\\skills\\relatorio-semanal\\gerar_relatorio.py docs\\relatorios-semanais\\semana-AAAA-MM-DD.json

O PDF sai ao lado do JSON, com o mesmo nome, e leva o JSON anexado ("fonte.json").

O documento é um material de estudo: mapa do projeto em diagrama, cada mudança da
semana explicada (problema, ideia, como funciona, diagrama, trecho real do código),
glossário, decisões, perguntas de revisão e respostas. O formato do JSON está
descrito em SKILL.md, na mesma pasta.

Conferências feitas ANTES de gerar (um erro para a geração com uma mensagem clara):
    - datas: semana começando numa segunda, sessões e lições dentro da semana,
      nada depois de "atualizado_em" nem depois de hoje; o dia da semana é
      calculado aqui, nunca escrito à mão;
    - caracteres: todo texto precisa existir na fonte (senão sairia um quadrado);
    - diagramas: toda ligação aponta para um nó que existe.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from xml.sax.saxutils import escape as escapar_xml

from reportlab.graphics.shapes import Drawing, Line, Polygon, PolyLine, Rect, String
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem,
                                PageBreak, Paragraph, SimpleDocTemplate, Spacer, XPreformatted)

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
PASTA_FONTES = os.path.join(tempfile.gettempdir(), "doc-padrao-fonts")
LARGURA_UTIL = A4[0] - 2 * 2.2 * cm      # largura do texto (margens de 2,2 cm)

# Paleta: tinta quase preta, cinzas e um único destaque verde-água (o do tema do painel),
# usado só para marcar o que é NOVO na semana.
TINTA = colors.HexColor("#111111")
APAGADO = colors.HexColor("#5A5A5A")
LINHA = colors.HexColor("#BBBBBB")
FUNDO_CODIGO = colors.HexColor("#F4F5F6")
NOVO_FUNDO = colors.HexColor("#DDF4F0")
NOVO_BORDA = colors.HexColor("#1F8A7A")
DADOS_FUNDO = colors.HexColor("#EEEEEE")
DECISAO_FUNDO = colors.HexColor("#FFF3D6")
DECISAO_BORDA = colors.HexColor("#A6781B")


# ---------------------------------------------------------------------------
# 1. Datas
# ---------------------------------------------------------------------------
def ler_data(texto, campo):
    """Converte 'DD/MM/AAAA' em date; para com mensagem clara se o formato estiver errado."""
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        sys.exit(f"Data inválida em '{campo}': {texto!r} (use DD/MM/AAAA).")


def conferir_datas(c, hoje):
    """Confere todas as datas; devolve (inicio, fim) da semana."""
    inicio = ler_data(c["semana_inicio"], "semana_inicio")
    if inicio.weekday() != 0:
        sys.exit(f"semana_inicio ({c['semana_inicio']}) não é uma segunda-feira.")
    fim = inicio + timedelta(days=6)
    atualizado = ler_data(c["atualizado_em"], "atualizado_em")
    if atualizado > hoje:
        sys.exit(f"atualizado_em ({c['atualizado_em']}) é posterior a hoje ({hoje:%d/%m/%Y}).")
    for grupo in ("sessoes", "licoes"):
        for item in c.get(grupo, []):
            d = ler_data(item["data"], f"{grupo}.data")
            if not inicio <= d <= fim:
                sys.exit(f"{grupo}: data {item['data']} fora da semana {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}.")
            if d > atualizado:
                sys.exit(f"{grupo}: data {item['data']} é posterior a atualizado_em ({c['atualizado_em']}).")
    for dec in c.get("decisoes", []):
        if ler_data(dec["data"], "decisoes.data") > atualizado:
            sys.exit(f"Decisão datada de {dec['data']}, depois de atualizado_em.")
    return inicio, fim


RAIZ_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def preencher_trechos(c):
    """Copia do arquivo real os trechos de código que ainda não estão no JSON.

    Cada "codigo" pode trazer só {"arquivo", "linha_inicial", "linha_final"}: o
    trecho é lido do projeto, para nunca divergir do original. Depois de lido, ele
    fica gravado no JSON ("trecho"), e o PDF continua igual mesmo que o código mude.
    Devolve True se algum trecho foi preenchido (o JSON precisa ser regravado).
    """
    mudou = False
    for l in c.get("licoes", []):
        cod = l.get("codigo")
        if not cod or cod.get("trecho"):
            continue
        caminho = os.path.join(RAIZ_PROJETO, cod["arquivo"])
        if not os.path.exists(caminho):
            sys.exit(f"Arquivo de código não encontrado: {cod['arquivo']}")
        with open(caminho, encoding="utf-8") as f:
            linhas = f.read().splitlines()
        ini, fim = int(cod["linha_inicial"]), int(cod["linha_final"])
        if not 1 <= ini <= fim <= len(linhas):
            sys.exit(f"Linhas {ini}-{fim} fora de {cod['arquivo']} ({len(linhas)} linhas).")
        cod["trecho"] = "\n".join(linhas[ini - 1:fim])
        mudou = True
    return mudou


# ---------------------------------------------------------------------------
# 2. Fontes: Inter (texto) e Consolas (código, vem com o Windows)
# ---------------------------------------------------------------------------
def _otf_para_ttf(src, dst):
    """Converte a fonte para TTF com contornos quadráticos (o formato que o reportlab aceita)."""
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont as FT, newTable
    f = FT(src)
    if "glyf" in f:
        f.flavor = None
        f.save(dst)
        return
    gs, ordem = f.getGlyphSet(), f.getGlyphOrder()
    glyf = newTable("glyf")
    glyf.glyphOrder = ordem
    glyf.glyphs = {}
    for n in ordem:
        pen = TTGlyphPen(gs)
        gs[n].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyf.glyphs[n] = pen.glyph()
    f["loca"] = newTable("loca")
    f["glyf"] = glyf
    m = newTable("maxp")
    m.tableVersion = 0x00010000
    for a in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
              "maxStackElements", "maxSizeOfInstructions", "maxComponentElements"):
        setattr(m, a, 0)
    m.maxZones = 1
    m.numGlyphs = len(ordem)
    f["maxp"] = m
    f["head"].glyphDataFormat = 0
    for t in ("CFF ", "VORG"):
        if t in f:
            del f[t]
    f["post"].formatType = 2.0
    f["post"].extraNames = []
    f["post"].mapping = {}
    f["post"].glyphOrder = ordem
    f.flavor = None
    f.sfntVersion = "\x00\x01\x00\x00"
    f.save(dst)


def preparar_inter():
    """Devolve (regular, negrito) da Inter em TTF; se não houver no Windows, baixa pelo npm (grátis)."""
    os.makedirs(PASTA_FONTES, exist_ok=True)
    reg = os.path.join(PASTA_FONTES, "Inter-Regular.ttf")
    neg = os.path.join(PASTA_FONTES, "Inter-Bold.ttf")
    if os.path.exists(reg) and os.path.exists(neg):
        return reg, neg
    pastas = [r"C:\Windows\Fonts", os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts")]
    fontes = {}
    for peso in ("Regular", "Bold"):
        achados = [p for pasta in pastas for ext in ("ttf", "otf")
                   for p in glob.glob(os.path.join(pasta, f"Inter-{peso}.{ext}"))]
        if achados:
            fontes[peso] = achados[0]
    if len(fontes) < 2:
        d = tempfile.mkdtemp()
        npm = "npm.cmd" if os.name == "nt" else "npm"
        subprocess.run([npm, "pack", "@fontsource/inter@5.1.0"], cwd=d, check=True, capture_output=True)
        pacote = glob.glob(os.path.join(d, "*.tgz"))[0]
        subprocess.run(["tar", "-xzf", pacote, "-C", d], check=True)
        arquivos = os.path.join(d, "package", "files")
        fontes = {"Regular": os.path.join(arquivos, "inter-latin-400-normal.woff"),
                  "Bold": os.path.join(arquivos, "inter-latin-700-normal.woff")}
    _otf_para_ttf(fontes["Regular"], reg)
    _otf_para_ttf(fontes["Bold"], neg)
    return reg, neg


def registrar_fontes():
    """Registra as fontes no reportlab e devolve o conjunto de caracteres que a Inter cobre."""
    from fontTools.ttLib import TTFont as FT
    reg, neg = preparar_inter()
    pdfmetrics.registerFont(TTFont("Inter", reg))
    pdfmetrics.registerFont(TTFont("Inter-Bold", neg))
    for italico, negrito in ((0, 0), (0, 1), (1, 0), (1, 1)):
        addMapping("Inter", negrito, italico, "Inter-Bold" if negrito else "Inter")
    consolas = r"C:\Windows\Fonts\consola.ttf"
    mono = "Courier"
    if os.path.exists(consolas):
        pdfmetrics.registerFont(TTFont("Consolas", consolas))
        mono = "Consolas"
    cobertos = set(chr(cp) for cp in FT(reg).getBestCmap())
    return mono, cobertos


def conferir_caracteres(c, cobertos):
    """Para se algum texto tiver caractere que a fonte não desenha (ex.: setas, emojis)."""
    faltando = {}

    def visitar(valor, caminho):
        if isinstance(valor, str):
            for ch in valor:
                if ch not in cobertos and ch not in "\n\t":
                    faltando.setdefault(ch, caminho)
        elif isinstance(valor, list):
            for i, v in enumerate(valor):
                visitar(v, f"{caminho}[{i}]")
        elif isinstance(valor, dict):
            for k, v in valor.items():
                if k != "trecho":            # o código usa a fonte mono, conferida à parte
                    visitar(v, f"{caminho}.{k}")

    visitar(c, "conteudo")
    if faltando:
        lista = ", ".join(f"{ch!r} (U+{ord(ch):04X}) em {onde}" for ch, onde in faltando.items())
        sys.exit(f"Caracteres que a fonte Inter não desenha: {lista}. Troque por texto (ex.: '->' por 'para').")


# ---------------------------------------------------------------------------
# 3. Diagramas (caixas numa grade, ligadas por setas)
# ---------------------------------------------------------------------------
def desenhar_diagrama(d):
    """Desenha um diagrama a partir da especificação do JSON e devolve um Drawing.

    Especificação: {"colunas": N, "nos": [...], "ligacoes": [...]}.
    Nó: {"id", "texto" ("Título\\nexplicação curta"), "linha", "coluna",
         "largura" (colunas ocupadas, padrão 1), "tipo": normal|novo|dados|externo|decisao}.
    Ligação: {"de", "para", "rotulo" (opcional), "tracejada" (opcional),
              "lado": "direita"|"esquerda" (opcional: contorna pela lateral, bom para laços)}.
    """
    nos = {n["id"]: n for n in d["nos"]}
    for lig in d.get("ligacoes", []):
        for ponta in ("de", "para"):
            if lig[ponta] not in nos:
                sys.exit(f"Diagrama '{d.get('titulo', '')}': a ligação aponta para o nó inexistente '{lig[ponta]}'.")

    usa_direita = any(l.get("lado") == "direita" for l in d.get("ligacoes", []))
    usa_esquerda = any(l.get("lado") == "esquerda" for l in d.get("ligacoes", []))
    margem_esq = 78 if usa_esquerda else 4
    margem_dir = 78 if usa_direita else 4
    largura = LARGURA_UTIL
    ncol = d["colunas"]
    larg_coluna = (largura - margem_esq - margem_dir) / ncol
    folga_h, folga_v, pad = d.get("folga_horizontal", 30), 34, 6
    T_TIT, T_TXT = 8.4, 7.4

    # 3a. Mede cada nó: quebra o texto na largura da caixa e calcula a altura.
    for n in nos.values():
        span = n.get("largura", 1)
        n["_w"] = span * larg_coluna - folga_h
        larg_texto = n["_w"] - 2 * pad
        if n.get("tipo") == "decisao":
            larg_texto = n["_w"] * 0.62
        partes = n["texto"].split("\n")
        n["_linhas"] = [(l, "Inter-Bold", T_TIT) for l in simpleSplit(partes[0], "Inter-Bold", T_TIT, larg_texto)]
        for p in partes[1:]:
            n["_linhas"] += [(l, "Inter", T_TXT) for l in simpleSplit(p, "Inter", T_TXT, larg_texto)]
        altura = sum(t + 2.2 for _, _, t in n["_linhas"]) + 2 * pad
        if n.get("tipo") == "decisao":
            altura *= 1.75
        n["_h"] = max(altura, 28)

    # 3b. Altura de cada linha da grade = maior nó da linha.
    nlinhas = max(n["linha"] for n in nos.values()) + 1
    alt_linha = [max([n["_h"] for n in nos.values() if n["linha"] == r] or [28]) for r in range(nlinhas)]
    altura_total = sum(alt_linha) + folga_v * (nlinhas - 1) + 8
    topo = [4 + sum(alt_linha[:r]) + folga_v * r for r in range(nlinhas)]

    # 3c. Posição (centro) de cada nó, com y do reportlab (de baixo para cima).
    for n in nos.values():
        x0 = margem_esq + n["coluna"] * larg_coluna + folga_h / 2
        n["_cx"] = x0 + n["_w"] / 2
        y_meio = topo[n["linha"]] + alt_linha[n["linha"]] / 2
        n["_cy"] = altura_total - y_meio

    dr = Drawing(largura, altura_total)

    def ponta_na_borda(n, dx, dy):
        """Ponto onde a reta que sai do centro do nó na direção (dx, dy) cruza a borda."""
        hw, hh = n["_w"] / 2, n["_h"] / 2
        if n.get("tipo") == "decisao":
            t = 1 / ((abs(dx) / hw if dx else 0) + (abs(dy) / hh if dy else 0))
        else:
            t = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        return n["_cx"] + dx * t, n["_cy"] + dy * t

    def seta(x1, y1, x2, y2, cor):
        """Ponta de seta em (x2, y2), apontando na direção do segmento."""
        dx, dy = x2 - x1, y2 - y1
        comp = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / comp, dy / comp
        tam = 5.5
        bx, by = x2 - ux * tam, y2 - uy * tam
        dr.add(Polygon([x2, y2, bx - uy * tam * 0.55, by + ux * tam * 0.55,
                        bx + uy * tam * 0.55, by - ux * tam * 0.55],
                       fillColor=cor, strokeColor=cor, strokeWidth=0.5))

    def rotulo(texto, x, y, alinhamento="meio"):
        linhas = simpleSplit(texto, "Inter", 6.8, 70)
        alt = len(linhas) * 8
        larg = max(pdfmetrics.stringWidth(l, "Inter", 6.8) for l in linhas) + 4
        x_ret = {"meio": x - larg / 2, "esquerda": x, "direita": x - larg}[alinhamento]
        dr.add(Rect(x_ret, y - alt / 2 - 1, larg, alt + 2, fillColor=colors.white, strokeColor=None))
        for i, l in enumerate(linhas):
            dr.add(String(x_ret + 2, y + alt / 2 - 7 - i * 8, l, fontName="Inter", fontSize=6.8,
                          fillColor=APAGADO))

    # 3d. Ligações primeiro (ficam por baixo das caixas); os rótulos são guardados para o fim.
    rotulos = []
    for lig in d.get("ligacoes", []):
        a, b = nos[lig["de"]], nos[lig["para"]]
        cor = APAGADO
        traco = (3, 2) if lig.get("tracejada") else None
        if lig.get("lado") in ("direita", "esquerda"):
            sinal = 1 if lig["lado"] == "direita" else -1
            xa = a["_cx"] + sinal * a["_w"] / 2
            xb = b["_cx"] + sinal * b["_w"] / 2
            xr = (max(xa, xb) + 14) if sinal > 0 else (min(xa, xb) - 14)
            pontos = [xa, a["_cy"], xr, a["_cy"], xr, b["_cy"], xb, b["_cy"]]
            dr.add(PolyLine(pontos, strokeColor=cor, strokeWidth=0.9, strokeDashArray=traco))
            seta(xr, b["_cy"], xb, b["_cy"], cor)
            if lig.get("rotulo"):
                rotulos.append((lig["rotulo"], xr + 4 * sinal, (a["_cy"] + b["_cy"]) / 2,
                                "esquerda" if sinal > 0 else "direita"))
        else:
            dx, dy = b["_cx"] - a["_cx"], b["_cy"] - a["_cy"]
            x1, y1 = ponta_na_borda(a, dx, dy)
            x2, y2 = ponta_na_borda(b, -dx, -dy)
            dr.add(Line(x1, y1, x2, y2, strokeColor=cor, strokeWidth=0.9, strokeDashArray=traco))
            seta(x1, y1, x2, y2, cor)
            if lig.get("rotulo"):
                rotulos.append((lig["rotulo"], (x1 + x2) / 2, (y1 + y2) / 2, "meio"))

    # 3e. Caixas e textos.
    for n in nos.values():
        tipo = n.get("tipo", "normal")
        x, y, w, h = n["_cx"] - n["_w"] / 2, n["_cy"] - n["_h"] / 2, n["_w"], n["_h"]
        if tipo == "decisao":
            dr.add(Polygon([n["_cx"], y + h, x + w, n["_cy"], n["_cx"], y, x, n["_cy"]],
                           fillColor=DECISAO_FUNDO, strokeColor=DECISAO_BORDA, strokeWidth=1))
        else:
            fundo = {"novo": NOVO_FUNDO, "dados": DADOS_FUNDO}.get(tipo, colors.white)
            borda = NOVO_BORDA if tipo == "novo" else TINTA
            dr.add(Rect(x, y, w, h, rx=0 if tipo == "dados" else 5, ry=0 if tipo == "dados" else 5,
                        fillColor=fundo, strokeColor=borda, strokeWidth=1.3 if tipo == "novo" else 0.8,
                        strokeDashArray=(3, 2) if tipo == "externo" else None))
        altura_texto = sum(t + 2.2 for _, _, t in n["_linhas"])
        yy = n["_cy"] + altura_texto / 2
        for texto, fonte, tam in n["_linhas"]:
            yy -= tam + 2.2
            dr.add(String(n["_cx"], yy + 1.6, texto, fontName=fonte, fontSize=tam,
                          fillColor=TINTA, textAnchor="middle"))

    # 3f. Rótulos das setas por último, para nenhuma caixa cobri-los.
    for texto, x, y, alinhamento in rotulos:
        rotulo(texto, x, y, alinhamento)
    return dr


# Legenda dos tipos de caixa (só os tipos usados aparecem).
NOMES_TIPOS = {"normal": "parte que já existia", "novo": "novo ou alterado nesta semana",
               "dados": "arquivo ou dado", "externo": "programa de fora do projeto",
               "decisao": "decisão (pergunta com sim ou não)"}


def legenda(tipos_usados, estilo):
    partes = [NOMES_TIPOS[t] for t in ("novo", "normal", "dados", "externo", "decisao") if t in tipos_usados]
    marcas = {"novo": "caixa verde", "normal": "caixa branca", "dados": "caixa cinza de cantos retos",
              "externo": "borda tracejada", "decisao": "losango"}
    texto = "; ".join(f"{marcas[t]}: {NOMES_TIPOS[t]}" for t in ("novo", "normal", "dados", "externo", "decisao")
                      if t in tipos_usados)
    return Paragraph(f"Legenda: {texto}.", estilo) if partes else Spacer(1, 1)


# ---------------------------------------------------------------------------
# 4. Montagem do PDF
# ---------------------------------------------------------------------------
def gerar(c, saida, hoje):
    inicio, fim = conferir_datas(c, hoje)
    mono, cobertos = registrar_fontes()
    conferir_caracteres(c, cobertos)

    FR, FB, TAM = "Inter", "Inter-Bold", 9.8
    TITULO = ParagraphStyle("TITULO", fontName=FB, fontSize=19, leading=23, textColor=TINTA, spaceAfter=4)
    META = ParagraphStyle("META", fontName=FR, fontSize=9, leading=12, textColor=APAGADO, spaceAfter=2)
    SECAO = ParagraphStyle("SECAO", fontName=FB, fontSize=14, leading=18, textColor=TINTA,
                           spaceAfter=5, keepWithNext=1)
    SUB = ParagraphStyle("SUB", fontName=FB, fontSize=11.8, leading=15, textColor=TINTA, spaceBefore=10,
                         spaceAfter=2, keepWithNext=1)
    SUBMETA = ParagraphStyle("SUBMETA", fontName=FR, fontSize=8.4, leading=11, textColor=APAGADO,
                             spaceAfter=5, keepWithNext=1)
    CORPO = ParagraphStyle("CORPO", fontName=FR, fontSize=TAM, leading=14.6, textColor=TINTA, spaceAfter=5)
    ITEM = ParagraphStyle("ITEM", parent=CORPO, spaceAfter=2)
    ROTULO = ParagraphStyle("ROTULO", fontName=FB, fontSize=TAM, leading=14, textColor=TINTA,
                            spaceBefore=5, spaceAfter=2, keepWithNext=1)
    ROTULO_COD = ParagraphStyle("ROTULO_COD", parent=ROTULO, keepWithNext=0)
    DESTAQUE = ParagraphStyle("DESTAQUE", parent=CORPO, backColor=NOVO_FUNDO, borderColor=NOVO_BORDA,
                              borderWidth=0.6, borderPadding=(6, 8, 6, 8), spaceBefore=6, spaceAfter=10,
                              leftIndent=8, rightIndent=8)
    LEGENDA = ParagraphStyle("LEGENDA", fontName=FR, fontSize=8, leading=10.5, textColor=APAGADO,
                             spaceBefore=3, spaceAfter=8)
    CODIGO = ParagraphStyle("CODIGO", fontName=mono, fontSize=7.7, leading=10.2, textColor=TINTA,
                            backColor=FUNDO_CODIGO, borderPadding=(5, 6, 5, 6), leftIndent=6, rightIndent=6,
                            spaceBefore=4, spaceAfter=8)

    def esc(t):
        """Escapa "&" e "<" soltos; mantém só as tags <b> e <i> (o reportlab lê o texto como XML)."""
        t = re.sub(r"&(?!amp;|lt;|gt;|quot;|#\d+;)", "&amp;", t)
        return re.sub(r"<(?!/?[bi]>)", "&lt;", t)

    def lista(itens, estilo=ITEM):
        return ListFlowable([ListItem(Paragraph(esc(i), estilo), leftIndent=16) for i in itens],
                            bulletType="1", bulletFormat="%s.", bulletFontName=FR, bulletFontSize=TAM,
                            leftIndent=16, spaceAfter=4)

    num_figura = [0]

    def figura(diag):
        """Diagrama + legenda + título numerado, mantidos juntos na mesma página."""
        num_figura[0] += 1
        tipos = {n.get("tipo", "normal") for n in diag["nos"]}
        return KeepTogether([Spacer(1, 4), desenhar_diagrama(diag),
                             Paragraph(f"<b>Figura {num_figura[0]}.</b> {esc(diag['titulo'])}", LEGENDA),
                             legenda(tipos, LEGENDA)])

    def bloco_codigo(cod):
        """Trecho real do código, com número de linha, seguido da explicação."""
        primeira = int(cod.get("linha_inicial", 1))
        linhas = cod["trecho"].rstrip("\n").split("\n")
        numeradas = "\n".join(f"{primeira + i:>4}  {escapar_xml(l)}" for i, l in enumerate(linhas))
        # Sem keepWithNext: um trecho longo pode continuar na página seguinte em vez de pular inteiro.
        partes = [CondPageBreak(4 * cm),
                  Paragraph(f"No código: <b>{esc(cod['arquivo'])}</b>, linhas {primeira} a "
                            f"{primeira + len(linhas) - 1}", ROTULO_COD),
                  XPreformatted(numeradas, CODIGO)]
        if cod.get("explicacao"):
            partes.append(Paragraph("Lendo o trecho:", ROTULO))
            partes.append(lista(cod["explicacao"]))
        return partes

    periodo = f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    rodape = f"{c['projeto']}  ·  Semana de {periodo}  ·  v{c['versao']}  ·  atualizado em {c['atualizado_em']}"

    def desenhar_rodape(tela, doc):
        tela.setFont(FR, 8)
        tela.setFillColor(APAGADO)
        tela.drawString(2.2 * cm, 1.2 * cm, rodape)
        tela.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(doc.page))

    blocos, num = [], [0]

    def secao(titulo, quebra=4):
        num[0] += 1
        blocos.append(CondPageBreak(quebra * cm))
        blocos.append(HRFlowable(width="100%", thickness=0.6, color=LINHA, spaceBefore=12, spaceAfter=8))
        blocos.append(Paragraph(f"{num[0]}. {esc(titulo)}", SECAO))
        return num[0]

    # --- Cabeçalho ------------------------------------------------------------------
    meta = (f"Semana de {periodo}  |  Versão {c['versao']}  |  Atualizado em {c['atualizado_em']}"
            f"  |  Status: {c['status']}")
    blocos += [Paragraph(esc(f"{c['projeto']}: o que foi construído nesta semana"), TITULO),
               Paragraph(esc(meta), META)]
    if c.get("como_ler"):
        blocos.append(Paragraph(esc(c["como_ler"]), DESTAQUE))

    # --- 1. Resumo --------------------------------------------------------------------
    secao("A semana em poucas linhas")
    blocos.append(lista(c["resumo"]))

    # --- 2. Mapa do projeto -------------------------------------------------------
    k = secao("O mapa do projeto", quebra=20)
    blocos.append(Paragraph(esc(c["mapa"]["texto"]), CORPO))
    blocos.append(figura(c["mapa"]["diagrama"]))
    for j, comp in enumerate(c["mapa"]["componentes"], 1):
        marca = " (novo nesta semana)" if comp.get("novo") else ""
        texto = f"<b>{esc(comp['nome'])}</b>{marca}: {esc(comp['o_que_e'])}"
        if comp.get("analogia"):
            texto += f" <i>Analogia:</i> {esc(comp['analogia'])}"
        blocos.append(Paragraph(texto, ITEM))
    blocos.append(Spacer(1, 4))

    # --- 3. Lições: cada mudança explicada ------------------------------------------
    k = secao("O que foi construído, explicado passo a passo", quebra=8)
    licoes = sorted(c["licoes"], key=lambda l: ler_data(l["data"], "licoes.data"))
    for j, l in enumerate(licoes, 1):
        d = ler_data(l["data"], "licoes.data")
        dia = DIAS_SEMANA[d.weekday()]
        cab = [CondPageBreak(6 * cm), Paragraph(f"{k}.{j} {esc(l['titulo'])}", SUB),
               Paragraph(esc(f"{dia.capitalize()}, {l['data']} ({l['sessao']})"), SUBMETA)]
        if l.get("em_uma_frase"):
            cab.append(Paragraph(f"<b>Em uma frase:</b> {esc(l['em_uma_frase'])}", DESTAQUE))
        blocos += cab
        blocos += [Paragraph("O problema", ROTULO), Paragraph(esc(l["problema"]), CORPO),
                   Paragraph("A ideia", ROTULO), Paragraph(esc(l["ideia"]), CORPO)]
        if l.get("como_funciona"):
            blocos += [Paragraph("Como funciona", ROTULO), lista(l["como_funciona"])]
        if l.get("diagrama"):
            blocos.append(figura(l["diagrama"]))
        if l.get("codigo"):
            blocos += bloco_codigo(l["codigo"])
        if l.get("python"):
            blocos += [Paragraph("Python usado aqui", ROTULO), lista(l["python"])]
        if l.get("alternativas"):
            blocos += [Paragraph("Outras opções e por que não", ROTULO), lista(l["alternativas"])]
        if l.get("como_sabemos"):
            blocos += [Paragraph("Como sabemos que funciona", ROTULO), Paragraph(esc(l["como_sabemos"]), CORPO)]

    # --- 4. Glossário ---------------------------------------------------------------
    secao("Glossário da semana")
    for g in sorted(c["glossario"], key=lambda g: g["termo"].lower()):
        texto = f"<b>{esc(g['termo'])}</b>: {esc(g['definicao'])}"
        if g.get("no_projeto"):
            texto += f" <i>No projeto:</i> {esc(g['no_projeto'])}"
        blocos.append(Paragraph(texto, ITEM))
    blocos.append(Spacer(1, 4))

    # --- 5 a 7. Decisões, problemas e próximos passos --------------------------------
    secao("Decisões da semana")
    blocos.append(lista([f"<b>{d['data']}</b> ({d['quem']}): {d['texto']}" for d in c["decisoes"]]
                        or ["Nenhuma decisão nova nesta semana."]))
    secao("Problemas e o que eles ensinaram")
    blocos.append(lista(c["aprendizados"] or ["Nada a registrar nesta semana."]))
    secao("Próximos passos e o que você vai aprender com eles")
    blocos.append(lista(c["proximos"]))

    # --- 8. Perguntas; respostas no fim ---------------------------------------------
    k_perg = secao("Teste seu entendimento")
    blocos.append(Paragraph("Tente responder sem olhar. As respostas estão na última seção.", CORPO))
    blocos.append(lista([p["pergunta"] for p in c["perguntas"]]))
    blocos.append(PageBreak())
    secao("Respostas")
    blocos.append(lista([f"{p['resposta']}" for p in c["perguntas"]]))

    temporario = saida + ".tmp"
    doc = SimpleDocTemplate(temporario, pagesize=A4, title=f"{c['projeto']}: semana de {periodo}",
                            leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=1.9 * cm, bottomMargin=1.9 * cm)
    doc.build(blocos, onFirstPage=desenhar_rodape, onLaterPages=desenhar_rodape)

    # Anexa o JSON de origem dentro do PDF.
    from pypdf import PdfReader, PdfWriter
    escritor = PdfWriter(clone_from=PdfReader(temporario))
    escritor.add_attachment("fonte.json", json.dumps(c, ensure_ascii=False, indent=2).encode("utf-8"))
    with open(saida, "wb") as f:
        escritor.write(f)
    os.remove(temporario)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".json"):
        sys.exit("Uso: gerar_relatorio.py docs\\relatorios-semanais\\semana-AAAA-MM-DD.json")
    caminho_json = sys.argv[1]
    with open(caminho_json, encoding="utf-8") as f:
        conteudo = json.load(f)
    saida_pdf = caminho_json[:-5] + ".pdf"
    if preencher_trechos(conteudo):
        with open(caminho_json, "w", encoding="utf-8") as f:
            json.dump(conteudo, f, ensure_ascii=False, indent=2)
            f.write("\n")
    gerar(conteudo, saida_pdf, date.today())
    print("ok:", saida_pdf)

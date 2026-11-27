# -*- coding: utf-8 -*-
"""Gera o relatório semanal do projeto em PDF, a partir de um arquivo JSON.

Uso (sempre pelo ambiente virtual do projeto):
    .venv\\Scripts\\python .claude\\skills\\relatorio-semanal\\gerar_relatorio.py docs\\relatorios-semanais\\semana-AAAA-MM-DD.json

O PDF sai ao lado do JSON, com o mesmo nome. O padrão visual é o do doc-projeto-pdf
(fonte Inter, seções numeradas, sem tabelas nem cores). O JSON também vai anexado
dentro do PDF (anexo "fonte.json"), para o documento poder ser refeito no futuro.

Datas: o script CONFERE as datas antes de gerar (a semana começa numa segunda,
cada sessão cai dentro da semana, nenhuma data é posterior a hoje) e calcula
sozinho o dia da semana de cada sessão. Assim, um erro de data impede o PDF
em vez de ir parar no documento.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta

from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem,
                                Paragraph, SimpleDocTemplate)

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
PASTA_FONTES = os.path.join(tempfile.gettempdir(), "doc-padrao-fonts")


# ---------------------------------------------------------------------------
# 1. Datas: leitura e conferência
# ---------------------------------------------------------------------------
def ler_data(texto, campo):
    """Converte 'DD/MM/AAAA' em date; para com uma mensagem clara se o formato estiver errado."""
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except (TypeError, ValueError):
        sys.exit(f"Data inválida em '{campo}': {texto!r} (use DD/MM/AAAA).")


def conferir_datas(c, hoje):
    """Confere todas as datas do relatório; devolve (inicio, fim) da semana."""
    inicio = ler_data(c["semana_inicio"], "semana_inicio")
    if inicio.weekday() != 0:
        sys.exit(f"semana_inicio ({c['semana_inicio']}) não é uma segunda-feira.")
    fim = inicio + timedelta(days=6)
    atualizado = ler_data(c["atualizado_em"], "atualizado_em")
    if atualizado > hoje:
        sys.exit(f"atualizado_em ({c['atualizado_em']}) é posterior a hoje ({hoje:%d/%m/%Y}).")
    vistas = set()
    for s in c["sessoes"]:
        d = ler_data(s["data"], "sessoes.data")
        if not inicio <= d <= fim:
            sys.exit(f"Sessão de {s['data']} fora da semana {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}.")
        if d > atualizado:
            sys.exit(f"Sessão de {s['data']} é posterior a atualizado_em ({c['atualizado_em']}).")
        if d in vistas:
            sys.exit(f"Duas sessões com a mesma data ({s['data']}): junte-as numa só.")
        vistas.add(d)
    for dec in c["decisoes"]:
        d = ler_data(dec["data"], "decisoes.data")
        if d > atualizado:
            sys.exit(f"Decisão datada de {dec['data']}, depois de atualizado_em.")
    return inicio, fim


# ---------------------------------------------------------------------------
# 2. Fonte Inter (procura no Windows; se não houver, baixa pelo npm, de graça)
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
    """Devolve os caminhos (regular, negrito) da Inter em TTF, preparando-os se preciso."""
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


# ---------------------------------------------------------------------------
# 3. Montagem do PDF
# ---------------------------------------------------------------------------
def gerar(c, saida, hoje):
    inicio, fim = conferir_datas(c, hoje)

    reg, neg = preparar_inter()
    pdfmetrics.registerFont(TTFont("Inter", reg))
    pdfmetrics.registerFont(TTFont("Inter-Bold", neg))
    for italico, negrito in ((0, 0), (0, 1), (1, 0), (1, 1)):
        addMapping("Inter", negrito, italico, "Inter-Bold" if negrito else "Inter")

    FR, FB, TAM = "Inter", "Inter-Bold", 9.8
    TINTA, APAGADO, LINHA = colors.HexColor("#111111"), colors.HexColor("#5A5A5A"), colors.HexColor("#BBBBBB")
    TITULO = ParagraphStyle("TITULO", fontName=FB, fontSize=19, leading=23, textColor=TINTA, spaceAfter=4)
    META = ParagraphStyle("META", fontName=FR, fontSize=9, leading=12, textColor=APAGADO, spaceAfter=2)
    SECAO = ParagraphStyle("SECAO", fontName=FB, fontSize=13.5, leading=17, textColor=TINTA,
                           spaceAfter=4, keepWithNext=1)
    SUB = ParagraphStyle("SUB", fontName=FB, fontSize=11.5, leading=15, textColor=TINTA, spaceBefore=8,
                         spaceAfter=3, keepWithNext=1)
    CORPO = ParagraphStyle("CORPO", fontName=FR, fontSize=TAM, leading=14.6, textColor=TINTA, spaceAfter=4)
    ITEM = ParagraphStyle("ITEM", parent=CORPO, spaceAfter=2)
    ROTULO = ParagraphStyle("ROTULO", parent=CORPO, spaceBefore=3, spaceAfter=2, keepWithNext=1)

    # Escapa o "&" solto (o reportlab lê o texto como XML simples).
    esc = lambda t: re.sub(r"&(?!amp;|lt;|gt;|quot;|#\d+;)", "&amp;", t)

    def lista(itens):
        return ListFlowable([ListItem(Paragraph(esc(i), ITEM), leftIndent=16) for i in itens],
                            bulletType="1", bulletFormat="%s.", bulletFontName=FR, bulletFontSize=TAM,
                            leftIndent=16, spaceAfter=3)

    periodo = f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    rodape = f"{c['projeto']}  ·  Semana de {periodo}  ·  v{c['versao']}  ·  atualizado em {c['atualizado_em']}"

    def desenhar_rodape(tela, doc):
        tela.setFont(FR, 8)
        tela.setFillColor(APAGADO)
        tela.drawString(2.3 * cm, 1.3 * cm, rodape)
        tela.drawRightString(A4[0] - 2.3 * cm, 1.3 * cm, str(doc.page))

    blocos, num = [], [0]

    def secao(titulo):
        num[0] += 1
        blocos.append(CondPageBreak(4 * cm))
        blocos.append(HRFlowable(width="100%", thickness=0.6, color=LINHA, spaceBefore=10, spaceAfter=7))
        blocos.append(Paragraph(f"{num[0]}. {esc(titulo)}", SECAO))
        return num[0]

    meta = (f"Semana de {periodo}  |  Versão {c['versao']}  |  Atualizado em {c['atualizado_em']}"
            f"  |  Status: {c['status']}")
    blocos += [Paragraph(esc(f"{c['projeto']}: relatório da semana"), TITULO), Paragraph(esc(meta), META)]

    secao("Onde o projeto estava no início da semana")
    blocos.append(Paragraph(esc(c["situacao"]), CORPO))

    secao("Foco da semana")
    blocos.append(Paragraph(esc(c["foco"]), CORPO))

    secao("Linha de raciocínio da semana")
    blocos.append(lista(c["raciocinio"]))

    k = secao("Sessões da semana")
    sessoes = sorted(c["sessoes"], key=lambda s: ler_data(s["data"], "sessoes.data"))
    for j, s in enumerate(sessoes, 1):
        d = ler_data(s["data"], "sessoes.data")
        dia = DIAS_SEMANA[d.weekday()].capitalize()
        bloco = [Paragraph(esc(f"{k}.{j} {dia}, {s['data']} ({s['sessao']}): {s['titulo']}"), SUB),
                 Paragraph("<b>O que foi feito:</b>", ROTULO), lista(s["feito"]),
                 Paragraph(f"<b>Por quê:</b> {esc(s['por_que'])}", CORPO),
                 Paragraph(f"<b>Resultado:</b> {esc(s['resultado'])}", CORPO)]
        if s.get("tecnico"):
            bloco.append(Paragraph(f"<b>Em termos técnicos:</b> {esc(s['tecnico'])}", CORPO))
        blocos.append(KeepTogether(bloco))

    secao("Decisões da semana")
    blocos.append(lista([f"<b>{d['data']}</b> ({d['quem']}): {d['texto']}" for d in c["decisoes"]]
                        or ["Nenhuma decisão nova nesta semana."]))

    secao("Problemas e aprendizados")
    blocos.append(lista(c["aprendizados"] or ["Nada a registrar nesta semana."]))

    secao("Próximos passos")
    blocos.append(lista(c["proximos"]))

    temporario = saida + ".tmp"
    doc = SimpleDocTemplate(temporario, pagesize=A4, title=f"{c['projeto']}: semana de {periodo}",
                            leftMargin=2.3 * cm, rightMargin=2.3 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm)
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
    gerar(conteudo, saida_pdf, date.today())
    print("ok:", saida_pdf)

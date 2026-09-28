"""
Utilidades python-pptx para la presentación del curso (paleta "Midnight Tech").

Convenciones:
  - Diapositivas en blanco: prs.slide_layouts[6]
  - Fondo: slide.background.fill.solid() + fore_color.rgb
  - Fuentes seguras: Calibri (títulos), Arial (cuerpo), Courier New (código)
"""
from __future__ import annotations

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------- Paleta
BG = RGBColor(0x0F, 0x19, 0x23)
PANEL = RGBColor(0x16, 0x23, 0x2F)
PANEL2 = RGBColor(0x1D, 0x2D, 0x3B)
BORDER = RGBColor(0x2A, 0x3E, 0x50)
TEXT = RGBColor(0xE6, 0xEE, 0xF5)
MUTED = RGBColor(0x8E, 0xA3, 0xB5)
CYAN = RGBColor(0x00, 0xD4, 0xFF)
GOLD = RGBColor(0xF5, 0xA6, 0x23)
GREEN = RGBColor(0x00, 0xE6, 0x76)
RED = RGBColor(0xFF, 0x5C, 0x7A)
PURPLE = RGBColor(0x9B, 0x7B, 0xFF)
DARK = RGBColor(0x0A, 0x12, 0x1A)

TITLE_FONT = "Calibri"
BODY_FONT = "Arial"
CODE_FONT = "Courier New"

SLIDE_W, SLIDE_H = 13.333, 7.5
FOOTER = "Fundamentos de Arquitectura LLM · BSG Institute"


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.n = 0

    # ------------------------------------------------------------ slides
    def blank(self, bg: RGBColor = BG):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = bg
        self.n += 1
        return s

    def content(self, tag: str, title: str, notes: str = "", footer: bool = True):
        s = self.blank()
        text(s, 0.6, 0.32, 12, 0.35, tag.upper(), size=12, color=CYAN, bold=True, font=BODY_FONT, spacing=150)
        text(s, 0.6, 0.62, 12.1, 0.85, title, size=32, color=TEXT, bold=True, font=TITLE_FONT)
        if footer:
            text(s, 0.6, 7.05, 8, 0.3, FOOTER, size=9, color=MUTED)
            text(s, 11.9, 7.05, 0.83, 0.3, str(self.n), size=9, color=MUTED, align=PP_ALIGN.RIGHT)
        if notes:
            add_notes(s, notes)
        return s

    def save(self, path: str):
        self.prs.save(path)


# ---------------------------------------------------------------- texto
def _apply_run(run, size, color, bold, italic, font, spacing=None):
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.name = font
    f.color.rgb = color
    if spacing:
        run._r.get_or_add_rPr().set("spc", str(spacing))


def text(slide, x, y, w, h, content, size=16, color=TEXT, bold=False, italic=False, font=BODY_FONT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, line_spacing=None, margin=0.0):
    """content puede ser str (\n = párrafo nuevo) o lista de párrafos; cada párrafo str o lista de runs
    (texto, {opciones}) para mezclar estilos."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(margin))
    paragraphs = content.split("\n") if isinstance(content, str) else content
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if line_spacing:
            p.line_spacing = line_spacing
        runs = [(para, {})] if isinstance(para, str) else para
        for rt, opts in runs:
            r = p.add_run()
            r.text = rt
            _apply_run(r, opts.get("size", size), opts.get("color", color), opts.get("bold", bold),
                       opts.get("italic", italic), opts.get("font", font), opts.get("spacing", spacing))
    return tb


def bullets(slide, x, y, w, h, items, size=16, color=TEXT, bullet_color=CYAN, space_after=8, font=BODY_FONT,
            char="•"):
    """items: lista de str o (str_negrita, str_normal) o ('  sub', ...) para sub-viñeta (2 espacios)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0))
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        level = 0
        if isinstance(item, str) and item.startswith("  "):
            level, item = 1, item.strip()
        p.space_after = Pt(space_after)
        pPr = p._p.get_or_add_pPr()
        indent = 0.28 if level == 0 else 0.26
        pPr.set("marL", str(Inches(indent + level * 0.35)))
        pPr.set("indent", str(-Inches(indent)))
        buClr = etree.SubElement(pPr, qn("a:buClr"))
        clr = etree.SubElement(buClr, qn("a:srgbClr"))
        clr.set("val", str(bullet_color if level == 0 else MUTED))
        buFont = etree.SubElement(pPr, qn("a:buFont"))
        buFont.set("typeface", "Arial")
        buChar = etree.SubElement(pPr, qn("a:buChar"))
        buChar.set("char", char if level == 0 else "–")
        sz = size if level == 0 else size - 2
        if isinstance(item, tuple):
            r = p.add_run()
            r.text = item[0]
            _apply_run(r, sz, color, True, False, font)
            r2 = p.add_run()
            r2.text = item[1]
            _apply_run(r2, sz, color if level == 0 else MUTED, False, False, font)
        else:
            r = p.add_run()
            r.text = item
            _apply_run(r, sz, color if level == 0 else MUTED, False, False, font)
    return tb


# ---------------------------------------------------------------- formas
def box(slide, x, y, w, h, fill=PANEL, line=None, radius=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_w=1.0):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = radius
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    shp.text_frame.text = ""
    return shp


def shape_text(shp, content, size=14, color=TEXT, bold=False, align=PP_ALIGN.CENTER, font=BODY_FONT,
               anchor=MSO_ANCHOR.MIDDLE, margin=0.08):
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(margin))
    paragraphs = content.split("\n") if isinstance(content, str) else content
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = [(para, {})] if isinstance(para, str) else para
        for rt, opts in runs:
            r = p.add_run()
            r.text = rt
            _apply_run(r, opts.get("size", size), opts.get("color", color), opts.get("bold", bold),
                       opts.get("italic", False), opts.get("font", font))
    return shp


def pill(slide, x, y, w, h, label, fill=CYAN, color=BG, size=12, bold=True):
    b = box(slide, x, y, w, h, fill=fill, radius=0.5)
    return shape_text(b, label, size=size, color=color, bold=bold, margin=0.02)


def circle(slide, x, y, d, label="", fill=CYAN, color=BG, size=16, bold=True):
    c = box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    if label:
        shape_text(c, label, size=size, color=color, bold=bold, margin=0)
    return c


def card(slide, x, y, w, h, title, body, accent=CYAN, icon=None, title_size=17, body_size=13, fill=PANEL):
    """Tarjeta: fondo tenue + ícono en círculo + título + cuerpo."""
    box(slide, x, y, w, h, fill=fill)
    tx = x + 0.25
    if icon:
        circle(slide, x + 0.25, y + 0.25, 0.5, icon, fill=accent, size=14)
        tx = x + 0.9
    text(slide, tx, y + 0.22, w - (tx - x) - 0.2, 0.6, title, size=title_size, color=accent, bold=True,
         font=TITLE_FONT, anchor=MSO_ANCHOR.MIDDLE)
    text(slide, x + 0.25, y + 0.9, w - 0.45, h - 1.05, body, size=body_size, color=TEXT, line_spacing=1.1)


def arrow(slide, x1, y1, x2, y2, color=MUTED, width=2.0, head=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if head:
        ln = c.line._get_or_add_ln()
        tail = etree.SubElement(ln, qn("a:tailEnd"))
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
    return c


def line(slide, x1, y1, x2, y2, color=BORDER, width=1.0):
    return arrow(slide, x1, y1, x2, y2, color=color, width=width, head=False)


def code_block(slide, x, y, w, h, code, size=12):
    b = box(slide, x, y, w, h, fill=DARK, line=BORDER, radius=0.04)
    shape_text(b, code, size=size, color=GREEN, font=CODE_FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
               margin=0.15)
    return b


# ---------------------------------------------------------------- tablas nativas
def _cell_borders(cell, color, width_pt=0.75):
    """Bordes finos del color indicado (por defecto PowerPoint/LibreOffice dibujan líneas blancas)."""
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = tcPr.find(qn(tag))
        if ln is not None:
            tcPr.remove(ln)
    # Los bordes deben ir ANTES del relleno (solidFill) dentro de tcPr.
    fill = tcPr.find(qn("a:solidFill"))
    for i, tag in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        ln = etree.Element(qn(tag), w=str(int(width_pt * 12700)), cap="flat", cmpd="sng", algn="ctr")
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=str(color))
        etree.SubElement(ln, qn("a:prstDash"), val="solid")
        if fill is not None:
            fill.addprevious(ln)
        else:
            tcPr.append(ln)


def table(slide, x, y, w, h, rows, col_widths=None, header_fill=PANEL2, font_size=12, header_color=CYAN,
          first_col_bold=True, zebra=(PANEL, BG)):
    n_rows, n_cols = len(rows), len(rows[0])
    gf = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = gf.table
    # Quitar el estilo por defecto para controlar colores
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    for attr in ("bandRow", "firstRow"):
        tblPr.set(attr, "0")
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for r, row in enumerate(rows):
        tbl.rows[r].height = Inches(h / n_rows)
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if r == 0 else zebra[r % 2]
            cell.margin_left = cell.margin_right = Inches(0.1)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            _cell_borders(cell, BORDER)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(val)
            is_head = r == 0
            _apply_run(run, font_size, header_color if is_head else (TEXT if c else (GOLD if first_col_bold else TEXT)),
                       is_head or (c == 0 and first_col_bold), False, BODY_FONT)
    return gf


# ---------------------------------------------------------------- gráficos nativos
def style_chart(chart, legend=True, number_format=None, log=False, y_title=None, y_min=None, y_max=None):
    chart.has_title = False
    chart.font.name = BODY_FONT
    chart.font.size = Pt(11)
    chart.font.color.rgb = MUTED
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.color.rgb = TEXT
        chart.legend.font.size = Pt(11)
    va = chart.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = BORDER
    va.format.line.fill.background()
    va.tick_labels.font.color.rgb = MUTED
    if number_format:
        va.tick_labels.number_format = number_format
        va.tick_labels.number_format_is_linked = False
    if log:
        scaling = va._element.find(qn("c:scaling"))
        lb = etree.SubElement(scaling, qn("c:logBase"))
        lb.set("val", "10")
        scaling.remove(lb)
        scaling.insert(0, lb)
    if y_min is not None:
        va.minimum_scale = y_min
    if y_max is not None:
        va.maximum_scale = y_max
    if y_title:
        va.has_title = True
        va.axis_title.text_frame.text = y_title
        r = va.axis_title.text_frame.paragraphs[0].runs[0]
        r.font.size = Pt(11)
        r.font.color.rgb = MUTED
        r.font.bold = False
    ca = chart.category_axis
    ca.tick_labels.font.color.rgb = TEXT
    ca.format.line.color.rgb = BORDER
    ca.has_major_gridlines = False
    return chart


def bar_chart(slide, x, y, w, h, categories, series: dict, colors, horizontal=False, clustered=True, **kw):
    data = CategoryChartData()
    if horizontal:  # las barras horizontales se dibujan de abajo hacia arriba: invertir para leer en orden
        categories = list(reversed(categories))
        series = {k: list(reversed(v)) for k, v in series.items()}
    data.categories = categories
    for name, values in series.items():
        data.add_series(name, values)
    kind = (XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED)
    gf = slide.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), data)
    chart = gf.chart
    for s, col in zip(chart.series, colors):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = col
    labels = kw.pop("labels", False)
    label_fmt = kw.pop("label_fmt", None)
    gap = kw.pop("gap", 60)
    chart.plots[0].gap_width = gap
    if labels:
        pl = chart.plots[0]
        pl.has_data_labels = True
        dl = pl.data_labels
        dl.font.size = Pt(11)
        dl.font.color.rgb = TEXT
        if label_fmt:
            dl.number_format = label_fmt
            dl.number_format_is_linked = False
    style_chart(chart, legend=len(series) > 1, **kw)
    return chart


def line_chart(slide, x, y, w, h, categories, series: dict, colors, **kw):
    data = CategoryChartData()
    data.categories = categories
    for name, values in series.items():
        data.add_series(name, values)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(x), Inches(y), Inches(w), Inches(h), data)
    chart = gf.chart
    for s, col in zip(chart.series, colors):
        s.format.line.color.rgb = col
        s.format.line.width = Pt(3)
        s.smooth = False
        s.marker.style = None
        s.marker.format.fill.background()
        from pptx.enum.chart import XL_MARKER_STYLE
        s.marker.style = XL_MARKER_STYLE.NONE
    style_chart(chart, legend=True, **kw)
    return chart


# ---------------------------------------------------------------- notas
def add_notes(slide, notes: str):
    slide.notes_slide.notes_text_frame.text = notes.strip()


__all__ = [n for n in dir() if not n.startswith("_")]
_unused = (Emu,)

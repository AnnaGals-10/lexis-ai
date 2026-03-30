"""Report generation module for formatting contract analysis results."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import io
from datetime import datetime

W = A4[0] - 5 * cm  # usable width

def _style(name, **kwargs):
    base = ParagraphStyle(name, fontName="Helvetica", fontSize=10,
                          textColor=colors.HexColor("#1a1a1a"), leading=16)
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base

STYLES = {
    "logo":     _style("logo", fontSize=11, fontName="Helvetica-Bold"),
    "eyebrow":  _style("eyebrow", fontSize=8, textColor=colors.HexColor("#aaaaaa"), spaceAfter=4),
    "title":    _style("title", fontSize=22, fontName="Helvetica-Bold", spaceAfter=4, leading=28),
    "meta":     _style("meta", fontSize=9, textColor=colors.HexColor("#888888"), spaceAfter=16),
    "section":  _style("section", fontSize=8, fontName="Helvetica-Bold",
                       textColor=colors.HexColor("#888888"), spaceAfter=10, leading=12),
    "body":     _style("body", fontSize=10, spaceAfter=6, leading=16),
    "small":    _style("small", fontSize=9, textColor=colors.HexColor("#555555"), leading=14, spaceAfter=4),
    "italic":   _style("italic", fontSize=9, fontName="Helvetica-Oblique",
                       textColor=colors.HexColor("#888888"), leading=14, leftIndent=10),
    "flag":     _style("flag", fontSize=10, fontName="Helvetica-Bold", spaceAfter=2),
    "bench":    _style("bench", fontSize=9, textColor=colors.HexColor("#9b8f7a"),
                       leading=14, spaceAfter=4, leftIndent=10),
    "neg_lbl":  _style("neg_lbl", fontSize=7, fontName="Helvetica-Bold",
                       textColor=colors.HexColor("#9b8f7a"), spaceAfter=2),
    "neg_txt":  _style("neg_txt", fontSize=9, textColor=colors.HexColor("#444444"),
                       leading=14, leftIndent=10, spaceAfter=6),
    "footer":   _style("footer", fontSize=8, textColor=colors.HexColor("#bbbbbb"), alignment=TA_CENTER),
}

HR  = lambda: HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e0e0e0"), spaceAfter=10)
HRt = lambda: HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#f0f0f0"), spaceAfter=6)
SP  = lambda h=0.4: Spacer(1, h * cm)


def generate_report(contract_name, summary, flags, risk, negotiations=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("LEXIS AI", STYLES["logo"]))
    story.append(Paragraph("Contract Analysis Report", STYLES["eyebrow"]))
    story.append(HR())
    story.append(SP(0.3))
    story.append(Paragraph(contract_name, STYLES["title"]))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        STYLES["meta"]
    ))

    # ── Overview table ────────────────────────────────────────────────────────
    score = risk.get("puntuacio", 0)
    rec   = risk.get("recomanacio", "—")
    tipus = summary.get("tipus_contracte", "—")
    durada = summary.get("durada", "Not specified")
    parts  = " · ".join(summary.get("parts_involucrades", []))

    score_color = colors.HexColor("#c0392b") if score >= 7 else \
                  colors.HexColor("#e67e22") if score >= 4 else \
                  colors.HexColor("#27ae60")

    overview = [
        [Paragraph("RISK SCORE", STYLES["section"]),
         Paragraph("RECOMMENDATION", STYLES["section"]),
         Paragraph("CONTRACT TYPE", STYLES["section"])],
        [Paragraph(f"<font size='24' color='#{score_color.hexval()[2:]}'><b>{score}/10</b></font>", STYLES["body"]),
         Paragraph(f"<b>{rec}</b>", STYLES["body"]),
         Paragraph(tipus, STYLES["body"])],
    ]
    tbl = Table(overview, colWidths=[4*cm, 5.5*cm, 7*cm])
    tbl.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LINEBELOW",   (0,0), (-1,0),  0.5, colors.HexColor("#e0e0e0")),
        ("LINEBELOW",   (0,1), (-1,1),  0.5, colors.HexColor("#e0e0e0")),
        ("TOPPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(SP(0.3))
    story.append(Paragraph(risk.get("justificacio", ""), STYLES["small"]))
    story.append(SP(0.3))

    # Parties / Duration
    info = [
        [Paragraph("PARTIES", STYLES["section"]), Paragraph("DURATION", STYLES["section"])],
        [Paragraph(parts or "—", STYLES["body"]),  Paragraph(durada, STYLES["body"])],
    ]
    info_tbl = Table(info, colWidths=[9*cm, 7.5*cm])
    info_tbl.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LINEBELOW",   (0,1), (-1,1),  0.5, colors.HexColor("#e0e0e0")),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ]))
    story.append(info_tbl)
    story.append(SP(0.6))

    # ── Risk clauses ──────────────────────────────────────────────────────────
    story.append(Paragraph(f"RISK CLAUSES  ({len(flags)} found)", STYLES["section"]))
    story.append(HR())

    neg_map = {}
    if negotiations:
        for n in negotiations:
            neg_map[n.get("titol", "")] = n.get("proposta", "")

    for flag in flags:
        risc = flag.get("risc", "low").lower()
        risk_hex = "c0392b" if "high" in risc or "alt" in risc else \
                   "e67e22" if "med"  in risc or "mitj" in risc else "888888"

        row = [[
            Paragraph(flag.get("titol", ""), STYLES["flag"]),
            Paragraph(
                f"<font color='#{risk_hex}'><b>{risc.upper()}</b></font>",
                ParagraphStyle("RiskLabel", fontSize=8, fontName="Helvetica-Bold", alignment=TA_RIGHT)
            )
        ]]
        rtbl = Table(row, colWidths=[13*cm, 3.5*cm])
        rtbl.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
        story.append(rtbl)
        story.append(Paragraph(flag.get("descripcio", ""), STYLES["small"]))

        if flag.get("benchmark"):
            story.append(Paragraph(f"Benchmark: {flag['benchmark']}", STYLES["bench"]))
        if flag.get("fragment"):
            story.append(Paragraph(f'"{flag["fragment"]}"', STYLES["italic"]))

        suggestion = neg_map.get(flag.get("titol", ""))
        if suggestion:
            story.append(SP(0.15))
            story.append(Paragraph("SUGGESTED REFORMULATION", STYLES["neg_lbl"]))
            story.append(Paragraph(suggestion, STYLES["neg_txt"]))

        story.append(HRt())
        story.append(SP(0.1))

    story.append(SP(0.4))

    # ── Executive summary ─────────────────────────────────────────────────────
    story.append(Paragraph("EXECUTIVE SUMMARY", STYLES["section"]))
    story.append(HR())

    punts = summary.get("punts_clau", [])
    obligacions = summary.get("obligacions_principals", [])

    if punts:
        story.append(Paragraph("KEY POINTS", ParagraphStyle("KP", fontSize=8,
            fontName="Helvetica-Bold", textColor=colors.HexColor("#bbbbbb"), spaceAfter=8)))
        for i, p in enumerate(punts):
            story.append(Paragraph(f"<b>{str(i+1).zfill(2)}</b>   {p}", STYLES["small"]))
            story.append(HRt())

    story.append(SP(0.3))

    if obligacions:
        story.append(Paragraph("MAIN OBLIGATIONS", ParagraphStyle("MO", fontSize=8,
            fontName="Helvetica-Bold", textColor=colors.HexColor("#bbbbbb"), spaceAfter=8)))
        for i, o in enumerate(obligacions):
            story.append(Paragraph(f"<b>{str(i+1).zfill(2)}</b>   {o}", STYLES["small"]))
            story.append(HRt())

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(SP(1))
    story.append(HR())
    story.append(Paragraph(
        "Generated by Lexis AI · For informational purposes only · This report does not constitute legal advice.",
        STYLES["footer"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# 07 · Generate PDF Report -- China NLP Social Listening (XHS)
# Produces: outputs/Laporan_KSF_China_NLP_2026.pdf
# Run: conda activate ml && python notebooks/07_generate_report.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from config.settings import DATA_RESULTS, OUTPUTS_DIR, FIGURES_DIR

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable, KeepTogether,
    PageBreak, NextPageTemplate,
)
from reportlab.pdfgen import canvas as pdfcanvas

# -- Constants --------------------------------------------------------
W, H   = A4
ML, MR = 2.2*cm, 2.2*cm
MT, MB = 2.5*cm, 2.0*cm
TW     = W - ML - MR

C_DARK   = colors.HexColor("#1A3A5C")
C_ACCENT = colors.HexColor("#2980B9")
C_LIGHT  = colors.HexColor("#D6EAF8")
C_TEXT   = colors.HexColor("#2C3E50")
C_GREY   = colors.HexColor("#7F8C8D")
C_WHITE  = colors.white

OUT_PDF  = OUTPUTS_DIR / "Laporan_KSF_China_NLP_2026.pdf"

# -- Load data --------------------------------------------------------
flavor_df     = pd.read_csv(DATA_RESULTS / "flavor_frequency.csv")
pain_df       = pd.read_csv(DATA_RESULTS / "pain_point_frequency.csv")
occasion_df   = pd.read_csv(DATA_RESULTS / "occasion_distribution.csv")
format_df     = pd.read_csv(DATA_RESULTS / "format_mentions.csv")
competitor_df = pd.read_csv(DATA_RESULTS / "competitor_sentiment.csv")
cluster_df    = pd.read_csv(DATA_RESULTS / "cluster_profiles.csv")

# -- Styles -----------------------------------------------------------
def S(name, **kw):
    return ParagraphStyle(name, **kw)

sTitle  = S("sTitle",  fontName="Helvetica-Bold",   fontSize=32, textColor=C_WHITE,  leading=40, spaceAfter=12)
sSubT   = S("sSubT",   fontName="Helvetica",         fontSize=14, textColor=C_WHITE,  leading=20, spaceAfter=8)
sBadge  = S("sBadge",  fontName="Helvetica",         fontSize=11, textColor=C_WHITE,  leading=14)
sMeta   = S("sMeta",   fontName="Helvetica",         fontSize=10, textColor=C_WHITE,  leading=16)
sH1     = S("sH1",     fontName="Helvetica-Bold",    fontSize=22, textColor=C_DARK,   leading=28, spaceBefore=6, spaceAfter=4)
sH2     = S("sH2",     fontName="Helvetica-Bold",    fontSize=14, textColor=C_DARK,   leading=20, spaceBefore=14, spaceAfter=6)
sBody   = S("sBody",   fontName="Helvetica",          fontSize=10, textColor=C_TEXT,   leading=15, spaceAfter=6,  alignment=TA_JUSTIFY)
sCapt   = S("sCapt",   fontName="Helvetica-Oblique",  fontSize=9,  textColor=C_GREY,   leading=13, spaceAfter=14, alignment=TA_CENTER)
sCall   = S("sCall",   fontName="Helvetica",          fontSize=10, textColor=C_TEXT,   leading=15)
sTableH = S("sTH",     fontName="Helvetica-Bold",    fontSize=9,  textColor=C_WHITE,  alignment=TA_LEFT, leading=12)
sTableC = S("sTC",     fontName="Helvetica",          fontSize=9,  textColor=C_TEXT,   alignment=TA_LEFT, leading=12)
sStatN  = S("sSN",     fontName="Helvetica-Bold",    fontSize=26, textColor=C_DARK,   leading=30, alignment=TA_CENTER)
sStatL  = S("sSL",     fontName="Helvetica",          fontSize=9,  textColor=C_GREY,   leading=13, alignment=TA_CENTER)

# -- NumberedCanvas: single-pass "Page X / N" -------------------------
class NumberedCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            if i > 0:
                self._draw_footer(i + 1, total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_footer(self, page_num, total):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#BDC3C7"))
        self.setLineWidth(0.5)
        self.line(ML, MB - 4*mm, W - MR, MB - 4*mm)
        self.setFont("Helvetica", 8)
        self.setFillColor(C_GREY)
        self.drawString(ML, MB - 8*mm, "Laporan China NLP Social Listening - KSF 2026")
        self.drawRightString(W - MR, MB - 8*mm, f"{page_num} / {total}")
        self.restoreState()


# -- Page callbacks ---------------------------------------------------
def cover_page(c, doc):
    c.saveState()
    c.setFillColor(C_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, 0, W, 0.8*cm, fill=1, stroke=0)
    c.restoreState()

def body_page(c, doc):
    pass  # footer handled by NumberedCanvas


# -- Helpers ----------------------------------------------------------
def fig(name, width=TW, caption=None):
    p = FIGURES_DIR / name
    if not p.exists():
        return []
    elems = [Image(str(p), width=width, height=width * 0.62)]
    if caption:
        elems.append(Paragraph(caption, sCapt))
    return elems

def h1(text):
    """H1 with HR, wrapped in KeepTogether so header never orphans."""
    block = [
        Paragraph(text, sH1),
        HRFlowable(width=TW, thickness=1.5, color=C_ACCENT, spaceAfter=10),
    ]
    return [KeepTogether(block)]

def h2(text):
    t = Table([[Paragraph(text, sH2)]], colWidths=[TW])
    t.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LINEBEFORE",   (0,0), (-1,-1), 4, C_ACCENT),
        ("BACKGROUND",   (0,0), (-1,-1), colors.white),
    ]))
    return [t, Spacer(1, 2)]

def body(text):
    return Paragraph(text, sBody)

def sp(h=6):
    return Spacer(1, h)

def callout(bold_intro, text):
    t = Table([[Paragraph(f'<b>{bold_intro}</b> {text}', sCall)]], colWidths=[TW])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_LIGHT),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LINEBEFORE",   (0,0), (-1,-1), 4, C_ACCENT),
        ("BOX",          (0,0), (-1,-1), 0.5, C_ACCENT),
    ]))
    return [t, sp(10)]

def dtable(headers, rows, col_widths=None):
    if col_widths is None:
        col_widths = [TW / len(headers)] * len(headers)
    data = [[Paragraph(h, sTableH) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), sTableC) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  C_ACCENT),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, C_LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#BDC3C7")),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    return [t, sp(8)]

def stat_cards(cards):
    n = len(cards)
    cw = TW / n
    t = Table(
        [[Paragraph(num, sStatN) for num, _ in cards],
         [Paragraph(lbl, sStatL) for _, lbl in cards]],
        colWidths=[cw]*n,
    )
    t.setStyle(TableStyle([
        ("BOX",          (0,0), (-1,-1), 0.5, C_ACCENT),
        ("INNERGRID",    (0,0), (-1,-1), 0.5, C_ACCENT),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    return [t, sp(14)]


# ====================================================================
# STORY
# ====================================================================
story = []

# -- COVER ------------------------------------------------------------
story.append(NextPageTemplate("Cover"))
story.append(Spacer(1, 8.0*cm))
story.append(Paragraph("Laporan Consumer Intelligence", sTitle))
story.append(Paragraph("China NLP Social Listening", sTitle))
story.append(sp(8))
story.append(Paragraph("untuk KSF Global Innovation Competition 2026", sSubT))
story.append(sp(14))

bt = Table(
    [[Paragraph("Xiaohongshu  |  Pasar China  |  Bahasa Mandarin", sBadge)]],
    colWidths=[TW],
)
bt.setStyle(TableStyle([
    ("BOX",          (0,0), (-1,-1), 1, C_WHITE),
    ("LEFTPADDING",  (0,0), (-1,-1), 10),
    ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ("TOPPADDING",   (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
]))
story.append(bt)
story.append(Spacer(1, 8.5*cm))
story.append(Paragraph("<b>Platform:</b> Xiaohongshu - media sosial China terbesar untuk rekomendasi produk", sMeta))
story.append(Paragraph("<b>Posts dianalisis:</b> 1.147 posts dan komentar, analisis sentimen berbasis AI", sMeta))
story.append(Paragraph("<b>Produk target:</b> MoBai - Yogurt Protein RTD, pasar urban China usia 25-38 tahun", sMeta))
story.append(Paragraph("<b>Cakupan analisis:</b> Flavor, pain point, momen konsumsi, format, dan persaingan brand", sMeta))

# -- BODY PAGES -------------------------------------------------------
story.append(NextPageTemplate("Body"))
story.append(PageBreak())

# ====================================================================
# 1. RINGKASAN EKSEKUTIF
# ====================================================================
story += h1("1. Ringkasan Eksekutif")
story.append(body(
    "Laporan ini menyajikan hasil analisis consumer intelligence berbasis media sosial China "
    "untuk mendukung pengembangan produk MoBai - yogurt protein RTD yang ditargetkan pada "
    "konsumen urban China usia 25-38 tahun. Data dikumpulkan dari Xiaohongshu, platform "
    "media sosial China dengan basis pengguna terbesar untuk rekomendasi produk kecantikan, "
    "kesehatan, dan makanan-minuman. Total 1.254 posts dan komentar berhasil dikumpulkan, "
    "menghasilkan 1.147 posts setelah proses pembersihan dan penghilangan duplikat."
))
story.append(body(
    "Analisis mencakup enam dimensi utama: preferensi flavor, pain point sensoris, momen "
    "konsumsi, daya tarik format produk, persaingan brand, dan segmentasi konsumen berbasis AI. "
    "Seluruh proses menggunakan model AI bahasa Mandarin untuk memastikan akurasi analisis "
    "sentimen pada konten berbahasa China."
))
story.append(sp(10))
story += stat_cards([
    ("1.147",   "Posts dianalisis\n(setelah dedup)"),
    ("81,8 %",  "Sentimen positif\nXiaohongshu"),
    ("k = 7",   "Segmen konsumen\nteridentifikasi"),
    ("Milk Tea","Flavor Teratas\n(202 mentions, 88% positif)"),
])
story.append(body(
    "Temuan utama: Milk Tea, Coconut, dan Matcha mendominasi percakapan flavor di Xiaohongshu "
    "dengan sentimen sangat positif. Tiga keluhan sensoris terbesar konsumen adalah aroma "
    "amis/fishy (40 mentions), rasa terlalu manis (39 mentions), dan harga terlalu tinggi "
    "(38 mentions). Segmentasi konsumen menunjukkan 71% posts berasal dari segmen Morning, "
    "mengonfirmasi positioning MoBai sebagai minuman pagi hari urban."
))
story += callout(
    "Catatan metodologis.",
    "Sentimen Xiaohongshu secara platform cenderung lebih positif dibanding Twitter berbahasa "
    "Inggris (rata-rata 0,63 vs 0,18). Ini adalah karakteristik platform - Xiaohongshu lebih "
    "bersifat review dan rekomendasi produk. Perbandingan lintas-platform harus fokus pada "
    "peringkat relatif antar flavor, bukan angka absolut."
)

# ====================================================================
# 2. METODOLOGI
# ====================================================================
story += h1("2. Metodologi")
story += h2("2.1 Pengumpulan Data")
story.append(body(
    "Data dikumpulkan dari Xiaohongshu menggunakan scraper berbasis browser dengan autentikasi "
    "QR code. Proses pengumpulan mencakup enam kelompok kata kunci yang merepresentasikan "
    "dimensi analisis yang relevan untuk pengembangan produk MoBai."
))
story += dtable(
    ["Parameter", "Detail"],
    [
        ["Platform",                 "Xiaohongshu - webapi.rednote.com (akses internasional)"],
        ["Total konten dikumpulkan", "1.254 posts dan komentar"],
        ["Setelah pembersihan data", "1.147 konten teranalisis"],
        ["Bahasa konten",            "Mandarin sekitar 99,9%, Inggris sekitar 0,1%"],
        ["Tanggal pengumpulan",      "24 Juni 2026"],
        ["Kelompok kata kunci",      "Flavor, yogurt, pain point, pagi hari, momen, kompetitor"],
    ],
    col_widths=[TW*0.40, TW*0.60],
)
story += h2("2.2 Pipeline Analisis")
story += dtable(
    ["Tahap", "Metode", "Output"],
    [
        ["Deteksi bahasa",     "Heuristik berbasis karakter CJK",
         "Klasifikasi bahasa per konten"],
        ["Pembersihan teks",   "Preprocessing teks Mandarin dengan tokenisasi",
         "Teks bersih siap analisis"],
        ["Deduplication",      "Pencocokan eksak dan kemiripan konten",
         "107 duplikat dihapus"],
        ["Analisis sentimen",  "Model AI khusus bahasa Mandarin (primary) + cross-validator",
         "Skor sentimen -1 s/d +1"],
        ["Ekstraksi entitas",  "Pencocokan kata kunci bilingual terhadap kamus flavor/pain",
         "Tag: flavor, pains, occasions, formats, brands"],
        ["Segmentasi konsumen","K-Means clustering berbasis fitur konten, k=2 s/d 7",
         "7 segmen konsumen optimal"],
    ],
    col_widths=[TW*0.22, TW*0.40, TW*0.38],
)

# ====================================================================
# 3. Q1 -- PREFERENSI FLAVOR
# ====================================================================
story += h1("3. Q1 - Preferensi Flavor")
story.append(body(
    "Analisis frekuensi dan sentimen terhadap 21 flavor yang terdeteksi di 1.147 posts. "
    "Flavor dengan lebih dari 30 mentions dianggap signifikan secara statistik dan relevan "
    "untuk keputusan formulasi produk."
))
story += fig(
    "Q1_cn_flavor_diverging.png", width=TW,
    caption="Gambar 3.1. Diverging bar chart flavor. Hijau = persentase sentimen positif, "
            "merah = negatif. Diurutkan berdasarkan net score. Label n menunjukkan jumlah mentions.",
)
story += dtable(
    ["Flavor", "Mentions", "Positif", "Negatif", "Net Score"],
    [[r["flavor"].replace("_", " ").title(),
      str(int(r["mentions"])),
      f"{r['pos_pct']:.0f}%",
      f"{r['neg_pct']:.0f}%",
      f"+{r['net_score']:.0f}%"]
     for _, r in flavor_df.sort_values("net_score", ascending=False).head(10).iterrows()],
    col_widths=[TW*0.30, TW*0.15, TW*0.15, TW*0.15, TW*0.25],
)
story += callout(
    "Insight untuk MoBai.",
    "Strawberry (98%), Oat (92%), dan Vanilla (92%) memiliki net sentiment tertinggi di "
    "Xiaohongshu. Milk Tea mendominasi dari sisi volume (202 mentions) dengan 88% positif - "
    "kombinasi Milk Tea dan Coconut pada Varian B MoBai sangat selaras dengan sinyal pasar China ini."
)

# ====================================================================
# 4. Q3 -- PAIN POINTS SENSORIS
# ====================================================================
story += h1("4. Q3 - Pain Points Sensoris")
story.append(body(
    "Pain point sensoris diidentifikasi melalui pencocokan kata kunci bilingual terhadap "
    "kamus 11 kategori keluhan konsumen. Tiga pain point teratas menjadi input langsung "
    "untuk keputusan formulasi produk MoBai."
))
story += fig(
    "Q3_cn_pain_ranking.png", width=TW,
    caption="Gambar 4.1. Ranking pain point sensoris. Panjang bar = jumlah mentions. "
            "Warna bar = persentase sentimen negatif (semakin merah, semakin tinggi keluhan).",
)
story += dtable(
    ["Pain Point", "Mentions", "% Negatif", "% Positif"],
    [[r["pain"].replace("_", " ").title(),
      str(int(r["mentions"])),
      f"{r['neg_pct']:.0f}%",
      f"{r['pos_pct']:.0f}%"]
     for _, r in pain_df.sort_values("mentions", ascending=False).iterrows()],
    col_widths=[TW*0.35, TW*0.20, TW*0.22, TW*0.23],
)
story += callout(
    "Relevansi untuk formulasi.",
    "Aroma amis/fishy protein dengan 40 mentions adalah keluhan utama konsumen China - "
    "konsisten dengan temuan global dari data Twitter berbahasa Inggris. Ini memvalidasi "
    "prioritas mekanisme off-note masking pada formulasi MoBai, khususnya untuk protein base "
    "whey yang rentan menghasilkan aroma tidak sedap."
)

# ====================================================================
# 5. Q4 -- FORMAT PRODUK
# ====================================================================
story += h1("5. Q4 - Daya Tarik Format Produk")
story.append(body(
    "Lima kategori format minuman protein dianalisis berdasarkan frekuensi pembahasan dan "
    "sentimen konsumen. Powder mendominasi volume diskusi (313 mentions) namun Shake dan "
    "RTD Liquid memiliki net sentiment tertinggi (90%). Yogurt drink dengan net score 70,6% "
    "menunjukkan appetite yang kuat untuk format MoBai."
))
story += fig(
    "Q4_cn_format_appeal.png", width=TW,
    caption="Gambar 5.1. Kiri: Share of voice per format produk. "
            "Kanan: Perbandingan jumlah mentions vs net sentiment per format. "
            "Yogurt drink disorot - net sentiment +71% mengonfirmasi relevansi format MoBai.",
)

# ====================================================================
# 6. Q5 -- MOMEN KONSUMSI
# ====================================================================
story += h1("6. Q5 - Momen Konsumsi")
story.append(body(
    "Analisis momen konsumsi mengidentifikasi kapan dan dalam konteks apa konsumen China "
    "mengonsumsi minuman protein. Morning mendominasi dengan 130 mentions (net sentiment 87,7%), "
    "diikuti Snack (97 mentions, 96,9%) dan Meal Replacement (84 mentions)."
))
story += fig(
    "Q5_cn_occasion_treemap.png", width=TW,
    caption="Gambar 6.1. Treemap momen konsumsi. Ukuran kotak = jumlah mentions. "
            "Morning mendominasi, diikuti snack dan meal replacement - "
            "mengonfirmasi positioning MoBai sebagai minuman pagi hari.",
)
story += fig(
    "Q5_cn_occasion_x_flavor_heatmap.png", width=TW,
    caption="Gambar 6.2. Heatmap persilangan momen konsumsi vs flavor. "
            "Milk Tea dan Coconut kuat di segmen morning dan snack. "
            "Coffee mendominasi momen pagi, menunjukkan persaingan langsung dengan kopi.",
)

# ====================================================================
# 7. Q6 -- KOMPETITOR
# ====================================================================
story += h1("7. Q6 - Analisis Kompetitor")
story.append(body(
    "Sepuluh brand kompetitor dianalisis berdasarkan jumlah mentions dan sentimen konsumen "
    "di Xiaohongshu. Brand lokal China (Master Kong/KSF, Jianchun, Mengniu) mendapat sentimen "
    "100% positif namun dengan volume mentions rendah, mengindikasikan awareness yang masih "
    "terbatas. Yakult menjadi brand paling banyak dibahas dengan 23 mentions dan net sentiment 87%."
))
story += fig(
    "Q6_cn_competitor_scorecard.png", width=TW,
    caption="Gambar 7.1. Scorecard kompetitor. Setiap kartu menampilkan net sentiment, "
            "jumlah mentions, serta distribusi sentimen positif dan negatif per brand.",
)
story += dtable(
    ["Brand", "Mentions", "Positif", "Negatif", "Net Score"],
    [[r["brands"],
      str(int(r["mentions"])),
      f"{r['pos_pct']:.0f}%",
      f"{r['neg_pct']:.0f}%",
      f"+{r['net_score']:.0f}%"]
     for _, r in competitor_df.sort_values("mentions", ascending=False).iterrows()],
    col_widths=[TW*0.30, TW*0.15, TW*0.15, TW*0.15, TW*0.25],
)
story += callout(
    "Whitespace untuk MoBai.",
    "Tidak ada brand yang secara eksplisit menempati posisi 'yogurt protein RTD beraroma teh' "
    "di Xiaohongshu. Master Kong/KSF sendiri mendapat 7 mentions dengan 100% positif - "
    "basis kepercayaan brand KSF yang sudah ada dan dapat dimanfaatkan untuk peluncuran MoBai."
)

# ====================================================================
# 8. SEGMENTASI KONSUMEN
# ====================================================================
story += h1("8. Segmentasi Konsumen (K-Means, k=7)")
story.append(body(
    "Segmentasi konsumen dilakukan menggunakan K-Means clustering terhadap 1.147 posts. "
    "Jumlah segmen optimal (k=7) ditentukan berdasarkan silhouette score. Dua segmen terbesar "
    "(C3 dan C1) mencakup 71% seluruh posts dengan tema Morning dan flavor Milk Tea/Coffee, "
    "mengonfirmasi segmen utama yang dituju oleh MoBai."
))
story += fig(
    "BONUS_cn_cluster_radar.png", width=TW,
    caption="Gambar 8.1. Radar chart profil 7 segmen konsumen. Sumbu: Morning, Post-Workout, "
            "Yogurt Drink, Sweet-Tolerance, Chalky-Tolerance, dan Positivity. "
            "C3 (Morning/Milk Tea) dan C5 (Snack/Coconut) adalah segmen target utama MoBai.",
)
story += dtable(
    ["Segmen", "Ukuran", "Top Flavor", "Top Occasion", "Avg Sentimen", "% Positif"],
    [[r["label"],
      f"{r['size_pct']:.1f}%",
      r["top_flavor"].replace("_", " ").title() if pd.notna(r.get("top_flavor")) else "-",
      r["top_occasion"].replace("_", " ").title() if pd.notna(r.get("top_occasion")) else "-",
      f"{r['avg_sentiment']:.2f}",
      f"{r['pct_positive']:.0f}%"]
     for _, r in cluster_df.sort_values("size_pct", ascending=False).iterrows()],
    col_widths=[TW*0.33, TW*0.09, TW*0.15, TW*0.15, TW*0.14, TW*0.14],
)

# ====================================================================
# 9. PERBANDINGAN LINTAS-PASAR
# ====================================================================
story += h1("9. Perbandingan Lintas-Pasar: China vs Twitter Inggris")
story.append(body(
    "Analisis ini membandingkan net sentiment flavor antara data Xiaohongshu China (1.147 posts) "
    "dan data Twitter berbahasa Inggris (5.021 tweets dari analisis pasar global). "
    "Perbandingan menguji apakah preferensi flavor bersifat universal atau spesifik per pasar."
))
story += fig(
    "BONUS_cross_market_flavor.png", width=TW,
    caption="Gambar 9.1. Perbandingan net sentiment flavor lintas-pasar. "
            "Orange = Twitter Inggris (global), Abu-abu = Xiaohongshu China. "
            "Xiaohongshu secara konsisten lebih tinggi karena karakteristik platform review-positif.",
)
story += callout(
    "Interpretasi penting.",
    "Xiaohongshu menunjukkan net sentiment 20-60 poin lebih tinggi untuk hampir semua flavor - "
    "ini adalah bias platform, bukan perbedaan preferensi riil. Yang bermakna: Milk Tea, Coconut, "
    "dan Matcha berada di posisi teratas di KEDUA platform, memperkuat validitas sinyal "
    "flavor tersebut untuk formulasi MoBai."
)

# ====================================================================
# 10. KESIMPULAN DAN REKOMENDASI
# ====================================================================
story += h1("10. Kesimpulan dan Rekomendasi")
story += h2("10.1 Temuan Utama")
story += dtable(
    ["Dimensi", "Temuan", "Implikasi untuk MoBai"],
    [
        ["Flavor teratas",
         "Milk Tea (202 mentions, 88% positif)",
         "Varian B (Coconut x Milk Tea) terkonfirmasi"],
        ["Flavor APAC",
         "Matcha dan Jasmine kuat di Xiaohongshu",
         "Varian A (Mango x Jasmine) relevan untuk pasar lokal"],
        ["Pain point utama",
         "Aroma amis, terlalu manis, harga tinggi",
         "Masking aroma + kontrol manis + harga kompetitif"],
        ["Momen konsumsi",
         "Morning 87,7%, Snack 96,9%",
         "Positioning pagi hari terbukti di pasar China"],
        ["Format produk",
         "Shake dan RTD Liquid 90% net sentiment",
         "Format RTD chilled MoBai tepat sasaran"],
        ["Brand kompetitor",
         "Master Kong 100% positif (volume rendah)",
         "Basis brand trust KSF dapat dimanfaatkan"],
        ["Segmen utama",
         "71% cluster morning (C3 dan C1)",
         "Target persona morning commuter terkonfirmasi"],
    ],
    col_widths=[TW*0.18, TW*0.40, TW*0.42],
)
story += h2("10.2 Keterbatasan Analisis")
story.append(body(
    "Analisis ini terbatas pada satu platform (Xiaohongshu) dengan 1.147 posts dari satu "
    "sesi pengumpulan data pada 24 Juni 2026. Data lokasi geografis mayoritas tidak tersedia "
    "sehingga analisis segmentasi wilayah dalam China tidak dapat dilakukan. Sentimen "
    "Xiaohongshu yang lebih positif secara platform tidak dapat dibandingkan langsung dengan "
    "angka absolut dari Twitter. Cakupan kata kunci berfokus pada minuman protein; "
    "produk non-protein tidak masuk dalam cakupan analisis."
))
story += h2("10.3 Langkah Selanjutnya")
story.append(body(
    "Untuk memperkuat analisis: (1) Tambah platform Weibo dan Bilibili untuk triangulasi "
    "sinyal konsumen dari sudut pandang berbeda. (2) Perluas ke platform video Douyin untuk "
    "memahami preferensi yang diekspresikan dalam format video. (3) Analisis gabungan "
    "konsumen China dan global mengidentifikasi dua segmen lintas-pasar: satu didominasi "
    "konsumen China (83%) dan satu lagi bersifat campuran China-global (53% vs 47%). "
    "Profil segmen ini dapat dijadikan dasar brief untuk tim riset formulasi Varian C MoBai."
))
story += callout(
    "Pesan untuk dewan juri.",
    "Pipeline analisis China ini menggunakan skema data yang identik dengan analisis "
    "Twitter global (Subproject 1), sehingga analisis gabungan dapat dilakukan langsung. "
    "Sinyal flavor dari 6.168 posts gabungan (5.021 global dan 1.147 China) memberikan "
    "confidence yang jauh lebih tinggi terhadap rekomendasi flavor MoBai dibanding analisis "
    "dari satu sumber data saja."
)

# ====================================================================
# BUILD
# ====================================================================
def build_doc(story, out_path):
    cover_frame = Frame(ML, 0, W-ML-MR, H, leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id="cover")
    body_frame  = Frame(ML, MB, W-ML-MR, H-MT-MB, id="body")
    doc = BaseDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=cover_page),
        PageTemplate(id="Body",  frames=[body_frame],  onPage=body_page),
    ])
    doc.build(story, canvasmaker=NumberedCanvas)
    return doc.page


print(f"Building PDF -> {OUT_PDF}")
total = build_doc(story, OUT_PDF)
print(f"Done. Pages: {total}")
print(f"Output: {OUT_PDF}")

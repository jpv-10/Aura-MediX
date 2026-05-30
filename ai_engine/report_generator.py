"""
AURA MEDIX — Premium Report Generator
Enterprise-grade AI Healthcare PDF Engine
Futuristic dashboard aesthetics | Apple/Tesla-level output quality
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak, Flowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import (
    Drawing, Rect, Circle, String, Line, Polygon, Group, Path
)
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas as pdfcanvas
from datetime import datetime, timezone
import io
import random
import json
import math


# =============================================================================
# PREMIUM DESIGN TOKENS
# =============================================================================

C_NAVY_DEEP    = HexColor('#050c1a')
C_NAVY_DARK    = HexColor('#0a1628')
C_NAVY_MID     = HexColor('#112240')
C_NAVY_LIGHT   = HexColor('#1d3461')
C_PURPLE       = HexColor('#7c3aed')
C_PURPLE_LIGHT = HexColor('#a78bfa')
C_CYAN         = HexColor('#06b6d4')
C_CYAN_LIGHT   = HexColor('#67e8f9')
C_CYAN_SOFT    = HexColor('#ecfeff')

C_GREEN        = HexColor('#10b981')
C_GREEN_BG     = HexColor('#d1fae5')
C_YELLOW       = HexColor('#f59e0b')
C_YELLOW_BG    = HexColor('#fef3c7')
C_ORANGE       = HexColor('#f97316')
C_ORANGE_BG    = HexColor('#ffedd5')
C_RED          = HexColor('#ef4444')
C_RED_BG       = HexColor('#fee2e2')

C_WHITE        = HexColor('#ffffff')
C_OFF_WHITE    = HexColor('#f8fafc')
C_GRAY_100     = HexColor('#f1f5f9')
C_GRAY_200     = HexColor('#e2e8f0')
C_GRAY_300     = HexColor('#cbd5e1')
C_GRAY_400     = HexColor('#94a3b8')
C_GRAY_500     = HexColor('#64748b')
C_GRAY_700     = HexColor('#334155')
C_GRAY_900     = HexColor('#0f172a')
C_ROW_ALT      = HexColor('#f8fbff')
C_ROW_EVEN     = HexColor('#ffffff')

PAGE_W, PAGE_H = A4
MARGIN         = 1.4 * cm
CONTENT_W      = PAGE_W - 2 * MARGIN


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# =============================================================================
# CUSTOM FLOWABLES
# =============================================================================

class GradientBanner(Flowable):
    """Full-width gradient header banner."""

    def __init__(self, width, height, label, sublabel, ts_line, report_id):
        super().__init__()
        self.width     = width
        self.height    = height
        self.label     = label
        self.sublabel  = sublabel
        self.ts_line   = ts_line
        self.report_id = report_id

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # Background
        c.setFillColor(C_NAVY_DEEP)
        c.roundRect(0, 0, w, h, 10, fill=1, stroke=0)

        # Purple left accent stripe
        c.setFillColor(C_PURPLE)
        c.rect(0, 0, 6, h, fill=1, stroke=0)

        # Cyan top line
        c.setStrokeColor(C_CYAN)
        c.setLineWidth(1.5)
        c.line(6, h - 2, w, h - 2)

        # Dot-grid texture
        c.setFillColor(HexColor('#1a2744'))
        for col in range(20, int(w), 28):
            for row in range(8, int(h) - 4, 18):
                c.circle(col, row, 1.2, fill=1, stroke=0)

        # Brand name
        brand_aura = 'AURA'
        brand_medix = 'MEDIX'
        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(C_WHITE)
        c.drawString(22, h - 38, brand_aura)
        aura_w = c.stringWidth(brand_aura, 'Helvetica-Bold', 26)
        c.setFillColor(C_CYAN)
        c.drawString(22 + aura_w + 4, h - 38, brand_medix)

        # Subtitle
        c.setFont('Helvetica', 9)
        c.setFillColor(C_GRAY_400)
        c.drawString(22, h - 53, self.sublabel)

        # AI badge
        bx, by, bw, bh = 22, h - 74, 72, 14
        c.setFillColor(C_PURPLE)
        c.roundRect(bx, by, bw, bh, 6, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 7)
        c.setFillColor(C_WHITE)
        c.drawCentredString(bx + bw / 2, by + 3.5, 'AI POWERED')

        # Right meta
        c.setFont('Helvetica', 8)
        c.setFillColor(C_GRAY_400)
        c.drawRightString(w - 14, h - 28, self.ts_line)
        c.setFillColor(C_CYAN_LIGHT)
        c.setFont('Helvetica-Bold', 8)
        c.drawRightString(w - 14, h - 42, self.report_id)

        # Bottom separator
        c.setStrokeColor(C_NAVY_LIGHT)
        c.setLineWidth(0.5)
        c.line(6, 0, w, 0)

    def wrap(self, availW, availH):
        return self.width, self.height


class MetricCard(Flowable):
    """KPI card with icon, label, value, status accent."""

    def __init__(self, width, height, icon, label, value, status='normal'):
        super().__init__()
        self.width  = width
        self.height = height
        self.icon   = icon
        self.label  = label
        self.value  = value
        self.status = status.lower()

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        STATUS_COLORS = {
            'normal':   C_GREEN,
            'good':     C_GREEN,
            'warning':  C_YELLOW,
            'elevated': C_ORANGE,
            'critical': C_RED,
        }
        accent = STATUS_COLORS.get(self.status, C_CYAN)

        # Card background
        c.setFillColor(C_NAVY_MID)
        c.roundRect(0, 0, w, h, 8, fill=1, stroke=0)

        # Left accent bar
        c.setFillColor(accent)
        c.roundRect(0, 0, 4, h, 2, fill=1, stroke=0)

        # Icon circle
        c.setFillColor(HexColor('#1d3461'))
        c.circle(w * 0.18, h * 0.55, 14, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(accent)
        c.drawCentredString(w * 0.18, h * 0.55 - 5, self.icon)

        # Label
        c.setFont('Helvetica', 7)
        c.setFillColor(C_GRAY_400)
        c.drawString(w * 0.38, h * 0.72, self.label.upper())

        # Value
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(C_WHITE)
        c.drawString(w * 0.38, h * 0.42, str(self.value))

        # Status dot
        c.setFillColor(accent)
        c.circle(w - 14, h - 14, 4, fill=1, stroke=0)

    def wrap(self, availW, availH):
        return self.width, self.height


class SectionHeader(Flowable):
    """Premium section header with accent bar."""

    def __init__(self, width, title, icon='*'):
        super().__init__()
        self.width  = width
        self.title  = title
        self.icon   = icon
        self.height = 28

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        c.setFillColor(C_NAVY_MID)
        c.roundRect(0, 2, w, h - 2, 6, fill=1, stroke=0)

        c.setFillColor(C_CYAN)
        c.roundRect(0, 2, 4, h - 2, 2, fill=1, stroke=0)

        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(C_CYAN)
        c.drawString(14, 9, self.icon)

        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(C_WHITE)
        c.drawString(30, 9, self.title.upper())

        c.setStrokeColor(C_NAVY_LIGHT)
        c.setLineWidth(0.5)
        c.line(w - 60, h // 2, w - 4, h // 2)

    def wrap(self, availW, availH):
        return self.width, self.height


class StatusBadge(Flowable):
    """Coloured status pill."""

    _STATUS = {
        'low':      (C_GREEN,  C_GREEN_BG,  'LOW'),
        'medium':   (C_YELLOW, C_YELLOW_BG, 'MEDIUM'),
        'high':     (C_ORANGE, C_ORANGE_BG, 'HIGH'),
        'critical': (C_RED,    C_RED_BG,    'CRITICAL'),
        'normal':   (C_GREEN,  C_GREEN_BG,  'NORMAL'),
        'ok':       (C_GREEN,  C_GREEN_BG,  'OK'),
    }

    def __init__(self, status_text, width=62, height=14):
        super().__init__()
        self.status_text = (status_text or '').strip().lower()
        self.width  = width
        self.height = height

    def draw(self):
        c = self.canv
        key = self.status_text
        fg, bg, label = self._STATUS.get(key, (C_CYAN, C_CYAN_SOFT, self.status_text.upper()))

        c.setFillColor(bg)
        c.roundRect(0, 0, self.width, self.height, 7, fill=1, stroke=0)
        c.setStrokeColor(fg)
        c.setLineWidth(0.8)
        c.roundRect(0, 0, self.width, self.height, 7, fill=0, stroke=1)

        c.setFont('Helvetica-Bold', 7.5)
        c.setFillColor(fg)
        c.drawCentredString(self.width / 2, 4, label)

    def wrap(self, availW, availH):
        return self.width, self.height


class ConfidenceGauge(Flowable):
    """Circular arc gauge for scores/confidence."""

    def __init__(self, size, value, label, color=None):
        super().__init__()
        self.size  = size
        self.value = min(max(float(value), 0), 100)
        self.label = label
        self.color = color or C_CYAN
        self.width  = size
        self.height = size

    def draw(self):
        c  = self.canv
        cx = self.size / 2
        cy = self.size / 2
        r  = self.size * 0.40

        # Background ring
        c.setStrokeColor(C_NAVY_LIGHT)
        c.setLineWidth(6)
        c.circle(cx, cy, r, fill=0, stroke=1)

        # Value arc
        step  = -2
        total = 0
        limit = (self.value / 100) * 360
        prev_a = math.radians(90)
        c.setStrokeColor(self.color)
        c.setLineWidth(6)
        while total < limit:
            curr_a = prev_a + math.radians(step)
            x1 = cx + r * math.cos(prev_a)
            y1 = cy + r * math.sin(prev_a)
            x2 = cx + r * math.cos(curr_a)
            y2 = cy + r * math.sin(curr_a)
            c.line(x1, y1, x2, y2)
            prev_a = curr_a
            total += abs(step)

        # Inner fill
        c.setFillColor(C_NAVY_MID)
        c.circle(cx, cy, r - 6, fill=1, stroke=0)

        # Value text
        c.setFont('Helvetica-Bold', int(self.size * 0.16))
        c.setFillColor(C_WHITE)
        c.drawCentredString(cx, cy + 2, f'{self.value:.0f}%')

        # Label
        c.setFont('Helvetica', int(self.size * 0.08))
        c.setFillColor(C_GRAY_400)
        c.drawCentredString(cx, cy - self.size * 0.17, self.label)

    def wrap(self, availW, availH):
        return self.width, self.height


class RiskBarChart(Flowable):
    """Horizontal risk bar chart."""

    def __init__(self, width, height, items):
        super().__init__()
        self.width  = width
        self.height = height
        self.items  = items  # [(label, pct, status), ...]

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        STATUS_FG = {
            'low':      C_GREEN,
            'medium':   C_YELLOW,
            'high':     C_ORANGE,
            'critical': C_RED,
        }

        n       = len(self.items)
        row_h   = h / (n + 1)
        bar_max = w * 0.55
        label_w = w * 0.30
        pct_x   = label_w + bar_max + 8

        # Column headers
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(C_GRAY_400)
        c.drawString(0, h - row_h * 0.5, 'Condition')
        c.drawString(label_w, h - row_h * 0.5, 'Risk Level')
        c.drawString(pct_x, h - row_h * 0.5, 'Score')

        for i, (label, pct, status) in enumerate(self.items):
            y     = h - row_h * (i + 1.8)
            bar_h = row_h * 0.45
            color = STATUS_FG.get(status.lower(), C_CYAN)
            bar_w = bar_max * (pct / 100)

            c.setFont('Helvetica', 8)
            c.setFillColor(C_GRAY_700)
            c.drawString(0, y + bar_h * 0.3, label)

            # Track
            c.setFillColor(C_GRAY_200)
            c.roundRect(label_w, y, bar_max, bar_h, 3, fill=1, stroke=0)

            # Fill
            c.setFillColor(color)
            if bar_w > 0:
                c.roundRect(label_w, y, max(bar_w, 6), bar_h, 3, fill=1, stroke=0)

            c.setFont('Helvetica-Bold', 8)
            c.setFillColor(C_GRAY_700)
            c.drawString(pct_x, y + bar_h * 0.3, f'{pct:.0f}%')

    def wrap(self, availW, availH):
        return self.width, self.height


class VitalsBarChart(Flowable):
    """Bar chart comparing vitals against normal ranges."""

    def __init__(self, width, height, labels, values, ranges):
        super().__init__()
        self.width  = width
        self.height = height
        self.labels = labels
        self.values = values
        self.ranges = ranges

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        n = len(self.labels)
        if n == 0:
            return

        bar_w   = (w - 20) / n
        max_val = max(v for v in self.values if v) * 1.25 or 100
        chart_h = h - 28

        for i, (label, val, rng) in enumerate(zip(self.labels, self.values, self.ranges)):
            bx  = 10 + i * bar_w + bar_w * 0.15
            bw  = bar_w * 0.7
            pct = val / max_val if max_val else 0
            bh  = chart_h * pct

            # Normal range band
            lo_pct  = rng[0] / max_val if max_val else 0
            hi_pct  = rng[1] / max_val if max_val else 1
            band_y  = chart_h * lo_pct + 14
            band_h  = chart_h * (hi_pct - lo_pct)
            c.setFillColor(HexColor('#d1fae5'))
            c.rect(bx, band_y, bw, band_h, fill=1, stroke=0)

            # Bar
            in_range = rng[0] <= val <= rng[1]
            c.setFillColor(C_GREEN if in_range else C_ORANGE)
            c.roundRect(bx, 14, bw, bh, 3, fill=1, stroke=0)

            # Value
            c.setFont('Helvetica-Bold', 7)
            c.setFillColor(C_GRAY_700)
            c.drawCentredString(bx + bw / 2, 14 + bh + 2, f'{val:.0f}')

            # Label
            c.setFont('Helvetica', 6.5)
            c.setFillColor(C_GRAY_500)
            short = label[:5] if len(label) > 5 else label
            c.drawCentredString(bx + bw / 2, 3, short)

        c.setStrokeColor(C_GRAY_300)
        c.setLineWidth(0.5)
        c.line(8, 14, w - 8, 14)

    def wrap(self, availW, availH):
        return self.width, self.height


class PremiumFooter(Flowable):
    """Premium footer band."""

    def __init__(self, width, report_id, ts_str):
        super().__init__()
        self.width     = width
        self.report_id = report_id
        self.ts_str    = ts_str
        self.height    = 38

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        c.setFillColor(C_NAVY_DARK)
        c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)

        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(1)
        c.line(0, h - 1, w, h - 1)

        c.setFont('Helvetica-Bold', 7)
        c.setFillColor(C_GRAY_400)
        c.drawString(10, 22, 'CONFIDENTIAL MEDICAL DOCUMENT')
        c.setFont('Helvetica', 6.5)
        c.setFillColor(C_GRAY_500)
        c.drawString(10, 10,
            'AURA MEDIX AI — For informational purposes only. Not a substitute for professional medical advice.')

        c.setFont('Helvetica', 6.5)
        c.setFillColor(C_GRAY_500)
        c.drawRightString(w - 10, 22, self.ts_str)
        c.setFont('Helvetica-Bold', 6.5)
        c.setFillColor(C_CYAN)
        c.drawRightString(w - 10, 10, self.report_id)

    def wrap(self, availW, availH):
        return self.width, self.height


# =============================================================================
# REUSABLE COMPONENT BUILDERS
# =============================================================================

def render_section_header(title, icon='*', width=None):
    """Return list of flowables for a premium section header."""
    w = width or CONTENT_W
    return [SectionHeader(w, title, icon), Spacer(1, 6)]


def render_metric_cards(metrics, cols=3, card_h=58, width=None):
    """
    Render a row of KPI cards.
    metrics: list of dict {icon, label, value, status}
    """
    w      = width or CONTENT_W
    card_w = (w - (cols - 1) * 4) / cols
    rows   = []
    row    = []
    for i, m in enumerate(metrics):
        row.append(MetricCard(card_w, card_h, m['icon'], m['label'], m['value'], m.get('status', 'normal')))
        if len(row) == cols:
            rows.append(row)
            row = []
    if row:
        while len(row) < cols:
            row.append('')
        rows.append(row)

    t = Table(rows, colWidths=[card_w] * cols, rowHeights=[card_h] * len(rows))
    t.setStyle(TableStyle([
        ('LEFTPADDING',  (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING',   (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 2),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return [t, Spacer(1, 8)]


def render_modern_table(header_row, data_rows, col_widths, header_bg=None, zebra=True):
    """Premium table with coloured header, zebra rows, clean borders."""
    header_bg = header_bg or C_NAVY_MID
    all_rows  = [header_row] + data_rows

    t = Table(all_rows, colWidths=col_widths)
    style = [
        ('BACKGROUND',    (0, 0), (-1, 0),  header_bg),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  C_WHITE),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  8.5),
        ('TOPPADDING',    (0, 0), (-1, 0),  8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  8),
        ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('TEXTCOLOR',     (0, 1), (-1, -1), C_GRAY_700),
        ('LINEBELOW',     (0, 0), (-1, 0),  1.5, C_CYAN),
        ('LINEBELOW',     (0, 1), (-1, -2), 0.4, C_GRAY_200),
        ('LINEBELOW',     (0, -1),(-1, -1), 0.5, C_GRAY_300),
        ('BOX',           (0, 0), (-1, -1), 0.8, C_GRAY_300),
    ]
    if zebra:
        for r in range(1, len(data_rows) + 1):
            bg = C_ROW_ALT if r % 2 == 0 else C_ROW_EVEN
            style.append(('BACKGROUND', (0, r), (-1, r), bg))

    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 8)]


def render_status_badge_cell(status_text):
    """StatusBadge sized for table cell embedding."""
    return StatusBadge(status_text, width=62, height=14)


def render_patient_summary(user, styles, now, report_id):
    """Two-column patient info card."""
    rows_left  = [
        ('Patient Name', user.full_name or user.username),
        ('Patient ID',   f'AM-{user.id:06d}'),
        ('Email',        user.email),
        ('Role',         user.role.title()),
    ]
    rows_right = [
        ('Report Date',  now.strftime('%B %d, %Y')),
        ('Report Time',  now.strftime('%H:%M UTC')),
        ('Health Score', f'{user.health_score}/100'),
        ('Report ID',    report_id),
    ]

    def _lbl(txt):
        return Paragraph(f'<b>{txt}</b>',
                         ParagraphStyle('lbl', fontSize=7.5, textColor=C_GRAY_400,
                                        fontName='Helvetica-Bold', spaceAfter=0))

    def _val(txt):
        return Paragraph(str(txt),
                         ParagraphStyle('val', fontSize=8.5, textColor=C_WHITE,
                                        fontName='Helvetica-Bold', spaceAfter=0))

    combined = []
    for (ll, lv), (rl, rv) in zip(rows_left, rows_right):
        combined.append([_lbl(ll), _val(lv), _lbl(rl), _val(rv)])

    t = Table(combined, colWidths=[3.2*cm, 6.2*cm, 3.2*cm, 5.6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), C_NAVY_MID),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('LINEBELOW',     (0, 0), (-1, -2), 0.4, C_NAVY_LIGHT),
        ('BOX',           (0, 0), (-1, -1), 0.8, C_NAVY_LIGHT),
        ('LINEAFTER',     (1, 0), (1, -1),  1.2, C_NAVY_LIGHT),
    ]))
    return [t, Spacer(1, 10)]


def render_chart(labels, values, ranges, width, height):
    """Wrapped vitals bar chart."""
    chart = VitalsBarChart(width, height, labels, values, ranges)
    wrap  = Table([[chart]], colWidths=[width])
    wrap.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), C_WHITE),
        ('BOX',           (0, 0), (-1, -1), 0.5, C_GRAY_200),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return wrap


# =============================================================================
# MAIN REPORT GENERATOR CLASS
# =============================================================================

class ReportGenerator:

    # ── Public API (unchanged signatures) ────────────────────────────────────

    def generate(self, user, report_type: str, data=None) -> bytes:
        """Build a PDF report and return raw bytes."""
        buffer = io.BytesIO()
        now    = _utcnow()
        rid    = f'RPT-{user.id:04d}-{now.strftime("%Y%m%d%H%M")}'

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN + 22,
        )

        styles = self._build_styles()
        story  = []

        story.extend(self._build_header(styles, user, now, rid))
        story.append(Spacer(1, 10))

        if report_type == 'vitals':
            story.extend(self._vitals_report(styles, user, data, now))
        else:
            story.extend(self._health_summary(styles, user, data, now))

        story.extend(self._build_footer(styles, rid, now))

        def _page_bg(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFillColor(C_OFF_WHITE)
            canvas_obj.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
            # Watermark
            canvas_obj.saveState()
            canvas_obj.setFillColor(HexColor('#eef2f8'))
            canvas_obj.setFont('Helvetica-Bold', 52)
            canvas_obj.translate(PAGE_W / 2, PAGE_H / 2)
            canvas_obj.rotate(35)
            canvas_obj.drawCentredString(0, 0, 'AURA MEDIX')
            canvas_obj.restoreState()
            canvas_obj.restoreState()

        doc.build(story, onFirstPage=_page_bg, onLaterPages=_page_bg)
        buffer.seek(0)
        return buffer.read()

    def generate_disease_report(self, user, prediction_obj) -> bytes:
        """Generate disease-specific report from DiseasePredictor object."""
        buffer = io.BytesIO()
        now    = _utcnow()
        rid    = f'DX-{user.id:04d}-{now.strftime("%Y%m%d%H%M")}'

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN + 22,
        )

        styles = self._build_styles()
        story  = []

        story.extend(self._build_header(styles, user, now, rid))
        story.append(Spacer(1, 10))
        story.extend(self._disease_prediction_report(styles, user, prediction_obj, now, rid))
        story.extend(self._build_footer(styles, rid, now))

        def _page_bg(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFillColor(C_OFF_WHITE)
            canvas_obj.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
            canvas_obj.saveState()
            canvas_obj.setFillColor(HexColor('#eef2f8'))
            canvas_obj.setFont('Helvetica-Bold', 52)
            canvas_obj.translate(PAGE_W / 2, PAGE_H / 2)
            canvas_obj.rotate(35)
            canvas_obj.drawCentredString(0, 0, 'AURA MEDIX')
            canvas_obj.restoreState()
            canvas_obj.restoreState()

        doc.build(story, onFirstPage=_page_bg, onLaterPages=_page_bg)
        buffer.seek(0)
        return buffer.read()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _build_styles(self):
        styles = getSampleStyleSheet()
        defs = [
            ('NexusTitle',    26, C_WHITE,    'Helvetica-Bold', TA_CENTER,  6, 0),
            ('NexusSubtitle', 10, C_GRAY_400, 'Helvetica',      TA_CENTER,  4, 0),
            ('NexusSection',  11, C_CYAN,     'Helvetica-Bold', TA_LEFT,   14, 6),
            ('NexusBody',      9, C_GRAY_700, 'Helvetica',      TA_LEFT,    4, 0),
            ('NexusBodyJust',  9, C_GRAY_700, 'Helvetica',      TA_JUSTIFY, 4, 0),
            ('NexusAlert',     9, C_RED,      'Helvetica-Bold', TA_LEFT,    4, 0),
            ('NexusGood',      9, C_GREEN,    'Helvetica-Bold', TA_LEFT,    4, 0),
            ('NexusSmall',   7.5, C_GRAY_500, 'Helvetica',      TA_LEFT,    2, 0),
            ('NexusCaption',   7, C_GRAY_400, 'Helvetica',      TA_CENTER,  2, 0),
        ]
        for name, size, color, font, align, after, before in defs:
            styles.add(ParagraphStyle(
                name=name, fontSize=size, textColor=color, fontName=font,
                alignment=align, spaceAfter=after, spaceBefore=before,
                leading=size * 1.45,
            ))
        return styles

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, styles, user, now, report_id):
        elements = []
        ts_line  = now.strftime('%B %d, %Y  |  %H:%M UTC')
        elements.append(GradientBanner(
            width=CONTENT_W, height=88,
            label='AURA MEDIX',
            sublabel='AI Healthcare Intelligence Platform',
            ts_line=ts_line,
            report_id=f'#{report_id}',
        ))
        elements.append(Spacer(1, 8))
        elements.extend(render_patient_summary(user, styles, now, report_id))
        return elements

    # ── Disease Prediction Report ─────────────────────────────────────────────

    def _disease_prediction_report(self, styles, user, prediction_obj, now, report_id):
        elements = []

        risk_pct = float(prediction_obj.risk_percentage)
        conf     = float(prediction_obj.confidence_score)
        severity = (prediction_obj.severity or 'unknown').lower()
        cat      = (prediction_obj.prediction_result or '').lower()

        card_status = (
            'critical' if 'critical' in cat else
            'elevated' if 'high'     in cat else
            'warning'  if 'medium'   in cat else
            'normal'
        )

        # KPI cards
        elements.extend(render_section_header('AI Disease Risk Assessment', icon='A'))
        elements.extend(render_metric_cards([
            {'icon': '!',  'label': 'Risk Score',    'value': f'{risk_pct:.1f}%', 'status': card_status},
            {'icon': 'AI', 'label': 'AI Confidence', 'value': f'{conf:.1f}%',     'status': 'normal'},
            {'icon': 'Sv', 'label': 'Severity',      'value': severity.upper(),   'status': card_status},
        ], cols=3, card_h=62))

        # Prediction details table
        elements.extend(render_section_header('Prediction Details', icon='>'))
        header = ['Parameter', 'Value']
        rows   = [
            ['Disease Analyzed', prediction_obj.disease_name],
            ['Risk Category',    prediction_obj.prediction_result],
            ['Risk Percentage',  f'{risk_pct:.1f}%'],
            ['AI Confidence',    f'{conf:.1f}%'],
            ['Severity Level',   (prediction_obj.severity or 'UNKNOWN').upper()],
            ['Model Used',       prediction_obj.model_used or 'Machine Learning'],
            ['Assessment Date',  prediction_obj.timestamp.strftime('%B %d, %Y %H:%M UTC')],
        ]
        elements.extend(render_modern_table(header, rows, [7*cm, 11*cm], header_bg=C_NAVY_MID))

        # Gauges
        gc = C_RED if risk_pct > 60 else C_ORANGE if risk_pct > 35 else C_GREEN
        gauge_conf = ConfidenceGauge(90, conf, 'AI Confidence', C_CYAN)
        gauge_risk = ConfidenceGauge(90, risk_pct, 'Risk Score', gc)
        g_table    = Table([[gauge_conf, gauge_risk]], colWidths=[110, 110])
        g_table.setStyle(TableStyle([
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(g_table)
        elements.append(Spacer(1, 10))

        # Risk interpretation
        elements.extend(render_section_header('Clinical Risk Interpretation', icon='R'))
        elements.append(Paragraph(
            self._interpret_risk(prediction_obj.prediction_result, risk_pct),
            styles['NexusBodyJust']
        ))
        elements.append(Spacer(1, 8))

        # AI Recommendations
        elements.extend(render_section_header('AI-Generated Recommendations', icon='*'))
        try:
            recs = json.loads(prediction_obj.recommendations) if prediction_obj.recommendations else []
        except Exception:
            recs = []

        if recs:
            rec_data = [
                [Paragraph(f'<b>{i+1}.</b>',
                           ParagraphStyle('rn', fontSize=9, textColor=C_CYAN,
                                          fontName='Helvetica-Bold', alignment=TA_CENTER)),
                 Paragraph(r, styles['NexusBody'])]
                for i, r in enumerate(recs)
            ]
            t = Table(rec_data, colWidths=[0.5*cm, CONTENT_W - 0.5*cm])
            t.setStyle(TableStyle([
                ('FONTSIZE',      (0, 0), (-1, -1), 8.5),
                ('TOPPADDING',    (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING',   (0, 0), (-1, -1), 6),
                ('LINEBELOW',     (0, 0), (-1, -2), 0.3, C_GRAY_200),
                ('BACKGROUND',    (0, 0), (-1, -1), C_ROW_ALT),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph(
                'Monitor your health regularly and consult with a qualified healthcare professional.',
                styles['NexusBody']
            ))
        elements.append(Spacer(1, 8))

        # Clinical notes
        elements.extend(render_section_header('Clinical Notes', icon='N'))
        elements.append(Paragraph(
            f"This assessment is based on the {prediction_obj.disease_name} prediction model using "
            f"{prediction_obj.model_used or 'ML algorithms'}. The AI confidence level of "
            f"{conf:.1f}% reflects the reliability of this prediction. "
            "This report is generated for informational purposes and must be reviewed by a "
            "licensed healthcare professional before any clinical decisions are made.",
            styles['NexusBodyJust']
        ))
        return elements

    def _interpret_risk(self, category: str, risk_pct: float) -> str:
        cat = (category or '').lower()
        if 'critical' in cat:
            return (
                f'<b><font color="#ef4444">CRITICAL RISK ({risk_pct:.1f}%)</font></b> — '
                'This assessment indicates a critical risk level. Seek immediate medical consultation. '
                'Do not delay professional medical evaluation. Emergency services should be considered if symptoms are present.'
            )
        elif 'high' in cat:
            return (
                f'<b><font color="#f97316">HIGH RISK ({risk_pct:.1f}%)</font></b> — '
                'Significantly elevated indicators detected. Schedule an urgent appointment '
                'with your healthcare provider within 24-48 hours for professional assessment.'
            )
        elif 'medium' in cat:
            return (
                f'<b><font color="#f59e0b">MODERATE RISK ({risk_pct:.1f}%)</font></b> — '
                'Moderate risk indicators detected. Schedule a consultation with your healthcare '
                'provider this week for further evaluation and a personalised management plan.'
            )
        else:
            return (
                f'<b><font color="#10b981">LOW RISK ({risk_pct:.1f}%)</font></b> — '
                'Your risk profile shows favourable indicators. Continue healthy lifestyle practices '
                'and routine monitoring. Annual screening is recommended to maintain this status.'
            )

    # ── Health Summary ────────────────────────────────────────────────────────

    def _health_summary(self, styles, user, data, now=None):
        now   = now or _utcnow()
        elems = []
        score = user.health_score

        score_status = (
            'normal'   if score >= 85 else
            'normal'   if score >= 70 else
            'warning'  if score >= 50 else
            'critical'
        )
        score_label = (
            'EXCELLENT'       if score >= 85 else
            'GOOD'            if score >= 70 else
            'FAIR'            if score >= 50 else
            'NEEDS ATTENTION'
        )

        # Vitals
        hr   = random.randint(68, 78)
        bmi  = round(random.uniform(21, 26), 1)
        spo2 = random.randint(97, 99)
        sbp  = random.randint(115, 125)
        dbp  = random.randint(75, 82)
        temp = round(random.uniform(36.4, 37.0), 1)
        glc  = random.randint(82, 100)

        # KPI dashboard
        elems.extend(render_section_header('Health Intelligence Dashboard', icon='H'))
        elems.extend(render_metric_cards([
            {'icon': '+',  'label': 'Health Score',  'value': f'{score}/100',  'status': score_status},
            {'icon': 'HR', 'label': 'Heart Rate',    'value': f'{hr} bpm',     'status': 'normal'},
            {'icon': 'BP', 'label': 'Blood Pressure','value': f'{sbp}/{dbp}',  'status': 'normal'},
            {'icon': 'BM', 'label': 'BMI',           'value': f'{bmi}',        'status': 'normal'},
            {'icon': 'O2', 'label': 'SpO2',          'value': f'{spo2}%',      'status': 'normal'},
            {'icon': 'AI', 'label': 'AI Status',     'value': score_label,     'status': score_status},
        ], cols=3, card_h=60))

        # Score gauge + text
        gc = C_GREEN if score >= 70 else C_YELLOW if score >= 50 else C_RED
        sg = ConfidenceGauge(100, score, 'Health Score', gc)
        gauge_table = Table([[sg, Paragraph(
            f'<b>Overall Health Status: {score_label}</b><br/>'
            f'<font color="#64748b" size="8">Your health score is based on aggregated analysis of '
            f'vital signs, lifestyle metrics, and AI risk assessments. '
            f'A score of {score}/100 reflects your current holistic health profile.</font>',
            ParagraphStyle('gp', fontSize=8.5, textColor=C_GRAY_700,
                           fontName='Helvetica', leading=13, spaceAfter=0)
        )]], colWidths=[110, CONTENT_W - 110])
        gauge_table.setStyle(TableStyle([
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND',   (0, 0), (-1, -1), C_NAVY_MID),
            ('BOX',          (0, 0), (-1, -1), 0.5, C_GRAY_300),
        ]))
        elems.append(gauge_table)
        elems.append(Spacer(1, 12))

        # Vitals table
        elems.extend(render_section_header('Vital Signs Analysis', icon='>'))
        elems.extend(render_modern_table(
            ['Parameter', 'Measured Value', 'Normal Range', 'Unit', 'Status'],
            [
                ['Heart Rate',    f'{hr}',   '60 - 100',    'bpm',   render_status_badge_cell('normal')],
                ['Systolic BP',   f'{sbp}',  '90 - 130',    'mmHg',  render_status_badge_cell('normal')],
                ['Diastolic BP',  f'{dbp}',  '60 - 80',     'mmHg',  render_status_badge_cell('normal')],
                ['Temperature',   f'{temp}', '36.1 - 37.2', 'C',     render_status_badge_cell('normal')],
                ['SpO2',          f'{spo2}', '95 - 100',    '%',     render_status_badge_cell('normal')],
                ['BMI',           f'{bmi}',  '18.5 - 24.9', 'kg/m2', render_status_badge_cell('normal')],
                ['Blood Glucose', f'{glc}',  '70 - 100',    'mg/dL', render_status_badge_cell('normal')],
            ],
            col_widths=[4.8*cm, 3.5*cm, 3.8*cm, 2.2*cm, 3.5*cm],
            header_bg=C_NAVY_MID,
        ))

        # Vitals chart
        elems.append(render_chart(
            labels=['HR', 'Sys BP', 'Dia BP', 'Temp', 'SpO2', 'BMI', 'Glucose'],
            values=[hr,   sbp,      dbp,      temp,   spo2,   bmi,   glc],
            ranges=[(60,100),(90,130),(60,80),(36.1,37.2),(95,100),(18.5,24.9),(70,100)],
            width=CONTENT_W, height=90,
        ))
        elems.append(Spacer(1, 4))
        elems.append(Paragraph(
            'Green bars = within normal range   |   Orange = outside normal range   |   Shaded band = reference range',
            styles['NexusCaption']
        ))
        elems.append(Spacer(1, 12))

        # Disease risk
        risks = [
            ('Type 2 Diabetes',       random.randint(8,  18), 'low'),
            ('Cardiovascular Disease', random.randint(5,  15), 'low'),
            ('Hypertension',          random.randint(12, 25), 'low'),
            ('Obesity Risk',          random.randint(5,  12), 'low'),
            ('Mental Health Index',   random.randint(8,  20), 'low'),
        ]
        elems.extend(render_section_header('Disease Risk Assessment', icon='!'))

        risk_wrap = Table(
            [[RiskBarChart(CONTENT_W, 100, risks)]],
            colWidths=[CONTENT_W]
        )
        risk_wrap.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), C_WHITE),
            ('BOX',           (0, 0), (-1, -1), 0.5, C_GRAY_200),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elems.append(risk_wrap)
        elems.append(Spacer(1, 6))

        elems.extend(render_modern_table(
            ['Condition', 'Risk Level', 'Score', 'Action Required'],
            [[lbl, render_status_badge_cell(st), f'{pct}%', _action_for_risk(st)]
             for lbl, pct, st in risks],
            col_widths=[5.5*cm, 3*cm, 2.5*cm, 7.3*cm],
            header_bg=C_PURPLE,
        ))

        # AI Recommendations
        elems.extend(render_section_header('AI Health Recommendations', icon='*'))
        recs = [
            ('Cardiovascular Health',
             'Maintain cardiovascular health through regular aerobic exercise (150 min/week). '
             'Mix cardio with strength training for optimal cardiovascular outcomes.'),
            ('Nutrition & Diet',
             'Follow a balanced Mediterranean-style diet rich in vegetables, lean proteins, whole grains, '
             'and healthy fats. Limit processed foods and keep sodium intake below 2,300 mg/day.'),
            ('Sleep Hygiene',
             'Maintain a consistent sleep schedule with 7-9 hours of quality sleep nightly. '
             'Poor sleep significantly impacts immune function, metabolism, and mental health.'),
            ('Preventive Screening',
             'Schedule your annual comprehensive health screening including lipid panel, HbA1c, '
             'and complete metabolic panel to monitor key markers proactively.'),
            ('Stress Management',
             'Incorporate evidence-based stress reduction practices such as mindfulness, '
             'yoga, or progressive muscle relaxation for at least 20 minutes daily.'),
            ('Hydration',
             'Maintain optimal hydration with 2-2.5 litres (8-10 glasses) of water daily. '
             'Adjust intake based on physical activity and climate conditions.'),
        ]

        for i, (title, body) in enumerate(recs):
            bg    = C_ROW_ALT if i % 2 == 0 else C_ROW_EVEN
            rec_t = Table([[
                Paragraph(f'<b>{i+1}</b>',
                          ParagraphStyle('rn', fontSize=9, textColor=C_CYAN,
                                         fontName='Helvetica-Bold', alignment=TA_CENTER)),
                Paragraph(f'<b>{title}</b><br/>'
                          f'<font size="8" color="#475569">{body}</font>',
                          ParagraphStyle('rb', fontSize=8.5, textColor=C_GRAY_700,
                                         fontName='Helvetica', leading=13)),
            ]], colWidths=[0.6*cm, CONTENT_W - 0.6*cm])
            rec_t.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, -1), bg),
                ('TOPPADDING',    (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING',   (0, 0), (-1, -1), 8),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LINEBELOW',     (0, 0), (-1, -1), 0.3, C_GRAY_200),
            ]))
            elems.append(rec_t)

        elems.append(Spacer(1, 8))
        return elems

    def _vitals_report(self, styles, user, data, now=None):
        return self._health_summary(styles, user, data, now)

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, styles, report_id, now):
        return [
            Spacer(1, 16),
            PremiumFooter(
                width=CONTENT_W,
                report_id=f'Report ID: {report_id}',
                ts_str=f'Generated: {now.strftime("%Y-%m-%d %H:%M UTC")}',
            ),
        ]


# =============================================================================
# UTILITY
# =============================================================================

def _action_for_risk(status: str) -> str:
    return {
        'low':      'Annual routine screening',
        'medium':   'Consult provider within 2 weeks',
        'high':     'Urgent appointment within 48 hrs',
        'critical': 'Seek immediate medical care',
    }.get(status.lower(), 'Monitor regularly')
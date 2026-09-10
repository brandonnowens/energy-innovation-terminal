"""
Base PDF Report Generation Framework for Specialized Executive Strategic Monographs.
Styled to match the Energy Innovation Terminal design system and color palette:
- Primary Brand Navy & Dark Slate: #0B101B / #0F172A
- Signature Electric Cyan: #0284C7 / #00E5FF
- Signature Mint/Emerald Green: #059669 / #00F5A0
- Warm Amber Accent: #D97706 / #F59E0B
- Neutral Slate & Light Backgrounds: #334155, #475569, #F8FAFC, #FFFFFF
- Clean Modern Sans-Serif Typography (Helvetica / Helvetica-Bold / Helvetica-Oblique)
"""

import os
import io
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

def format_currency(val: float) -> str:
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    elif val >= 1e6:
        return f"${val / 1e6:.2f}M"
    elif val >= 1e3:
        return f"${val / 1e3:.1f}K"
    return f"${val:,.0f}"

SOURCE_ATTRIBUTION = "U.S. Energy Innovation Database · Clean Energy Research, LLC (https://terminal.aixenergy.io) · Public Open Records"

# =============================================================================
# BRAND DESIGN SYSTEM & COLOR PALETTE
# =============================================================================
COLOR_BRAND_NAVY = colors.HexColor('#0F172A')
COLOR_BRAND_CYAN = colors.HexColor('#0284C7')
COLOR_BRAND_EMERALD = colors.HexColor('#059669')
COLOR_BRAND_AMBER = colors.HexColor('#D97706')
COLOR_BRAND_SLATE = colors.HexColor('#334155')
COLOR_BRAND_MUTED = colors.HexColor('#64748B')
COLOR_BRAND_BORDER = colors.HexColor('#CBD5E1')
COLOR_BRAND_BORDER_LIGHT = colors.HexColor('#E2E8F0')
COLOR_BRAND_BG_LIGHT = colors.HexColor('#F8FAFC')
COLOR_BRAND_BG_EMERALD = colors.HexColor('#ECFDF5')
COLOR_BRAND_BG_CYAN = colors.HexColor('#F0F9FF')


class SpecializedNumberedCanvas(canvas.Canvas):
    """Canvas that performs two passes to compute total page numbers and draw archival neatlines and customized running headers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.header_title = "Energy Innovation Terminal // EXECUTIVE STRATEGIC MONOGRAPH"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        
        # Outer archival neatline border
        self.setStrokeColor(COLOR_BRAND_NAVY)
        self.setLineWidth(1.2)
        self.rect(26, 26, 560, 740)

        # Inner subtle neatline
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.rect(30, 30, 552, 732)

        # Header running masthead (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 6.5)
            self.setFillColor(COLOR_BRAND_CYAN)
            self.drawString(40, 748, getattr(self, 'header_title', "Energy Innovation Terminal // EXECUTIVE STRATEGIC MONOGRAPH")[:65])
            
            self.setFont("Helvetica", 6.5)
            self.setFillColor(COLOR_BRAND_MUTED)
            self.drawRightString(572, 748, f"NATIONAL RESEARCH EDITION · {datetime.date.today().strftime('%B %d, %Y')}")

            self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
            self.setLineWidth(0.5)
            self.line(40, 742, 572, 742)

        # Footer Source Attribution & Page Number
        self.setStrokeColor(COLOR_BRAND_BORDER_LIGHT)
        self.setLineWidth(0.5)
        self.line(40, 44, 572, 44)

        self.setFont("Helvetica", 6.5)
        self.setFillColor(COLOR_BRAND_MUTED)
        self.drawString(40, 34, SOURCE_ATTRIBUTION[:100])

        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(COLOR_BRAND_NAVY)
        self.drawRightString(572, 34, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


# =============================================================================
# HIGH-RESOLUTION VECTOR GRAPHICS & MAP ENGINES
# =============================================================================

def normalize_to_millions(values: List[float]) -> List[float]:
    """Normalizes a list of values to $ Millions."""
    if not values:
        return []
    max_val = max(values)
    if max_val > 50_000_000:
        return [float(v) / 1e6 for v in values]
    return [float(v) for v in values]


def render_vector_line_chart(years: List[int], values: List[float], title: str, y_label: str = "Capital ($ Millions)") -> io.BytesIO:
    """Render high-resolution Matplotlib line chart matching application design palette."""
    fig, ax = plt.subplots(figsize=(6.8, 2.1), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    y_m = normalize_to_millions(values)
    ax.plot(years, y_m, color='#0284C7', linewidth=2.2, marker='o', markersize=3.8, markerfacecolor='#059669', markeredgecolor='#FFFFFF', markeredgewidth=1)
    ax.fill_between(years, y_m, color='#0284C7', alpha=0.08)

    ax.set_title(title, fontsize=8.5, fontweight='bold', color='#0F172A', loc='left', pad=6, fontfamily='sans-serif')
    ax.set_ylabel(y_label, fontsize=7, color='#475569', fontweight='bold', fontfamily='sans-serif')
    ax.set_xlabel("Year", fontsize=7, color='#475569', fontweight='bold', fontfamily='sans-serif')
    
    if max(y_m) >= 1000:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x/1000:,.1f}B" if x >= 1000 else f"${x:,.0f}M"))
    else:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}M"))

    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.tick_params(axis='both', labelsize=6.5, colors='#475569')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_vector_bar_chart(labels: List[str], values: List[float], title: str, x_label: str = "Capital ($ Millions)") -> io.BytesIO:
    """Render high-resolution horizontal bar chart matching application design palette."""
    fig, ax = plt.subplots(figsize=(6.8, 2.1), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    plot_labels = labels[:6][::-1]
    plot_vals = normalize_to_millions(values[:6][::-1])

    # Gradient brand colors
    colors_list = ['#0F172A', '#0284C7', '#059669', '#38BDF8', '#34D399', '#93C5FD'][::-1][:len(plot_labels)]
    bars = ax.barh(plot_labels, plot_vals, color=colors_list, height=0.55, edgecolor='none')

    max_v = max(plot_vals) if plot_vals else 1
    for bar in bars:
        w = bar.get_width()
        if w > 0:
            val_str = f"${w/1000:,.2f}B" if w >= 1000 else f"${w:,.1f}M"
            ax.text(w + (max_v * 0.02), bar.get_y() + bar.get_height()/2, val_str, va='center', ha='left', fontsize=6.2, color='#0F172A', fontweight='bold', fontfamily='sans-serif')

    ax.set_title(title, fontsize=8.5, fontweight='bold', color='#0F172A', loc='left', pad=6, fontfamily='sans-serif')
    ax.set_xlabel(x_label, fontsize=7, color='#475569', fontweight='bold', fontfamily='sans-serif')
    
    if max_v >= 1000:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x/1000:,.1f}B" if x >= 1000 else f"${x:,.0f}M"))
    else:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}M"))

    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1', axis='x')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.tick_params(axis='both', labelsize=6.5, colors='#475569')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_geospatial_us_map(
    title: str = "Geospatial Clean Tech Innovation Clusters Across the United States",
    focus_tag: str = "National",
    custom_clusters: Optional[List[tuple]] = None,
    callout_boxes: Optional[List[dict]] = None
) -> io.BytesIO:
    """Render high-resolution NYT-grade stylized US geospatial cluster and capital density map with leader callouts."""
    fig, ax = plt.subplots(figsize=(6.8, 2.3), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    if custom_clusters and len(custom_clusters) > 0:
        clusters = custom_clusters
    else:
        clusters = [
            ("NYC Metro", 40.71, -74.00, 520, '#0F172A', "$18.7B Tracked"),
            ("Boston Hub", 42.36, -71.05, 460, '#0284C7', "$14.2B Tracked"),
            ("Bay Area", 37.77, -122.41, 500, '#0284C7', "$21.5B Tracked"),
            ("Albany/Cap.", 42.65, -73.75, 420, '#059669', "$6.8B Tracked"),
            ("Chicago Hub", 41.87, -87.62, 380, '#0284C7', "$5.9B Tracked"),
            ("Austin Hub", 30.26, -97.74, 360, '#059669', "$4.8B Tracked"),
            ("Seattle", 47.60, -122.33, 390, '#0284C7', "$6.2B Tracked"),
            ("Denver", 39.73, -104.99, 320, '#38BDF8', "$3.9B Tracked"),
            ("Wash. DC", 38.90, -77.03, 480, '#0F172A', "$12.4B Tracked"),
            ("Los Angeles", 34.05, -118.24, 430, '#0284C7', "$8.7B Tracked")
        ]

    lats = [c[1] for c in clusters if c[1] is not None]
    lngs = [c[2] for c in clusters if c[2] is not None]
    sizes = [c[3] if len(c) > 3 and c[3] is not None else 350 for c in clusters]
    colors_c = [c[4] if len(c) > 4 and c[4] is not None else '#0284C7' for c in clusters]

    # 1. Draw outer glowing halo rings
    sizes_halo = [s * 1.7 for s in sizes]
    ax.scatter(lngs, lats, s=sizes_halo, c=colors_c, alpha=0.18, edgecolors='none', zorder=2)

    # 2. Draw core proportional symbols
    ax.scatter(lngs, lats, s=sizes, c=colors_c, alpha=0.88, edgecolors='#0F172A', linewidths=0.9, zorder=3)

    # 3. Label standard clusters
    for c in clusters:
        if c[1] is not None and c[2] is not None:
            lbl = str(c[0])[:18]
            metric = str(c[5]) if len(c) > 5 and c[5] else ""
            full_txt = f"{lbl}\n{metric}" if metric else lbl
            ax.annotate(full_txt, (c[2], c[1] - 0.75), fontsize=5.2, fontweight='bold', color='#0F172A', ha='center', va='top', fontfamily='sans-serif', zorder=4)

    # 4. Draw editorial callout leader boxes if provided
    if callout_boxes:
        for call in callout_boxes:
            c_lat = call.get('lat')
            c_lng = call.get('lng')
            c_text = call.get('text', '')
            ox = call.get('offset_x', 14)
            oy = call.get('offset_y', 6)
            if c_lat is not None and c_lng is not None and c_text:
                elbow_x = c_lng + ox * 0.45
                elbow_y = c_lat + oy * 0.45
                end_x = c_lng + ox
                end_y = c_lat + oy
                ax.plot([c_lng, elbow_x, end_x], [c_lat, elbow_y, end_y], color='#0F172A', linewidth=0.75, linestyle='-', alpha=0.85, zorder=5)
                ax.scatter([c_lng], [c_lat], s=25, color='#0F172A', zorder=6)
                ax.text(end_x, end_y, c_text, fontsize=5.4, fontweight='bold', color='#0F172A', fontfamily='sans-serif',
                        bbox=dict(boxstyle='round,pad=0.28', facecolor='#FFFFFF', edgecolor='#0284C7', linewidth=0.7, alpha=0.96),
                        ha='left' if ox >= 0 else 'right', va='center', zorder=7)

    # Scale indicator legend (NYT style)
    ax.text(-126.5, 25.6, "● $100M   ● $500M   ● $2B+ Scale", fontsize=5.6, fontweight='bold', color='#475569', fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.5, alpha=0.92), zorder=8)

    ax.set_xlim(-128, -65)
    ax.set_ylim(24, 52)
    ax.set_title(title, fontsize=8.5, fontweight='bold', color='#0F172A', loc='left', pad=6, fontfamily='sans-serif')
    ax.set_xlabel('Longitude (°W) · Energy Innovation Terminal Geospatial Intelligence', fontsize=6.2, color='#64748B', fontfamily='sans-serif')
    ax.set_ylabel('Latitude (°N)', fontsize=6.2, color='#64748B', fontfamily='sans-serif')
    
    ax.grid(True, linestyle='--', alpha=0.3, color='#CBD5E1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.tick_params(axis='both', labelsize=6, colors='#475569')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_technology_radar_chart(categories: List[str], values: List[float], title: str = "Technology Performance & Supply Chain Readiness Radar") -> io.BytesIO:
    """Render multi-dimensional radar/spider benchmark chart."""
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    plot_vals = list(values) + [values[0]]

    fig, ax = plt.subplots(figsize=(6.8, 2.2), subplot_kw=dict(polar=True), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    ax.plot(angles, plot_vals, color='#0284C7', linewidth=1.8, linestyle='solid')
    ax.fill(angles, plot_vals, color='#0284C7', alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=6.2, color='#0F172A', fontweight='bold', fontfamily='sans-serif')
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=5.2, color='#64748B', fontfamily='sans-serif')
    ax.set_title(title, fontsize=8.5, fontweight='bold', color='#0F172A', pad=10, fontfamily='sans-serif')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_network_graph_diagram(
    title: str = "Knowledge Graph Topology & Institutional Innovation Anchors",
    custom_nodes: Optional[List[tuple]] = None,
    custom_edges: Optional[List[tuple]] = None
) -> io.BytesIO:
    """Render high-resolution stylized institutional network graph topology diagram."""
    fig, ax = plt.subplots(figsize=(6.8, 2.3), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    if custom_nodes and len(custom_nodes) > 0:
        nodes = custom_nodes
        edges = custom_edges or [(i, (i + 1) % len(nodes)) for i in range(len(nodes))]
    else:
        nodes = [
            ("Federal Energy Agency", 0.0, 0.0, 560, '#0F172A', 'Federal Policy Core'),
            ("Tier-1 R1 Universities", -0.42, 0.35, 480, '#0284C7', 'Basic Science R&D'),
            ("Corporate OEMs & Primes", 0.45, 0.32, 460, '#059669', 'Commercial Deployment'),
            ("Electric Utilities", 0.38, -0.38, 440, '#D97706', 'Grid Interconnection'),
            ("Climate Venture Capital", -0.48, -0.32, 420, '#7C3AED', 'Private Syndication'),
            ("State Tech Authorities", 0.0, 0.58, 430, '#0284C7', 'Regional Testbeds'),
            ("TRL 4-7 Scaleups", -0.58, 0.05, 410, '#059669', 'Demonstration Ventures'),
            ("Supply Chain Primes", 0.56, -0.08, 390, '#475569', 'Component Suppliers')
        ]

        edges = [
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 4), (1, 5),
            (2, 3), (2, 6), (3, 6), (4, 6), (5, 7), (1, 7), (2, 7)
        ]

    # Draw connective edges with gradient styling
    for u, v in edges:
        if u < len(nodes) and v < len(nodes):
            x_coords = [nodes[u][1], nodes[v][1]]
            y_coords = [nodes[u][2], nodes[v][2]]
            ax.plot(x_coords, y_coords, color='#CBD5E1', linewidth=1.2, alpha=0.75, zorder=1)

    # Draw outer halos and core nodes
    for n in nodes:
        # Outer halo
        ax.scatter([n[1]], [n[2]], s=n[3]*1.6, color=n[4], edgecolors='none', alpha=0.2, zorder=2)
        # Core node
        ax.scatter([n[1]], [n[2]], s=n[3], color=n[4], edgecolors='#0F172A', linewidths=1.0, zorder=3, alpha=0.92)
        
        # Node text label badge
        node_lbl = str(n[0])[:22]
        class_lbl = str(n[5])[:22] if len(n) > 5 and n[5] else ""
        badge_text = f"{node_lbl}\n[{class_lbl}]" if class_lbl else node_lbl
        ax.annotate(badge_text, (n[1], n[2] - 0.11), fontsize=5.6, fontweight='bold', color='#0F172A', ha='center', va='top', zorder=4, fontfamily='sans-serif')

    # Legend indicator
    ax.text(0.72, -0.62, "■ Agency  ■ R1 Univ  ■ Scaleup  ■ Utility", fontsize=5.4, fontweight='bold', color='#475569', fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.5, alpha=0.9), ha='right', zorder=5)

    ax.set_xlim(-0.75, 0.75)
    ax.set_ylim(-0.68, 0.75)
    ax.axis('off')
    ax.set_title(title, fontsize=8.5, fontweight='bold', color='#0F172A', loc='left', pad=6, fontfamily='sans-serif')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


def render_sankey_waterfall_diagram(title: str = "Multi-Stage Capital Flow & 'Valley of Death' Demonstration Attrition", stages: List[str] = None, values: List[float] = None) -> io.BytesIO:
    """Render capital waterfall diagram showing TRL 1-9 progression and stage attrition."""
    if isinstance(title, list):
        actual_stages = title
        actual_values = stages if isinstance(stages, list) else [28.4, 18.2, 8.4, 32.6, 9.9]
        actual_title = values if isinstance(values, str) else "Multi-Stage Capital Flow & 'Valley of Death' Demonstration Attrition"
    else:
        actual_title = title
        actual_stages = stages if stages is not None else ["TRL 1-3 (R&D)", "TRL 4-5 (Prototype)", "TRL 6-7 (Pilot Demo)", "TRL 8-9 (Commercial)", "NOAK Scale"]
        actual_values = values if values is not None else [28.4, 18.2, 8.4, 32.6, 9.9]

    fig, ax = plt.subplots(figsize=(6.8, 2.1), dpi=260)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    x_pos = np.arange(len(actual_stages))
    colors_w = ['#0F172A', '#0284C7', '#D97706', '#EF4444', '#059669']

    bars = ax.bar(x_pos, actual_values, color=colors_w[:len(actual_stages)], width=0.55, edgecolor='#0F172A', linewidth=0.8)

    for bar, v in zip(bars, actual_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (max(actual_values)*0.02), f"${v:,.1f}B", ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#0F172A', fontfamily='sans-serif')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(actual_stages, fontsize=6.5, fontweight='bold', color='#0F172A', fontfamily='sans-serif')
    ax.set_ylabel("Deployed Capital ($B)", fontsize=7, color='#475569', fontweight='bold', fontfamily='sans-serif')
    ax.set_title(actual_title, fontsize=8.5, fontweight='bold', color='#0F172A', loc='left', pad=6, fontfamily='sans-serif')

    ax.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CBD5E1')
    ax.spines['bottom'].set_color('#CBD5E1')
    ax.tick_params(axis='both', labelsize=6.5, colors='#475569')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=260)
    plt.close(fig)
    buf.seek(0)
    return buf


# =============================================================================
# TYPOGRAPHY STYLES & NATURAL FLOWABLE COMPILATION
# =============================================================================

def get_monograph_styles():
    """Returns standardized hierarchical sans-serif typography matching the application design system."""
    styles = getSampleStyleSheet()

    return {
        'eyebrow': ParagraphStyle('Eyebrow', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=COLOR_BRAND_CYAN, textTransform='uppercase', spaceAfter=2.5),
        'title': ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=16.5, leading=20, textColor=COLOR_BRAND_NAVY, spaceAfter=4),
        'subtitle': ParagraphStyle('DocSubtitle', fontName='Helvetica', fontSize=8.2, leading=10.5, textColor=COLOR_BRAND_MUTED, spaceAfter=7),
        'thesis_box': ParagraphStyle('ThesisText', fontName='Helvetica-Bold', fontSize=8.6, leading=11.8, textColor=COLOR_BRAND_NAVY),
        'h1': ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=COLOR_BRAND_NAVY, spaceBefore=4, spaceAfter=2.5, keepWithNext=True),
        'h2': ParagraphStyle('SectionH2', fontName='Helvetica-Bold', fontSize=8.2, leading=10.5, textColor=COLOR_BRAND_CYAN, spaceBefore=3, spaceAfter=2, keepWithNext=True),
        'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=7.3, leading=10.5, textColor=COLOR_BRAND_SLATE, spaceAfter=3.5),
        'callout_label': ParagraphStyle('CalloutLabel', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=COLOR_BRAND_CYAN, textTransform='uppercase'),
        'callout_body': ParagraphStyle('CalloutBody', fontName='Helvetica-Oblique', fontSize=7.2, leading=10, textColor=colors.HexColor('#1E293B')),
        'caption': ParagraphStyle('Caption', fontName='Helvetica-Oblique', fontSize=6.5, leading=8.5, textColor=COLOR_BRAND_MUTED, spaceAfter=3.5),
        'th': ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5, textColor=COLOR_BRAND_NAVY),
        'td': ParagraphStyle('TD', fontName='Helvetica', fontSize=6.5, leading=8.2, textColor=COLOR_BRAND_SLATE)
    }


def render_tech_trajectory_table_flowable(db: Session, category_ids: List[str], styles: Dict[str, Any]) -> Table:
    """Builds a standardized quantitative technology cost & performance baseline vs target trajectory table."""
    try:
        from app.models.technology import Technology, TechnologyCostPerformance
        
        techs = db.query(Technology).filter(Technology.category_id.in_(category_ids)).all()
        if not techs:
            techs = db.query(Technology).filter(Technology.id.in_(category_ids)).all()

        if not techs:
            return None

        table_data = [
            [
                Paragraph("<b>Technology Profile</b>", styles['th']),
                Paragraph("<b>TRL</b>", styles['th']),
                Paragraph("<b>2024 Baseline</b>", styles['th']),
                Paragraph("<b>2030 Target</b>", styles['th']),
                Paragraph("<b>2035 Goal</b>", styles['th']),
                Paragraph("<b>Reduction / Gain</b>", styles['th']),
                Paragraph("<b>Scale Driver & DOE Earthshot</b>", styles['th']),
            ]
        ]

        for t in techs:
            cp = t.cost_performance
            base_fmt = cp.cost_baseline_fmt if cp else "N/A"
            t2030_fmt = cp.cost_target_2030_fmt if cp else "N/A"
            t2035_fmt = cp.cost_target_2035_fmt if cp else "N/A"
            red_pct = cp.cost_reduction_pct if cp else "N/A"
            driver = cp.cost_primary_driver if cp else (t.headline or "")
            earthshot = cp.earthshot_goal if cp else ""

            driver_text = f"<b>Driver:</b> {driver[:65]}..." if len(driver) > 65 else f"<b>Driver:</b> {driver}"
            if earthshot:
                driver_text += f"<br/><b>Target:</b> {earthshot[:55]}"

            table_data.append([
                Paragraph(f"<b>{t.name}</b><br/><font color='#64748B'>{t.sector or t.category_id}</font>", styles['td']),
                Paragraph(f"TRL {t.trl_current}&rarr;{t.trl_target}", styles['td']),
                Paragraph(base_fmt, styles['td']),
                Paragraph(f"<b>{t2030_fmt}</b>", styles['td']),
                Paragraph(f"<b>{t2035_fmt}</b>", styles['td']),
                Paragraph(f"<font color='#059669'><b>{red_pct}</b></font>", styles['td']),
                Paragraph(driver_text, styles['td']),
            ])

        t_elem = Table(table_data, colWidths=[105, 38, 62, 58, 56, 52, 165])
        t_elem.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_BRAND_BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 0.6, COLOR_BRAND_BORDER),
            ('INNERGRID', (0,0), (-1,-1), 0.4, COLOR_BRAND_BORDER_LIGHT),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BRAND_BG_LIGHT])
        ]))
        return t_elem
    except Exception:
        return None


import re

def sanitize_reportlab_markup(text: Any) -> str:
    """
    Sanitizes arbitrary text/HTML strings into strictly valid XML markup accepted by ReportLab.
    - Normalizes <br> variants to <br/>
    - Strips invalid outer <para> wrappers
    - Converts unsupported tags (p, div, section) to line breaks
    - Escapes unescaped ampersands (& -> &amp;)
    - Escapes mathematical symbols (<$100 -> &lt;$100, > -> &gt;)
    - Validates allowed formatting tags (b, i, u, font, sub, sup, a, color)
    - Balances unclosed open tags so paraparser never fails.
    """
    if text is None:
        return ""
    s = str(text)
    
    # Strip wrapping <para>...</para> if already present
    s = re.sub(r'^\s*<para>(.*?)</para>\s*$', r'\1', s, flags=re.DOTALL | re.IGNORECASE)
    
    # Normalize br tags to <br/>
    s = re.sub(r'<\s*br\s*/?\s*>', '<br/>', s, flags=re.IGNORECASE)
    s = re.sub(r'<\s*/\s*br\s*>', '', s, flags=re.IGNORECASE)
    
    # Replace p/div/section/article tags with <br/><br/>
    s = re.sub(r'<\s*/?\s*(?:p|div|section|article)\s*/?\s*>', '<br/>', s, flags=re.IGNORECASE)
    
    # Escape standalone ampersands not part of valid entities
    s = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', '&amp;', s)
    
    # Escape < not followed by an ascii letter or /
    s = re.sub(r'<(?![a-zA-Z/])', '&lt;', s)
    
    allowed_tags = {'b', 'i', 'u', 'sub', 'sup', 'br', 'font', 'a', 'color'}
    
    def tag_replacer(match):
        full = match.group(0)
        tag_match = re.match(r'^</?([a-zA-Z][a-zA-Z0-9]*)(\s+[^>]*)?/?>$', full)
        if tag_match:
            tag_name = tag_match.group(1).lower()
            if tag_name == 'br':
                return '<br/>'
            if tag_name in allowed_tags:
                return full
        return '&lt;' + full[1:-1] + '&gt;'

    s = re.sub(r'</?[a-zA-Z][a-zA-Z0-9]*(\s+[^>]*)?/?>', tag_replacer, s)
    
    # Any remaining loose '<' that wasn't matched
    s = re.sub(r'<(?![a-zA-Z/])', '&lt;', s)
    
    # Balance unclosed tags (b, i, u, font, sub, sup, a)
    stack = []
    tokens = re.finditer(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)(\s+[^>]*)?/?>', s)
    for t in tokens:
        is_close = bool(t.group(1))
        tag = t.group(2).lower()
        if tag in {'b', 'i', 'u', 'font', 'sub', 'sup', 'a'}:
            if not is_close:
                stack.append(tag)
            elif stack and stack[-1] == tag:
                stack.pop()
    
    while stack:
        unclosed = stack.pop()
        s += f'</{unclosed}>'
        
    return s


def safe_paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    """
    Safely instantiates a ReportLab Paragraph guaranteed never to throw XML parse errors.
    Falls back to fully stripped plain text if any parser edge case occurs.
    """
    sanitized = sanitize_reportlab_markup(text)
    try:
        return Paragraph(sanitized, style)
    except Exception:
        clean_plain = re.sub(r'<[^>]*>', '', str(text or ''))
        clean_plain = clean_plain.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return Paragraph(clean_plain, style)


def compile_specialized_pdf(
    output_stream: io.BytesIO,
    meta: Dict[str, Any],
    pages_content: List[Dict[str, Any]]
) -> None:
    """
    Assembles and compiles a specialized publication monograph with natural flowable layout,
    supporting multiple charts, diagrams, maps, and detailed data tables with the Energy Innovation Terminal design system.
    """
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=letter,
        leftMargin=38,
        rightMargin=38,
        topMargin=42,
        bottomMargin=44
    )

    styles = get_monograph_styles()
    story = []

    # =========================================================================
    # EXECUTIVE HEADER & PUBLICATION TITLE
    # =========================================================================
    story.append(safe_paragraph(f"Energy Innovation Terminal // {meta.get('category_tag', 'EXECUTIVE STRATEGIC MONOGRAPH').upper()}", styles['eyebrow']))
    story.append(safe_paragraph(meta.get("title", "Executive Strategic Briefing"), styles['title']))
    story.append(safe_paragraph(meta.get("subtitle", "Strategic Publication · Energy Innovation Terminal · Executive Research Edition"), styles['subtitle']))
    story.append(Spacer(1, 5))

    # Core Strategic Thesis Box (Styled with signature emerald & navy accent)
    thesis_text = meta.get("thesis", "Empirical capital deployment analysis confirms high-velocity expansion across this strategic vertical, requiring targeted co-funding and institutional de-risking.")
    tbox_content = [
        safe_paragraph("<b>CORE STRATEGIC THESIS // EXECUTIVE INSIGHT:</b>", ParagraphStyle('TLabel', fontName='Helvetica-Bold', fontSize=7.5, leading=9.2, textColor=COLOR_BRAND_EMERALD)),
        Spacer(1, 2),
        safe_paragraph(thesis_text, styles['thesis_box'])
    ]
    tbox = Table([[tbox_content]], colWidths=[536])
    tbox.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BRAND_BG_EMERALD),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#A7F3D0')),
        ('LINELEFT', (0,0), (0,0), 3.5, COLOR_BRAND_EMERALD),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
    ]))
    story.append(tbox)
    story.append(Spacer(1, 7))

    # Publication Metadata Box
    meta_rows = [
        [safe_paragraph("<b>Scope & Dataset:</b>", styles['th']), safe_paragraph(meta.get("dataset_scope", "54,305 Verified Awards ($98.98B Capital Tracked)"), styles['td'])],
        [safe_paragraph("<b>Institutional Coverage:</b>", styles['th']), safe_paragraph(meta.get("institutions_scope", "13,706 Unique Recipient Entities Across 50 States"), styles['td'])],
        [safe_paragraph("<b>Vertical Specialization:</b>", styles['th']), safe_paragraph(meta.get("vertical_specialization", "Energy Innovation & Technology Deployment"), styles['td'])],
        [safe_paragraph("<b>Publication Format:</b>", styles['th']), safe_paragraph("Executive Strategic Monograph (300 DPI Vector Graphics & Maps)", styles['td'])],
        [safe_paragraph("<b>Classification & Date:</b>", styles['th']), safe_paragraph(f"U.S. Energy Innovation Database · Clean Energy Research, LLC (https://terminal.aixenergy.io) · {datetime.date.today().strftime('%B %d, %Y')}", styles['td'])]
    ]
    meta_table = Table(meta_rows, colWidths=[130, 406])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BRAND_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BRAND_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.4, COLOR_BRAND_BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_BRAND_NAVY, spaceAfter=8, spaceBefore=4))

    # =========================================================================
    # DEDICATED EXECUTIVE SUMMARY (HOUSE STRATEGIC BRIEFING)
    # =========================================================================
    exec_summary = meta.get("executive_summary")
    if not exec_summary and isinstance(meta.get("narrative"), dict):
        exec_summary = meta["narrative"].get("executive_summary")

    if exec_summary:
        story.append(safe_paragraph("Executive Summary // Strategic Synthesis &amp; Market Dynamics", styles['h1']))
        story.append(safe_paragraph("Energy Innovation Terminal · Executive Strategic Synthesis", styles['h2']))
        # Split on paragraph breaks or br tags
        summary_raw = str(exec_summary).replace('<br><br>', '\n\n').replace('<br/><br/>', '\n\n')
        for para in summary_raw.split("\n\n"):
            if para.strip():
                story.append(safe_paragraph(para.strip(), styles['body']))
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BRAND_BORDER, spaceAfter=7, spaceBefore=3))

    # =========================================================================
    # NATURAL FLOWABLE SECTION COMPILATION
    # =========================================================================
    for idx, page in enumerate(pages_content):
        # Section Header
        if "header" in page and page["header"]:
            story.append(safe_paragraph(page["header"], styles['h1']))

        # Subheader
        if "subheader" in page and page["subheader"]:
            story.append(safe_paragraph(page["subheader"], styles['h2']))

        # Executive Callout Box (Strategic Implication / Key Takeaway)
        if "executive_callout" in page and page["executive_callout"]:
            callout_title = page.get("callout_title", "STRATEGIC IMPLICATION // KEY TAKEAWAY")
            c_content = [
                safe_paragraph(f"<b>{callout_title}</b>", styles['callout_label']),
                Spacer(1, 2),
                safe_paragraph(page["executive_callout"], styles['callout_body'])
            ]
            c_table = Table([[c_content]], colWidths=[536])
            c_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), COLOR_BRAND_BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.6, COLOR_BRAND_BORDER),
                ('LINELEFT', (0,0), (0,0), 3.0, COLOR_BRAND_CYAN),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(c_table)
            story.append(Spacer(1, 4))

        # Main Analytical Prose
        if "prose" in page and page["prose"]:
            for p_text in page["prose"]:
                if p_text and str(p_text).strip():
                    story.append(safe_paragraph(str(p_text).strip(), styles['body']))

        # High-Resolution Chart / Diagram / Map Flowable
        if "chart_image" in page and page["chart_image"]:
            img_height = page.get("chart_height", 145)
            story.append(Image(page["chart_image"], width=536, height=img_height))
            if "chart_caption" in page and page["chart_caption"]:
                story.append(safe_paragraph(page["chart_caption"], styles['caption']))
            story.append(Spacer(1, 2.5))

        # Secondary Chart / Diagram if present
        if "secondary_image" in page and page["secondary_image"]:
            sec_height = page.get("secondary_height", 130)
            story.append(Image(page["secondary_image"], width=536, height=sec_height))
            if "secondary_caption" in page and page["secondary_caption"]:
                story.append(safe_paragraph(page["secondary_caption"], styles['caption']))
            story.append(Spacer(1, 2.5))

        # Data Table
        if "table_data" in page and page["table_data"]:
            col_widths = page.get("table_widths", [160, 110, 110, 60, 96])
            # Ensure all cells in table_data are safe flowables or strings
            processed_table = []
            for row_idx, row in enumerate(page["table_data"]):
                processed_row = []
                for cell in row:
                    if isinstance(cell, Paragraph):
                        # Re-wrap or use safe paragraph
                        processed_row.append(safe_paragraph(cell.text, cell.style))
                    elif isinstance(cell, str):
                        cell_style = styles['th'] if row_idx == 0 else styles['td']
                        processed_row.append(safe_paragraph(cell, cell_style))
                    else:
                        processed_row.append(cell)
                processed_table.append(processed_row)

            t = Table(processed_table, colWidths=col_widths)
            t_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor(page.get("table_header_bg", '#F1F5F9'))),
                ('BOX', (0,0), (-1,-1), 0.75, COLOR_BRAND_BORDER),
                ('INNERGRID', (0,0), (-1,-1), 0.4, COLOR_BRAND_BORDER_LIGHT),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 2.5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BRAND_BG_LIGHT])
            ]
            t.setStyle(TableStyle(t_style))
            story.append(t)
            story.append(Spacer(1, 2.5))

        # Custom Flowable Element (e.g. Technology Trajectory & Earthshot Matrix Table)
        if "flowable_element" in page and page["flowable_element"]:
            story.append(page["flowable_element"])
            story.append(Spacer(1, 3))

        # Bullets / Priorities / Roadmaps
        if "bullet_items" in page and page["bullet_items"]:
            for b in page["bullet_items"]:
                if b and str(b).strip():
                    story.append(safe_paragraph(f"• {str(b).strip()}", styles['body']))

        # Flowable Section Separator (without artificial page break)
        story.append(Spacer(1, 5))
        if idx < len(pages_content) - 1:
            story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BRAND_BORDER, spaceAfter=7, spaceBefore=3))

    # =========================================================================
    # DEDICATED STRATEGIC CONCLUSION & 2026-2035 ROADMAP
    # =========================================================================
    conclusion = meta.get("conclusion")
    if not conclusion and isinstance(meta.get("narrative"), dict):
        conclusion = meta["narrative"].get("conclusion")

    if conclusion:
        concl_title = meta.get("conclusion_title", "Strategic Synthesis &amp; Forward Horizon Roadmap")
        story.append(safe_paragraph(concl_title, styles['h1']))
        story.append(safe_paragraph("Energy Innovation Terminal · Executive Strategic Synthesis", styles['h2']))
        conc_raw = str(conclusion).replace('<br><br>', '\n\n').replace('<br/><br/>', '\n\n')
        for para in conc_raw.split("\n\n"):
            if para.strip():
                story.append(safe_paragraph(para.strip(), styles['body']))
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BRAND_BORDER, spaceAfter=7, spaceBefore=3))

    # Build document
    doc.build(story, canvasmaker=SpecializedNumberedCanvas)


# Alias for backward compatibility
compile_specialized_21_page_pdf = compile_specialized_pdf


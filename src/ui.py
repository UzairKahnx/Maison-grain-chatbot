"""
Presentation helpers for the Maison & Grain Streamlit app.

All artwork is local inline SVG, so the app has no external image dependencies and
looks identical on localhost and on Streamlit Community Cloud.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def load_svg(name: str) -> str:
    """Return an SVG file as text (empty string if the asset is missing)."""
    path = ASSETS_DIR / name
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except OSError:
        return ""


def svg_data_uri(name: str) -> str:
    svg = load_svg(name)
    if not svg:
        return ""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
  --espresso: #2E2A27;
  --walnut: #8A6F54;
  --oak: #C9A87C;
  --linen: #FBF7F1;
  --sand: #F1E6D6;
  --terracotta: #B85C38;
}

.stApp {
  background: linear-gradient(135deg, #FBF7F1 0%, #F7EFE3 45%, #F2E6D5 100%);
  font-family: 'DM Sans', sans-serif;
  color: var(--espresso);
}
h1, h2, h3, .mg-serif { font-family: 'Playfair Display', Georgia, serif; }
#MainMenu, footer, .stDeployButton { visibility: hidden; }
header { height: 0 !important; }

/* ---------- Hero ---------- */
.mg-hero {
  position: relative;
  height: 250px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 18px 40px rgba(92, 62, 35, 0.16);
  background-color: #EED9BC;
  background-image: linear-gradient(120deg, #EED9BC, #D9B992);
  background-size: cover;
  background-position: center 55%;
  display: flex;
  align-items: center;
  margin: 6px 0 14px 0;
}
.mg-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(46,42,39,.80) 0%, rgba(46,42,39,.58) 40%, rgba(46,42,39,.05) 78%);
}
.mg-hero-content { position: relative; z-index: 2; padding: 0 46px; max-width: 620px; }
.mg-eyebrow {
  font-size: 11px; letter-spacing: 3.2px; font-weight: 700;
  color: #F7DFC4; text-transform: uppercase; margin-bottom: 10px;
}
.mg-hero h1 {
  font-size: clamp(28px, 3.2vw, 44px); line-height: 1.12;
  color: #FFF9F1; margin: 0 0 10px 0; font-weight: 700;
}
.mg-hero p { color: #F6E9D9; font-size: 14.5px; line-height: 1.55; margin: 0; max-width: 470px; }
.mg-pill-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
.mg-pill {
  background: rgba(255,252,246,.92); color: #4A3829; border-radius: 100px;
  padding: 7px 14px; font-size: 11.5px; font-weight: 600; letter-spacing: .2px;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
}

/* ---------- Trust bar ---------- */
.mg-trust { display: flex; gap: 12px; margin-bottom: 16px; }
.mg-trust-item {
  flex: 1; background: rgba(255,255,255,.72); border: 1px solid rgba(201,168,124,.35);
  border-radius: 14px; padding: 12px 16px; display: flex; align-items: center; gap: 12px;
  box-shadow: 0 3px 12px rgba(92,62,35,.05);
}
.mg-trust-icon { font-size: 22px; }
.mg-trust-title { font-weight: 700; font-size: 12.5px; color: var(--espresso); }
.mg-trust-sub { font-size: 11px; color: #8C7A68; margin-top: 1px; }

/* ---------- Chat ---------- */
[data-testid="stChatMessage"] {
  border-radius: 18px !important;
  padding: 10px 14px !important;
  margin: 8px 0 !important;
  box-shadow: 0 4px 16px rgba(92,62,35,.07) !important;
  border: 1px solid rgba(201,168,124,.28) !important;
  background: rgba(255,253,249,.94) !important;
}
[data-testid="stChatMessage"] p { line-height: 1.62; font-size: 14.5px; }
[data-testid="stChatMessage"] ul { padding-left: 20px; }
[data-testid="stChatMessage"] li { margin: 4px 0; }
.stChatMessage { border-radius: 18px; }
[data-testid="stChatInput"] {
  border-radius: 18px !important;
  box-shadow: 0 8px 24px rgba(92,62,35,.12) !important;
}
[data-testid="stChatInput"] textarea {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 14.5px !important;
}
.stButton > button {
  border-radius: 100px !important;
  border: 1px solid rgba(184,92,56,.28) !important;
  background: rgba(255,255,255,.8) !important;
  color: #6E4A33 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  padding: 7px 14px !important;
  transition: all .2s ease !important;
}
.stButton > button:hover {
  background: var(--terracotta) !important;
  color: #fff !important;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(184,92,56,.28) !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F6EBDC 0%, #F3E5D1 100%) !important;
  border-right: 1px solid rgba(138,111,84,.18);
}
[data-testid="stSidebar"] .block-container { padding-top: 18px; }
[data-testid="stSidebar"] .stButton > button {
  background: #fff !important; color: #6E4A33 !important; width: 100%;
}
.mg-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 0 12px 0; border-bottom: 1px solid rgba(138,111,84,.25);
  margin-bottom: 14px;
}
.mg-logo {
  width: 46px; height: 46px; border-radius: 50%;
  background: linear-gradient(135deg, #B85C38, #8A6F54);
  color: #FFF6E9; display: flex; align-items: center; justify-content: center;
  font-family: 'Playfair Display', serif; font-size: 17px; font-weight: 700;
  box-shadow: 0 5px 14px rgba(138,111,84,.3); flex-shrink: 0;
}
.mg-brand-name { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; color: #3B3028; line-height: 1.1; }
.mg-brand-sub { font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #9A7C5C; margin-top: 3px; }
.mg-side-label { font-size: 10.5px; letter-spacing: 1.8px; text-transform: uppercase; color: #9A7C5C; font-weight: 700; margin: 16px 0 8px 0; }
.mg-badge {
  display: inline-block; padding: 5px 11px; border-radius: 100px;
  font-size: 11px; font-weight: 700; letter-spacing: .3px;
}
.mg-badge-live { background: #E4F0E6; color: #326A42; }
.mg-badge-demo { background: #FCE9D8; color: #A45A2C; }
.mg-note { font-size: 11.5px; color: #8C7A68; line-height: 1.5; }
.mg-divider { height: 1px; background: rgba(138,111,84,.2); margin: 16px 0; }

/* ---------- Collection cards ---------- */
.mg-section-title {
  font-family: 'Playfair Display', serif; font-size: 20px; color: #3B3028;
  margin: 20px 0 4px 0;
}
.mg-section-sub { font-size: 12.5px; color: #907B66; margin-bottom: 14px; }
.mg-cards { display: flex; gap: 14px; margin-bottom: 6px; }
.mg-card {
  flex: 1; background: rgba(255,255,255,.78); border: 1px solid rgba(201,168,124,.35);
  border-radius: 16px; overflow: hidden; box-shadow: 0 5px 18px rgba(92,62,35,.07);
  transition: transform .2s ease, box-shadow .2s ease;
}
.mg-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(92,62,35,.13); }
.mg-card svg { width: 100%; height: auto; display: block; }
.mg-card-body { padding: 12px 14px 14px 14px; }
.mg-card-name { font-weight: 700; font-size: 13.5px; color: #3B3028; }
.mg-card-detail { font-size: 11.5px; color: #8C7A68; margin-top: 3px; line-height: 1.4; }
.mg-card-price { font-size: 11.5px; color: var(--terracotta); font-weight: 700; margin-top: 7px; }

.mg-config { font-size: 12.5px; line-height: 1.6; color: #6E5B49; }
.mg-config b { color: #3B3028; }
.mg-config code { background: rgba(184,92,56,.1); padding: 1px 5px; border-radius: 5px; color: #8E4529; }

.mg-footer {
  text-align: center; font-size: 11px; color: #A08C76;
  padding: 18px 0 6px 0; border-top: 1px solid rgba(138,111,84,.18); margin-top: 22px;
}
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: #D6BFA2; border-radius: 10px; }
::-webkit-scrollbar-track { background: transparent; }

@media (max-width: 760px) {
  .mg-hero { height: 210px; }
  .mg-hero-content { padding: 0 22px; }
  .mg-trust { flex-direction: column; }
  .mg-cards { flex-direction: column; }
}
</style>
"""


def apply_custom_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    uri = svg_data_uri("hero.svg")
    style = (
        f"background-image: url('{uri}');"
        if uri
        else "background-image: linear-gradient(120deg,#F1DFC7,#D9B992);"
    )
    st.markdown(
        f"""
        <div class="mg-hero" style="{style}">
          <div class="mg-hero-content">
            <div class="mg-eyebrow">Maison &amp; Grain · Est. 1998</div>
            <h1>Find the piece<br/>that feels like home.</h1>
            <p>Your personal interior styling companion. Explore our collection, get
               thoughtful advice on fit and finishes, and design a space you'll love
               coming back to.</p>
            <div class="mg-pill-row">
              <span class="mg-pill">🛋️ Curated collection</span>
              <span class="mg-pill">✨ Complimentary style advice</span>
              <span class="mg-pill">🌿 Made to last</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trust_bar() -> None:
    st.markdown(
        """
        <div class="mg-trust">
          <div class="mg-trust-item"><div class="mg-trust-icon">🎯</div><div>
            <div class="mg-trust-title">Domain expertise</div>
            <div class="mg-trust-sub">Furniture &amp; interiors only</div></div></div>
          <div class="mg-trust-item"><div class="mg-trust-icon">📐</div><div>
            <div class="mg-trust-title">Fit &amp; finish guidance</div>
            <div class="mg-trust-sub">Sizes, materials &amp; care</div></div></div>
          <div class="mg-trust-item"><div class="mg-trust-icon">🤝</div><div>
            <div class="mg-trust-title">No pressure, ever</div>
            <div class="mg-trust-sub">Honest, friendly advice</div></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_collection() -> None:
    products = [
        ("sofa.svg", "Linden Bouclé Sofa", "Cream bouclé · solid walnut legs", "from $1,890*"),
        ("chair.svg", "Arlo Lounge Chair", "Cognac leather · walnut frame", "from $740*"),
        ("table.svg", "Onda Round Dining Table", "Solid oak · seats 4–6", "from $1,290*"),
    ]
    cards = ""
    for svg_name, name, detail, price in products:
        art = load_svg(svg_name)
        cards += f"""
        <div class="mg-card">
          {art}
          <div class="mg-card-body">
            <div class="mg-card-name">{name}</div>
            <div class="mg-card-detail">{detail}</div>
            <div class="mg-card-price">{price}</div>
          </div>
        </div>
        """
    st.markdown(
        f"""
        <div class="mg-section-title">The collection</div>
        <div class="mg-section-sub">A few of our most-loved pieces — ask Maya for details.</div>
        <div class="mg-cards">{cards}</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("* Indicative starting prices. Confirm with the showroom.")


def render_brand() -> None:
    st.markdown(
        """
        <div class="mg-brand">
          <div class="mg-logo">M&amp;G</div>
          <div>
            <div class="mg-brand-name">Maison &amp; Grain</div>
            <div class="mg-brand-sub">Furniture Showroom</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

"""
build-html.py — Genera carlo-rondon.html desde data.json
Ejecutar desde la raíz del proyecto: python build/build-html.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data.json"
OUT_PATH = ROOT / "carlo-rondon.html"


def load():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def bold_md(text):
    """Convierte **texto** en <strong>texto</strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def render_metrics(metrics):
    if not metrics:
        return ""
    items = ""
    for m in metrics:
        items += f"""
        <div class="metric-card">
          <div class="metric-num">{m['valor']}</div>
          <div class="metric-label">{m['label']}</div>
        </div>"""
    return f'<div class="metrics-row">{items}\n        </div>'


def render_role(role):
    metrics_html = render_metrics(role["metricas"])
    logros_html = ""
    for logro in role["logros"]:
        logros_html += f'<li>{bold_md(logro)}</li>\n'

    tag_html = ""
    if role.get("tag"):
        tag_html = f'<span class="role-tag">{role["tag"]}</span>'

    return f"""
        <div class="role-block">
          <div class="role-header">
            <span class="role-title">{role['titulo']}</span>
            {tag_html}
            <span class="role-period">{role['periodo']}</span>
          </div>
          {metrics_html}
          <ul class="logros-list">
            {logros_html}
          </ul>
        </div>"""


def render_skills(skills):
    if not skills:
        return ""
    tags = "".join(f'<span class="skill-tag">{s}</span>' for s in skills)
    return f'<div class="skills-row">{tags}</div>'


def render_accordion(exp, idx):
    is_open = "open" if idx == 0 else ""
    roles_html = "".join(render_role(r) for r in exp["roles"])
    skills_html = render_skills(exp["skills"])

    logo_html = f"""<img src="{exp['logo_url']}" alt="{exp['empresa']}" class="company-logo"
               onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
          <div class="company-logo-fallback" style="background:{exp['logo_color']};color:{exp['logo_text_color']};display:none">{exp['logo_fallback']}</div>"""

    return f"""
      <div class="acc-card cs {is_open}" data-delay-idx="{idx}">
        <button class="acc-header" onclick="toggleAcc(this)">
          <div class="acc-company-info">
            <div class="company-logo-wrap">
              {logo_html}
            </div>
            <div class="acc-company-text">
              <span class="company-name">{exp['empresa']}</span>
              <span class="company-meta">{exp['periodo']} · {exp['duracion']}</span>
            </div>
          </div>
          <svg class="acc-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </button>
        <div class="acc-body">
          <div class="acc-body-inner">
            {roles_html}
            {skills_html}
          </div>
        </div>
      </div>"""


def render_competencias(comps):
    html = ""
    for i, c in enumerate(comps):
        items_html = "".join(f"<li>{item}</li>" for item in c["items"])
        html += f"""
      <div class="comp-card cs" data-delay-idx="{i}">
        <div class="comp-num">{c['numero']}</div>
        <div class="comp-emoji">{c['emoji']}</div>
        <h3 class="comp-title">{c['titulo']}</h3>
        <ul class="comp-items">{items_html}</ul>
      </div>"""
    return html


def render_educacion(edu_list):
    html = ""
    for e in edu_list:
        html += f"""
          <div class="edu-item">
            <div class="edu-siglas">{e['siglas']}</div>
            <div class="edu-text">
              <div class="edu-nivel">{e['nivel']}</div>
              <div class="edu-titulo">{e['titulo']}</div>
              <div class="edu-inst">{e['institucion']}</div>
            </div>
          </div>"""
    return html


def render_certificaciones(certs):
    html = ""
    for c in certs:
        badge = '<span class="cert-badge cert-badge--curso">En curso</span>' if c["estado"] == "en_curso" else '<span class="cert-badge cert-badge--ok">✓</span>'
        html += f"""
          <div class="cert-item">
            <div class="cert-info">
              <span class="cert-nombre">{c['nombre']}</span>
              <span class="cert-entidad">{c['entidad']} · {c['año']}</span>
            </div>
            {badge}
          </div>"""
    return html


def render_idiomas(idiomas):
    html = ""
    for lang in idiomas:
        nota_html = f'<span class="lang-nota">{lang["nota"]}</span>' if lang.get("nota") else ""
        html += f"""
          <div class="lang-item">
            <div class="lang-top">
              <span class="lang-nombre">{lang['nombre']}</span>
              <span class="lang-nivel">{lang['nivel']}</span>
            </div>
            {nota_html}
            <div class="lbar-track">
              <div class="lbar-fill" data-w="{lang['porcentaje']}"></div>
            </div>
          </div>"""
    return html


def render_proyectos(proyectos):
    html = ""
    for p in proyectos:
        if p["estado"] == "en_construccion":
            estado_html = '<span class="proj-status proj-status--wip">🔨 En construcción</span>'
        else:
            estado_html = '<span class="proj-status proj-status--soon">Próximamente</span>'
        skills_html = "".join(f'<span class="skill-tag">{s}</span>' for s in p["skills"])
        html += f"""
      <div class="proj-card cs" data-delay-idx="{p['numero']}" style="background:{p['gradient']}">
        <div class="proj-num">{p['numero']}</div>
        <div class="proj-emoji">{p['emoji']}</div>
        <h3 class="proj-title">{p['titulo']}</h3>
        <p class="proj-desc">{p['descripcion']}</p>
        <div class="proj-footer">
          <div class="skills-row">{skills_html}</div>
          {estado_html}
        </div>
      </div>"""
    return html


def render_hero_metrics(metricas):
    html = ""
    for m in metricas:
        label = m["label"].replace("\n", "<br>")
        html += f"""
        <div class="hero-metric">
          <span class="hero-metric-val">{m['valor']}</span>
          <span class="hero-metric-label">{label}</span>
        </div>"""
    return html


def build(d):
    p = d["persona"]
    accordions = "".join(render_accordion(exp, i) for i, exp in enumerate(d["experiencia"]))
    comps = render_competencias(d["competencias"])
    edu = render_educacion(d["educacion"])
    certs = render_certificaciones(d["certificaciones"])
    idiomas = render_idiomas(d["idiomas"])
    proyectos = render_proyectos(d["proyectos"])
    hero_metrics = render_hero_metrics(d["metricas"])

    # Split bio into chars for reveal animation
    perfil_chars = "".join(
        f'<span class="ch-span">{c}</span>' if c != " " else '<span class="ch-span ch-sp"> </span>'
        for c in d["perfil"]
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['nombre']} {p['apellido']} — {p['titulo']}</title>
<meta name="description" content="{p['tagline']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
/* ─── RESET & BASE ─────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg: #000000;
  --bg-card: #0e0e0e;
  --bg-card-2: #0a0a0a;
  --bg-card-3: #080808;
  --cream: #E1E0CC;
  --cream-2: #DEDBC8;
  --muted: #5a6070;
  --muted-2: #3d4451;
  --border: rgba(255,255,255,0.06);
  --border-2: rgba(255,255,255,0.04);
  --wa: rgba(37,211,102,0.85);
}}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg);
  color: var(--cream);
  font-family: 'Almarai', sans-serif;
  font-weight: 400;
  line-height: 1.6;
  overflow-x: hidden;
}}
a {{ color: inherit; text-decoration: none; }}
strong {{ color: var(--cream); font-weight: 700; }}

/* ─── NOISE OVERLAY ──────────────────────────────────────────── */
.noise-overlay {{ position: relative; }}
.noise-overlay::after {{
  content: '';
  position: absolute; inset: 0; z-index: 2;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.6; mix-blend-mode: overlay; pointer-events: none;
}}

/* ─── PULL-UP ANIMATION ─────────────────────────────────────── */
.pu-word  {{ display: inline-block; overflow: hidden; vertical-align: bottom; }}
.pu-inner {{ display: inline-block; transform: translateY(110%); opacity: 0; will-change: transform, opacity; }}
.pu-inner.in {{
  transition: transform 0.9s cubic-bezier(0.16,1,0.3,1), opacity 0.6s cubic-bezier(0.16,1,0.3,1);
  transform: translateY(0); opacity: 1;
}}

/* ─── CARDS FADE-IN ──────────────────────────────────────────── */
.cs {{
  opacity: 0;
  transform: scale(0.96) translateY(10px);
  transition: opacity 0.7s ease, transform 0.7s cubic-bezier(0.22,1,0.36,1);
}}
.cs.in {{ opacity: 1; transform: scale(1) translateY(0); }}

/* ─── CHAR REVEAL ────────────────────────────────────────────── */
.ch-span {{ opacity: 0.1; transition: opacity 0.1s; }}

/* ─── LANGUAGE BARS ──────────────────────────────────────────── */
.lbar-track {{
  height: 3px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  margin-top: 8px;
  overflow: hidden;
}}
.lbar-fill {{
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, var(--muted), var(--cream-2));
  border-radius: 99px;
  transition: width 1.4s cubic-bezier(0.22,1,0.36,1);
}}

/* ─── NAV ────────────────────────────────────────────────────── */
.nav-pill {{
  position: fixed;
  top: 0; left: 50%; transform: translateX(-50%);
  z-index: 100;
  background: #000;
  border-radius: 0 0 20px 20px;
  padding: 12px 28px;
  display: flex; gap: 28px; align-items: center;
  border: 1px solid var(--border);
  border-top: none;
}}
.nav-pill a {{
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(222,219,200,0.45);
  transition: color 0.2s;
}}
.nav-pill a:hover {{ color: var(--cream); }}

/* ─── BUTTONS ────────────────────────────────────────────────── */
.btn-cream {{
  display: inline-flex; align-items: center;
  background: var(--cream-2);
  color: #000;
  font-family: 'Almarai', sans-serif;
  font-weight: 700;
  font-size: 13px;
  border-radius: 9999px;
  padding: 10px 10px 10px 20px;
  gap: 8px;
  border: none; cursor: pointer;
  transition: gap 0.25s ease;
}}
.btn-cream:hover {{ gap: 13px; }}
.btn-cream .btn-circle {{
  width: 30px; height: 30px;
  background: #000;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}}
.btn-cream .btn-circle svg {{ width: 14px; height: 14px; }}

.btn-outline {{
  display: inline-flex; align-items: center; gap: 8px;
  border: 1.5px solid rgba(222,219,200,0.18);
  border-radius: 9999px;
  padding: 10px 20px;
  color: rgba(222,219,200,0.65);
  font-family: 'Almarai', sans-serif;
  font-weight: 400;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}}
.btn-outline:hover {{
  border-color: rgba(222,219,200,0.4);
  color: var(--cream);
}}

/* ─── SECTION LABELS ─────────────────────────────────────────── */
.section-label {{
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 32px;
  display: flex; align-items: center; gap: 12px;
}}
.section-label::before {{
  content: '';
  display: inline-block;
  width: 24px; height: 1px;
  background: var(--muted-2);
}}

/* ─── HERO ───────────────────────────────────────────────────── */
#hero {{
  min-height: 100svh;
  display: flex; flex-direction: column; justify-content: center;
  padding: 120px 5vw 80px;
  position: relative;
  overflow: hidden;
}}
.hero-glow {{
  position: absolute;
  width: 600px; height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(78,78,120,0.12) 0%, transparent 70%);
  top: -100px; right: -100px;
  pointer-events: none;
}}
.hero-name-block {{
  line-height: 0.86;
  margin-bottom: 40px;
  position: relative; z-index: 3;
}}
.hero-name-first {{
  display: block;
  font-size: clamp(34px, 7vw, 105px);
  font-weight: 300;
  color: rgba(225,224,204,0.45);
  letter-spacing: -0.02em;
}}
.hero-name-last {{
  display: block;
  font-size: clamp(62px, 17vw, 265px);
  font-weight: 800;
  color: var(--cream);
  letter-spacing: -0.055em;
  line-height: 0.86;
}}
.hero-titulo {{
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: clamp(16px, 2.5vw, 22px);
  color: rgba(222,219,200,0.55);
  margin-bottom: 12px;
  position: relative; z-index: 3;
}}
.hero-tagline {{
  font-size: clamp(13px, 1.5vw, 15px);
  color: rgba(222,219,200,0.35);
  max-width: 480px;
  line-height: 1.7;
  margin-bottom: 40px;
  position: relative; z-index: 3;
}}
.hero-ctas {{
  display: flex; gap: 12px; flex-wrap: wrap;
  position: relative; z-index: 3;
}}
.hero-metrics-row {{
  display: flex; gap: 32px; flex-wrap: wrap;
  margin-top: 64px;
  padding-top: 40px;
  border-top: 1px solid var(--border);
  position: relative; z-index: 3;
}}
.hero-metric {{
  display: flex; flex-direction: column; gap: 4px;
}}
.hero-metric-val {{
  font-size: 28px;
  font-weight: 800;
  color: var(--cream);
  letter-spacing: -0.03em;
}}
.hero-metric-label {{
  font-size: 11px;
  color: var(--muted);
  line-height: 1.4;
}}

/* ─── TRAYECTORIA ────────────────────────────────────────────── */
#trayectoria {{
  padding: 100px 5vw;
  max-width: 860px;
  margin: 0 auto;
}}
.bio-wrap {{ margin-bottom: 64px; }}
.bio-text {{
  font-size: clamp(14px, 1.8vw, 17px);
  line-height: 1.9;
  color: var(--cream-2);
  cursor: default;
}}

/* ─── ACCORDION ──────────────────────────────────────────────── */
.acc-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  margin-bottom: 12px;
  overflow: hidden;
}}
.acc-header {{
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  color: var(--cream);
}}
.acc-company-info {{ display: flex; align-items: center; gap: 16px; }}
.company-logo-wrap {{
  width: 48px; height: 48px;
  border-radius: 10px;
  background: #fff;
  display: flex; align-items: center; justify-content: center;
  padding: 5px;
  flex-shrink: 0;
  overflow: hidden;
}}
.company-logo {{ width: 100%; height: 100%; object-fit: contain; }}
.company-logo-fallback {{
  width: 100%; height: 100%;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: -0.02em;
}}
.acc-company-text {{ display: flex; flex-direction: column; gap: 3px; text-align: left; }}
.company-name {{ font-size: 15px; font-weight: 700; color: var(--cream); }}
.company-meta {{ font-size: 11px; color: var(--muted); }}
.acc-chevron {{
  width: 18px; height: 18px;
  color: var(--muted);
  flex-shrink: 0;
  transition: transform 0.4s cubic-bezier(0.22,1,0.36,1);
}}
.acc-card.open .acc-chevron {{ transform: rotate(180deg); }}
.acc-body {{ max-height: 0; overflow: hidden; transition: max-height 0.5s cubic-bezier(0.22,1,0.36,1); }}
.acc-card.open .acc-body {{ max-height: 1200px; padding-bottom: 24px; }}
.acc-body-inner {{ padding: 0 24px; }}

/* ─── ROLES ──────────────────────────────────────────────────── */
.role-block {{
  padding: 20px 0;
  border-top: 1px solid var(--border-2);
}}
.role-block:first-child {{ border-top: none; }}
.role-header {{
  display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px;
  margin-bottom: 12px;
}}
.role-title {{ font-size: 14px; font-weight: 700; color: var(--cream); }}
.role-tag {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 7px;
}}
.role-period {{
  font-size: 11px;
  color: var(--muted);
  margin-left: auto;
  white-space: nowrap;
}}
.metrics-row {{
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 14px;
}}
.metric-card {{
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 10px 14px;
  min-width: 90px;
}}
.metric-num {{ font-size: 14px; font-weight: 800; color: var(--cream); line-height: 1; }}
.metric-label {{ font-size: 9px; color: var(--muted); margin-top: 4px; line-height: 1.3; }}
.logros-list {{
  list-style: none;
  display: flex; flex-direction: column; gap: 8px;
}}
.logros-list li {{
  font-size: 13px;
  color: rgba(222,219,200,0.7);
  padding-left: 16px;
  position: relative;
  line-height: 1.7;
}}
.logros-list li::before {{
  content: '–';
  position: absolute; left: 0;
  color: var(--muted-2);
}}
.skills-row {{
  display: flex; flex-wrap: wrap; gap: 6px;
  margin-top: 16px;
}}
.skill-tag {{
  font-size: 10px;
  font-weight: 700;
  color: var(--muted);
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 10px;
  letter-spacing: 0.04em;
}}

/* ─── COMPETENCIAS ───────────────────────────────────────────── */
#competencias {{ padding: 100px 5vw; }}
#competencias .section-inner {{ max-width: 860px; margin: 0 auto; }}
.comp-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}}
.comp-card {{
  background: var(--bg-card-2);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 24px;
}}
.comp-num {{
  font-size: 10px;
  color: var(--muted-2);
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}}
.comp-emoji {{ font-size: 24px; margin-bottom: 12px; }}
.comp-title {{
  font-size: 14px;
  font-weight: 800;
  color: var(--cream);
  margin-bottom: 16px;
}}
.comp-items {{
  list-style: none;
  display: flex; flex-direction: column; gap: 6px;
}}
.comp-items li {{
  font-size: 12px;
  color: rgba(222,219,200,0.55);
  padding-left: 12px;
  position: relative;
  line-height: 1.5;
}}
.comp-items li::before {{
  content: '·';
  position: absolute; left: 0;
  color: var(--muted-2);
}}

/* ─── FORMACIÓN ──────────────────────────────────────────────── */
#formacion {{ padding: 100px 5vw; }}
#formacion .section-inner {{ max-width: 860px; margin: 0 auto; }}
.formacion-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}}
@media (max-width: 640px) {{
  .formacion-grid {{ grid-template-columns: 1fr; }}
  .comp-grid {{ grid-template-columns: 1fr 1fr; }}
}}
.formacion-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
}}
.formacion-card-title {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 20px;
}}
.edu-item {{
  display: flex; gap: 16px; align-items: flex-start;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-2);
}}
.edu-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
.edu-siglas {{
  width: 40px; height: 40px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 800; color: var(--muted);
  flex-shrink: 0;
}}
.edu-nivel {{ font-size: 10px; color: var(--muted); margin-bottom: 3px; }}
.edu-titulo {{ font-size: 13px; font-weight: 700; color: var(--cream); margin-bottom: 3px; }}
.edu-inst {{ font-size: 11px; color: rgba(222,219,200,0.4); }}
.cert-item {{
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-2);
}}
.cert-item:last-child {{ border-bottom: none; }}
.cert-info {{ display: flex; flex-direction: column; gap: 2px; }}
.cert-nombre {{ font-size: 11px; font-weight: 700; color: var(--cream-2); line-height: 1.4; }}
.cert-entidad {{ font-size: 10px; color: var(--muted); }}
.cert-badge {{
  font-size: 9px;
  font-weight: 700;
  border-radius: 6px;
  padding: 3px 8px;
  white-space: nowrap;
  flex-shrink: 0;
}}
.cert-badge--ok {{ background: rgba(34,197,94,0.1); color: #4ade80; }}
.cert-badge--curso {{ background: rgba(250,204,21,0.1); color: #fbbf24; }}
.lang-item {{ padding: 12px 0; border-bottom: 1px solid var(--border-2); }}
.lang-item:last-child {{ border-bottom: none; }}
.lang-top {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }}
.lang-nombre {{ font-size: 13px; font-weight: 700; color: var(--cream); }}
.lang-nivel {{ font-size: 11px; color: var(--muted); }}
.lang-nota {{ font-size: 10px; color: rgba(222,219,200,0.35); display: block; margin-bottom: 4px; }}
.wa-card {{
  margin-top: 16px;
  background: rgba(37,211,102,0.06);
  border: 1px solid rgba(37,211,102,0.15);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex; align-items: center; gap: 16px;
}}
.wa-icon {{ font-size: 22px; }}
.wa-text {{ flex: 1; }}
.wa-text-label {{ font-size: 10px; color: rgba(37,211,102,0.6); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }}
.wa-text-num {{ font-size: 15px; font-weight: 700; color: rgba(37,211,102,0.9); }}
.wa-btn {{
  background: rgba(37,211,102,0.12);
  border: 1px solid rgba(37,211,102,0.25);
  border-radius: 9999px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(37,211,102,0.85);
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}}
.wa-btn:hover {{ background: rgba(37,211,102,0.2); }}

/* ─── PROYECTOS ──────────────────────────────────────────────── */
#proyectos {{ padding: 100px 5vw; }}
#proyectos .section-inner {{ max-width: 860px; margin: 0 auto; }}
.proj-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}}
.proj-card {{
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 32px 28px;
  display: flex; flex-direction: column; gap: 12px;
}}
.proj-num {{ font-size: 10px; color: rgba(222,219,200,0.25); font-weight: 700; letter-spacing: 0.1em; }}
.proj-emoji {{ font-size: 28px; }}
.proj-title {{ font-size: 15px; font-weight: 800; color: var(--cream); line-height: 1.3; }}
.proj-desc {{ font-size: 12px; color: rgba(222,219,200,0.5); line-height: 1.7; flex: 1; }}
.proj-footer {{ display: flex; flex-direction: column; gap: 10px; margin-top: auto; }}
.proj-status {{
  font-size: 10px;
  font-weight: 700;
  border-radius: 6px;
  padding: 4px 10px;
  align-self: flex-start;
}}
.proj-status--wip {{ background: rgba(251,191,36,0.1); color: #fbbf24; }}
.proj-status--soon {{ background: rgba(255,255,255,0.05); color: var(--muted); }}

/* ─── CONTACTO ───────────────────────────────────────────────── */
#contacto {{
  padding: 120px 5vw 100px;
  text-align: center;
  position: relative;
  overflow: hidden;
}}
.contacto-glow {{
  position: absolute;
  width: 700px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(60,60,100,0.15) 0%, transparent 70%);
  bottom: -100px; left: 50%; transform: translateX(-50%);
  pointer-events: none;
}}
.contacto-title {{
  font-size: clamp(52px, 12vw, 140px);
  font-weight: 800;
  color: var(--cream);
  letter-spacing: -0.05em;
  line-height: 0.9;
  margin-bottom: 24px;
  position: relative; z-index: 3;
}}
.contacto-sub {{
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: clamp(16px, 2vw, 20px);
  color: rgba(222,219,200,0.45);
  margin-bottom: 48px;
  position: relative; z-index: 3;
}}
.contacto-links {{
  display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;
  position: relative; z-index: 3;
}}
.contact-link {{
  display: inline-flex; align-items: center; gap: 8px;
  border: 1px solid var(--border);
  border-radius: 9999px;
  padding: 12px 22px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(222,219,200,0.55);
  letter-spacing: 0.06em;
  transition: border-color 0.2s, color 0.2s;
}}
.contact-link:hover {{ border-color: rgba(222,219,200,0.3); color: var(--cream); }}
.contact-link svg {{ width: 14px; height: 14px; }}
.wa-contact-link {{
  border-color: rgba(37,211,102,0.2);
  color: rgba(37,211,102,0.7);
}}
.wa-contact-link:hover {{
  border-color: rgba(37,211,102,0.5);
  color: rgba(37,211,102,0.95);
}}
.footer-note {{
  margin-top: 80px;
  font-size: 10px;
  color: var(--muted-2);
  letter-spacing: 0.1em;
  position: relative; z-index: 3;
}}

/* ─── RESPONSIVE ─────────────────────────────────────────────── */
@media (max-width: 480px) {{
  .nav-pill {{ gap: 16px; padding: 10px 16px; }}
  .formacion-grid {{ grid-template-columns: 1fr; }}
  .hero-metrics-row {{ gap: 20px; }}
}}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav-pill">
  <a href="#trayectoria">Trayectoria</a>
  <a href="#competencias">Skills</a>
  <a href="#formacion">Formación</a>
  <a href="#proyectos">Proyectos</a>
  <a href="#contacto">Contacto</a>
</nav>

<!-- HERO -->
<section id="hero" class="noise-overlay">
  <div class="hero-glow"></div>

  <div class="hero-name-block">
    <span class="hero-name-first pu-word"><span class="pu-inner">{p['nombre']}</span></span>
    <br>
    <span class="hero-name-last pu-word"><span class="pu-inner">{p['apellido']}</span></span>
  </div>

  <p class="hero-titulo pu-word"><span class="pu-inner">{p['titulo']}</span></p>
  <p class="hero-tagline">{p['tagline']}</p>

  <div class="hero-ctas">
    <a href="#contacto" class="btn-cream">
      Contactar
      <span class="btn-circle">
        <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M2 12L12 2M12 2H6M12 2v6"/>
        </svg>
      </span>
    </a>
    <a href="Carlo Rondon CV.docx" download class="btn-outline">
      <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px">
        <path d="M7 1v8M4 6l3 3 3-3M2 11h10"/>
      </svg>
      Descargar CV
    </a>
    <a href="{p['whatsapp_link']}" target="_blank" class="btn-outline" style="border-color:rgba(37,211,102,0.2);color:rgba(37,211,102,0.7)">
      <svg viewBox="0 0 14 14" fill="currentColor" style="width:13px;height:13px">
        <path d="M7 0C3.13 0 0 3.13 0 7c0 1.23.32 2.39.88 3.39L0 14l3.7-.86A6.96 6.96 0 007 14c3.87 0 7-3.13 7-7s-3.13-7-7-7zm3.56 9.72c-.15.42-1.46.82-1.78.82-.07 0-.13 0-.2-.02-.32-.05-1.47-.58-2.47-1.43a7.2 7.2 0 01-1.63-2.16c-.28-.63-.09-1.08.05-1.31.14-.24.34-.44.52-.6.16-.13.22-.15.32-.15.09 0 .32.09.47.42l.6 1.34c.07.16.03.22-.03.32l-.22.28c-.07.09-.15.19-.06.37.09.18.41.74.9 1.2.5.47 1.07.72 1.25.8.18.08.29.07.39-.04l.28-.32c.11-.13.19-.11.32-.06l1.3.61c.32.15.32.3.23.73z"/>
      </svg>
      WhatsApp
    </a>
  </div>

  <div class="hero-metrics-row">
    {hero_metrics}
  </div>
</section>

<!-- TRAYECTORIA -->
<section id="trayectoria">
  <p class="section-label">Trayectoria profesional</p>
  <div class="bio-wrap">
    <p class="bio-text" id="bio-text">{perfil_chars}</p>
  </div>

  <!-- Accordions -->
  <div id="accordion-list">
    {accordions}
  </div>
</section>

<!-- COMPETENCIAS -->
<section id="competencias">
  <div class="section-inner">
    <p class="section-label">Competencias</p>
    <div class="comp-grid">
      {comps}
    </div>
  </div>
</section>

<!-- FORMACIÓN -->
<section id="formacion">
  <div class="section-inner">
    <p class="section-label">Formación & Certificaciones</p>
    <div class="formacion-grid">

      <!-- Educación + Certifs -->
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div class="formacion-card">
          <p class="formacion-card-title">Educación</p>
          {edu}
        </div>
        <div class="formacion-card">
          <p class="formacion-card-title">Certificaciones</p>
          {certs}
        </div>
      </div>

      <!-- Idiomas + WhatsApp -->
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div class="formacion-card">
          <p class="formacion-card-title">Idiomas</p>
          {idiomas}
        </div>
        <a href="{p['whatsapp_link']}" target="_blank" class="wa-card" style="text-decoration:none;">
          <div class="wa-icon">💬</div>
          <div class="wa-text">
            <div class="wa-text-label">WhatsApp directo</div>
            <div class="wa-text-num">{p['whatsapp']}</div>
          </div>
          <div class="wa-btn">Escribir</div>
        </a>
      </div>

    </div>
  </div>
</section>

<!-- PROYECTOS -->
<section id="proyectos">
  <div class="section-inner">
    <p class="section-label">Proyectos de datos</p>
    <div class="proj-grid">
      {proyectos}
    </div>
  </div>
</section>

<!-- CONTACTO -->
<section id="contacto" class="noise-overlay">
  <div class="contacto-glow"></div>
  <p class="section-label" style="justify-content:center">Contacto</p>
  <h2 class="contacto-title">Hablemos.</h2>
  <p class="contacto-sub">Disponible para oportunidades en banca, fintech y datos.</p>
  <div class="contacto-links">
    <a href="mailto:{p['email']}" class="contact-link">
      <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="1" y="3" width="12" height="9" rx="2"/>
        <path d="M1 5l6 4 6-4"/>
      </svg>
      {p['email']}
    </a>
    <a href="{p['whatsapp_link']}" target="_blank" class="contact-link wa-contact-link">
      <svg viewBox="0 0 14 14" fill="currentColor" style="width:14px;height:14px">
        <path d="M7 0C3.13 0 0 3.13 0 7c0 1.23.32 2.39.88 3.39L0 14l3.7-.86A6.96 6.96 0 007 14c3.87 0 7-3.13 7-7s-3.13-7-7-7zm3.56 9.72c-.15.42-1.46.82-1.78.82-.07 0-.13 0-.2-.02-.32-.05-1.47-.58-2.47-1.43a7.2 7.2 0 01-1.63-2.16c-.28-.63-.09-1.08.05-1.31.14-.24.34-.44.52-.6.16-.13.22-.15.32-.15.09 0 .32.09.47.42l.6 1.34c.07.16.03.22-.03.32l-.22.28c-.07.09-.15.19-.06.37.09.18.41.74.9 1.2.5.47 1.07.72 1.25.8.18.08.29.07.39-.04l.28-.32c.11-.13.19-.11.32-.06l1.3.61c.32.15.32.3.23.73z"/>
      </svg>
      {p['whatsapp']}
    </a>
    <a href="{p['linkedin']}" target="_blank" class="contact-link">
      <svg viewBox="0 0 14 14" fill="currentColor" style="width:14px;height:14px">
        <path d="M12.6 0H1.4C.63 0 0 .63 0 1.4v11.2C0 13.37.63 14 1.4 14h11.2c.77 0 1.4-.63 1.4-1.4V1.4C14 .63 13.37 0 12.6 0zM4.2 11.9H2.1V5.25h2.1V11.9zM3.15 4.34a1.22 1.22 0 110-2.44 1.22 1.22 0 010 2.44zM11.9 11.9H9.8V8.68c0-.78-.01-1.79-1.09-1.79-1.09 0-1.26.85-1.26 1.73V11.9H5.35V5.25h2.01v.92h.03c.28-.53.96-1.09 1.98-1.09 2.12 0 2.51 1.4 2.51 3.21V11.9z"/>
      </svg>
      LinkedIn
    </a>
    <a href="Carlo Rondon CV.docx" download class="contact-link">
      <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" style="width:14px;height:14px">
        <path d="M7 1v8M4 6l3 3 3-3M2 11h10"/>
      </svg>
      Descargar CV
    </a>
  </div>
  <p class="footer-note">{p['ubicacion']} · {p['email']}</p>
</section>

<script>
// ─── PULL-UP WORDS ON LOAD ─────────────────────────────────────
(function () {{
  const els = document.querySelectorAll('.pu-inner');
  els.forEach((el, i) => {{
    setTimeout(() => el.classList.add('in'), 120 + i * 90);
  }});
}})();

// ─── INTERSECTION OBSERVER HELPER ─────────────────────────────
function onVisible(selector, callback, threshold = 0.15) {{
  const obs = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        callback(entry.target);
        obs.unobserve(entry.target);
      }}
    }});
  }}, {{ threshold }});
  document.querySelectorAll(selector).forEach(el => obs.observe(el));
}}

// ─── CARDS FADE-IN STAGGER ─────────────────────────────────────
onVisible('.cs', el => {{
  const idx = parseInt(el.dataset.delayIdx || 0);
  setTimeout(() => el.classList.add('in'), idx * 130);
}});

// ─── LANGUAGE BARS ─────────────────────────────────────────────
onVisible('.lbar-fill', el => {{
  const w = el.dataset.w;
  setTimeout(() => el.style.width = w + '%', 200);
}}, 0.3);

// ─── CHAR REVEAL ON SCROLL ────────────────────────────────────
(function () {{
  const container = document.getElementById('bio-text');
  if (!container) return;
  const spans = container.querySelectorAll('.ch-span');

  function update() {{
    const rect = container.getBoundingClientRect();
    const vh = window.innerHeight;
    const progress = 1 - (rect.top / vh);
    const ratio = Math.max(0, Math.min(1, progress * 1.4 - 0.2));
    const active = Math.floor(ratio * spans.length);
    spans.forEach((s, i) => {{
      s.style.opacity = i < active ? '1' : '0.1';
    }});
  }}
  window.addEventListener('scroll', update, {{ passive: true }});
  update();
}})();

// ─── ACCORDION ────────────────────────────────────────────────
function toggleAcc(btn) {{
  const card = btn.closest('.acc-card');
  card.classList.toggle('open');
}}
</script>
</body>
</html>"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"[OK] carlo-rondon.html generado ({OUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(load())

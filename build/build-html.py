"""
build-html.py — Genera carlo-rondon.html bilingüe (EN default / ES) desde data.json
Cada texto lleva data-en / data-es y un runtime JS intercambia el idioma en vivo.
Ejecutar desde la raíz del proyecto: python build/build-html.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data.json"
OUT_PATH = ROOT / "carlo-rondon.html"

# Nombres de archivo del CV descargable por idioma
DOCX_EN = "Carlo Rondon CV.docx"
DOCX_ES = "Carlo Rondon CV ES.docx"

# ─── Strings de interfaz (chrome), bilingües ───────────────────
UI = {
    "nav_trayectoria":  {"en": "Experience",   "es": "Trayectoria"},
    "nav_skills":       {"en": "Skills",        "es": "Skills"},
    "nav_formacion":    {"en": "Education",     "es": "Formación"},
    "nav_proyectos":    {"en": "Projects",      "es": "Proyectos"},
    "nav_contacto":     {"en": "Contact",       "es": "Contacto"},
    "label_trayectoria":{"en": "Professional experience", "es": "Trayectoria profesional"},
    "label_competencias":{"en": "Skills",       "es": "Competencias"},
    "label_formacion":  {"en": "Education & Certifications", "es": "Formación & Certificaciones"},
    "label_portafolio": {"en": "Portfolio",     "es": "Portafolio"},
    "label_contacto":   {"en": "Contact",       "es": "Contacto"},
    "edu_title":        {"en": "Education",      "es": "Educación"},
    "cert_title":       {"en": "Certifications", "es": "Certificaciones"},
    "lang_title":       {"en": "Languages",      "es": "Idiomas"},
    "wa_label":         {"en": "Direct WhatsApp","es": "WhatsApp directo"},
    "wa_btn":           {"en": "Message",        "es": "Escribir"},
    "download_cv":      {"en": "Download CV",    "es": "Descargar CV"},
    "contacto_title":   {"en": "Let's talk.",    "es": "Hablemos."},
    "contacto_sub":     {"en": "Open to payments and fintech leadership roles across Latin America.",
                         "es": "Abierto a roles de liderazgo en payments y fintech en Latinoamérica."},
    "cert_badge_curso": {"en": "In progress",    "es": "En curso"},
    "proj_wip":         {"en": "Under construction", "es": "En construcción"},
    "proj_soon":        {"en": "Coming soon",    "es": "Próximamente"},
    "proj_live":        {"en": "Live",           "es": "Live"},
    "proj_link":        {"en": "View project ↗", "es": "Ver proyecto ↗"},
}


def load():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


# ─── Helpers de idioma ─────────────────────────────────────────
def EN(v):
    return v["en"] if isinstance(v, dict) and "en" in v else v

def ES(v):
    return v["es"] if isinstance(v, dict) and "es" in v else v

def esc_attr(s):
    return str(s).replace("&", "&amp;").replace('"', "&quot;")

def esc_text(s):
    return str(s).replace("&", "&amp;")

def bold_md(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

def attrs(en_html, es_html):
    """Atributos data-en / data-es (contenido HTML permitido)."""
    return f'data-en="{esc_attr(en_html)}" data-es="{esc_attr(es_html)}"'

def node(v, cls="", tag="span", extra=""):
    """Elemento de texto bilingüe simple (contenido de texto plano)."""
    en, es = EN(v), ES(v)
    c = f'class="{cls}" ' if cls else ""
    x = f" {extra}" if extra else ""
    return f'<{tag} {c}{attrs(en, es)}{x}>{esc_text(en)}</{tag}>'

def ui(key, cls="", tag="span", extra=""):
    return node(UI[key], cls=cls, tag=tag, extra=extra)


# ─── Render de secciones ───────────────────────────────────────
def render_metrics(metrics):
    if not metrics:
        return ""
    items = ""
    for m in metrics:
        v, l = m["valor"], m["label"]
        items += f"""
        <div class="metric-card">
          <div class="metric-num" {attrs(EN(v), ES(v))}>{esc_text(EN(v))}</div>
          <div class="metric-label" {attrs(EN(l), ES(l))}>{esc_text(EN(l))}</div>
        </div>"""
    return f'<div class="metrics-row">{items}\n        </div>'


def render_role(role):
    metrics_html = render_metrics(role["metricas"])
    logros_html = ""
    for logro in role["logros"]:
        en = bold_md(EN(logro))
        es = bold_md(ES(logro))
        logros_html += f'<li {attrs(en, es)}>{esc_text(en)}</li>\n'

    tag = role.get("tag")
    tag_html = ""
    if tag:
        tag_html = f'<span class="role-tag" {attrs(EN(tag), ES(tag))}>{esc_text(EN(tag))}</span>'

    tit, per = role["titulo"], role["periodo"]
    return f"""
        <div class="role-block">
          <div class="role-header">
            <span class="role-title" {attrs(EN(tit), ES(tit))}>{esc_text(EN(tit))}</span>
            {tag_html}
            <span class="role-period" {attrs(EN(per), ES(per))}>{esc_text(EN(per))}</span>
          </div>
          {metrics_html}
          <ul class="logros-list">
            {logros_html}
          </ul>
        </div>"""


def render_skills(skills):
    if not skills:
        return ""
    tags = "".join(
        f'<span class="skill-tag" {attrs(EN(s), ES(s))}>{esc_text(EN(s))}</span>'
        for s in skills
    )
    return f'<div class="skills-row">{tags}</div>'


def render_accordion(exp, idx):
    is_open = "open" if idx == 0 else ""
    roles_html = "".join(render_role(r) for r in exp["roles"])
    skills_html = render_skills(exp["skills"])

    emp = exp["empresa"]
    per, dur = exp["periodo"], exp["duracion"]
    en_meta = f"{EN(per)} · {EN(dur)}"
    es_meta = f"{ES(per)} · {ES(dur)}"

    logo_html = f"""<img src="{exp['logo_url']}" alt="{esc_attr(EN(emp))}" class="company-logo"
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
              <span class="company-name" {attrs(EN(emp), ES(emp))}>{esc_text(EN(emp))}</span>
              <span class="company-meta" {attrs(en_meta, es_meta)}>{esc_text(en_meta)}</span>
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
        items_html = "".join(
            f'<li {attrs(EN(item), ES(item))}>{esc_text(EN(item))}</li>'
            for item in c["items"]
        )
        t = c["titulo"]
        html += f"""
      <div class="comp-card cs" data-delay-idx="{i}">
        <div class="comp-num">{c['numero']}</div>
        <div class="comp-emoji">{c['emoji']}</div>
        <h3 class="comp-title" {attrs(EN(t), ES(t))}>{esc_text(EN(t))}</h3>
        <ul class="comp-items">{items_html}</ul>
      </div>"""
    return html


def render_educacion(edu_list):
    html = ""
    for e in edu_list:
        niv, tit, inst = e["nivel"], e["titulo"], e["institucion"]
        html += f"""
          <div class="edu-item">
            <div class="edu-siglas">{e['siglas']}</div>
            <div class="edu-text">
              <div class="edu-nivel" {attrs(EN(niv), ES(niv))}>{esc_text(EN(niv))}</div>
              <div class="edu-titulo" {attrs(EN(tit), ES(tit))}>{esc_text(EN(tit))}</div>
              <div class="edu-inst" {attrs(EN(inst), ES(inst))}>{esc_text(EN(inst))}</div>
            </div>
          </div>"""
    return html


def render_certificaciones(certs):
    html = ""
    for c in certs:
        if c["estado"] == "en_curso":
            b = UI["cert_badge_curso"]
            badge = f'<span class="cert-badge cert-badge--curso" {attrs(EN(b), ES(b))}>{esc_text(EN(b))}</span>'
        else:
            badge = '<span class="cert-badge cert-badge--ok">✓</span>'
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
        nom, niv = lang["nombre"], lang["nivel"]
        nota_html = ""
        if lang.get("nota"):
            n = lang["nota"]
            nota_html = f'<span class="lang-nota" {attrs(EN(n), ES(n))}>{esc_text(EN(n))}</span>'
        html += f"""
          <div class="lang-item">
            <div class="lang-top">
              <span class="lang-nombre" {attrs(EN(nom), ES(nom))}>{esc_text(EN(nom))}</span>
              <span class="lang-nivel" {attrs(EN(niv), ES(niv))}>{esc_text(EN(niv))}</span>
            </div>
            {nota_html}
            <div class="lbar-track">
              <div class="lbar-fill" data-w="{lang['porcentaje']}"></div>
            </div>
          </div>"""
    return html


def render_proyectos(proyectos):
    estado_map = {"en_construccion": ("proj_wip", "proj-status--wip"),
                  "proximamente":    ("proj_soon", "proj-status--soon"),
                  "activo":          ("proj_live", "proj-status--live")}
    html = ""
    for p in proyectos:
        key, cls = estado_map.get(p["estado"], ("proj_soon", "proj-status--soon"))
        u = UI[key]
        estado_html = f'<span class="proj-status {cls}" {attrs(EN(u), ES(u))}>{esc_text(EN(u))}</span>'

        skills_html = "".join(
            f'<span class="skill-tag" {attrs(EN(s), ES(s))}>{esc_text(EN(s))}</span>'
            for s in p["skills"]
        )
        link_html = ""
        if p.get("link"):
            pl = UI["proj_link"]
            link_html = (f'<a href="{p["link"]}" target="_blank" class="proj-link" '
                         f'{attrs(EN(pl), ES(pl))}>{esc_text(EN(pl))}</a>')

        t, d = p["titulo"], p["descripcion"]
        html += f"""
      <div class="proj-card cs" data-delay-idx="{p['numero']}" style="background:{p['gradient']}">
        <div class="proj-num">{p['numero']}</div>
        <div class="proj-emoji">{p['emoji']}</div>
        <h3 class="proj-title" {attrs(EN(t), ES(t))}>{esc_text(EN(t))}</h3>
        <p class="proj-desc" {attrs(EN(d), ES(d))}>{esc_text(EN(d))}</p>
        <div class="proj-footer">
          <div class="skills-row">{skills_html}</div>
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
            {estado_html}
            {link_html}
          </div>
        </div>
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

    titulo, tagline, perfil = p["titulo"], p["tagline"], d["perfil"]
    ubic = p["ubicacion"]

    # meta title/desc por idioma
    meta = {
        "en": {"title": f"{p['nombre']} {p['apellido']} — {EN(titulo)}", "desc": EN(tagline)},
        "es": {"title": f"{p['nombre']} {p['apellido']} — {ES(titulo)}", "desc": ES(tagline)},
    }
    meta_json = json.dumps(meta, ensure_ascii=False)

    dl = f'data-href-en="{DOCX_EN}" data-href-es="{DOCX_ES}"'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta['en']['title']}</title>
<meta name="description" content="{esc_attr(meta['en']['desc'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&family=Instrument+Serif:ital@1&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
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

.noise-overlay {{ position: relative; }}
.noise-overlay::after {{
  content: '';
  position: absolute; inset: 0; z-index: 2;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.6; mix-blend-mode: overlay; pointer-events: none;
}}

.pu-word  {{ display: inline-block; overflow: hidden; vertical-align: bottom; }}
.pu-inner {{ display: inline-block; transform: translateY(110%); opacity: 0; will-change: transform, opacity; }}
.pu-inner.in {{
  transition: transform 0.9s cubic-bezier(0.16,1,0.3,1), opacity 0.6s cubic-bezier(0.16,1,0.3,1);
  transform: translateY(0); opacity: 1;
}}

.cs {{
  opacity: 0;
  transform: scale(0.96) translateY(10px);
  transition: opacity 0.7s ease, transform 0.7s cubic-bezier(0.22,1,0.36,1);
}}
.cs.in {{ opacity: 1; transform: scale(1) translateY(0); }}

.ch-span {{ opacity: 0.1; transition: opacity 0.1s; }}

.lbar-track {{
  height: 3px; background: rgba(255,255,255,0.06);
  border-radius: 99px; margin-top: 8px; overflow: hidden;
}}
.lbar-fill {{
  height: 100%; width: 0;
  background: linear-gradient(90deg, var(--muted), var(--cream-2));
  border-radius: 99px;
  transition: width 1.4s cubic-bezier(0.22,1,0.36,1);
}}

/* ─── NAV ─── */
.nav-pill {{
  position: fixed;
  top: 0; left: 50%; transform: translateX(-50%);
  z-index: 100;
  background: #000;
  border-radius: 0 0 20px 20px;
  padding: 10px 20px;
  display: flex; gap: 22px; align-items: center;
  border: 1px solid var(--border);
  border-top: none;
}}
.nav-pill a {{
  font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: rgba(222,219,200,0.45);
  transition: color 0.2s;
}}
.nav-pill a:hover {{ color: var(--cream); }}
.lang-switch {{
  display: flex; gap: 2px; margin-left: 4px;
  border: 1px solid var(--border); border-radius: 9999px; padding: 2px;
}}
.lang-btn {{
  background: none; border: none; cursor: pointer;
  font-family: 'Almarai', sans-serif; font-size: 10px; font-weight: 700;
  letter-spacing: 0.06em; color: rgba(222,219,200,0.4);
  padding: 4px 9px; border-radius: 9999px; transition: background 0.2s, color 0.2s;
}}
.lang-btn.active {{ background: var(--cream-2); color: #000; }}
.lang-btn:hover:not(.active) {{ color: var(--cream); }}

.section-label {{
  font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--muted); font-weight: 700; margin-bottom: 32px;
  display: flex; align-items: center; gap: 12px;
}}
.section-label::before {{
  content: ''; display: inline-block; width: 24px; height: 1px; background: var(--muted-2);
}}

/* ─── HERO ─── */
#hero {{
  min-height: 100svh;
  display: flex; flex-direction: column; justify-content: center;
  padding: 120px 5vw 80px; position: relative; overflow: hidden;
}}
.hero-glow {{
  position: absolute; width: 600px; height: 600px; border-radius: 50%;
  background: radial-gradient(circle, rgba(78,78,120,0.12) 0%, transparent 70%);
  top: -100px; right: -100px; pointer-events: none;
}}
.hero-name-block {{ line-height: 0.86; margin-bottom: 40px; position: relative; z-index: 3; }}
.hero-name-first {{
  display: block; font-size: clamp(30px, 6vw, 92px); font-weight: 300;
  color: rgba(225,224,204,0.45); letter-spacing: -0.02em;
}}
.hero-name-last {{
  display: block; font-size: clamp(54px, 14.5vw, 220px); font-weight: 800;
  color: var(--cream); letter-spacing: -0.055em; line-height: 0.86;
}}
.hero-titulo {{
  font-family: 'Almarai', sans-serif; font-weight: 400;
  font-size: clamp(12px, 1.4vw, 15px); color: rgba(222,219,200,0.45);
  letter-spacing: 0.06em; margin-bottom: 20px; position: relative; z-index: 3;
}}
.hero-tagline {{
  font-size: clamp(13px, 1.5vw, 15px); color: rgba(222,219,200,0.35);
  max-width: 480px; line-height: 1.7; margin-bottom: 40px;
  position: relative; z-index: 3;
}}

/* ─── TRAYECTORIA ─── */
#trayectoria {{ padding: 100px 5vw; max-width: 860px; margin: 0 auto; }}
.bio-wrap {{ margin-bottom: 64px; }}
.bio-text {{ font-size: clamp(14px, 1.8vw, 17px); line-height: 1.9; color: var(--cream-2); cursor: default; }}

/* ─── ACCORDION ─── */
.acc-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; margin-bottom: 12px; overflow: hidden; }}
.acc-header {{ width: 100%; background: none; border: none; cursor: pointer; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; color: var(--cream); }}
.acc-company-info {{ display: flex; align-items: center; gap: 16px; }}
.company-logo-wrap {{ width: 48px; height: 48px; border-radius: 10px; background: #fff; display: flex; align-items: center; justify-content: center; padding: 5px; flex-shrink: 0; overflow: hidden; }}
.company-logo {{ width: 100%; height: 100%; object-fit: contain; }}
.company-logo-fallback {{ width: 100%; height: 100%; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; letter-spacing: -0.02em; }}
.acc-company-text {{ display: flex; flex-direction: column; gap: 3px; text-align: left; }}
.company-name {{ font-size: 15px; font-weight: 700; color: var(--cream); }}
.company-meta {{ font-size: 11px; color: var(--muted); }}
.acc-chevron {{ width: 18px; height: 18px; color: var(--muted); flex-shrink: 0; transition: transform 0.4s cubic-bezier(0.22,1,0.36,1); }}
.acc-card.open .acc-chevron {{ transform: rotate(180deg); }}
.acc-body {{ max-height: 0; overflow: hidden; transition: max-height 0.5s cubic-bezier(0.22,1,0.36,1); }}
.acc-card.open .acc-body {{ max-height: 1400px; padding-bottom: 24px; }}
.acc-body-inner {{ padding: 0 24px; }}

.role-block {{ padding: 20px 0; border-top: 1px solid var(--border-2); }}
.role-block:first-child {{ border-top: none; }}
.role-header {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }}
.role-title {{ font-size: 14px; font-weight: 700; color: var(--cream); }}
.role-tag {{ font-size: 10px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); background: rgba(255,255,255,0.05); border: 1px solid var(--border); border-radius: 4px; padding: 2px 7px; }}
.role-period {{ font-size: 11px; color: var(--muted); margin-left: auto; white-space: nowrap; }}
.metrics-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }}
.metric-card {{ background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 10px 14px; min-width: 90px; }}
.metric-num {{ font-size: 14px; font-weight: 800; color: var(--cream); line-height: 1; }}
.metric-label {{ font-size: 9px; color: var(--muted); margin-top: 4px; line-height: 1.3; }}
.logros-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
.logros-list li {{ font-size: 13px; color: rgba(222,219,200,0.7); padding-left: 16px; position: relative; line-height: 1.7; }}
.logros-list li::before {{ content: '–'; position: absolute; left: 0; color: var(--muted-2); }}
.skills-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 16px; }}
.skill-tag {{ font-size: 10px; font-weight: 700; color: var(--muted); background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 6px; padding: 4px 10px; letter-spacing: 0.04em; }}

/* ─── COMPETENCIAS ─── */
#competencias {{ padding: 100px 5vw; }}
#competencias .section-inner {{ max-width: 860px; margin: 0 auto; }}
.comp-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
.comp-card {{ background: var(--bg-card-2); border: 1px solid var(--border); border-radius: 16px; padding: 28px 24px; }}
.comp-num {{ font-size: 10px; color: var(--muted-2); font-weight: 700; letter-spacing: 0.1em; margin-bottom: 12px; }}
.comp-emoji {{ font-size: 24px; margin-bottom: 12px; }}
.comp-title {{ font-size: 14px; font-weight: 800; color: var(--cream); margin-bottom: 16px; }}
.comp-items {{ list-style: none; display: flex; flex-direction: column; gap: 6px; }}
.comp-items li {{ font-size: 12px; color: rgba(222,219,200,0.55); padding-left: 12px; position: relative; line-height: 1.5; }}
.comp-items li::before {{ content: '·'; position: absolute; left: 0; color: var(--muted-2); }}

/* ─── FORMACIÓN ─── */
#formacion {{ padding: 100px 5vw; }}
#formacion .section-inner {{ max-width: 860px; margin: 0 auto; }}
.formacion-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
@media (max-width: 640px) {{ .formacion-grid {{ grid-template-columns: 1fr; }} .comp-grid {{ grid-template-columns: 1fr 1fr; }} }}
.formacion-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 28px; }}
.formacion-card-title {{ font-size: 10px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 20px; }}
.edu-item {{ display: flex; gap: 16px; align-items: flex-start; padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid var(--border-2); }}
.edu-item:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
.edu-siglas {{ width: 40px; height: 40px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: var(--muted); flex-shrink: 0; }}
.edu-nivel {{ font-size: 10px; color: var(--muted); margin-bottom: 3px; }}
.edu-titulo {{ font-size: 13px; font-weight: 700; color: var(--cream); margin-bottom: 3px; }}
.edu-inst {{ font-size: 11px; color: rgba(222,219,200,0.4); }}
.cert-item {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-2); }}
.cert-item:last-child {{ border-bottom: none; }}
.cert-info {{ display: flex; flex-direction: column; gap: 2px; }}
.cert-nombre {{ font-size: 11px; font-weight: 700; color: var(--cream-2); line-height: 1.4; }}
.cert-entidad {{ font-size: 10px; color: var(--muted); }}
.cert-badge {{ font-size: 9px; font-weight: 700; border-radius: 6px; padding: 3px 8px; white-space: nowrap; flex-shrink: 0; }}
.cert-badge--ok {{ background: rgba(34,197,94,0.1); color: #4ade80; }}
.cert-badge--curso {{ background: rgba(250,204,21,0.1); color: #fbbf24; }}
.lang-item {{ padding: 12px 0; border-bottom: 1px solid var(--border-2); }}
.lang-item:last-child {{ border-bottom: none; }}
.lang-top {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }}
.lang-nombre {{ font-size: 13px; font-weight: 700; color: var(--cream); }}
.lang-nivel {{ font-size: 11px; color: var(--muted); }}
.lang-nota {{ font-size: 10px; color: rgba(222,219,200,0.35); display: block; margin-bottom: 4px; }}
.wa-card {{ margin-top: 16px; background: rgba(37,211,102,0.06); border: 1px solid rgba(37,211,102,0.15); border-radius: 16px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; }}
.wa-icon {{ font-size: 22px; }}
.wa-text {{ flex: 1; }}
.wa-text-label {{ font-size: 10px; color: rgba(37,211,102,0.6); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }}
.wa-text-num {{ font-size: 15px; font-weight: 700; color: rgba(37,211,102,0.9); }}
.wa-btn {{ background: rgba(37,211,102,0.12); border: 1px solid rgba(37,211,102,0.25); border-radius: 9999px; padding: 8px 16px; font-size: 12px; font-weight: 700; color: rgba(37,211,102,0.85); cursor: pointer; transition: background 0.2s; white-space: nowrap; }}
.wa-btn:hover {{ background: rgba(37,211,102,0.2); }}

/* ─── PORTAFOLIO ─── */
#portafolio {{ padding: 100px 5vw; }}
#portafolio .section-inner {{ max-width: 860px; margin: 0 auto; }}
.proj-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
.proj-card {{ border: 1px solid var(--border); border-radius: 20px; padding: 32px 28px; display: flex; flex-direction: column; gap: 12px; }}
.proj-num {{ font-size: 10px; color: rgba(222,219,200,0.25); font-weight: 700; letter-spacing: 0.1em; }}
.proj-emoji {{ font-size: 28px; }}
.proj-title {{ font-size: 15px; font-weight: 800; color: var(--cream); line-height: 1.3; }}
.proj-desc {{ font-size: 12px; color: rgba(222,219,200,0.5); line-height: 1.7; flex: 1; }}
.proj-footer {{ display: flex; flex-direction: column; gap: 10px; margin-top: auto; }}
.proj-status {{ font-size: 10px; font-weight: 700; border-radius: 6px; padding: 4px 10px; align-self: flex-start; }}
.proj-status--wip {{ background: rgba(251,191,36,0.1); color: #fbbf24; }}
.proj-status--soon {{ background: rgba(255,255,255,0.05); color: var(--muted); }}
.proj-status--live {{ background: rgba(34,197,94,0.1); color: #4ade80; }}
.proj-link {{ font-size: 10px; font-weight: 700; color: rgba(222,219,200,0.5); letter-spacing: 0.06em; border-bottom: 1px solid rgba(222,219,200,0.15); padding-bottom: 1px; transition: color 0.2s, border-color 0.2s; }}
.proj-link:hover {{ color: var(--cream); border-color: rgba(222,219,200,0.4); }}

/* ─── CONTACTO ─── */
#contacto {{ padding: 120px 5vw 100px; text-align: center; position: relative; overflow: hidden; }}
.contacto-glow {{ position: absolute; width: 700px; height: 400px; border-radius: 50%; background: radial-gradient(circle, rgba(60,60,100,0.15) 0%, transparent 70%); bottom: -100px; left: 50%; transform: translateX(-50%); pointer-events: none; }}
.contacto-title {{ font-size: clamp(52px, 12vw, 140px); font-weight: 800; color: var(--cream); letter-spacing: -0.05em; line-height: 0.9; margin-bottom: 24px; position: relative; z-index: 3; }}
.contacto-sub {{ font-family: 'Instrument Serif', serif; font-style: italic; font-size: clamp(16px, 2vw, 20px); color: rgba(222,219,200,0.45); margin-bottom: 48px; position: relative; z-index: 3; }}
.contacto-links {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; position: relative; z-index: 3; }}
.contact-link {{ display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--border); border-radius: 9999px; padding: 12px 22px; font-size: 12px; font-weight: 700; color: rgba(222,219,200,0.55); letter-spacing: 0.06em; transition: border-color 0.2s, color 0.2s; }}
.contact-link:hover {{ border-color: rgba(222,219,200,0.3); color: var(--cream); }}
.contact-link svg {{ width: 14px; height: 14px; }}
.wa-contact-link {{ border-color: rgba(37,211,102,0.2); color: rgba(37,211,102,0.7); }}
.wa-contact-link:hover {{ border-color: rgba(37,211,102,0.5); color: rgba(37,211,102,0.95); }}
.footer-note {{ margin-top: 80px; font-size: 10px; color: var(--muted-2); letter-spacing: 0.1em; position: relative; z-index: 3; }}

@media (max-width: 480px) {{
  .nav-pill {{ gap: 14px; padding: 10px 14px; }}
  .formacion-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<!-- NAV -->
<nav class="nav-pill">
  <a href="#trayectoria" {attrs(EN(UI['nav_trayectoria']), ES(UI['nav_trayectoria']))}>{esc_text(EN(UI['nav_trayectoria']))}</a>
  <a href="#competencias" {attrs(EN(UI['nav_skills']), ES(UI['nav_skills']))}>{esc_text(EN(UI['nav_skills']))}</a>
  <a href="#formacion" {attrs(EN(UI['nav_formacion']), ES(UI['nav_formacion']))}>{esc_text(EN(UI['nav_formacion']))}</a>
  <a href="#portafolio" {attrs(EN(UI['nav_proyectos']), ES(UI['nav_proyectos']))}>{esc_text(EN(UI['nav_proyectos']))}</a>
  <a href="#contacto" {attrs(EN(UI['nav_contacto']), ES(UI['nav_contacto']))}>{esc_text(EN(UI['nav_contacto']))}</a>
  <div class="lang-switch">
    <button class="lang-btn" data-lang="en" onclick="setLang('en')">EN</button>
    <button class="lang-btn" data-lang="es" onclick="setLang('es')">ES</button>
  </div>
</nav>

<!-- HERO -->
<section id="hero" class="noise-overlay">
  <div class="hero-glow"></div>
  <div class="hero-name-block">
    <span class="hero-name-first pu-word"><span class="pu-inner">{p['nombre']}</span></span>
    <br>
    <span class="hero-name-last pu-word"><span class="pu-inner">{p['apellido']}</span></span>
  </div>
  <p class="hero-titulo pu-word"><span class="pu-inner" {attrs(EN(titulo), ES(titulo))}>{esc_text(EN(titulo))}</span></p>
  <p class="hero-tagline" {attrs(EN(tagline), ES(tagline))}>{esc_text(EN(tagline))}</p>
</section>

<!-- TRAYECTORIA -->
<section id="trayectoria">
  <p class="section-label">{ui('label_trayectoria')}</p>
  <div class="bio-wrap">
    <p class="bio-text" id="bio-text" data-en="{esc_attr(EN(perfil))}" data-es="{esc_attr(ES(perfil))}"></p>
  </div>
  <div id="accordion-list">
    {accordions}
  </div>
</section>

<!-- COMPETENCIAS -->
<section id="competencias">
  <div class="section-inner">
    <p class="section-label">{ui('label_competencias')}</p>
    <div class="comp-grid">
      {comps}
    </div>
  </div>
</section>

<!-- FORMACIÓN -->
<section id="formacion">
  <div class="section-inner">
    <p class="section-label">{ui('label_formacion')}</p>
    <div class="formacion-grid">
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div class="formacion-card">
          <p class="formacion-card-title">{ui('edu_title')}</p>
          {edu}
        </div>
        <div class="formacion-card">
          <p class="formacion-card-title">{ui('cert_title')}</p>
          {certs}
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:16px;">
        <div class="formacion-card">
          <p class="formacion-card-title">{ui('lang_title')}</p>
          {idiomas}
        </div>
        <a href="{p['whatsapp_link']}" target="_blank" class="wa-card" style="text-decoration:none;">
          <div class="wa-icon">💬</div>
          <div class="wa-text">
            <div class="wa-text-label">{ui('wa_label')}</div>
            <div class="wa-text-num">{p['whatsapp']}</div>
          </div>
          <div class="wa-btn">{ui('wa_btn')}</div>
        </a>
      </div>
    </div>
  </div>
</section>

<!-- PORTAFOLIO -->
<section id="portafolio">
  <div class="section-inner">
    <p class="section-label">{ui('label_portafolio')}</p>
    <div class="proj-grid">
      {proyectos}
    </div>
  </div>
</section>

<!-- CONTACTO -->
<section id="contacto" class="noise-overlay">
  <div class="contacto-glow"></div>
  <p class="section-label" style="justify-content:center">{ui('label_contacto')}</p>
  <h2 class="contacto-title">{ui('contacto_title', cls='', tag='span')}</h2>
  <p class="contacto-sub">{ui('contacto_sub')}</p>
  <div class="contacto-links">
    <a href="mailto:{p['email']}" class="contact-link">
      <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="1" y="3" width="12" height="9" rx="2"/><path d="M1 5l6 4 6-4"/>
      </svg>
      <span>{p['email']}</span>
    </a>
    <a href="{p['whatsapp_link']}" target="_blank" class="contact-link wa-contact-link">
      <svg viewBox="0 0 14 14" fill="currentColor" style="width:14px;height:14px">
        <path d="M7 0C3.13 0 0 3.13 0 7c0 1.23.32 2.39.88 3.39L0 14l3.7-.86A6.96 6.96 0 007 14c3.87 0 7-3.13 7-7s-3.13-7-7-7zm3.56 9.72c-.15.42-1.46.82-1.78.82-.07 0-.13 0-.2-.02-.32-.05-1.47-.58-2.47-1.43a7.2 7.2 0 01-1.63-2.16c-.28-.63-.09-1.08.05-1.31.14-.24.34-.44.52-.6.16-.13.22-.15.32-.15.09 0 .32.09.47.42l.6 1.34c.07.16.03.22-.03.32l-.22.28c-.07.09-.15.19-.06.37.09.18.41.74.9 1.2.5.47 1.07.72 1.25.8.18.08.29.07.39-.04l.28-.32c.11-.13.19-.11.32-.06l1.3.61c.32.15.32.3.23.73z"/>
      </svg>
      <span>{p['whatsapp']}</span>
    </a>
    <a href="{p['linkedin']}" target="_blank" class="contact-link">
      <svg viewBox="0 0 14 14" fill="currentColor" style="width:14px;height:14px">
        <path d="M12.6 0H1.4C.63 0 0 .63 0 1.4v11.2C0 13.37.63 14 1.4 14h11.2c.77 0 1.4-.63 1.4-1.4V1.4C14 .63 13.37 0 12.6 0zM4.2 11.9H2.1V5.25h2.1V11.9zM3.15 4.34a1.22 1.22 0 110-2.44 1.22 1.22 0 010 2.44zM11.9 11.9H9.8V8.68c0-.78-.01-1.79-1.09-1.79-1.09 0-1.26.85-1.26 1.73V11.9H5.35V5.25h2.01v.92h.03c.28-.53.96-1.09 1.98-1.09 2.12 0 2.51 1.4 2.51 3.21V11.9z"/>
      </svg>
      <span>LinkedIn</span>
    </a>
    <a href="{DOCX_EN}" download class="contact-link" {dl}>
      <svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" style="width:14px;height:14px">
        <path d="M7 1v8M4 6l3 3 3-3M2 11h10"/>
      </svg>
      {ui('download_cv')}
    </a>
  </div>
  <p class="footer-note"><span {attrs(EN(ubic), ES(ubic))}>{esc_text(EN(ubic))}</span> · {p['email']}</p>
</section>

<script>
window.__META = {meta_json};
const LANG_KEY = 'cv-lang';

function currentLang() {{
  try {{ return localStorage.getItem(LANG_KEY) || 'en'; }} catch (e) {{ return 'en'; }}
}}

function buildBio(lang) {{
  const c = document.getElementById('bio-text');
  if (!c) return;
  const text = c.getAttribute('data-' + lang) || c.getAttribute('data-en') || '';
  let html = '';
  for (const ch of text) {{
    html += ch === ' '
      ? '<span class="ch-span ch-sp"> </span>'
      : '<span class="ch-span">' + ch + '</span>';
  }}
  c.innerHTML = html;
}}

function applyLang(lang) {{
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-en]').forEach(function (el) {{
    if (el.id === 'bio-text') return;
    const v = el.getAttribute('data-' + lang);
    if (v !== null) el.innerHTML = v;
  }});
  buildBio(lang);
  if (window.updateBio) window.updateBio();

  const M = window.__META || {{}};
  if (M[lang]) {{
    document.title = M[lang].title;
    const md = document.querySelector('meta[name=description]');
    if (md) md.setAttribute('content', M[lang].desc);
  }}
  document.querySelectorAll('[data-href-en]').forEach(function (a) {{
    a.setAttribute('href', a.getAttribute('data-href-' + lang));
  }});
  document.querySelectorAll('.lang-btn').forEach(function (b) {{
    b.classList.toggle('active', b.dataset.lang === lang);
  }});
  try {{ localStorage.setItem(LANG_KEY, lang); }} catch (e) {{}}
}}

function setLang(lang) {{ applyLang(lang); }}

// Aplica idioma ANTES de las animaciones de entrada
applyLang(currentLang());

// ─── PULL-UP WORDS ─── */
(function () {{
  document.querySelectorAll('.pu-inner').forEach(function (el, i) {{
    setTimeout(function () {{ el.classList.add('in'); }}, 120 + i * 90);
  }});
}})();

function onVisible(selector, callback, threshold) {{
  const obs = new IntersectionObserver(function (entries) {{
    entries.forEach(function (entry) {{
      if (entry.isIntersecting) {{ callback(entry.target); obs.unobserve(entry.target); }}
    }});
  }}, {{ threshold: threshold || 0.15 }});
  document.querySelectorAll(selector).forEach(function (el) {{ obs.observe(el); }});
}}

onVisible('.cs', function (el) {{
  const idx = parseInt(el.dataset.delayIdx || 0);
  setTimeout(function () {{ el.classList.add('in'); }}, idx * 130);
}});

onVisible('.lbar-fill', function (el) {{
  const w = el.dataset.w;
  setTimeout(function () {{ el.style.width = w + '%'; }}, 200);
}}, 0.3);

// ─── CHAR REVEAL ON SCROLL ─── */
(function () {{
  const container = document.getElementById('bio-text');
  if (!container) return;
  window.updateBio = function () {{
    const spans = container.querySelectorAll('.ch-span');
    const rect = container.getBoundingClientRect();
    const vh = window.innerHeight;
    const progress = 1 - (rect.top / vh);
    const ratio = Math.max(0, Math.min(1, progress * 1.4 - 0.2));
    const active = Math.floor(ratio * spans.length);
    spans.forEach(function (s, i) {{ s.style.opacity = i < active ? '1' : '0.1'; }});
  }};
  window.addEventListener('scroll', window.updateBio, {{ passive: true }});
  window.updateBio();
}})();

function toggleAcc(btn) {{
  btn.closest('.acc-card').classList.toggle('open');
}}
</script>
</body>
</html>"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"[OK] carlo-rondon.html generado ({OUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build(load())

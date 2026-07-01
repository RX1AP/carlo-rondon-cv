# Carlo Rondón — CV Web

CV web profesional con sistema de diseño Prisma (dark/cinematic) y CV descargable en DOCX.

## Flujo de trabajo

```bash
# 1. Editar el contenido
#    Solo tocar data.json — es la fuente única de verdad

# 2. Regenerar ambos archivos
python build/build-all.py

# 3. Deploy (Netlify detecta el push automáticamente)
git add -A
git commit -m "update: descripción del cambio"
git push
```

## Estructura

```
carlo-rondon-cv/
├── data.json              ← EDITAR AQUÍ
├── carlo-rondon.html      ← Generado. No editar directamente.
├── Carlo Rondon CV.docx   ← Generado. No editar directamente.
├── netlify.toml
├── build/
│   ├── build-html.py
│   ├── build-docx.py
│   └── build-all.py
└── README.md
```

## Instalar dependencias

```bash
pip install python-docx jinja2
```

## Deploy

Conectado a Netlify. Cada `git push` a `main` dispara un deploy automático en ~30s.

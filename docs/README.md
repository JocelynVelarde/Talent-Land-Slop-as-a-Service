# Tecovolt Docs

Documentación del proyecto Tecovolt para el track **Qualcomm Sustainable Power Cities** en Talent Land 2025.

Built with [Hugo](https://gohugo.io/) + [Docsy](https://www.docsy.dev/) theme.

## Quick start (local development)

### Prerequisites

- [Hugo extended](https://gohugo.io/installation/) (v0.110.0+)
- [Go](https://go.dev/dl/) (1.21+)
- [Node.js](https://nodejs.org/) (v20+)

### Setup

```bash
# Clone the repo
git clone https://github.com/JocelynVelarde/Talent-Land-Slop-as-a-Service.git
cd Talent-Land-Slop-as-a-Service/docs

# Install dependencies
npm install

# Run locally
hugo server
```

The site will be available at `http://localhost:1313/`.

## Deployment

The site auto-deploys to GitHub Pages on push to `main` via the workflow in `.github/workflows/deploy-github-pages.yml`.

### Manual setup (first time only)

1. Create a `gh-pages` branch and push it
2. In repo Settings → Pages, set source to "Deploy from a branch" and select `gh-pages` / `/(root)`
3. Push to `main` — the GitHub Action will build and deploy automatically

## Structure

```
docs/
├── .github/workflows/       # GitHub Actions for deployment
├── assets/scss/              # Custom Tecovolt styles and variables
├── content/en/
│   ├── _index.md             # Landing page
│   ├── docs/
│   │   ├── problem/          # Problemática energética en México
│   │   ├── solution/         # Tecovolt: la solución
│   │   ├── architecture/     # Arquitectura técnica dual MCU+MPU
│   │   ├── edge-ai/          # Modelos de IA, pipeline, DSP blocks
│   │   ├── hardware/         # BOM, sensores, actuadores, enclosure
│   │   ├── scalability/      # Mercado, competencia, escalabilidad
│   │   ├── financial/        # Proyección financiera
│   │   ├── journey/          # Hitos y progreso del hackathon
│   │   └── team/             # El equipo SAAS
│   └── blog/                 # Updates del equipo
├── hugo.toml                 # Hugo configuration
├── go.mod                    # Go modules (Docsy theme)
└── package.json              # Node dependencies (PostCSS)
```

## Team — Slop as a Service (SAAS)

Bini Vázquez · Diego Pérez Rossi · Jocelyn Velarde Barrón · Armando Mac Beath

Tecnológico de Monterrey · Monterrey / Puebla / CDMX

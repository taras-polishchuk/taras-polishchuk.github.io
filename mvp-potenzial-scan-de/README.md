# Potenzial-Scan Lite — German mockup (Mission D)

**Live URL:** https://taras-polishchuk.github.io/mvp-potenzial-scan-de/

**Style:** Liquid Glass (light theme, glassmorphism, premium animations).

**Language:** German (DE), Mittelstand target audience.

## Versions

- This folder: Mission D (Liquid Glass primary) — recommended baseline
- Sibling `mvp-potenzial-scan-heron/`: Mission E (Heron style) — alternative warm-orange design
- Sibling `insidedynamic-redesign/`: Mission F (CEO pitch) — full marketing site redesign
- Archived `ARCHIVE-2026-08-31/mvp-potenzial-scan-landing-v2/`: original landing page v2.0 (retired)

## Architecture

- Pre-Intelligence Dossier (email-driven company research via Perplexity Sonar API)
- 8 production hooks tagged `// PRODUCTION HOOK:` for backend integration
- 17 keyframe animations
- DSGVO Art. 6 Abs. 1 lit. a consent flow
- 6-tier kill switch (build flag → URL `?nomedia=1` → `?dm=0` → localStorage → A/B bucket → server circuit breaker)
- Full architecture decision: see main `mvp-product/architecture-decisions/pre-intel-dossier.md`

## Source

Original mockup lives at `mvp-product/mockup/index.html` in the target repo.
Published copy is byte-identical (SHA-256 `1a5b40588204e4fc6f95e9260073c012a3a8e26e38afb8b1c6876dc96468632b`).

## Test URL parameters

- `?email=anna@mueller-praezisionsteile.de&company=Müller+Praezisionsteile+GmbH` — shows dossier with mock data
- `?nomedia=1` — suppresses dossier
- `?dm=0` — legacy direct-mail suppression

## Mission timeline

- Mission A: Independent Industrial Dossier redesign
- Mission B: Liquid Glass Luminous (template for this version)
- Mission C: Pre-Intelligence Dossier integration
- Mission D: German translation + layout validation (this version)
- Mission E: Heron style alternative
- Mission F: CEO-pitch marketing site redesign

# Taras Polishchuk — Frontend Developer Portfolio

> Personal portfolio — a single-page site with an interactive projects overlay, particle canvas background, and custom cursor.

🌐 **Live:** [taras-polishchuk.github.io](https://taras-polishchuk.github.io)

---

## About

A zero-dependency portfolio built with vanilla HTML, CSS, and JavaScript. No frameworks, no build step — just a single `index.html`. Features a dark glassmorphism design with a hero card, animated entrance, 3D tilt effect, and a full-screen projects overlay.

---

## Structure

```
taras-polishchuk.github.io/
└── index.html    # The entire portfolio — styles, markup, and scripts in one file
```

---

## Features

- **Particle canvas background** — animated floating dots with mouse repulsion
- **Custom cursor** — dot + lerp ring + lazy glow, mix-blend-mode difference
- **Hero card** — glassmorphism card with 3D tilt on hover and idle float animation
- **Projects overlay** — full-screen overlay with staggered card entrance, scroll/swipe trigger
- **Keyboard navigation** — `Esc` to close, `←` `→` to move between project cards
- **Intro loader** — animated progress bar on initial load
- **Fully responsive** — adapts to mobile, custom cursor hidden on touch devices
- **Reduced motion support** — respects `prefers-reduced-motion`

---

## Projects

Each project lives in its own repository and is deployed to GitHub Pages via GitHub Actions:

| Project | Repo | Live | Stack |
|---|---|---|---|
| **Locus** | [taras-polishchuk/locus](https://github.com/taras-polishchuk/locus) | [taras-polishchuk.github.io/locus/](https://taras-polishchuk.github.io/locus/) | HTML · CSS · JS · Web Audio API |
| **Shopify Dev KB** | [taras-polishchuk/shopify-dev-kb](https://github.com/taras-polishchuk/shopify-dev-kb) | [taras-polishchuk.github.io/shopify-dev-kb/](https://taras-polishchuk.github.io/shopify-dev-kb/) | Svelte 5 · TypeScript · Tailwind |
| **Ubuntu Cheatsheet** | [taras-polishchuk/ubuntu-cheatsheet](https://github.com/taras-polishchuk/ubuntu-cheatsheet) | [taras-polishchuk.github.io/ubuntu-cheatsheet/](https://taras-polishchuk.github.io/ubuntu-cheatsheet/) | HTML · CSS · JS |
| **UI Lab** | [taras-polishchuk/ui-lab](https://github.com/taras-polishchuk/ui-lab) | [taras-polishchuk.github.io/ui-lab/](https://taras-polishchuk.github.io/ui-lab/) | HTML · CSS · JS |

---

## Run Locally

No install required — just open the file:

```bash
git clone https://github.com/taras-polishchuk/taras-polishchuk.github.io.git
cd taras-polishchuk.github.io
open index.html
```

---

## Deployment

Hosted on **GitHub Pages** directly from the `main` branch. Any push to `main` is live immediately — no CI needed for this repo since there's no build step.

The project repos each have a `.github/workflows/deploy.yml` that runs on push and deploys via the GitHub Actions Pages API.

---

## Author

**Taras Polishchuk** — Frontend Developer

- GitHub: [@taras-polishchuk](https://github.com/taras-polishchuk)
- LinkedIn: [taras-p-349902213](https://www.linkedin.com/in/taras-p-349902213/)
- Telegram: [@taras_pie](https://t.me/taras_pie)
- Email: poli.taras.shchuk@gmail.com
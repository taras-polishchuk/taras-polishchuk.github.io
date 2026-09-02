# Potenzial-Scan Lite — Portfolio Style variant

> **Variant:** Portfolio Style v2.0 (dark theme, warm amber `#d4a017` primary)
> **Source:** [`../mvp-potenzial-scan-de/`](../mvp-potenzial-scan-de/) — Liquid Glass (light theme, primary amber)
> **Generated:** 2026-09-02 by Codex Mission G (replaces v1.0 violet/mint variant from 2026-08-31)
> **SHA-256:** `d39aa52867494aee7e939a9e10446e61671afa5c2856ec700e0858aa2ee26216`

## What this is

A second visual variant of the Potenzial-Scan Lite landing page. Same **layout,
sections, blocks, and logic** as the source — only the **visual tokens** (colors,
surfaces, glass effects, typography) are remapped to the
[`taras-polishchuk.github.io`](../../) design system.

## Visual diff from source

| Aspect | Source (DE) | This variant (portfolio) |
|--------|-------------|---------------------------|
| Background | `#f2eee5` warm paper | `#0a0a0b` deep dark |
| Surface | `#e6dfd2` light cream | `#111113` charcoal |
| Primary | `#d4a017` warm amber | `#d4a017` warm amber |
| Accent | `#f0b825` bright amber | `#f0cf73` bright amber |
| Text on bg | `#0b0b0d` deep ink | `#e8e8f0` light off-white |
| Display font | Inter Tight | Cabinet Grotesk |
| Body font | Inter Tight | Inter |
| Theme | Light / warm | Dark / cool |

> **Note (2026-09-02):** v1.0 had `--amber: #7c6fff` violet and `--amber-bright: #4eecc8` mint. Operator rejected as "не дуже красиво вийшло". v2.0 (Codex Mission G) restores the canonical Taras amber palette (`#d4a017` / `#f0cf73`) on the same dark `#0a0a0b` background, matching the approved Mission E (Heron-style) visual vocabulary.

## What is preserved 100%

- 5 `<section>` elements, 3 with IDs (`#intro`, `#wizard`, `#results`)
- 2 inline `<script>` blocks (logic / animations)
- All headings (1× h1, 8× h2, 6× h3)
- Glassmorphism classes and effects (`.glass`, ambient-field with sky/rose blops)
- Animation keyframes (`drift-b`, `drift-c`, etc.)
- Layout grid, spacing, radius (2px sharp corners)
- Wizard step structure (3-step flow)
- Form fields, options, results rendering

## How to preview

Open `index.html` in any browser. For GitHub Pages deployment:

1. Create branch from `taras-polishchuk.github.io` repo
2. Copy this directory to repo root
3. Push to GitHub Pages

## Operator's brief

> "Не змінювати той, що там зараз актуальний, який є лінка на моєму портфоліо.
> Потрібно зробити ще одне, але в стилістиці мого портфоліо. Тобто кольори,
> стилістика, поведінка, анімація, блоки, які там зараз є, треба залишити.
> Ось, розкладку не міняємо. Міняємо тільки кольори і зовнішній вигляд без
> зміни розкладки. Зовсім не міняємо той дизайн розкладки. І елементи, і блоки,
> які там зараз є. І логіку поведінки. Просто міняємо візуально трошки."

**Status:** Mission requirements met — visual-only reskin, layout/behavior/animations
preserved 100%. Source file (`mvp-potenzial-scan-de/index.html`) is **untouched**.

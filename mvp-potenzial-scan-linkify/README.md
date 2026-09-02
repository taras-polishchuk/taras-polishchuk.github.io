# Mission G — Visual rationale

## Outcome

Mission G keeps `source-mockup.html` intact and reproduces its complete Potenzial-Scan journey in `index.html`: introduction, five-step wizard, Pre-Intelligence Dossier, result dashboard, contact call-to-action, and persistent legal footer. The document structure, German copy, IDs, form fields, data attributes, production hooks, URL controls, bucketing scaffold, function names, event handlers, and interactive animations are preserved.

The change is deliberately a visual reskin. A final CSS cascade layer applies the supplied Linkify / InsideDynamic system without restructuring application markup or rewriting behavior.

## Visual decisions

- **Ink-first canvas:** The page now uses `#0A0C12`, with `#11141C` and `#171B26` providing restrained elevation. This replaces Mission D's cream Liquid Glass surface and gives the pitch the same dark, technical atmosphere as Linkify.
- **Linkify signature background:** Two fixed radial gradients introduce teal and indigo light in opposite regions. A 64 px grid sits above them and fades through a radial mask. Both remain behind the application, preserving contrast and interaction.
- **Teal hierarchy:** `#36E0C4` is the sole primary signal color across actions, progress, focus states, diagram scans, selected choices, dossier accents, and recommendation borders. `#6E8BFF` appears only as a secondary gradient endpoint and ambient depth color.
- **Brand typography:** Space Grotesk at weight 600 drives headings, buttons, labels, and navigational markers. Inter is used for body copy and controls at a readable 17 px / 1.65 baseline. The previous Inter Tight and amber/monospace-led visual language is removed from the rendered design.
- **Focused measure:** The shell contracts from 1440 px to 1140 px. Headlines use Linkify's `clamp(2.5rem, 6vw, 4.25rem)` scale, while paragraphs keep comfortable line lengths and a muted but accessible contrast.
- **Marker language:** Eyebrows use the Linkify leading teal rule, uppercase treatment, and wide tracking. The hero's key phrase uses the supplied white-to-teal-to-indigo text gradient.
- **Solid depth instead of glass:** Dossier, wizard rail, analysis, gate, results, and recommendation surfaces use solid dark gradients, subtle white borders, 16 px corners, and soft black shadows. Backdrop blur is limited to the site header rather than used as a card material.
- **Actions:** Buttons use a maximum 16 px radius, never a pill silhouette. Primary actions are teal with dark ink text; secondary actions use quiet translucent surfaces and teal border feedback.
- **Spacing:** Major views use the Linkify rhythm of `clamp(64px, 9vw, 120px)`. Smaller internal gaps stay compact enough that the wizard remains task-focused.
- **Motion:** Existing interactive reveal, analysis, scan, loading, and dossier animations remain available. Motion is subordinate to the static mesh and grid, and the existing reduced-motion handling remains intact.

## Mission D comparison

| Area | Mission D | Mission G |
|---|---|---|
| Canvas | Warm cream, luminous blobs | Deep ink, teal/indigo mesh, masked grid |
| Type | Inter Tight with strong mono influence | Space Grotesk display, Inter body |
| Primary accent | Warm amber `#d4a017` | Signal teal `#36E0C4` |
| Secondary accent | Warm glass tints | Electric indigo `#6E8BFF`, secondary only |
| Cards | Translucent Liquid Glass | Solid dark elevation with soft shadow |
| Corners | Mixed sharp/glass geometry | Cohesive 16 px / 10 px system |
| Content width | 1440 px | 1140 px |
| Section rhythm | Composition-specific | Linkify's generous responsive spacing |
| Visual emphasis | Material effects and shimmer | Contrast, typography, mesh, grid, restrained lift |

## Anti-slop audit

- No invented metrics, testimonials, logos, or claims were added.
- No emoji or decorative stock imagery was added.
- Teal remains primary; indigo is never used as the dominant action color.
- Buttons do not use pill geometry.
- German Sie-form and DSGVO language are unchanged.
- Background effects are the supplied Linkify signature rather than generic decorative blobs.
- Cards share one surface, border, radius, and shadow vocabulary.
- All interactive controls retain visible focus feedback and reduced-motion support.

## Responsive review targets

The layout is tuned for 1440 px, 1024 px, 768 px, and 420 px widths. At desktop sizes the intro remains a focused two-column composition. At tablet size the dossier follows the hero copy and the wizard rail becomes a compact horizontal context card. At phone size forms, recommendations, result sections, and calls to action become single-column, with German compounds allowed to wrap rather than being clipped or reduced to unreadable sizes.

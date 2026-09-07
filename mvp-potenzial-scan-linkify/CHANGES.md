# Mission I changes

- Made the `intel-processes` tags compact and responsive: 10px type, 4px × 8px padding, 5px gaps, pill corners, and explicit container/item width constraints for dynamic content.
- Tightened the dossier panel without changing its structure: reduced outer padding, header spacing, company-name size, domain spacing, fact-row padding, section spacing, and source spacing.
- Rebalanced the facts grid so the longer German industry value receives more space while the founding/team value remains readable.
- Preserved all existing sections, IDs, classes, JavaScript logic, URL parameters, data attributes, production hooks, and the linkify.cloud palette.
- Audited the Mission D baseline and Mission G output for Ukrainian Cyrillic in visible copy, placeholders, loading/error states, ARIA labels, JavaScript strings, and metadata; no Ukrainian text was present.

## Validation

- Cyrillic matches in `index.html`: 0 (Unicode-aware scan)
- Existing screen IDs preserved unchanged: `intro`, `wizard`, and `results`. The supplied `intro|wizard|s6|s7` check returns 2 for both the Mission D baseline and Mission G because neither source contains `s6` or `s7` IDs.
- Production hook markers preserved: 5
- Layout checked at 1440×900, 1280×800, 768×1024, and 390×844.

# sa-learning-manual/ — deployment target

> **Live:** https://taras-polishchuk.github.io/sa-learning-manual/

This directory is a **deployment target**, not a source of truth. The canonical
artifact lives at `/home/taras/projects/learn/sa-learning-manual/` (a separate
git repo with its own versioning and tags).

## How deployments work

1. Edit `index.html` ONLY in `/home/taras/projects/learn/sa-learning-manual/`.
2. Run the build script from this directory:
   ```bash
   cd /home/taras/projects/career/taras-polishchuk.github.io/sa-learning-manual
   ./publish.sh
   ```
   The script copies the source `index.html` into this directory atomically
   (via `mktemp` + `mv`).
3. Commit + push:
   ```bash
   git add sa-learning-manual/index.html
   git commit -m "deploy(sa-learning-manual): refresh from source"
   git push origin main
   ```
4. GitHub Pages redeploys in 30–90s.

## Files in this directory

| File | Role |
|---|---|
| `index.html` | Build output. Copied verbatim from `/home/taras/projects/learn/sa-learning-manual/index.html`. Manually editing this file is a bug — it gets clobbered by the next `./publish.sh` run. |
| `publish.sh` | The build script. |
| `README.md` | This file. |

## Drift detection

Run `./publish.sh --check` from this directory to verify the deployment copy
still matches the source. Exit code:

- `0` — in sync
- `1` — drift (source newer than deployment, or vice versa)
- `2` — source missing entirely (treat as fatal)

## Tagging the source

To mark a deployable milestone in the source repo:
```bash
./publish.sh --tag v0.2.0
```
This creates an annotated git tag in the source repo. The source's `CHANGELOG.md`
records what changed per tag; this directory has no separate changelog.

## Why this pattern

The source is private (lives in `/home/taras/projects/learn/`), versioned, and
has its own changelog. The deployment is public (GitHub Pages) and only needs
the rendered HTML. Decoupling them means:

- Source can evolve (new content, design tweaks) without polluting the portfolio
  repo's git history.
- A botched edit to the deployment copy can't break the source — `./publish.sh`
  just overwrites it on next run.
- Future migrations (move to a different deployment channel, host on a CDN, ...)
  don't require touching the source repo.

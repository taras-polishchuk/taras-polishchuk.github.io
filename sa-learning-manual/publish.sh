#!/usr/bin/env bash
# publish.sh — copy the canonical SA Learning Manual from source to deployment.
#
# Source of truth:      /home/taras/projects/learn/sa-learning-manual/
# Deployment target:    <this repo>/sa-learning-manual/index.html
# Live URL after push:  https://taras-polishchuk.github.io/sa-learning-manual/
#
# Usage:
#   ./publish.sh                       # copy source -> deployment
#   ./publish.sh --check               # verify deployment matches source (exit 0/1)
#   ./publish.sh --tag <v0.X.Y>        # also create git tag in source repo
#
# Convention: edit ONLY in the source repo. This deployment copy is build output —
# any manual edit here gets clobbered by the next `./publish.sh` run.

set -euo pipefail

SRC="/home/taras/projects/learn/sa-learning-manual/index.html"
DST_DIR="$(cd "$(dirname "$0")" && pwd)"
DST="$DST_DIR/index.html"

if [ ! -f "$SRC" ]; then
  echo "FATAL: source not found at $SRC" >&2
  echo "       (expected learn/sa-learning-manual/ to exist and contain index.html)" >&2
  exit 2
fi

case "${1:-}" in
  --check)
    if [ ! -f "$DST" ]; then
      echo "DRIFT: $DST missing"; exit 1
    fi
    if ! cmp -s "$SRC" "$DST"; then
      echo "DRIFT: source and deployment differ"
      echo "  source:      $(stat -c '%s bytes  %y' "$SRC")"
      echo "  deployment:  $(stat -c '%s bytes  %y' "$DST")"
      echo "Run: ./publish.sh"
      exit 1
    fi
    echo "OK: deployment matches source"
    exit 0
    ;;
  --tag)
    if [ -z "${2:-}" ]; then
      echo "Usage: $0 --tag <vX.Y.Z>"; exit 2
    fi
    cd /home/taras/projects/learn/sa-learning-manual
    git tag -a "$2" -m "Deploy $2 — $(date -u +%Y-%m-%d)"
    echo "Tagged source repo: $2"
    exit 0
    ;;
  "")
    : # default: copy
    ;;
  *)
    echo "Unknown arg: $1"; echo "Usage: $0 [--check|--tag <vX.Y.Z>]"; exit 2
    ;;
esac

# Atomic copy via temp file
TMP="$(mktemp "$DST_DIR/.index.html.tmp.XXXXXX")"
cp "$SRC" "$TMP"
mv "$TMP" "$DST"

# Report
SRC_SHA=$(sha256sum "$SRC" | cut -c1-12)
DST_SHA=$(sha256sum "$DST" | cut -c1-12)
SRC_SIZE=$(stat -c '%s' "$SRC")
echo "Copied: $SRC"
echo "  size:  $SRC_SIZE bytes"
echo "  sha:   $SRC_SHA (source) / $DST_SHA (deployment)"
echo ""
echo "Next steps:"
echo "  cd $DST_DIR"
echo "  git add sa-learning-manual/index.html"
echo "  git commit -m 'deploy(sa-learning-manual): refresh from source'"
echo "  git push origin main"

#!/usr/bin/env bash
# publish.sh — copy the canonical InsideDynamic Architecture analysis
# from source to deployment (GitHub Pages).
#
# Source of truth:      /home/taras/projects/work/insidedynamic/06-correspondence/SA-ARCHITECTURE-AX1-COOLIFY.md
# Deployment target:    <this repo>/insidedynamic-architecture/index.html
# Live URL after push:  https://taras-polishchuk.github.io/insidedynamic-architecture/
#
# Usage:
#   ./publish.sh                # build from source (default)
#   ./publish.sh --check        # verify deployment matches source (exit 0/1)
#   ./publish.sh --push         # also git commit + push to GitHub
#   ./publish.sh --tag <v0.X.Y> # also create git tag
#
# Convention: edit ONLY in the source repo. This deployment copy is
# build output — any manual edit here gets clobbered by the next
# ./publish.sh run.

set -euo pipefail

SRC_MD="/home/taras/projects/work/insidedynamic/06-correspondence/SA-ARCHITECTURE-AX1-COOLIFY.md"
MEETING_MD="/home/taras/projects/work/insidedynamic/06-correspondence/MEETING-BRIEFING-2026-08-25.md"
DST_DIR="$(cd "$(dirname "$0")" && pwd)"
DST="$DST_DIR/index.html"

# Render source MD → standalone HTML with Mermaid + dark theme
render_html() {
  local md_path="$1"

  # Extract title
  local title
  title=$(grep -m 1 '^# ' "$md_path" | sed 's/^# //')

  cat <<'HEADER'
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InsideDynamic Architecture | Taras Polishchuk</title>
HEADER

  cat <<'META'
<meta name="description" content="InsideDynamic GmbH architecture analysis: Plesk ax1 + Coolify container platform + Proxmox dev-server. Two-worlds infrastructure, agent-first operations, self-hosted open-source stack.">
<meta name="author" content="Taras Polishchuk">
<meta property="og:title" content="InsideDynamic Architecture — Target State">
<meta property="og:description" content="Two-worlds architecture analysis for InsideDynamic GmbH. Plesk + Coolify + Proxmox. Self-hosted, open-source, agent-friendly.">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://taras-polishchuk.github.io/insidedynamic-architecture/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230d9488'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dominant-baseline='central' font-family='sans-serif' font-size='20' fill='white'%3E%E2%97%88%3E%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400..700&display=swap" rel="stylesheet">
META

  cat <<'STYLE'
<style>
  :root {
    --bg: #0a0a0b;
    --bg-soft: #131316;
    --bg-card: #1a1a1f;
    --border: #2a2a32;
    --text: #e4e4e7;
    --text-muted: #a1a1aa;
    --accent: #14b8a6;
    --accent-soft: rgba(20, 184, 166, 0.15);
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --success: #10b981;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    padding: 2rem 1rem;
  }
  .container { max-width: 1200px; margin: 0 auto; }
  header {
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
  }
  .breadcrumb {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
  }
  .breadcrumb a { color: var(--text-muted); text-decoration: none; }
  .breadcrumb a:hover { color: var(--accent); }
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
  }
  h2 {
    font-size: 1.5rem;
    margin-top: 3rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }
  h3 {
    font-size: 1.15rem;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    color: var(--accent);
  }
  .subtitle { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 1rem; }
  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 1rem;
  }
  .meta-item strong { color: var(--text); }
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .stat {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
  }
  .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.2;
  }
  .stat-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
  }
  .risk-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  .risk {
    background: var(--bg-soft);
    border-left: 4px solid var(--text-muted);
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
  }
  .risk-critical { border-left-color: var(--danger); }
  .risk-high { border-left-color: var(--warning); }
  .risk-medium { border-left-color: var(--info); }
  .risk-low { border-left-color: var(--success); }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }
  th, td {
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
  }
  th {
    background: var(--bg-soft);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: var(--bg-soft); }
  ul, ol { margin: 0.5rem 0 0.5rem 1.5rem; }
  li { margin-bottom: 0.25rem; }
  code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    background: var(--bg-soft);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    color: var(--accent);
  }
  pre {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    margin: 1rem 0;
  }
  pre code {
    background: none;
    padding: 0;
    color: var(--text);
    font-size: 0.8rem;
    line-height: 1.5;
  }
  .arch-diagram {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
    overflow-x: auto;
  }
  .mermaid { background: var(--bg-card); text-align: center; }
  .timeline {
    position: relative;
    padding: 1rem 0;
  }
  .timeline::before {
    content: '';
    position: absolute;
    left: 1.25rem;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border);
  }
  .phase {
    position: relative;
    padding-left: 3rem;
    margin-bottom: 2rem;
  }
  .phase::before {
    content: '';
    position: absolute;
    left: 0.5rem;
    top: 0.25rem;
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
    background: var(--accent);
    border: 3px solid var(--bg);
  }
  .phase h4 {
    font-size: 1.05rem;
    margin-bottom: 0.25rem;
    color: var(--text);
  }
  .phase-meta {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
  }
  .badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    background: var(--accent-soft);
    color: var(--accent);
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.5rem;
  }
  .badge-danger { background: rgba(239, 68, 68, 0.15); color: var(--danger); }
  .badge-warning { background: rgba(245, 158, 11, 0.15); color: var(--warning); }
  .badge-info { background: rgba(59, 130, 246, 0.15); color: var(--info); }
  footer {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.85rem;
    text-align: center;
  }
  footer a { color: var(--accent); text-decoration: none; }
</style>
STYLE

  cat <<'HEADER2'
</head>
<body>

<div class="container">

  <header>
    <div class="breadcrumb">
      <a href="/">← Taras Polishchuk</a> › InsideDynamic Architecture
    </div>
HEADER2

  echo "    <h1>InsideDynamic Architecture — Target State</h1>"
  echo "    <p class=\"subtitle\">Two-worlds infrastructure: Plesk ax1 (webhosting) + Coolify containers (apps). Agent-first operations, self-hosted, open-source.</p>"
  echo "    <div class=\"meta\">"
  echo "      <div class=\"meta-item\"><strong>Author:</strong> Taras Polishchuk, Solution Architect</div>"
  echo "      <div class=\"meta-item\"><strong>Date:</strong> 2026-08-25</div>"
  echo "      <div class=\"meta-item\"><strong>Status:</strong> Proposal for Viktor review</div>"
  echo "    </div>"
  echo "  </header>"

  # Quick stats grid
  cat <<'STATS'
  <div class="stats">
    <div class="stat"><div class="stat-value">2</div><div class="stat-label">Infrastructure Worlds</div></div>
    <div class="stat"><div class="stat-value">56</div><div class="stat-label">Domains on ax1</div></div>
    <div class="stat"><div class="stat-value">8</div><div class="stat-label">KI Agents (KIwerk.one)</div></div>
    <div class="stat"><div class="stat-value">20</div><div class="stat-label">Issues to fix (P0+P1)</div></div>
    <div class="stat"><div class="stat-value">4</div><div class="stat-label">Phased roadmap</div></div>
    <div class="stat"><div class="stat-value">€0-15</div><div class="stat-label">Total monthly cost</div></div>
  </div>
STATS

  # Convert MD to HTML (simple Python script)
  python3 - "$md_path" <<'PYEOF'
import sys
import re
import html

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    md = f.read()

# Strip frontmatter if any
md = re.sub(r'^---.*?---\n', '', md, flags=re.DOTALL)

in_code = False
in_table = False
in_list = False
in_arch = False
lines_out = []

for line in md.split('\n'):
    # Code blocks
    if line.startswith('```'):
        if in_code:
            lines_out.append('</code></pre>')
            in_code = False
        else:
            lang = line[3:].strip()
            lines_out.append(f'<pre><code class="language-{lang}">')
            in_code = True
        continue

    if in_code:
        lines_out.append(html.escape(line))
        continue

    # Architecture diagram detection (mermaid)
    if '```mermaid' in line or 'graph TB' in line:
        in_arch = True
        lines_out.append('<div class="arch-diagram">')
        if '```mermaid' in line:
            lines_out.append('<pre class="mermaid">')
        else:
            lines_out.append('<pre class="mermaid">')
        continue

    if in_arch and line.strip() == '```':
        lines_out.append('</pre></div>')
        lines_out.append('<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>')
        lines_out.append('<script>mermaid.initialize({startOnLoad:true, theme:"dark", themeVariables:{primaryColor:"#1a1a1f", primaryTextColor:"#e4e4e7", primaryBorderColor:"#14b8a6", lineColor:"#2a2a32", mainBkg:"#1a1a1f", background:"#0a0a0b"}});</script>')
        in_arch = False
        continue

    if in_arch:
        lines_out.append(line)
        continue

    # Headings
    if line.startswith('# '):
        lines_out.append(f'<h1>{line[2:]}</h1>')
    elif line.startswith('## '):
        lines_out.append(f'<h2>{line[3:]}</h2>')
    elif line.startswith('### '):
        lines_out.append(f'<h3>{line[4:]}</h3>')
    elif line.startswith('#### '):
        lines_out.append(f'<h4>{line[5:]}</h4>')
    # Tables
    elif line.startswith('|') and '|' in line[1:]:
        cells = [c.strip() for c in line.strip('|').split('|')]
        if not in_table:
            lines_out.append('<table>')
            in_table = True
        if all(set(c) <= set('-: ') for c in cells):
            continue  # separator row
        if line.startswith('| #') or (lines_out and lines_out[-1].startswith('<table>')):
            # First row = headers
            lines_out.append('<thead><tr>')
            for c in cells:
                lines_out.append(f'<th>{html.escape(c)}</th>')
            lines_out.append('</tr></thead><tbody>')
        else:
            lines_out.append('<tr>')
            for c in cells:
                lines_out.append(f'<td>{html.escape(c)}</td>')
            lines_out.append('</tr>')
    # Lists
    elif line.startswith('- ') or line.startswith('* '):
        if not in_list:
            lines_out.append('<ul>')
            in_list = True
        lines_out.append(f'<li>{html.escape(line[2:])}</li>')
    elif re.match(r'^\d+\.\s', line):
        if not in_list:
            lines_out.append('<ol>')
            in_list = True
        content = re.sub(r'^\d+\.\s', '', line)
        lines_out.append(f'<li>{html.escape(content)}</li>')
    # Blockquote
    elif line.startswith('> '):
        lines_out.append(f'<blockquote style="border-left:3px solid var(--accent);padding-left:1rem;color:var(--text-muted);margin:0.5rem 0;">{html.escape(line[2:])}</blockquote>')
    # Horizontal rule
    elif line.strip() == '---':
        lines_out.append('<hr style="border:none;border-top:1px solid var(--border);margin:2rem 0;">')
    # Empty line
    elif line.strip() == '':
        if in_list:
            lines_out.append('</ul>' if lines_out[-1].endswith('</li>') and '<ol>' in '\n'.join(lines_out[-10:]) and '</ul>' not in '\n'.join(lines_out[-5:]) else '')
            if lines_out and lines_out[-1] in ['</ul>', '</ol>']:
                in_list = False
            elif in_list:
                in_list = False
                if '<ol>' in '\n'.join(lines_out[-10:]):
                    lines_out.append('</ol>')
                else:
                    lines_out.append('</ul>')
        if in_table and '\n'.join(lines_out[-50:]).count('<td>') > 0 and '\n'.join(lines_out[-50:]).count('</tr>') > 0:
            lines_out.append('</tbody></table>')
            in_table = False
    # Paragraph
    else:
        if line.strip():
            content = html.escape(line)
            # Inline code
            content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
            # Bold
            content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
            # Italic
            content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)
            lines_out.append(f'<p>{content}</p>')

# Close any open tags
if in_table:
    lines_out.append('</tbody></table>')
if in_list:
    lines_out.append('</ul>')

print('\n'.join(lines_out))
PYEOF

  cat <<'FOOTER'
  <footer>
    <p>
      <strong>Author:</strong> Taras Polishchuk ·
      <a href="https://taras-polishchuk.github.io/">taras-polishchuk.github.io</a> ·
      Last updated: 2026-08-25
    </p>
    <p>
      Sources: Viktor 24.08 (7 знахідок), Statusaufnahme ax1 24.08, infra-audit dev-server 24.08,
      KIwerk.one Confluence (70 pages), Notion (2 pages, 113 blocks).
    </p>
  </footer>

</div>

</body>
</html>
FOOTER
}

case "${1:-}" in
  --check)
    if [ ! -f "$DST" ]; then
      echo "DRIFT: $DST missing"; exit 1
    fi
    # Simple check: does it contain key content?
    if ! grep -q "InsideDynamic Architecture — Target State" "$DST"; then
      echo "DRIFT: deployment does not contain expected content"
      exit 1
    fi
    echo "OK: deployment matches source"
    exit 0
    ;;
  --push)
    render_html "$SRC_MD" > "$DST"
    echo "Rendered → $DST"
    cd "$DST_DIR"
    git add insidedynamic-architecture/
    git commit -m "Deploy insideDynamic architecture analysis $(date -u +%Y-%m-%d)"
    git push
    echo "Pushed to GitHub"
    ;;
  --tag)
    if [ -z "${2:-}" ]; then
      echo "Usage: $0 --tag <vX.Y.Z>"; exit 2
    fi
    render_html "$SRC_MD" > "$DST"
    cd "$DST_DIR"
    git add insidedynamic-architecture/
    git commit -m "Deploy $2 — $(date -u +%Y-%m-%d)"
    git tag -a "$2" -m "Deploy $2"
    git push && git push origin "$2"
    echo "Tagged and pushed: $2"
    ;;
  "")
    render_html "$SRC_MD" > "$DST"
    echo "Rendered → $DST ($(wc -c < "$DST") bytes)"
    echo "Next: ./publish.sh --push"
    ;;
  *)
    echo "Usage: $0 [--check|--push|--tag <vX.Y.Z>]"
    exit 2
    ;;
esac

#!/usr/bin/env python3
"""render_architecture.py — convert InsideDynamic architecture MD to standalone HTML.

Source: /home/taras/projects/work/insidedynamic/06-correspondence/SA-ARCHITECTURE-AX1-COOLIFY.md
Output: /home/taras/projects/career/taras-polishchuk.github.io/insidedynamic-architecture/index.html
"""
import sys
import re
import html
from pathlib import Path

SRC = Path("/home/taras/projects/work/insidedynamic/06-correspondence/SA-ARCHITECTURE-AX1-COOLIFY.md")
DST = Path("/home/taras/projects/career/taras-polishchuk.github.io/insidedynamic-architecture/index.html")

HTML_HEAD = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InsideDynamic Architecture | Taras Polishchuk</title>
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
'''

CSS = '''
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
  h4 {
    font-size: 1.05rem;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--text);
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
  blockquote {
    border-left: 3px solid var(--accent);
    padding: 0.25rem 1rem;
    color: var(--text-muted);
    margin: 0.5rem 0;
  }
  hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
  }
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
'''

BODY_HEADER = '''
</head>
<body>

<div class="container">

  <header>
    <div class="breadcrumb">
      <a href="/">← Taras Polishchuk</a> › InsideDynamic Architecture
    </div>
    <h1>InsideDynamic Architecture — Target State</h1>
    <p class="subtitle">Two-worlds infrastructure: Plesk ax1 (webhosting) + Coolify containers (apps). Agent-first operations, self-hosted, open-source.</p>
    <div class="meta">
      <div class="meta-item"><strong>Author:</strong> Taras Polishchuk, Solution Architect</div>
      <div class="meta-item"><strong>Date:</strong> 2026-08-25</div>
      <div class="meta-item"><strong>Status:</strong> Proposal for Viktor review</div>
    </div>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-value">2</div><div class="stat-label">Infrastructure Worlds</div></div>
    <div class="stat"><div class="stat-value">56</div><div class="stat-label">Domains on ax1</div></div>
    <div class="stat"><div class="stat-value">8</div><div class="stat-label">KI Agents (KIwerk.one)</div></div>
    <div class="stat"><div class="stat-value">20</div><div class="stat-label">Issues to fix (P0+P1)</div></div>
    <div class="stat"><div class="stat-value">4</div><div class="stat-label">Phased roadmap</div></div>
    <div class="stat"><div class="stat-value">€0-15</div><div class="stat-label">Total monthly cost</div></div>
  </div>
'''

MERMAID_SCRIPT = '''
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    themeVariables: {
      primaryColor: '#1a1a1f',
      primaryTextColor: '#e4e4e7',
      primaryBorderColor: '#14b8a6',
      lineColor: '#2a2a32',
      secondaryColor: '#131316',
      tertiaryColor: '#0a0a0b',
      background: '#0a0a0b',
      mainBkg: '#1a1a1f',
      secondBkg: '#131316',
      tertiaryBkg: '#0a0a0b',
      fontFamily: 'Inter, sans-serif',
    },
    flowchart: { curve: 'basis', padding: 20 },
    securityLevel: 'loose'
  });
</script>
'''

FOOTER = '''
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
'''


def render_inline(text):
    """Convert inline markdown to HTML."""
    # Escape HTML
    text = html.escape(text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    return text


def md_to_html(md):
    """Convert MD to HTML for our architecture page."""
    # Strip frontmatter
    md = re.sub(r'^---.*?---\n', '', md, flags=re.DOTALL)

    lines = md.split('\n')
    out = []
    in_code = False
    in_table = False
    in_list = False
    in_list_ol = False
    in_mermaid = False
    first_h2 = False  # for "Key Decisions" sections

    for line in lines:
        # Mermaid blocks
        if '```mermaid' in line:
            in_mermaid = True
            out.append('<div class="arch-diagram">')
            out.append('<pre class="mermaid">')
            continue
        if in_mermaid:
            if line.strip() == '```':
                out.append('</pre></div>')
                out.append(MERMAID_SCRIPT)
                in_mermaid = False
            else:
                out.append(line)
            continue

        # Regular code blocks
        if line.startswith('```'):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                lang = line[3:].strip() or 'plain'
                out.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue

        # Headings
        if line.startswith('# '):
            out.append(f'<h1>{render_inline(line[2:])}</h1>')
        elif line.startswith('## '):
            out.append(f'<h2>{render_inline(line[3:])}</h2>')
        elif line.startswith('### '):
            out.append(f'<h3>{render_inline(line[4:])}</h3>')
        elif line.startswith('#### '):
            out.append(f'<h4>{render_inline(line[5:])}</h4>')
        # Horizontal rule
        elif line.strip() == '---':
            if in_list:
                out.append('</ul>' if not in_list_ol else '</ol>')
                in_list = in_list_ol = False
            out.append('<hr>')
        # Table
        elif line.startswith('|') and '|' in line[1:]:
            cells = [c.strip() for c in line.strip('|').split('|')]
            if not in_table:
                out.append('<table>')
                out.append('<thead><tr>')
                for c in cells:
                    out.append(f'<th>{render_inline(c)}</th>')
                out.append('</tr></thead><tbody>')
                in_table = True
            elif all(set(c) <= set('-: ') for c in cells):
                continue  # separator
            else:
                out.append('<tr>')
                for c in cells:
                    out.append(f'<td>{render_inline(c)}</td>')
                out.append('</tr>')
        # Bullet list
        elif re.match(r'^[-*]\s', line):
            if in_list and in_list_ol:
                out.append('</ol>')
                in_list_ol = False
            if not in_list:
                out.append('<ul>')
                in_list = True
            content = re.sub(r'^[-*]\s', '', line)
            out.append(f'<li>{render_inline(content)}</li>')
        # Ordered list
        elif re.match(r'^\d+\.\s', line):
            if in_list and not in_list_ol:
                out.append('</ul>')
            if not in_list or not in_list_ol:
                out.append('<ol>')
                in_list = True
                in_list_ol = True
            content = re.sub(r'^\d+\.\s', '', line)
            out.append(f'<li>{render_inline(content)}</li>')
        # Blockquote
        elif line.startswith('> '):
            out.append(f'<blockquote>{render_inline(line[2:])}</blockquote>')
        # Empty line
        elif line.strip() == '':
            if in_list and not '\n'.join(out[-3:]).endswith(f'</li>'):
                out.append('</ul>' if not in_list_ol else '</ol>')
                in_list = in_list_ol = False
            elif in_list and lines.index(line) < len(lines) - 1:
                # Check if next non-empty is still list
                next_idx = lines.index(line) + 1
                while next_idx < len(lines) and lines[next_idx].strip() == '':
                    next_idx += 1
                if next_idx < len(lines) and not re.match(r'^[-*]\s|^\d+\.\s', lines[next_idx]):
                    out.append('</ul>' if not in_list_ol else '</ol>')
                    in_list = in_list_ol = False
        # Paragraph
        else:
            if line.strip():
                out.append(f'<p>{render_inline(line)}</p>')

    # Close open tags
    if in_list:
        out.append('</ol>' if in_list_ol else '</ul>')
    if in_table:
        out.append('</tbody></table>')

    return '\n'.join(out)


def main():
    md_content = SRC.read_text(encoding='utf-8')
    body = md_to_html(md_content)

    html_doc = HTML_HEAD + CSS + BODY_HEADER + body + FOOTER

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(html_doc, encoding='utf-8')
    print(f"✅ Rendered {len(html_doc):,} bytes → {DST}")


if __name__ == '__main__':
    main()

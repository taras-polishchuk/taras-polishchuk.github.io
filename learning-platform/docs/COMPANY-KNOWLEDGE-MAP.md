# InsideDynamic — Knowledge Map (canonical synthesis)

> **Audience:** AI agents + new specialists onboarding to InsideDynamic GmbH.
> **Source of truth:** `work/insidedynamic/01-agents/_system-map.md`, `02-infrastructure/`,
> `06-correspondence/{SA-ARCHITECT*,AGENT-PROMPTS,confluence,notion,JUNIOR-ONBOARDING-PLAN}.md`,
> `09-adr/ADR-013-plane-task-tracker.md`, `09-adr/ADR-014-server-baseline.md`,
> `04-people/{viktor,maksym,dmytro,role-mapping}.md`.
> **Method:** verified facts only; inferences marked `[Inferred]`.
> **Filter rule:** every company fact below is traceable to a Tier-A source (path + section).
> **Last synthesized:** 2026-08-25.

---

## 1. Company profile

| Field | Value | Source |
|---|---|---|
| Legal name | InsideDynamic GmbH | `README.md` §1 |
| Sector | IT consulting + AI agent deployment (KWork One franchise partner) | `_system-map.md`, `notion/EXTRACTION-SUMMARY.md` |
| HQ | Mannheim, Germany (DE compliance regime) | inferred from DE regulation references + `viktor.md` |
| CEO / Auftraggeber | **Viktor Nikolayev** | `04-people/viktor.md`, Notion Page 1 author |
| Headcount (current) | 4 persons: CEO + Solution Architect + 2 executors | `role-mapping.md` |
| Languages | German (canonical for clients) + English (technical) + Ukrainian (Taras) | inferred from artifacts |
| Working model | Hybrid: self-hosted infrastructure + franchise reference architecture | `_system-map.md` |

**What the company does (synthesized):**
1. Builds and operates **8 production AI agents** that other German SMBs buy as a managed service.
2. Hosts and maintains **client web properties** on Plesk webhosting (legacy) and Coolify containers (modern).
3. Sells AI-assisted sales/support/capture infrastructure under the **KWork One franchise** umbrella, drawing reference architecture from KIwerk.one Confluence.

---

## 2. The 8 AI products

Each row is **VERIFIED** from `_system-map.md` + `confluence/INDEX.md`. KIwerk.one pages
are the reference implementations; InsideDynamic adapts them.

| # | Product | Channel | Tech stack (verified) | KIwerk.one ref |
|---|---|---|---|---|
| 1 | **Phone** (KI-Telefonassistent) | Inbound + outbound voice | VAPI → **LiveKit** (migration planned, ADR-002), n8n, telephony, LLM | Page 248381444 (master prompt), 353075201 (Dograh), 2490372 (process) |
| 2 | **Chat** | Multi-channel (uChat) | uChat, LLM, CRM (Odoo) | Page 6946817 (Chatbot Multi-Channel) |
| 3 | **Knowledge** | RAG over client corpora | RAG, **Qdrant**, **Ollama + OpenWebUI**, Docling | Page 19988494, 162332702, 26148865 |
| 4 | **Document** (KI-DMS) | ecoDMS integration | **ecoDMS** (€100/yr subscription), n8n, DATYF | Page 301727746, 302579716 |
| 5 | **Email** (Mail-Support) | Inbound mail | n8n, vector storage, LLM, QA-agent | Page 139132929 |
| 6 | **Feedback** | Customer feedback | n8n, PostgreSQL, Telegram alerts | Page 327516161 |
| 7 | **Lead Crawler** | Web research | n8n AI-nodes, LLM, **Google Places API** | Page 340197377, 126156802 |
| 8 | **Recruiting** (KI-Bewerbungsassistent) | Voice + form | n8n, VAPI, LLM, Google Drive | Page 148340739, 152666113 — **RESTRICTED (EU AI Act, 1.08.2026)** |

**Cross-cutting patterns:**
- Every agent uses **n8n** as orchestrator.
- Knowledge / RAG stack is uniform: **OpenWebUI + Ollama + Qdrant + Docling**.
- LLM runtime: currently **Claude Code** (under Viktor); plan is **Hermes + GPT-5/5.1 via OpenRouter** for personal agents, **Ollama local / Mistral** for client agents.

**Restricted by EU regulation (1.08.2026):**
- � AI scoring of job applicants
- ❌ Real-time AI prompting of sales staff during calls
- → Recruiting agent must operate **without** these features.

---

## 3. Architecture layers

```
┌─────────────────────────────────────────────────────────────┐
│  Edge layer                                                  │
│   Cloudflare (DNS, WAF, CDN, Access) — existing             │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  Application layer                                           │
│   • 8 production AI agents (above)                          │
│   • Linkify products (TalkHub, linkify-products, linkify-jobs)│
│   • 51 consulting client projects on Coolify                │
│   • MVP webapp (TASK-3, planned)                            │
└─────────────────────────────────────────────────────────────�
                            │
┌─────────────────────────────────────────────────────────────┐
│  Orchestration layer                                         │
│   n8n (per-agent) — workflows as code                       │
│   Plane Community Edition (task tracking, MCP-native)       │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  AI / model layer                                            │
│   VAPI (phone) → LiveKit (planned)                          │
│   Ollama + OpenWebUI (local LLM)                            │
│   Claude Code (developer assistant) → Hermes (planned)      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  Data layer                                                  │
│   PostgreSQL 16 (Supabase for flexpos-abrechnung)           │
│   Qdrant (vectors)                                           │
│   Redis 7 (cache, Plane)                                     │
│   MinIO [planned] (S3-compatible object storage)             │
│   ecoDMS (document archive, DE-compliant)                   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure layer                                        │
│   Proxmox VE (hypervisor — existing cluster)                 │
│   Coolify (container PaaS — Master on IONOS, 2 Hetzner slaves)│
│   Hetzner Cloud (4 environments)                            │
│   Plesk ax1 (legacy webhosting, 56 domains)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Infrastructure inventory (verified)

| Asset | Role | Status |
|---|---|---|
| `cp.flxo.cloud` (IONOS, Berlin) | **Coolify Master** | verified live |
| `srv-datq5` (Hetzner, Falkenstein) | Coolify slave — TalkHub (own + RAZERTECH) | knapp (2c/3GB, 5 containers) |
| `alex-parts-prod` (Hetzner) | Coolify slave — Lichtex | **disconnected** (SSH closed, 24.08) |
| `ax1.webpanel24.de` (Plesk, 217.154.83.16) | 30 subscriptions, 56 domains | 12c/23GB/697GB; 2 infected sites; 14 SSL expired; backup OK except 1 unencrypted + 4 stale |
| `dev-server` (Proxmox VM, 192.168.10.124) | Workstation + 7 Claude Code sessions | **no backup, no monitoring** |
| `R720` (Proxmox, `pve-x`) | Agents — 20c/40vCPU/64GB | VERIFIED |
| `R740` (Proxmox) | Client projects + flexpos-abrechnung | VERIFIED (specs TBD) |
| `Debian 13` (new) | Viktor's personal agent | VERIFIED |
| `NAS` | Storage, 2×5TB RAID 0 | VERIFIED |
| Hetzner Storage Box | External backup target (€3.5/TB/mo) | VERIFIED |

**Source-of-truth docs:**
- `02-infrastructure/hardware.md` (verified 24.08 + audit)
- `02-infrastructure/coolify.md` (Coolify Master confirmed on IONOS)
- `06-correspondence/SA-ARCHITECT-ANALYSIS.md` (2-worlds architecture)

---

## 5. Tech stack by project (verified from audit)

| Project | Stack |
|---|---|
| `flexpos-abrechnung` (Billing) | Fastify 5 + React 19 + MUI v6 + PostgreSQL (Supabase) |
| `indyn-portal` (Internal Portal) | Python 3.12 + FastAPI + SQLAlchemy 2.0 async + PostgreSQL 16 (RLS) + Alembic + React 19 + MUI v6 |
| `linkify-products` | React 19 + TS + MUI v6 |
| `linkify-jobs` | Next.js + Docker |
| `netyo-landing` | Astro + Tailwind |
| `netyo-saas` | FastAPI, Makefile, Python/Docker |
| `viktor` (Python utility) | pyproject.toml |

**Cross-project patterns:** TypeScript + React 19 + MUI v6 for frontends; FastAPI/Fastify for APIs; PostgreSQL everywhere.

---

## 6. Roles (verified via Notion Page 1 + Page 2)

| German (Notion) | English | Person |
|---|---|---|
| Director / CEO | Director / CEO | **Viktor Nikolayev** |
| Softwareentwickler | Software Developer | **Maksym Moisa** |
| Ingenieur für Infrastruktur | DevOps Engineer | **Dmytro Yachichko** |
| Solution Architect (new) | Solution Architect | **Taras Polishchuk** |
| 7 other internal + external roles | TBD | hiring |

Sales is a **phase model** (Opener / Setter / Closer), not separate job titles.

---

## 7. Knowledge base index

| System | What's in it | Access |
|---|---|---|
| **Notion** (canonical) | Role definitions, phone sales playbook (Setter-Karte), HR docs | Taras has full read via Notion MCP |
| **KIwerk.one Confluence** (`kiwerkone.atlassian.net/wiki/spaces/te`) | 70 pages: agent reference architecture, master prompts, GDPR, RAG, Coolify setup, n8n, MCP, ecoDMS | Viktor is owner (last edit 2026-07-22); full extract at `06-correspondence/confluence/kiwerk-critical-pages-text.json` (1.3 MB) |
| **Plesk ax1** | 56 domain configs + WP Toolkit state | Viktor (Maksym read-only) |
| **Coolify** | App configs, deployments, environment vars | Viktor + Maksym |
| **Vaultwarden** (planned) | Passwords (post TASK-1) | 4 users on @indyn.de |

**Important:** Notion holds references only. Passwords/MFA/recovery/API keys/secrets/private keys → **Vaultwarden** (ADR-009). This rule is verbatim from Notion Page 1.

---

## 8. EU regulatory boundaries (CRITICAL)

| Rule | Source | Effective |
|---|---|---|
| AI scoring of job candidates — **PROHIBITED** | EU AI Act | 2026-08-01 |
| AI prompting of sales staff during calls — **PROHIBITED** | EU AI Act | 2026-08-01 |
| GDPR Art. 22 (automated decisions) | EU GDPR | ongoing |
| Server backup encryption (§ 203 StGB for healthcare clients) | German law | ongoing |
| DMS mandatory for revenue > €60k | German law | since 2019 |
| Notion stores role references only; Vaultwarden stores secrets | InsideDynamic policy (Notion Page 1) | ongoing |

---

## 9. Active risks (selected, from SA-ARCHITECT-ANALYSIS.md)

| ID | Risk | Severity |
|---|---|---|
| INF-001 | `life.netyo.de` + `indyn.de` infected — investigate BEFORE any update/backup | CRITICAL |
| INF-002 | Server backup unencrypted (GDPR violation) | CRITICAL |
| INF-003 | 14 SSL certs expired (customer-facing) | CRITICAL |
| INF-004 | `alex-parts-prod` SSH closed — Hetzner Console rescue needed | HIGH |
| INF-005 | `srv-datq5` zero buffer — OOM risk | HIGH |
| INF-006 | `netyo.de` wp-config.php missing — restore | HIGH |
| INF-007 | `lic.linkify.cloud` SPOF — RAZERTECH impacted if ax1 dies | HIGH |
| INF-008 | 2 undocumented container stacks outside Coolify | HIGH |
| INF-009 | 4 WordPress not in WP Toolkit | HIGH |
| INF-010 | 339/443 plugins no auto-update | MEDIUM |
| INF-011 | 4 stale backups (linkify.cloud 5 months) | MEDIUM |
| INF-012 | Own sites outdated (insidedynamic.de WP 6.9.7) | MEDIUM |
| INF-013 | Stale backup cron / unknown inventory | LOW |

---

## 10. Confirmed gaps & future work

- **Plane Community Edition** deployment (TASK-2, ADR-013) — greenfield, MCP-native.
- **Vaultwarden** deployment (TASK-1, ADR-009) — 4 users.
- **MVP Web App** (TASK-3) — Next.js 14 trial experience.
- **Voice migration** VAPI → LiveKit (ADR-002).
- **Hermes adoption** for personal agent — Viktor.
- **KIwerk Confluence** still has 50 non-extracted pages — partial coverage.

---

*This map is the single source of truth that the learning platform UI references for the company orientation path. Any company fact in the UI must cite a source row from this map.*

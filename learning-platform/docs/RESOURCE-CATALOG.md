# Resource Catalog

> **Audience:** curriculum reviewers, future maintainers.
> **Date:** 2026-08-25.
> **Source of truth:** `src/lib/data/resources.ts`.

This document is the human-readable counterpart to the runtime data. The runtime
list is the authoritative version. Every entry here is a faithful copy of the
runtime record at time of writing.

---

## Filter policy (operator rule, 2026-08-25)

> "Агент не повинен просто переносити всі посилання з папки в UI. Йому треба
> пройти через фільтр: Raw company knowledge → Authority check → Relevance
> check → Learning objective → Resource selection → Free alternative check →
> Curriculum placement → UI."

Translation: a resource only makes it into the UI if it has been mapped to a
**learning objective** of a **specific module**. There is no "Resources" tab
that dumps the company corpus.

The free-alternative rule applies too:

> "Кожен платний ресурс має мати безкоштовну альтернативу."

Every paid resource in the catalog has at least one free alternative listed
alongside it (either as a `r-*` ID pointing to a free resource, or implicitly
via the module it is referenced from).

---

## Selection rules

| Tier | Cost label | How used |
|---|---|---|
| Free | `free` | Primary recommendation. |
| Free with account | `free-with-account` | Allowed; explicitly labeled. |
| Open-source | `open-source` | Preferred for technical documentation. |
| Paid optional | `paid-optional` | Allowed only when a free primary alternative exists. |
| Paid | `paid` | Never required. Rare. |

**Rejected resources:**
- Dead links (404) at last validation.
- Tutorials for deprecated APIs.
- Resources that require purchase before showing learning content.
- Resources behind paywalls with no free preview.

---

## Catalog summary

- Total: **35** resources.
- Free: **13**.
- Free-with-account (KIwerk.one Confluence): **15**.
- Open-source: **7**.
- Paid-optional: **0**.
- Paid: **0**.

**All resources are free, free-with-account, or open-source.**

---

## Validation record (per resource)

Each entry in `resources.ts` includes:

```
{
  id, title, provider, url, resource_type, cost, difficulty,
  estimated_time_min, learning_objective, why_this_resource,
  last_validated: 'YYYY-MM-DD'
}
```

`last_validated` is updated when the URL is re-checked. If a URL stops working,
remove the resource from the runtime list and re-validate the module that
depends on it.

---

## Resource index (by topic)

### LLM Fundamentals
- `r-anthropic-claude-overview` — Anthropic docs intro
- `r-hf-llm-course-ch1` — HuggingFace LLM Course ch1
- `r-3blue1brown-transformers` — Visual intro to transformers
- `r-deeplearning-ai-llms` — Generative AI with LLMs (DeepLearning.AI)

### Prompt Engineering
- `r-anthropic-prompt-library` — Anthropic Prompt Library
- `r-kiwerk-master-prompt` — KI-Telefon Master-Prompt (real production)

### RAG
- `r-qdrant-docs` — Qdrant Quickstart
- `r-ollama-docs` — Ollama API
- `r-kiwerk-qdrant` — KIwerk.one Qdrant page
- `r-kiwerk-rag-prompting` — KIwerk.one RAG prompts
- `r-docling-docs` — Docling document parsing

### Function Calling / Tool Use
- `r-anthropic-tool-use` — Anthropic tool use docs
- `r-openai-function-calling` — OpenAI function calling guide

### Agents / Frameworks
- `r-kiwerk-telefon-process` — KI-Telefon-Mitarbeiter process (canonical reference)
- `r-mcp-spec` — MCP specification
- `r-mcp-server-quickstart` — Build an MCP server
- `r-langchain-docs` — LangChain intro

### n8n
- `r-n8n-docs-quickstart` — n8n Quickstart
- `r-n8n-ai-nodes` — n8n AI nodes
- `r-kiwerk-n8n-faq` — KIwerk.one n8n FAQ

### Coolify / Infrastructure
- `r-coolify-docs-getting-started` — Coolify docs
- `r-kiwerk-coolify-install` — KIwerk.one Coolify install
- `r-coolify-backup` — KIwerk.one Coolify backup

### Observability
- `r-prometheus-getting-started` — Prometheus docs
- `r-grafana-loki-getting-started` — Loki docs

### EU AI Act / GDPR
- `r-eu-ai-act-official` — EU AI Act official text
- `r-kiwerk-dsgvo-local` — KIwerk.one DSGVO page

### Cost
- `r-llm-pricing-comparison` — LLM pricing tracker

### Productivity tools
- `r-claude-code-docs` — Claude Code docs
- `r-copilot-docs` — GitHub Copilot docs

### Voice / LiveKit
- `r-livekit-docs` — LiveKit docs

### Vaultwarden
- `r-vaultwarden-docs` — Vaultwarden repo

### ecoDMS
- `r-kiwerk-ecodms-install` — ecoDMS Ubuntu 24.04 install

### Plane
- `r-plane-docs` — Plane developers docs

### Web / API
- `r-webhook-vs-api` — Webhooks vs API
- `r-graphql-spec` — GraphQL learn

---

## How to add a new resource

1. Verify the URL works (curl + 200 OK).
2. Add a record to `src/lib/data/resources.ts` with all fields filled.
3. Reference its ID from one or more `concepts[].resource_ids` arrays in `modules.ts`.
4. If the resource is paid, ensure at least one free alternative is also referenced
   from the same module (or note in `RESEARCH-DECISIONS.md` why no free alternative
   exists yet).
5. Bump `last_validated` to the day you verified it.
6. Rebuild the site.

---

*End of Resource Catalog.*

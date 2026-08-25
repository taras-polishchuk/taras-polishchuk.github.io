# Curriculum Architecture

> **Audience:** curriculum designers, future maintainers.
> **Date:** 2026-08-25.
> **Source of truth:** `src/lib/data/{types,modules,resources,index}.ts`.

---

## 1. Three parallel tracks

The platform runs **three concurrent tracks** rather than one linear list. This was
chosen for two reasons:

1. **A new specialist needs orientation before AI fundamentals.** They must
   understand the company context (who we are, what we sell, where knowledge lives)
   before they can reason about prompts or RAG.
2. **The Onboarding Sprint is operational, the AI Specialist Journey is technical.**
   A 4-week sprint produces a shipped artifact. A 90-day journey produces an
   architect. Conflating them produces neither.

```
Orientation (2-3h)
  └── required before Onboarding Sprint OR AI Specialist Journey

Onboarding Sprint (4 weeks)
  ├── Week 1: AI Foundations
  ├── Week 2: Agents + MCP
  ├── Week 3: Production AI
  ├── Week 4: AI for productivity
  └── Capstone: 90-day plan

AI Specialist Journey (90+ days)
  ├── Foundation (transformers, sampling, cost)
  ├── LLM Engineering (versioned prompts)
  ├── RAG Systems
  ├── Tools & Integrations (webhooks, n8n)
  ├── AI Agents
  ├── MCP
  ├── Observability & Evaluation
  ├── Production Operations (EU AI Act, GDPR)
  ├── Architecture (ADRs, Coolify topology)
  └── Capstone: production-style AI system
```

---

## 2. Module structure

Every module has the same shape (see `src/lib/data/types.ts`):

```ts
interface Module {
  id: string;
  track_id: 'orientation' | 'onboarding-sprint' | 'ai-specialist';
  title: string;
  subtitle: string;
  purpose: string;                    // one-sentence "why"
  learning_outcomes: string[];        // 3-5 observable outcomes
  estimated_time_min: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  prerequisites: string[];            // module ids
  unlocked_by_default?: boolean;      // orientation modules + first module of each track
  concepts: Concept[];                // 2-5 atomic units
  practical_artifact?: { ... };       // optional ship-this deliverable
  internal_resources: InternalResource[];  // workspace sources
}
```

### Concept

A concept is an atomic learning unit (30-180 min). It has:

- A title and a one-sentence purpose.
- An estimated time.
- 0+ resource IDs from `resources.ts`.
- An optional practice task.

### Why "concept" and not "lesson"?

A lesson implies a session. A concept is an atomic unit of knowledge that can be
read in 30 minutes or expanded into a 2-hour session. Specialists are adults with
uneven schedules; the unit must be small enough to finish in one sitting.

---

## 3. The artifact-per-stage principle

Every major module in the Onboarding Sprint and the AI Specialist Journey requires
a **practical artifact**:

| Module | Artifact | Why |
|---|---|---|
| Foundation | LLM behavior experiment | Tests understanding of sampling |
| LLM Engineering | Versioned production prompt | Treats prompts as code |
| RAG | Mini RAG system | Proves ingestion + retrieval end-to-end |
| Tools | Validated API integration | Tests webhook + LLM + n8n |
| Agents | Controlled agent workflow | Tests handoff contracts |
| MCP | MCP integration | Tests the standard |
| Observability | Trace + evaluation report | Closes the loop |
| Production | Small internal automation | Backs up state before mutation |
| Architecture | ADR | Practices decision discipline |
| Sprint Week 4 | Role-specific capstone | Demonstrates AI assistance |

**Without an artifact, the specialist cannot claim competence.** This is the same
This is the same pattern InsideDynamic uses internally for the Solution Architect work —
see the company's ADR directory.

---

## 4. Prerequisite graph

The dependency graph is stored on each module as `prerequisites: string[]`.
Helpers in `src/lib/progress/prereq.ts`:

- `isModuleUnlocked(module, completedIds)` — true if all prereqs are in completedIds.
- `getLockReasons(module, completedIds, prereqMap)` — returns human-readable
  reasons for the locked state, used by `ModuleCard.svelte`.

**Unlocked by default:**
- Orientation modules `m-company-overview`, `m-ai-products`, `m-architecture`,
  `m-infrastructure`, `m-tools-and-knowledge` (all orientation modules).
- The first module of each non-orientation track (`m-sprint-w1-foundations`,
  `m-spec-foundation`) — these also require the orientation chain to be useful
  but are unlocked to allow specialists who already know the company to skip
  orientation entirely.

---

## 5. Progression levels

Stored in `src/lib/data/modules.ts → PROGRESSION_LEVELS`:

| Level | Modules required |
|---|---|
| Start | 0 |
| Foundation | 2 |
| Builder | 4 |
| Engineer | 6 |
| Specialist | 8 |
| Capstone | 10 |

Levels are visible in the Journey Map and on the home page status card. They are
not "achievements" with badges — they are honest reporting of where the learner
is in the progression.

---

## 6. Data-driven design

All curriculum content lives in `src/lib/data/`. Components consume the data;
components do NOT hardcode module titles, resource URLs, or prerequisites.

**Consequence:** Adding a new module means adding a row to `MODULES` and (if new
resources are needed) to `RESOURCES`. No component changes are required.

**Consequence:** Reordering the curriculum means editing `prerequisites` on each
module. The UI updates automatically.

---

## 7. What is intentionally NOT in the curriculum

- **Vendor-specific deep dives** beyond what InsideDynamic uses.
  - Example: we don't include LangChain-specific advanced patterns. Specialists
    read the LangChain docs themselves when they need them.
- **General software engineering fundamentals** (algorithms, data structures).
  - Pre-requisite for any engineer; not the platform's job to teach.
- **German language training.** Required for the role, but out of scope.
- **Sales training** for the SDR/AE roles — that lives in Notion Page 2.
- **Project management training** — that's what Plane is for.

---

## 8. Maintenance cadence

| Trigger | Action |
|---|---|
| A new InsideDynamic product is added | Add a concept to `m-ai-products` |
| A KIwerk.one page is updated | Update `confluence/INDEX.md`, then update affected module internal resources |
| A new ADR is ratified | Add a reference from the relevant module |
| A resource URL dies | Remove or replace in `resources.ts`; mark `last_validated` |
| A regulatory change | Update `m-spec-production` immediately |
| Schema change in curriculum | Bump schema note; no data migration needed (TS not runtime) |

---

*End of Curriculum Architecture.*

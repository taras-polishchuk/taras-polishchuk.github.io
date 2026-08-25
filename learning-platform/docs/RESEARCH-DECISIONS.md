# Research Decisions

> **Audience:** curriculum reviewers, future maintainers.
> **Date:** 2026-08-25.

This document captures the **why** behind curriculum decisions — what we
considered, what we rejected, and where we punted.

---

## 1. Three tracks instead of one

**Considered:** one 4-week course that mixes orientation and AI fundamentals.

**Rejected:** orientation and AI fundamentals serve different audiences. A new
specialist needs company context before they can reason about InsideDynamic
products. Mixing them produces neither orientation nor fundamentals.

**Chosen:** three concurrent tracks. Orientation is mandatory, fast (2-3h), and
precedes the other two. Onboarding Sprint is 4 weeks and operationally
oriented. AI Specialist Journey is 90+ days and technically oriented.

---

## 2. Onboarding Sprint is 4 weeks, not a semester

**Considered:** 12-week course that covers everything.

**Rejected:** specialists are adults with day jobs. Long courses get abandoned.

**Chosen:** 4-week sprint with weekly milestones and a capstone. Maps directly
to the company AI-specialist onboarding syllabus (operator's curated curriculum).

---

## 3. AI Specialist Journey is 90+ days, not 4 weeks

**Considered:** packing everything into the 4-week sprint.

**Rejected:** the AI Specialist Journey requires depth that a 4-week sprint
cannot provide. RAG, agents, MCP, observability, and architecture each need
their own week of focused work.

**Chosen:** separate 90-day track. Specialists pursue this AFTER the Onboarding
Sprint.

---

## 4. Filter rule (operator-added 2026-08-25)

**Operator instruction:**

> "Агент не повинен просто переносити всі посилання з папки в UI. Йому треба
> пройти через фільтр: Raw company knowledge → Authority check → Relevance
> check → Learning objective → Resource selection → Free alternative check →
> Curriculum placement → UI."

**Implemented as:**
- No raw "document dump" view in the UI.
- Every resource in `resources.ts` has a `learning_objective` field.
- Every concept has at least one resource (or zero if it's purely internal).
- Resources are referenced by concept, not by module directly. The resource
  catalog is a debug view, not the primary navigation.

---

## 5. Free-first resource policy

**Considered:** paid courses like DeepLearning.AI paid tier, AIE, Coursera
specializations.

**Rejected:** every paid course has a free alternative. Requiring a paid course
excludes some specialists and increases onboarding cost.

**Chosen:** free / free-with-account / open-source for primary recommendations.
Paid = optional alternative only.

---

## 6. Two parallel timelines (operator 2026-08-25)

**Operator correction:** the original mission brief had a single 4-week course.
The operator added that the curriculum should run two parallel timelines:

- Onboarding Sprint (4 weeks).
- AI Specialist Journey (90+ days).

Both share the same Orientation pre-requisite.

---

## 7. What is intentionally NOT in the curriculum

- **Vendor deep dives** beyond what InsideDynamic uses.
  - LangChain is referenced; CrewAI / AutoGen are not.
- **General software engineering** (algorithms, data structures, OS fundamentals).
- **German language training.**
- **Sales training** (Notion Page 2 has the Sales playbook).
- **Project management training** (Plane is the source of truth).

---

## 8. What we punted on

| Topic | Why deferred | Plan |
|---|---|---|
| Per-role specific tracks (QA / Frontend / Infra) | The Junior Onboarding Plan covers this in narrative form; converting to structured data is a separate mission | After v1 ships, add `m-sprint-w1-qa`, `m-sprint-w1-fe`, `m-sprint-w1-infra` |
| KIwerk.one Confluence coverage beyond the 19 extracted pages | 50 pages remain; the extraction is incomplete | Re-extract in a follow-up mission; add as resources |
| Hands-on lab environment | Requires deployable sandbox; out of scope for static site | Future Coolify-deployed lab |
| Quiz / knowledge check components | Requires backend for cross-user analytics | Future: optional server-side progress sync |
| Mentor pairing UI | Requires multi-user accounts | Out of scope; pairing happens via Telegram / Plane |

---

## 9. How curriculum quality is judged

A module is "done" when:
1. It has a clear `purpose`.
2. Every concept has at least one resource OR a clear justification for why not.
3. At least one practical artifact is defined for major modules.
4. Every internal resource points to a real workspace path.
5. Every external resource has a working URL, last-validated date, and rationale.
6. Prerequisites form an acyclic graph.
7. A specialist who follows the module can answer the learning outcomes.

---

*End of Research Decisions.*

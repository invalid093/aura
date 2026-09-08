# Decision Records (ADRs)

One file per significant decision: `ADR-XXXX-<slug>.md`.

A decision is "significant" if reversing it would invalidate work already done, or if it changes
anything Claude is forbidden to change silently (`CLAUDE.md`): the research question, hypotheses,
metrics, test sets, assumptions, fault definitions, experimental criteria, or interpretation.

Format: Context → Decision → Alternatives considered → Consequences → Status → Revisit conditions.

| ID | Title | Date | Status |
|----|-------|------|--------|
| ADR-0001 | Repository structure and infrastructure scale | 2026-09-08 | Accepted |
| ADR-0002 | Research question selection | 2026-09-08 | Accepted (provisional on TV-N1) |
| ADR-0003 | Aircraft model selection | 2026-09-08 | Accepted (blocked on A-1) |
| ADR-0004 | Storage strategy: no Git LFS, no cloud | 2026-09-08 | Accepted |
| ADR-0005 | Sensor suite excludes GPS | 2026-09-08 | Accepted (with mandatory sensitivity run) |
| ADR-0006 | Licensing deferred; no licence during Phase 0 | 2026-09-08 | Accepted (supersedes an earlier MIT licence) |

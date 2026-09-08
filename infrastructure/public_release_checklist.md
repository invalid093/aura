# Public Release Checklist

**Run before every push to a public remote.** If any item is uncertain: **do not push. Flag it for
researcher review.**

Authoritative policy: [`../docs/public_repository_policy.md`](../docs/public_repository_policy.md)

Governing rule:

> **Publish the scientific record, not the entire laboratory.**

And for any individual artefact:

> Does publishing this materially improve scientific transparency, reproducibility, or
> understanding of AURA? If not, keep it local or archive it.

**Both the working tree and the git history must pass.** They are audited separately — information
can exist in an earlier commit and no longer be in the current tree.

---

## Privacy

- [ ] No personal email addresses, phone numbers, or home addresses.
- [ ] No usernames that reveal private accounts; no private URLs.
- [ ] **Commit author *and* committer identity checked** — git metadata is published alongside file
      contents, and is the easiest thing to miss.
- [ ] No local machine paths (`C:\Users\...`, `/Users/...`, `Downloads/`, `Desktop/`, `AppData/`,
      `OneDrive/`). Documentation uses repository-relative paths.
- [ ] No machine names, local usernames or environment-specific configuration.
- [ ] No private correspondence, browser/session data, or unpublished documents belonging to others.
- [ ] Legitimate authorship attribution **retained** — the objective is preventing unnecessary
      exposure, not anonymising the researcher.

## Security

- [ ] No `.env`, `*.pem`, `*.key`, `credentials.*`, `secrets.*`, SSH material or cloud credentials.
- [ ] Secret scan run over the working tree **and** the full history.
- [ ] No placeholder secrets that could be mistaken for real credentials.
- [ ] `.gitignore` covers secret patterns — and is not assumed sufficient on its own.
- [ ] If a real credential was ever committed: stop; do not merely delete it in a later commit;
      determine whether it must be revoked; remove it from history; document the incident privately.

## Licensing

- [ ] **No `LICENSE` file** — present or anywhere in history.
- [ ] No accidental claim implying permission to reuse.
- [ ] README states plainly that no reuse licence has been granted.
- [ ] Third-party material carries correct attribution; unresolved licences are documented as
      unresolved rather than assumed permissive.

## Scientific integrity

- [ ] Every claim is supported by identified evidence.
- [ ] Exploratory results labelled; not presented as findings.
- [ ] Validated vs preliminary vs exploratory clearly distinguished.
- [ ] Reconnaissance observations are **not** presented as experimental results.
- [ ] Overstating language reviewed (*demonstrates, proves, solves, guarantees, robust, reliable,
      superior, state of the art, novel, unprecedented, significantly improves, validated*).
- [ ] Limitations stated where a reader will see them, not only in an appendix.
- [ ] Negative results and important failures present, not omitted.
- [ ] README does not make the project look more mature than it is.

## Reproducibility

- [ ] Findings trace: finding → analysis → experiment ID → dataset ID → configuration →
      code/model version.
- [ ] Experiment IDs, dataset IDs and configurations referenced in reports actually exist.
- [ ] Figures cite the script and commit that produced them.
- [ ] Traceability infrastructure exists even where no findings do yet.

## Data

- [ ] No bulk raw output committed merely because it exists.
- [ ] Published data limited to what is necessary for reproducibility, not cheaply regenerable, or
      a benchmark artefact.
- [ ] Manifests, checksums, seeds and generation procedures present for data that is *not* published.
- [ ] No scientifically important evidence deleted merely to shrink the repository.
- [ ] Everything published is legally publishable.

## Code

- [ ] Published code is scientifically useful: methodology, experiment definitions, analysis,
      reproducibility scripts, schemas, validation.
- [ ] Scratch code, debugging scripts, obsolete implementations and machine-specific utilities
      excluded.
- [ ] **No methodological detail withheld under cover of this rule.** If a conclusion depends on an
      implementation choice, that choice is documented.

## Literature

- [ ] No unauthorised copies of copyrighted papers; no binary paper files.
- [ ] No substantial portions of sources reproduced; summaries original.
- [ ] Literature claims accurately represent the source, including the verification level of the entry.

## Structure and coherence

- [ ] Repository makes sense to someone who knows nothing about AURA.
- [ ] Documentation links resolve; referenced files exist; repository-relative paths work.
- [ ] No accidental binary files; no unnecessary large tracked files.
- [ ] No stale or contradictory project descriptions.
- [ ] Working tree clean.

## Commit hygiene

- [ ] Commits describe meaningful changes, prefixed by area (`research:`, `literature:`,
      `experiment:`, `analysis:`, `docs:`, `infrastructure:`, `results:`).
- [ ] No trivial messages (`update`, `fixed`, `final2`) unless they affect reproducibility.
- [ ] Public history not rewritten to conceal legitimate research development.

---

# Audit record

## 2026-09-08 — Final pre-publication audit (Phase 0)

**Scope:** full working tree (73 files), complete git history, git metadata, repository
configuration. **Auditor:** Claude, under `../docs/public_repository_policy.md`.

| # | Item | Result |
|---|------|--------|
| 1 | Privacy audit | **PASS** — no personal email, phone, address or private URL in tree or history |
| 2 | Git history audit | **PASS** — 1 commit at audit time, 72 files, no deletions, no licence artefact, 0 unreachable commits |
| 3 | Git identity verified | **PASS** — derived from `gh api user` (id 228505230, login `invalid093`), not guessed |
| 4 | No personal email exposed | **PASS** — GitHub noreply address; authorship attribution retained |
| 5 | No personal machine paths | **PASS** — only `downloads/` matches were NASA NTRS public URLs |
| 6 | No credentials or secrets | **PASS** — no key/token/certificate patterns in tree or history |
| 7 | No unauthorised copyrighted material | **PASS** — no binary files; citation metadata and links only |
| 8 | No proprietary/private material | **PASS** — all sources public and unclassified |
| 9 | No licence file | **PASS** — absent from tree and from all history |
| 10 | No accidental licensing claims | **PASS** — remaining "MIT" mentions document its *removal* (ADR-0006) |
| 11 | Raw data policy | **PASS** — no datasets exist yet; manifest and provenance infrastructure in place |
| 12 | Large generated data excluded | **PASS** — 282 KB total tracked; largest file 39 KB |
| 13 | Code publication reviewed | **PASS** — no code tracked yet; implementation directories are placeholders |
| 14 | README represents maturity | **PASS** — states Phase 0, no validated findings, unverified novelty |
| 15 | Scientific claims reviewed | **PASS** — see note below |
| 16 | Preliminary vs validated distinguished | **PASS** — separate README sections; preliminary items labelled reconnaissance observations |
| 17 | Research log reviewed | **PASS** — DATE/DECISION/RATIONALE/EVIDENCE/IMPACT/NEXT STEP; no diary material |
| 18 | Literature reviewed | **PASS** — 70 entries with stratified verification field; unverified authorship marked, not invented |
| 19 | Third-party dependencies documented | **PASS** — `EXTERNAL_SOURCES.md`; all 6 recorded as licence-unverified |
| 20 | Internal links verified | **PASS** — all markdown links resolve |
| 21 | Repository structure reviewed | **PASS** — reading order provided in README |
| 22 | Evidence/provenance structure verified | **PASS** — registry, schemas, manifests, test-set access log in place |
| 23 | `.gitignore` verified | **PASS** — excludes bulk data, caches, checkpoints, secrets; manifests explicitly re-included |
| 24 | Working tree clean | **PASS** |

**Scientific-claims note (item 15).** Scanned for: *demonstrates, proves, solves, guarantees,
unprecedented, state of the art, significantly improves, superior, novel, robust, reliable,
validated*. Findings: `demonstrates`, `solves`, `unprecedented`, `superior`,
`significantly improves` — zero occurrences. `guarantees` and `robust` — used only to describe
**cited third-party results** (conformal coverage, RAIM integrity, deep-ensemble comparisons), each
attributed and carrying its caveat. `novel`/`novelty` — every occurrence concerns *assessing*
novelty or stating it is **unverified**. `validated` — every occurrence is either "no validated
results", an assumption-status label, or "not a validated model of a real F-16". `proves` — only
in the idiom "proves intractable". **No unsupported claim found; no rewording required.**

### Issues found and corrected during this audit cycle

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | MIT `LICENSE` added by default during setup, against policy §7 | **Blocking** | File removed; README states no licence granted; [`ADR-0006`](../docs/decisions/ADR-0006-licensing-deferred.md) records the decision; unpublished commit amended so no licence ever existed in publishable history |
| 2 | Commit author/committer carried a personal email address | **Blocking** | Amended to the GitHub noreply address verified via `gh api user`; reflog expired and objects pruned so the pre-amend commit is unrecoverable |
| 3 | README lacked the required maturity sections | Non-blocking | Rewritten with Current Research Question / Status / Validated Findings / Preliminary Findings / Open Questions / Known Limitations, plus a reading order |
| 4 | Research log used a narrative format | Non-blocking | Rewritten to DATE/DECISION/RATIONALE/EVIDENCE/IMPACT/NEXT STEP |
| 5 | `docs/public_repository_policy.md` referenced but absent | Non-blocking | Created as the policy of record |
| 6 | Default branch was `master` | Cosmetic | Renamed to `main` |

### Non-blocking observations carried forward

- Implementation directories (`aircraft/`, `sensors/`, `faults/`, `estimation/`, `diagnosis/`,
  `autonomy/`, `simulation/`) are empty placeholders held by `.gitkeep`. Justified by the
  architecture; they will be populated in Phase 1b.
- The repository contains **no code**. This is correct for Phase 0 but means the code-publication
  and reproducibility-traceability items above are verified as *infrastructure*, not as practice.
  Both must be re-audited at the first Phase 1 push.
- The literature index rests largely on abstract-level evidence (3 of 70 read in full). This is
  disclosed in the index, its README and the review — but a reader who skips those could still
  over-read the gap claims.

---

## 2026-09-08 — Second audit: first push containing code, data and results (EXP-0002)

The first release verified the code, raw-data and provenance sections **as infrastructure**. This
push exercises them **in practice** for the first time, so they were audited as if for the first time.

| Area | Result |
|---|---|
| Privacy (tree + history + metadata) | **PASS** — only occurrences of `C:\Users`-style patterns are the policy text describing what to scan for. All 4 commits carry the GitHub noreply identity |
| Secrets | **PASS** — no key, token, certificate or credential-assignment patterns |
| Licence | **PASS** — no `LICENSE` file; no licence claim in any source file. **AeroBenchVVPython was found to be GPL-3.0 and was deliberately NOT vendored** (ADR-0007), so no copyleft obligation is inherited |
| **Raw data policy (first real test)** | **PASS** — 90 trajectory files (18 MB) generated; **0 committed**. Published instead: dataset manifest `DS-0001.yaml`, per-file SHA-256 checksums, generation script, configuration and seedless-determinism guarantee. The recipe is published, the bulk is not |
| **Code publication (first real test)** | **PASS** — 9 files, 1609 lines: model, trim solver, fault injection, controller, simulation harness, analysis, pilot verification, experiment runner, figures. Every file is methodology or reproducibility code. No scratch, debug or machine-specific utilities. **No methodological detail withheld** — the full model, metric and threshold are in the published code and config |
| Binary files | **PASS** — 3 PNG figures, each generated by a committed script with a sidecar JSON recording experiment, dataset, script and commit |
| Scientific claims | **PASS** — see note below |
| Preliminary vs validated | **PASS** — README separates one validated result (EXP-0002) from literature reconnaissance observations, and states explicitly what the result does *not* show |
| Failures published | **PASS** — FAIL-0001 is published in full, including that the invalidated condition had produced the most favourable-looking numbers |
| Provenance traceability | **PASS** — finding → report → `exp0002_results.json` → `DS-0001` → config SHA-256 → commit; figures carry sidecars |
| Internal links | **PASS** — all markdown links resolve from their own directory |
| Total staged | 571 KiB |

**Scientific-claims note.** Substantive (non-policy) occurrences: `demonstrates`, `solves`,
`unprecedented`, `superior`, `significantly improves` — **zero**. `proves` — four, all either the
idiom "proves intractable" or the epistemically correct code comment *"trim convergence proves an
equilibrium exists; it does not prove the closed loop can hold it"*. `guarantees` — one, describing
conformal prediction with its exchangeability caveat. `robust` — two new uses, both attached to the
measurements that support them (ρ ≥ 0.9992 across step sizes; magnitude and duration sweeps).

**Claims specifically checked against evidence:**
- "PASS" is reported **with its thin margin stated in the same sentence** (1 verdict flip in 153).
- The invalidated condition is not quietly dropped — its exclusion, and the fact that it was the
  most favourable result, is in the README, FINDINGS, report and handoff.
- No claim is made that uncertainty-aware diagnosis works; the report states explicitly that
  EXP-0002 cannot establish that.

**Non-blocking observations carried forward**

- TV-D10 (self-implemented aircraft model) is **HIGH and unmitigated**, and is disclosed in the
  README, FINDINGS, the report's limitations and the handoff.
- EXP-0002 is noise-free; every distance is an upper bound. Disclosed in all four places.
- The systematic literature search remains outstanding, so no novelty claim may be published.

---

## 2026-09-08 — Third audit: EXP-0010 (analysis code, results, figures)

| Area | Result |
|---|---|
| Privacy / machine paths | **PASS** — clean in tree, history and commit metadata |
| Secrets | **PASS** |
| Licence | **PASS** — no licence file; no licence claim in any source file |
| Raw data | **PASS** — 0 bulk trajectory files committed; DS-0001 (90 files, 18 MB) stays unpublished and regenerable. **EXP-0010 generated no new bulk data at all** — it reused DS-0001 |
| **Compact derived data — a deliberate exception** | The 3.4 KB `P_iso_surface.npz` (360 values: the central result surface) was being excluded by a `.gitignore` rule written for *large* arrays. It is now **published**, with the exception documented in `.gitignore`: it lets a reader reproduce the figures without re-running the experiment, which is exactly what the data policy asks for |
| Code | **PASS** — 4 new files, 857 lines: analysis module, pilot verification, runner, figures. All methodology or reproducibility code |
| Scientific claims | **PASS** — see note |
| Preliminary vs validated | **PASS** — README states two validated results and leads with the one that *weakens* a project premise |
| Failures / corrections published | **PASS** — the circularity self-correction is published in the report, FINDINGS, the handoff and as a machine-readable artefact |
| Provenance | **PASS** — figures carry sidecars; results record config SHA-256 and commit; registry entry created |
| Internal links | **PASS** |
| Total staged | ~800 KiB |

**Scientific-claims note.** Substantive occurrences of `demonstrates`, `solves`, `unprecedented`,
`superior`, `significantly improves`: **zero**. `guarantees`: one, describing conformal prediction
with its caveat. `proves`: six — four are the idiom "proves intractable", one is the epistemically
correct code comment about trim, and two state that a closed form *proves* two fault classes
intersect, which is an algebraic identity and therefore correct usage. `robust`: every use is
attached to the measurement supporting it (Δ ≤ 0.01 for heavy tails; ordering preserved across
magnitudes; 1.83× spread).

**Claims specifically checked against evidence:**
- Every probability is labelled an **upper bound** wherever it appears, because the classifier knows
  the templates exactly.
- η ≥ 10 is labelled an **experimental stress level**, not a sensor claim, in the spec, config,
  report and figures.
- The result that *weakens* AURA's premise leads the README and FINDINGS rather than being buried.
- A claim from the first draft was **downgraded after testing it**, and the downgrade is published.

---

## 2026-09-08 — Fourth audit: EXP-0011 (magnitude grid, analysis, results)

| Area | Result |
|---|---|
| Privacy / machine paths | **PASS** |
| Secrets | **PASS** |
| Licence | **PASS** — no licence file; no licence claim in source |
| Raw data | **PASS** — DS-0002 is 416 files / 40 MB, **0 committed**; manifest + per-file SHA-256 + generation script published instead. DS-0001 (18 MB) likewise unpublished |
| Compact derived data | The 2.8 KB `P_class_surface.npz` is published, under the same documented `.gitignore` exception as EXP-0010's surface: it lets a reader reproduce the figures without re-running |
| **Cross-platform portability (caught in this audit)** | `template_index.json` recorded 488 paths with Windows backslashes, which would not resolve on Linux or macOS. Normalised to POSIX separators and the generator patched so future runs are portable. Not a privacy issue, but it would have broken reproduction on any other machine |
| Code | **PASS** — 4 new files, 1047 lines: analysis module, magnitude-grid generator, runner, figures. All methodology or reproducibility code |
| Scientific claims | **PASS** — `demonstrates`, `solves`, `unprecedented`, `superior`, `significantly improves`: zero substantive occurrences |
| Preliminary vs validated | **PASS** — README leads with the fact that three experiments have now failed to find the motivating ambiguity |
| Failures and self-corrections published | **PASS** — all three EXP-0011 design defects are published in the report, the registry entry, FINDINGS and the handoff, including the bug that forced a full re-run |
| Provenance | **PASS** — figures carry sidecars; results record config SHA-256 and commit; DS-0002 manifest links to parent DS-0001 |
| Internal links | **PASS** |
| Total staged | ~853 KiB |

**Claims specifically checked against evidence:**
- Every probability is labelled an upper bound (template families still assumed known, TV-M5).
- The magnitude range is labelled **experimental**, not physically calibrated, in the spec, config
  and report.
- The headline finding — that being wrong about magnitude is worse than being uncertain — is
  reported together with the fact that Case B measures this **because of a flaw in the
  pre-registration**, not by design.
- Post-hoc analyses (window-local detectability, Case B′) are labelled post-hoc wherever they appear,
  and the pre-registered versions are still reported.

---

# PUBLIC RELEASE: PASS

Audited 2026-09-08 against `../docs/public_repository_policy.md`. First audit: all 24 items pass,
both blocking issues corrected before publication. Second audit (code + data + results): all items
pass. Third audit (EXP-0010): all items pass; one deliberate publication decision (compact derived
result surface). Fourth audit (EXP-0011): all items pass; one portability defect found and fixed
(Windows path separators in a published index). No blocking issues in audits two through four.

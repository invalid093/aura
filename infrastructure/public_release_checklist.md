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

# PUBLIC RELEASE: PASS

Audited 2026-09-08 against `../docs/public_repository_policy.md`. All 24 checklist items pass; both
blocking issues found were corrected before publication. Repository approved for public GitHub.

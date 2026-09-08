# Public Repository Policy

**Status:** Authoritative for all publication decisions.
**Operational checklist:** [`../infrastructure/public_release_checklist.md`](../infrastructure/public_release_checklist.md)
**Agent obligations:** [`../CLAUDE.md`](../CLAUDE.md)

---

## 1. Governing principle

> **Publish the scientific record, not the entire laboratory.**

The AURA repository is a **public-facing research record**, not a mirror of the private
computational environment. It should let an external researcher follow:

```
Research Question → Scientific Motivation → Literature / Gap → Hypothesis
→ Methodology → Experiments → Evidence → Findings → Limitations → Next Question
```

It should **not** contain everything generated during development.

### Priorities

Publish: scientific reasoning, research questions, methodology, experiment definitions, validated
findings, supporting evidence, reproducibility information, important failures and negative
results, research progress, high-quality documentation.

Do not prioritise: volume of code, volume of data, raw computational output, temporary experiments,
internal notes, private information, unnecessary implementation details.

---

## 2. Publication hierarchy

| Level | Contents | Publish? |
|---|---|---|
| 1 — Public research narrative | README, research questions, methodology, direction, findings | Yes |
| 2 — Scientific evidence | Experiment definitions, metrics, configurations, figures, tables, validation results | Yes |
| 3 — Reproducibility infrastructure | Analysis code, experiment scripts, small reference data, manifests, schemas | Yes |
| 4 — Large evidence | Raw simulation data, large datasets, model checkpoints, archives | Only when scientifically justified |

| Category | Public? |
|---|---|
| Research question, literature analysis, gap, hypotheses, methodology | YES |
| Experiment definitions, validated results, important negative results | YES |
| Reproducibility documentation | YES |
| Small reference datasets | CASE-BY-CASE |
| Large raw datasets | GENERALLY NO |
| Temporary simulation output, scratch code | NO |
| Credentials, private information, unverified proprietary material | NEVER |
| Licence file | NO FOR NOW (§7) |

---

## 3. Privacy — never commit

Personal email addresses, phone numbers, physical addresses, private account information,
usernames revealing private accounts, private URLs, browser/session data, private correspondence,
or unpublished documents belonging to others.

**This applies to git metadata as well as file contents.** The commit author and committer identity
is published alongside the files and is the easiest thing to miss.

The objective is to prevent *unnecessary* exposure of private information — **not to anonymise
authorship.** Legitimate public attribution containing the researcher's name is fine.

If uncertain whether something is appropriate: **do not commit it; flag it for researcher review.**

## 4. Machine-specific information

No local paths (`C:\Users\...`, `/Users/...`, `Downloads/`, `Desktop/`, `AppData/`, `OneDrive/`),
machine names, local usernames, private drive names, or environment-specific configuration.
Documentation uses repository-relative paths so it remains understandable on another computer.

## 5. Credentials and secrets

Never commit `.env`, `*.pem`, `*.key`, `credentials.*`, `secrets.*`, API keys, tokens, passwords,
SSH material, certificates or cloud credentials. `.gitignore` covers these patterns, but
`.gitignore` is **not** assumed sufficient — the working tree and history are both scanned.

Do not commit placeholder secrets that resemble real credentials.

If a real credential is ever committed: **stop**; do not merely delete it in a later commit;
determine whether it must be revoked; remove it from history; document the incident privately.

## 6. Data

Do not publish raw data automatically. The repository generally carries dataset descriptions, IDs,
manifests, metadata, provenance, checksums, generation procedures, representative small examples,
links to public source datasets, and the configurations and seeds able to reproduce important
datasets.

> **Publish the recipe and the evidence rather than millions of redundant data points.**

A dataset is published only when it clears all of: legally publishable; necessary for
reproducibility; reasonably small; not cheaply regenerable; free of private or proprietary content;
and materially improves transparency.

**Do not delete scientifically important evidence merely to make the repository smaller.** If a
dataset is valuable but too large for GitHub, document where it should eventually be hosted.

## 7. Licensing

**No licence during Phase 0.** No MIT/BSD/Apache/GPL is added merely because it is conventional.
Until a deliberate decision is made, the repository carries no licence and implies no permission to
reuse.

The reason is substantive: AURA's external dependencies and research assets have not had their
licensing conditions verified. Outbound terms cannot responsibly be set before inbound obligations
are known.

When the project reaches suitable maturity, source-code licence, dataset licence, documentation
licence, publication rights and third-party obligations are evaluated **separately**.
See [`decisions/ADR-0006-licensing-deferred.md`](decisions/ADR-0006-licensing-deferred.md).

## 8. Code

Publish code that contributes to methodology, analysis, reproducibility, validation or scientific
understanding. Do not publish scratch code, debugging scripts, abandoned prototypes,
machine-specific utilities or disposable generated code.

**This rule must never be used to conceal a methodological detail.** If a scientific conclusion
depends on an implementation choice, that choice is documented sufficiently for independent
evaluation.

## 9. Scientific honesty

- Exploratory, validated and final results are distinguished, and exploratory work is labelled.
- Reconnaissance observations are never presented as experimental results.
- Claims carry evidence classes: `FACT` / `CALCULATION` / `OBSERVATION` / `INTERPRETATION` /
  `HYPOTHESIS` / `ASSUMPTION` / `LIMITATION`.
- Overstating language (*demonstrates, proves, guarantees, robust, superior, novel, validated*) is
  used only where evidence supports it.
- **The repository must not appear more mature than the research.** At Phase 0,
  *"Validated findings: none"* is the correct and honest status.
- Scientifically meaningful failures and negative results are published, not hidden.

Before publishing a major scientific claim: the experiment is documented, the dataset identified,
the configuration preserved, the analysis reproducible, the validation stage passed, the limitations
documented, and the wording within the evidence.

## 10. Literature

Citation metadata, DOIs, official and legitimate open-access links, and original summaries only.
**No unauthorised copies of copyrighted papers**, and no reproduction of substantial portions of a
source. Literature claims must accurately represent what the source says — including the
verification level of the entry.

## 11. Third-party material

For every external code library, dataset, aircraft model, image, figure or document, record source,
version, attribution, licence and usage restrictions.

**Public downloadability does not imply reusability.** Where licensing is unresolved, document the
uncertainty and make no outbound licensing claim. Register:
[`../data/manifests/EXTERNAL_SOURCES.md`](../data/manifests/EXTERNAL_SOURCES.md).

## 12. Research log

Public entries follow: **DATE / DECISION / RATIONALE / EVIDENCE / IMPACT / NEXT STEP.**
Scientifically meaningful decisions are retained; private diary-style material is not published.

## 13. Commits and branches

Commit messages describe meaningful scientific or engineering changes, prefixed by area:
`research:`, `literature:`, `experiment:`, `analysis:`, `docs:`, `results:`, `infrastructure:`.
Avoid `update`, `fixed`, `final2` and similar unless they materially affect reproducibility.

**Public history is not rewritten to conceal legitimate research development.** Rewriting is
reserved for removing private information, credentials or licensing artefacts *before* publication.

Branches (`research/*`, `experiment/*`, `feature/*`) are used only when an effort is substantial
enough that it should not immediately modify the stable research record. No complex Git process
without a practical reason.

## 14. Release gate

Every push runs [`../infrastructure/public_release_checklist.md`](../infrastructure/public_release_checklist.md),
which covers privacy, security, scientific integrity, reproducibility, data, code, literature,
licensing and commit hygiene — across **both** the working tree and git history.

If any item is uncertain: **do not push. Flag it for researcher review.**

---

## 15. The final test

> Does publishing this artefact materially improve scientific transparency, reproducibility, or
> understanding of AURA?

If yes, consider publishing. If no, keep it local or archive it. If it contains private or sensitive
information, unnecessary raw data, or unresolved material that could mislead a reader: **do not
publish it.**

The standard is: **public, transparent, reproducible, scientifically honest — but not unnecessarily
exposed.**

Do not let the desire to have a public repository override scientific integrity.

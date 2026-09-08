# Public Release Checklist

**Run before every push to a public remote.** If any item is uncertain: **do not push. Flag it for
researcher review.**

The governing rule for what belongs in the public repository:

> **Publish the scientific record, not the entire laboratory.**

And for any individual artefact:

> Does publishing this materially improve scientific transparency, reproducibility, or
> understanding of AURA? If not, keep it local or archive it.

---

## Privacy

- [ ] No personal email addresses, phone numbers, or home addresses.
- [ ] No usernames that reveal private accounts.
- [ ] **Check the commit author and committer identity, not just file contents.** Git metadata is
      published too, and is the easiest thing to miss.
- [ ] No local machine paths (e.g. `C:\Users\<name>\...`). Documentation uses repository-relative
      paths so it remains understandable on another computer.
- [ ] No private correspondence, browser/session data, or unpublished documents belonging to others.

## Security

- [ ] No `.env`, `*.pem`, `*.key`, `credentials.*`, `secrets.*`, SSH material or cloud credentials.
- [ ] Secret scan run over the working tree **and** the commit history.
- [ ] If a credential was ever committed: stop; do not merely delete it in a later commit; determine
      whether it must be revoked; remove it from history; document the incident privately.

## Scientific integrity

- [ ] Every claim is supported by identified evidence.
- [ ] Exploratory results are labelled exploratory and are not presented as findings.
- [ ] Validated and final results are distinguished from each other.
- [ ] Limitations are stated where a reader will actually see them, not only in an appendix.
- [ ] No wording exceeds the evidence. Hypotheses are not phrased as conclusions.
- [ ] Negative results and important failures are present, not omitted.
- [ ] The README does not make the project look more mature than it is.

## Reproducibility

- [ ] Every published finding traces: finding → analysis → experiment ID → dataset ID →
      configuration → model/code version.
- [ ] Experiment IDs, dataset IDs and configurations referenced in reports actually exist in the
      repository.
- [ ] Figures cite the script and commit that produced them.

## Data

- [ ] No bulk raw output committed merely because it exists.
- [ ] Published data is limited to what is necessary for reproducibility, cannot reasonably be
      regenerated, or constitutes a benchmark artefact.
- [ ] Manifests, checksums, seeds and generation procedures are present for data that is *not*
      published.
- [ ] Everything published is legally publishable.

## Code

- [ ] Published code is scientifically useful: methodology, experiment definitions, analysis,
      reproducibility scripts, schemas, validation.
- [ ] Scratch code, debugging scripts, obsolete implementations and machine-specific utilities are
      excluded.
- [ ] **No methodological detail is being withheld under cover of this rule.** If a conclusion
      depends critically on an implementation detail, that detail is documented sufficiently for
      independent evaluation.

## Literature and licensing

- [ ] No copyrighted papers uploaded. Citation metadata, DOIs and official links only.
- [ ] No substantial portions of papers reproduced; summaries are original.
- [ ] External material carries correct attribution.
- [ ] Nothing implies permission to reuse that has not been deliberately granted (see
      [`../docs/decisions/ADR-0006-licensing-deferred.md`](../docs/decisions/ADR-0006-licensing-deferred.md)).

## Commit hygiene

- [ ] Commits describe meaningful scientific or engineering changes, prefixed by area
      (`research:`, `literature:`, `experiment:`, `analysis:`, `docs:`, `results:`).
- [ ] No trivial commits (`update`, `fixed`, `final2`) unless they materially affect reproducibility.
- [ ] Public history is not rewritten to hide inconvenient research development. Rewriting is
      reserved for removing private information or credentials before publication.

---

## Record of checks performed

| Date | Commit | Checked by | Issues found | Resolution |
|---|---|---|---|---|
| 2026-09-08 | Phase 0 | Claude | (1) MIT licence added by default, against policy. (2) Commit author identity carried a personal email address. | (1) `LICENSE` removed; [`ADR-0006`](../docs/decisions/ADR-0006-licensing-deferred.md) records the deferral. (2) Commit amended to a non-identifying author before any publication; researcher to set their preferred public identity before the first push. |

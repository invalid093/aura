# EXP-0012 — Research Handoff

**Self-contained. No attachments required. Written for independent critical review.**
**Date:** 2026-09-08 · **Status:** COMPLETED · **Decision gate: A *and* D simultaneously**

Evidence classes are marked throughout: `FACT` / `CALCULATION` / `OBSERVATION` / `INTERPRETATION` /
`HYPOTHESIS` / `ASSUMPTION` / `LIMITATION`. Interpretation is never presented as fact.

---

## Research question

When an aircraft experiences a fault absent from the diagnostic hypothesis library, does a
physics-based diagnostic system recognise that its hypotheses are inadequate, or does it confidently
assign the observation to an incorrect known fault?

## Why this experiment was conducted

Three prior experiments failed to find the diagnostic ambiguity AURA was designed around: it is
absent at realistic sensor noise (EXP-0010), absent under unknown fault magnitude (EXP-0011), and
transient where it exists. What they repeatedly surfaced instead was **misplaced confidence** —
notably that a hypothesis *support* excluding the truth produces error that **worsens with more
data**. EXP-0012 tests the largest version of that mechanism: a fault the model has never seen.

## Pre-registered prediction

**`FACT` (derived, then verified numerically).** The posterior is *structurally* incapable of
expressing hypothesis-space mismatch: $P(j|y)=\exp(\mathrm{LL}_j)/\sum\exp(\mathrm{LL}_k)$, and a
uniform lack of fit adds the same constant to every log-likelihood, cancelling in the softmax.
Pilot check: displacing the unseen fault far from *every* known hypothesis left confidence at
**1.0000 → 1.0000** while the residual rose **2637 → 7634**.

Because of this, "confidently wrong" was near-guaranteed and would have been a trivial result. The
experiment was therefore built around the second question: **does the non-learning residual already
supply the missing signal?**

**`CALCULATION` — pre-registered prediction P2.** The residual $R=\min_j\lVert y-w_j\rVert^2/\eta^2$
is $\chi^2(KN)$ under a correct hypothesis, so mismatch is detectable iff
$\lVert\Delta_{\min}\rVert/\eta > \sqrt{z_\alpha}(2KN)^{1/4}$ — **9.2 at 0.5 s, 13.0 at 2 s, 22.4 at
18 s**. Not refitted.

## Hypothesis space

$H_{\text{known}}$ = 18 classes from EXP-0010/0011: `F0`; bias/scale/drift/stuck on
$\{q,a_z,V_t,\alpha\}$; `F6` elevator effectiveness. Magnitude marginalised over the EXP-0011 grid.
**No "unknown" class was added to the primary experiment.** The classifier receives only the noisy
measurement vector.

## Unseen-fault definitions

| ID | Mechanism | Cat. | Why outside the library |
|---|---|---|---|
| UF-001 | AoA vane stiction | A | `F4` is a total freeze; this is partial and signal-dependent |
| UF-002 | Rate-gyro saturation | A | `F2` is linear; this is a nonlinearity |
| UF-003 | Pitot partial blockage (pneumatic lag) | A | No dynamic/filtering fault exists |
| UF-004 | Static-port blockage | B | Cross-channel; **no library fault acts on altitude** |
| UF-005 | Pitch static-stability loss | C | `F6` changes *control* effectiveness, not *stability* |
| UF-006 | Airframe icing drag rise | C | No aerodynamic-degradation hypothesis exists |

## Experimental design

4 flight conditions × 7 windows (0.25–18 s) × 6 unseen faults × 3 magnitudes × 3 noise levels =
**1512 cells**, 10 000 replications each. 72 new simulations (DS-0003); the hypothesis library reused
unchanged. Runtime 520 s. FC-4 not resurrected.

## Controls

**`FACT`** Case A: known faults through the identical pipeline — **56/56 correct, normalised residual
1.000** (exactly the χ² expectation). Any OOD failure is therefore not general classifier failure.
Envelope validity: 0 of 72 trajectories excluded. Extending the shared simulation harness left all
prior experiments **bit-identical**.

## Primary metrics

$FC(t)=P(\text{confidence}\ge\tau)$ with **τ = 0.95 reused from EXP-0010/0011**, not chosen here.
Secondary: median/max confidence, runner-up margin, nearest-known continuous manifold distance,
normalised residual, χ² p-value, winning-hypothesis identity.

**Confidence is defined as** a posterior over $H_{\text{known}}$ under a uniform class prior and the
stated noise model — a probability *conditional on the hypothesis space containing the truth*, the
condition this experiment deliberately violates. It is **not** the probability the diagnosis is
correct, and is never called that.

## Key results

**`FACT`** Failure-mode census (three modes kept strictly separate):

| Subset | caught by residual | not yet detectable | ambiguous | **confidently wrong** |
|---|---|---|---|---|
| All 1512 cells | 47.4% | 39.9% | 6.9% | **5.8%** |
| η=1, magnitude ×1 | 57.1% | 31.0% | 1.2% | **10.7%** |
| Full 18 s window | 66.7% | 17.1% | 5.6% | **10.6%** |
| Full window, η=1, ×1 | 83.3% | — | — | **16.7%** |

**`FACT`** **P2 agreement: 1502 of 1512 cells (99.3%).** The closed-form threshold predicts when the
framework catches itself and when it does not.

**`FACT`** **23 cells remain confidently wrong at the full 18 s window; all six unseen faults are
represented.** Twelve of them diagnose a genuinely faulted aircraft as **healthy**.

## Confidence behaviour

**`FACT`** UF-003 (pitot lag): confidence in `F0` — *no fault* — rises **0.133 → 0.993** across the
window sweep while the χ² test rejects only **14%**.
UF-005 (stability loss): confidence in `F6` is **1.0000 at every window from 0.25 s**; χ² rejects
2–5% for the first 2 s.

**`OBSERVATION`** Confidence and correctness diverge cleanly: confidence rises monotonically with
observation while the diagnosis remains wrong.

## Observation-window behaviour

**`OBSERVATION`** The dangerous cells concentrate at **5–18 s — after the manoeuvre**, not at short
windows where non-detection dominates. More observation shifts cells into "caught by the residual"
but **never eliminates the dangerous mode**.

## Manifold-distance results

**`FACT`** Nearest-known distance at 18 s: UF-003 **16.6** (below the 22.4 threshold → not caught);
UF-001 31.4; UF-005 68.0; UF-002 166.9; UF-004 207.0; UF-006 375.9 (all above → caught).
**`INTERPRETATION`** False confidence is explained by proximity to a known manifold.

## Validity attacks

| Attack | Result |
|---|---|
| W-A nearest-known | Main result **survives and is strongest here** |
| W-B easy OOD | **Rejected immediately** by the existing residual (100%). Obvious OOD needs no ML |
| W-C pre-manoeuvre windows | Correctly labelled *not yet detectable*, not confident misdiagnosis — the effect is **not** merely non-detection |
| W-D noise ×100 and magnitude ×4 | Effect survives; the persistent set shifts but never empties |
| W-E known-fault control | 56/56 correct |
| W-F envelope validity | 0/72 excluded |

Condition dependence is weak (4–6 dangerous cells of 42 at each condition).

## Failures / bugs / corrections

**No experiment failed.** Two pilot checks failed, and **both were bugs in the checks, not the design**:

1. Detectability was judged by *maximum per-sample* deviation; UF-003 sits at 0.73σ per sample but
   accumulates to a deflection of 16.6 over 1801 samples. Wrong statistic; corrected to accumulated
   deflection.
2. The direct-simulation reference used a *profile* minimum over magnitude while the code under test
   *marginalises*. Different estimators, so they disagreed at high noise. Reference corrected.

A physical insight fell out of (1) and is recorded: **a pneumatic lag is a continuum between two
library hypotheses** (τ→0 no fault, τ→∞ stuck sensor), so it can never be far from the library.

## What the evidence supports

- **`FACT`** A reproducible, adversarially-tested reliability problem exists: confident wrong
  diagnosis of unseen faults, undetected by goodness-of-fit, persisting at full observation.
- **`FACT`** A simple non-learning statistic — the χ² residual, **added to the framework in
  EXP-0012** (it did not exist in EXP-0010 or EXP-0011) — nevertheless catches 47–83% of mismatch, a
  computes, and the failure boundary is predictable to 99.3%.
- **`INTERPRETATION`** The dangerous cases are exactly the near-manifold ones — the faults a designer
  is least likely to anticipate, because they resemble faults the library *does* contain.

## What the evidence does NOT support

- It does **not** support building an ML OOD detector now. Most of the problem is solved by a
  non-learning statistic, and the remainder has not been shown beyond non-learning methods.
- It does **not** show that unseen faults are generally undetectable — the opposite, for most.
- It says nothing about real sensors, real aircraft, safer autonomy, or operational applicability.
- It does not establish that AURA's *original* premise (diagnostic ambiguity) was right; that premise
  remains unsupported after four experiments. The problem found here is a different one.

## Limitations

1. **`ASSUMPTION`** Known-fault template families are known exactly (TV-M5); only the true fault is outside.
2. **`LIMITATION`** Six unseen faults, one self-implemented aircraft (TV-D10), one excitation, equal priors.
3. **`LIMITATION`** Normal approximation to the χ² tail (adequate at $KN\ge338$, still approximate).
4. **`LIMITATION`** τ = 0.95 reused, not tuned; unseen-fault magnitudes experimental, not calibrated.

## Decision gate

**Gate D for the majority** — the framework indicates poor fit once the residual is added, with an analytically
predictable boundary. **Gate A for a specific minority** — at least four physically meaningful unseen
faults produce persistent, undetected, confident misdiagnosis. Both were permitted by the
pre-registration and both are supported; forcing one verdict would misrepresent the evidence.

**§25's threshold is met:** not "the classifier gets unseen faults wrong", but *the classifier becomes
more confident in a wrong diagnosis as evidence accumulates, while the fit statistic stays silent*.

## Implications for AURA

The cumulative evidence across EXP-0002, 0010, 0011 and 0012 is that **AURA's original premise —
diagnostic ambiguity — is not supported**, while a *different* problem is: **misplaced confidence
arising from a wrong hypothesis support.** EXP-0011 measured it for magnitude; EXP-0012 measures it
for the taxonomy and finds it larger, persistent, and undetected by the natural fit statistic in the
cases that matter most.

The correct next move is **not** ML. It is to attack the narrow, well-defined residue.

## Recommended next experiment

**EXP-0013 — can anything non-learning help where the residual is provably blind?** Restrict to the
near-manifold regime and test whether a *second excitation designed to increase separation* resolves
it. Isolation has been excitation-driven in every experiment so far, so this is the obvious lever,
it is cheap, and it is auditable. **Only if non-learning options fail is an ML/uncertainty approach
scientifically justified** — and the target would then be precisely defined rather than assumed.

## Reproducibility information

Commit recorded in the results payload; config SHA-256 `6eb80ec7f851…`; Python 3.13.15, NumPy 2.5.2.
Seeds derived deterministically per cell from base 20261210. N = 10 000 chosen in the pilot from
measured variance (worst-case binomial half-width 0.01 at 95% requires 9604). Datasets DS-0001,
DS-0002, DS-0003 with manifests and per-file SHA-256. All simulations deterministic; no RNG in
trajectory generation.

## Public artifacts

Published: experiment specification, configuration, unseen-fault taxonomy, analysis and generation
code, compact result summary, manifests and checksums, figures FIG-013/014/015 with provenance
sidecars, this handoff, the technical report. **Not published:** 72 unseen-fault trajectories
(6.3 MB) and the 506 library trajectories — regenerable from the published configuration and code.

---

```text
AURA_CONTEXT:
experiment=EXP-0012
status=COMPLETED
question=does a physics-based diagnostic system recognise that its hypotheses are inadequate when the true fault is absent from the library
key_fact_1=the posterior is STRUCTURALLY unable to express hypothesis-space mismatch -- a uniform misfit cancels in the softmax (verified: confidence 1.0000 unchanged while residual rose 2637 -> 7634)
key_fact_2=the residual is a chi-square goodness-of-fit statistic; mismatch detectable iff ||D_min||/eta > sqrt(z)*(2KN)^(1/4) = 22.4 at the full window
census=47.4% caught by residual, 39.9% not yet detectable, 6.9% ambiguous, 5.8% CONFIDENTLY WRONG (all 1512 cells); 16.7% confidently wrong at full window, reference noise, nominal magnitude
prediction_P2=closed-form threshold agrees with observation in 1502/1512 cells (99.3%), not refitted
persistent_danger=23 cells still confidently wrong at 18 s; all six unseen faults represented; 12 diagnose a faulted aircraft as HEALTHY
sharpest_cases=UF-003 pitot lag -> "no fault" with confidence rising 0.133 to 0.993 while chi2 rejects only 14%; UF-005 stability loss -> elevator-effectiveness loss at confidence 1.0000 with chi2 rejecting 2-5% for the first 2 s
control=56/56 known faults correct, normalised residual 1.000
validity_attacks=near-manifold strongest; easy OOD rejected 100% by the existing residual; pre-manoeuvre correctly labelled non-detection not misdiagnosis; effect survives noise x100 and magnitude x4
decision_gate=A AND D simultaneously -- Gate D for the majority (framework self-protects, no ML needed), Gate A for a near-manifold minority (persistent, undetected, confident misdiagnosis)
limitations=known template families (TV-M5); 6 unseen faults; one self-implemented aircraft (TV-D10); one excitation; equal priors; normal approximation to the chi2 tail
research_implication=AURA's ORIGINAL premise (diagnostic ambiguity) remains unsupported after four experiments. A DIFFERENT problem is now supported by measurement: misplaced confidence from a wrong hypothesis support. But 47-83% of it is solved by a simple non-learning statistic added in EXP-0012, so ML is NOT yet justified
next_experiment=EXP-0013 -- test whether a second excitation designed to increase separation resolves the near-manifold residue, before considering any learning approach
```

---

# FOR AN INDEPENDENT REVIEWER

**Criticise, not confirm.** Attacks worth making:

- **Is FACT 1 too convenient?** It makes "confidently wrong" near-tautological, which lets the report
  claim the trivial result was avoided. But does framing it that way *understate* a genuine finding
  — that real systems do use exactly this softmax and would be exactly this wrong?
- **Is the χ² residual test a fair representative of "the existing framework"?** It was not part of
  the diagnostic pipeline in EXP-0010 or EXP-0011; it was added here. Is crediting the framework with
  robustness it did not previously exercise legitimate?
- **Are the six unseen faults adversarial enough?** They were designed by the same person who knew
  the library. A genuinely independent fault set might be nearer or further.
- **Is 5.8% a lot or a little?** The report treats it as decisive. An alternative reading is that a
  95% self-protection rate is a *success* and the residue is an acceptable engineering risk.
- **Does the persistent-danger count depend on the τ = 0.95 and α = 0.01 choices?** Both were reused
  rather than tuned, but neither was justified for *this* experiment specifically.
- **Four experiments have now failed to support AURA's original premise.** Is continuing to relax
  assumptions until *something* fails a legitimate research strategy, or is it a form of searching
  for a problem to fit a pre-existing solution?

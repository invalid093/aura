"""
Fault-class isolation with unknown fault magnitude — EXP-0011.

Implements the measures pre-registered in experiments/EXP-0011/experiment_spec.md §8.

Fault magnitude is treated as an **unknown nuisance parameter**, not as extra noise.
The diagnostic objective is fault-CLASS isolation with magnitude marginalised out:

    p(y | class) = sum_m p(y | class, m) p(m)

Exact Monte Carlo reduction (as in EXP-0010, but stronger). With y = w_i + eta*z in
sigma units, the score of template j is

    score_j = ||w_j||^2 - 2 M_ij - 2 eta t_j ,    t = z.w ~ N(0, M)

and t depends on **neither the true template i nor eta**. One draw of t therefore
serves every true template and every noise level in a cell.

All probabilities are conditional on the model, taxonomy, magnitude grid and prior,
class priors, noise model and window (spec §9). They are upper bounds: the template
*families* are still assumed exactly known (TV-M5).
"""

from __future__ import annotations

import numpy as np
from math import erf, sqrt


def _phi(x):
    x = np.asarray(x, dtype=np.float64)
    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))


class TemplateSet:
    """Templates for one flight condition and observation window, in sigma units."""

    def __init__(self, W, labels, valid):
        self.W = np.asarray(W, dtype=np.float64)          # (n_templates, K*N)
        self.labels = list(labels)                        # [(class, magnitude_or_None), ...]
        self.valid = np.asarray(valid, dtype=bool)
        self.M = self.W @ self.W.T
        self.classes = sorted({c for c, _ in self.labels})
        self.by_class = {c: [k for k, (cc, _) in enumerate(self.labels) if cc == c]
                         for c in self.classes}

    # ---------------------------------------------------------------- geometry
    def squared_deflection(self):
        d = np.diag(self.M)
        D = d[:, None] + d[None, :] - 2.0 * self.M
        np.fill_diagonal(D, 0.0)
        return np.maximum(D, 0.0)

    def detectable(self, nominal_index, min_deflection):
        """Templates far enough from nominal to be detectable at eta = 1."""
        D = self.squared_deflection()
        return np.sqrt(D[nominal_index]) >= float(min_deflection)

    def manifold_overlap(self, eta=1.0, restrict=None):
        """Worst-case-magnitude separation between every pair of CLASSES.

        D_min(A,B) = min over admissible magnitudes of the deflection between a
        template of class A and a template of class B. This is the adversarial
        question: can *some* magnitude of A mimic *some* magnitude of B?
        """
        D = np.sqrt(self.squared_deflection()) / float(eta)
        adm = self.valid if restrict is None else (self.valid & restrict)
        cls = self.classes
        out = np.full((len(cls), len(cls)), np.nan)
        argmin = {}
        for a, ca in enumerate(cls):
            ia = [k for k in self.by_class[ca] if adm[k]]
            for b, cb in enumerate(cls):
                if b <= a:
                    continue
                ib = [k for k in self.by_class[cb] if adm[k]]
                if not ia or not ib:
                    continue
                sub = D[np.ix_(ia, ib)]
                k = int(np.argmin(sub))
                r, c = divmod(k, sub.shape[1])
                out[a, b] = out[b, a] = float(sub[r, c])
                argmin[(ca, cb)] = (self.labels[ia[r]], self.labels[ib[c]], float(sub[r, c]))
        return cls, out, argmin

    # -------------------------------------------------------------- classifier
    def classify_mc(self, eta, n_mc, rng, case="C", prior_indices=None,
                    true_indices=None, estimate_magnitude=False):
        """Monte Carlo probability of correct fault-CLASS identification.

        case "A": the classifier is told the true magnitude, so it compares only
                  templates at that magnitude (reproduces the EXP-0010 assumption).
        case "B"/"C": the classifier marginalises over the magnitudes allowed by
                  `prior_indices` (uniform prior), and picks the most likely class.
        """
        M = self.M
        n = M.shape[0]
        diag = np.diag(M)

        # One draw of t serves every true template and every eta.
        evals, evecs = np.linalg.eigh(M)
        A = evecs * np.sqrt(np.clip(evals, 0.0, None))
        t = rng.standard_normal(size=(n_mc, n)) @ A.T                # (n_mc, n)

        admissible = self.valid.copy()
        if prior_indices is not None:
            keep = np.zeros(n, dtype=bool)
            keep[list(prior_indices)] = True
            admissible &= keep

        truths = [k for k in range(n) if self.valid[k]] if true_indices is None \
            else list(true_indices)

        correct = np.zeros(len(truths))
        mag_err = []
        confusion = {}

        for idx, i in enumerate(truths):
            # score_j = ||w_j||^2 - 2 M_ij - 2 eta t_j
            score = diag[None, :] - 2.0 * M[i][None, :] - 2.0 * float(eta) * t

            if case == "A":
                # Only templates at the true magnitude, plus magnitude-free classes
                # (F0, F4), which are always admissible.
                # Convention, declared in the report: when the TRUE fault has no
                # magnitude parameter, the alternatives are evaluated at the nominal
                # magnitude m = 1, since "the known magnitude" is otherwise undefined.
                mag_i = self.labels[i][1]
                ref = 1.0 if mag_i is None else mag_i
                cand = np.array([k for k in range(n) if self.valid[k]
                                 and (self.labels[k][1] == ref
                                      or self.labels[k][1] is None)])
                sc = score[:, cand]
                pick = cand[np.argmin(sc, axis=1)]
                chosen = np.array([self.labels[k][0] for k in pick])
            else:
                # marginal likelihood per class: logsumexp over admissible magnitudes
                lls = np.full((n_mc, len(self.classes)), -np.inf)
                for ci, c in enumerate(self.classes):
                    ks = [k for k in self.by_class[c] if admissible[k]]
                    if not ks:
                        continue
                    a = -score[:, ks] / (2.0 * float(eta) ** 2)
                    amax = a.max(axis=1, keepdims=True)
                    lls[:, ci] = (amax[:, 0]
                                  + np.log(np.exp(a - amax).sum(axis=1) / len(ks)))
                chosen = np.array(self.classes)[np.argmax(lls, axis=1)]

            true_class = self.labels[i][0]
            hit = chosen == true_class
            correct[idx] = hit.mean()

            if estimate_magnitude and self.labels[i][1] is not None:
                ks = [k for k in self.by_class[true_class] if admissible[k]]
                if ks:
                    pick_m = np.array(ks)[np.argmin(score[:, ks], axis=1)]
                    est = np.array([self.labels[k][1] for k in pick_m], dtype=float)
                    mag_err.append(float(np.mean(np.abs(est - self.labels[i][1])
                                                 / self.labels[i][1])))

            vals, counts = np.unique(chosen, return_counts=True)
            confusion[f"{true_class}|{self.labels[i][1]}"] = {
                str(v): int(c) for v, c in zip(vals, counts)}

        return {
            "P_class": float(correct.mean()),
            "per_template_P_class": correct.tolist(),
            "truth_labels": [f"{self.labels[i][0]}|{self.labels[i][1]}" for i in truths],
            "mean_relative_magnitude_error": float(np.mean(mag_err)) if mag_err else None,
            "confusion": confusion,
        }


def p_disc_from_deflection(D, eta=1.0):
    """Optimal binary discrimination probability from a deflection."""
    return _phi(np.asarray(D, dtype=np.float64) / (2.0 * float(eta)))


def overlap_band(p, bands):
    if not np.isfinite(p):
        return "undefined"
    if p >= bands["clearly_separated"]:
        return "clearly_separated"
    if p >= bands["partially_overlapping"]:
        return "partially_overlapping"
    if p >= bands["strongly_overlapping"]:
        return "strongly_overlapping"
    return "structurally_intersecting"


# ---------------------------------------------------------------------------
# Continuous manifold intersection.
#
# A discrete magnitude grid can never reach the true minimum separation between two
# fault families -- it can only sample near it. Reporting the grid minimum would make
# the headline number an artefact of grid resolution.
#
# If a class's response is (near-)linear in magnitude, its family is a line segment in
# template space, w(m) ~ w0 + m*u, and the minimum distance between two such segments
# has a closed form. Everything below is computed from the Gram matrix, so no
# high-dimensional vectors are formed.
#
# The linear fit's residual is reported alongside, so a reader can see how good the
# approximation is rather than having to trust it.
# ---------------------------------------------------------------------------

def _fit_coeffs(mags):
    """Least-squares coefficients C such that [w0; u] = C @ W_class, for w ~ w0 + m*u."""
    X = np.column_stack([np.ones(len(mags)), np.asarray(mags, dtype=np.float64)])
    return np.linalg.pinv(X.T @ X) @ X.T, X


def linear_family_fits(ts, admissible):
    """Fit w(m) ~ w0 + m*u per class. Returns coefficient rows and fit residuals.

    All quantities derive from the Gram matrix; W is never re-multiplied.
    """
    out = {}
    for c in ts.classes:
        ks = [k for k in ts.by_class[c] if admissible[k]]
        if not ks:
            continue
        mags = [ts.labels[k][1] for k in ks]
        if any(m is None for m in mags) or len(ks) < 2:
            # magnitude-free class (F0, F4): a single point, u = 0
            e = np.zeros(len(ts.labels)); e[ks[0]] = 1.0
            out[c] = {"w0": e, "u": np.zeros(len(ts.labels)),
                      "m_min": None, "m_max": None, "residual_frac": 0.0,
                      "n_points": len(ks), "point_class": True}
            continue
        C, X = _fit_coeffs(mags)
        A = np.zeros((2, len(ts.labels)))
        for j, k in enumerate(ks):
            A[:, k] = C[:, j]
        # residual of the linear fit, in Gram terms: ||W_c - X (C W_c)||_F / ||W_c||_F
        R = np.zeros((len(ks), len(ts.labels)))
        for j, k in enumerate(ks):
            R[j, k] = 1.0
        R = R - X @ A
        num = float(np.sqrt(max(np.trace(R @ ts.M @ R.T), 0.0)))
        E = np.zeros((len(ks), len(ts.labels)))
        for j, k in enumerate(ks):
            E[j, k] = 1.0
        den = float(np.sqrt(max(np.trace(E @ ts.M @ E.T), 1e-30)))
        out[c] = {"w0": A[0], "u": A[1], "m_min": float(min(mags)),
                  "m_max": float(max(mags)), "residual_frac": num / den,
                  "n_points": len(ks), "point_class": False}
    return out


def continuous_manifold_overlap(ts, admissible, eta=1.0):
    """Minimum separation between fault families with magnitude varying CONTINUOUSLY
    within its admissible range. Returns (classes, D_min matrix, argmin magnitudes)."""
    fits = linear_family_fits(ts, admissible)
    cls = [c for c in ts.classes if c in fits]
    n = len(cls)
    D = np.full((n, n), np.nan)
    arg = {}
    for ia in range(n):
        fa = fits[cls[ia]]
        for ib in range(ia + 1, n):
            fb = fits[cls[ib]]
            d0 = fa["w0"] - fb["w0"]
            ua, ub = fa["u"], -fb["u"]
            # minimise ||d0 + s*ua + t*ub||^2 over the admissible box
            G = np.array([[ua @ ts.M @ ua, ua @ ts.M @ ub],
                          [ub @ ts.M @ ua, ub @ ts.M @ ub]])
            b = -np.array([ua @ ts.M @ d0, ub @ ts.M @ d0])
            lo = np.array([fa["m_min"] if not fa["point_class"] else 0.0,
                           fb["m_min"] if not fb["point_class"] else 0.0])
            hi = np.array([fa["m_max"] if not fa["point_class"] else 0.0,
                           fb["m_max"] if not fb["point_class"] else 0.0])
            try:
                st = np.linalg.solve(G + 1e-12 * np.eye(2), b)
            except np.linalg.LinAlgError:                        # pragma: no cover
                st = np.zeros(2)
            best, bst = np.inf, None
            # unconstrained solution clamped to the box, plus every corner and edge
            cands = [np.clip(st, lo, hi)]
            for sv in (lo[0], hi[0]):
                den = G[1, 1]
                tv = (b[1] - G[1, 0] * sv) / den if den > 1e-30 else lo[1]
                cands.append(np.array([sv, np.clip(tv, lo[1], hi[1])]))
            for tv in (lo[1], hi[1]):
                den = G[0, 0]
                sv = (b[0] - G[0, 1] * tv) / den if den > 1e-30 else lo[0]
                cands.append(np.array([np.clip(sv, lo[0], hi[0]), tv]))
            for sv in (lo[0], hi[0]):
                for tv in (lo[1], hi[1]):
                    cands.append(np.array([sv, tv]))
            for st_ in cands:
                v = d0 + st_[0] * ua + st_[1] * ub
                q = float(v @ ts.M @ v)
                if q < best:
                    best, bst = q, st_
            D[ia, ib] = D[ib, ia] = np.sqrt(max(best, 0.0)) / float(eta)
            # Report the ACTUAL magnitude for point classes (F0, F4) rather than the
            # placeholder 0.0 used in the box, so the output is not misleading.
            ma = None if fa["point_class"] else float(bst[0])
            mb = None if fb["point_class"] else float(bst[1])
            arg[(cls[ia], cls[ib])] = (ma, mb, float(D[ia, ib]))
    n_degenerate = sum(1 for f in fits.values() if f["point_class"])
    return cls, D, arg, fits, n_degenerate

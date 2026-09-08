"""
Practical (statistical) fault diagnosability under measurement uncertainty — EXP-0010.

Implements the measures pre-registered in experiments/EXP-0010/experiment_spec.md §8.

The classifier throughout is the Bayes-optimal 18-way rule with **known templates** and
known Gaussian noise. Every probability it produces is therefore an **upper bound** on
what any real diagnoser could achieve, because no real system knows the fault templates
exactly. Reported as such.

Efficiency note (exact, not an approximation). With w_j = y_j/(eta*sigma) and true fault
i, correct isolation requires, for all j != i,

    ||v_j||^2 - 2 z.v_j > 0,      v_j = w_j - w_i,   z ~ N(0, I)

Writing u_j = z.v_j, the vector u is Gaussian with covariance G_jk = v_j.v_k, which is
obtainable from a single 18x18 Gram matrix per (condition, window). So the Monte Carlo
runs in 18 dimensions rather than 13 x N, at ~1e4 lower cost. Verified against direct
full-dimensional simulation in the pilot (validity attack V-C).
"""

from __future__ import annotations

import numpy as np
from math import erf, sqrt

from aircraft.gfw1 import CHANNELS


def _phi(x):
    """Standard normal CDF, vectorised, without scipy."""
    x = np.asarray(x, dtype=np.float64)
    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))


def sigma_vector(cfg_exp0002: dict) -> np.ndarray:
    s = cfg_exp0002["sensors"]["sigma"]
    return np.array([float(s[ch]) for ch in CHANNELS], dtype=np.float64)


def load_window(traj: dict[str, np.ndarray], t: np.ndarray, sigma: np.ndarray,
                onset: float, window: float) -> np.ndarray:
    """Stack templates as a (n_faults, K*N) matrix in sigma units, for one window."""
    mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
    rows = [(traj[k][mask] / sigma).ravel() for k in traj]
    return np.asarray(rows, dtype=np.float64)


def gram(W: np.ndarray) -> np.ndarray:
    """18x18 Gram matrix of the templates (in sigma units)."""
    return W @ W.T


def squared_deflection(M: np.ndarray) -> np.ndarray:
    """D_jk = ||w_j - w_k||^2, from the Gram matrix. Diagonal is zero."""
    diag = np.diag(M)
    D = diag[:, None] + diag[None, :] - 2.0 * M
    np.fill_diagonal(D, 0.0)
    return np.maximum(D, 0.0)          # guard tiny negatives from round-off


def p_disc(D: np.ndarray, eta: float) -> np.ndarray:
    """Closed-form pairwise probability of correct discrimination for the optimal
    binary test between two known signals in white Gaussian noise:

        P = Phi( d' / 2 ),   d' = sqrt(D) / eta

    Exact; no Monte Carlo. Diagonal set to nan (a fault is not compared with itself).
    """
    dprime = np.sqrt(D) / float(eta)
    P = _phi(dprime / 2.0)
    np.fill_diagonal(P, np.nan)
    return P


def conditional_gram(M: np.ndarray, i: int) -> np.ndarray:
    """G^(i)_jk = (w_j - w_i).(w_k - w_i), for all j,k (row/col i is identically zero)."""
    return M - M[i][None, :] - M[:, i][:, None] + M[i, i]


def p_iso_mc(M: np.ndarray, eta: float, n_mc: int, rng: np.random.Generator,
             return_confusion: bool = False):
    """Monte Carlo probability of correct 18-way isolation.

    Exact reduction to an 18-dimensional Gaussian (see module docstring).
    Returns (P_iso_mean, per_fault_P_iso[, confusion_matrix]).
    """
    n = M.shape[0]
    Meff = M / (float(eta) ** 2)
    per_fault = np.zeros(n, dtype=np.float64)
    confusion = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        G = conditional_gram(Meff, i)
        others = [j for j in range(n) if j != i]
        Gs = G[np.ix_(others, others)]
        thresh = np.diag(Gs) / 2.0

        # Symmetric PSD square root via eigendecomposition (robust to rank deficiency)
        evals, evecs = np.linalg.eigh(Gs)
        evals = np.clip(evals, 0.0, None)
        A = evecs * np.sqrt(evals)

        z = rng.standard_normal(size=(n_mc, Gs.shape[0]))
        u = z @ A.T                                  # u ~ N(0, Gs)

        margin = thresh[None, :] - u                 # correct iff every margin > 0
        correct = np.all(margin > 0.0, axis=1)
        per_fault[i] = correct.mean()

        if return_confusion:
            # Which hypothesis wins when the true one loses: smallest score
            # score_j = ||v_j||^2 - 2 u_j  (score_i = 0 for the true hypothesis)
            score = thresh[None, :] * 2.0 - 2.0 * u
            wrong = ~correct
            confusion[i, i] = correct.sum()
            if wrong.any():
                pick = np.argmin(score[wrong], axis=1)
                idx = np.array(others)[pick]
                np.add.at(confusion[i], idx, 1.0)
            confusion[i] /= n_mc

    out = (float(per_fault.mean()), per_fault)
    return out + (confusion,) if return_confusion else out


def p_detect_mc(M: np.ndarray, eta: float, n_mc: int, rng: np.random.Generator,
                nominal_index: int = 0):
    """Detection performance, kept separate from isolation (brief §10).

    P_det: probability the classifier does NOT return F0 when a fault is present.
    P_FA:  probability it does NOT return F0 when no fault is present.
    """
    n = M.shape[0]
    Meff = M / (float(eta) ** 2)
    det = []
    for i in range(n):
        G = conditional_gram(Meff, i)
        others = [j for j in range(n) if j != i]
        Gs = G[np.ix_(others, others)]
        evals, evecs = np.linalg.eigh(Gs)
        A = evecs * np.sqrt(np.clip(evals, 0.0, None))
        z = rng.standard_normal(size=(n_mc, Gs.shape[0]))
        u = z @ A.T
        score = np.diag(Gs)[None, :] - 2.0 * u        # score_j; true hypothesis scores 0
        best = np.min(score, axis=1)
        best_idx = np.array(others)[np.argmin(score, axis=1)]
        chose_true = best > 0.0
        chosen = np.where(chose_true, i, best_idx)
        det.append((chosen != nominal_index).mean())
    det = np.asarray(det)
    return {
        "P_det": float(det[np.arange(n) != nominal_index].mean()),
        "P_FA": float(det[nominal_index]),
        "per_fault_P_not_nominal": det,
    }


def p_iso_direct(W: np.ndarray, eta: float, n_mc: int, rng: np.random.Generator,
                 sigma_len: int, noise: str = "gaussian", df: int = 4,
                 rho: float = 0.5, n_channels: int = 13):
    """Direct full-dimensional simulation — used only for validity attacks V-B and V-C.

    Slow by design: it makes no distributional shortcut, so it can both verify the Gram
    reduction (Gaussian) and test non-Gaussian and temporally correlated noise.
    """
    n, dim = W.shape
    Weff = W / float(eta)
    per_fault = np.zeros(n)
    n_time = dim // n_channels

    for i in range(n):
        ok = 0
        for _ in range(n_mc):
            if noise == "gaussian":
                z = rng.standard_normal(dim)
            elif noise == "student_t":
                # scaled to unit variance so the comparison is at matched power
                z = rng.standard_t(df, size=dim) / np.sqrt(df / (df - 2.0))
            elif noise == "ar1":
                e = rng.standard_normal((n_time, n_channels))
                z = np.empty_like(e)
                z[0] = e[0]
                for t in range(1, n_time):
                    z[t] = rho * z[t - 1] + np.sqrt(1 - rho ** 2) * e[t]
                z = z.ravel()
            else:                                             # pragma: no cover
                raise ValueError(noise)
            y = Weff[i] + z
            d2 = np.sum((y[None, :] - Weff) ** 2, axis=1)
            ok += int(np.argmin(d2) == i)
        per_fault[i] = ok / n_mc
    return float(per_fault.mean()), per_fault


def practical_ambiguity_pairs(ids, P, threshold=0.95):
    """Pairs whose optimal binary discrimination probability falls below the threshold."""
    out = []
    n = len(ids)
    for a in range(n):
        for b in range(a + 1, n):
            if P[a, b] < threshold:
                out.append((ids[a], ids[b], float(P[a, b])))
    out.sort(key=lambda p: p[2])
    return out

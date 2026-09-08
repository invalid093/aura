"""
Response-based fault distinguishability analysis (EXP-0002).

Implements the metric pre-registered in experiments/EXP-0002/experiment_spec.md 6.
Nothing here selects a metric or threshold based on results.

Terminology: this measures RESPONSE-BASED DISTINGUISHABILITY, not structural
isolability in the Frisk/Krysander sense. The two are different quantities and
only the former can depend on flight condition. See
docs/decisions/ADR-0008-distinguishability-vs-structural-isolability.md.
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import CHANNELS


def sigma_vector(cfg: dict) -> np.ndarray:
    """Pre-declared per-channel sensor noise scale, in CHANNELS order."""
    s = cfg["sensors"]["sigma"]
    return np.array([float(s[ch]) for ch in CHANNELS], dtype=np.float64)


def distance_matrix(runs: dict[str, dict], cfg: dict,
                    compare_from: float | None = None) -> tuple[list[str], np.ndarray]:
    """Pairwise normalised RMS response distance.

        d_ij = sqrt( mean_over_channels_and_samples( ((y_i - y_j)/sigma)^2 ) )

    Units: multiples of per-sample, per-channel RMS sensor noise.
    Only post-onset samples are compared.
    """
    ids = list(runs.keys())
    sig = sigma_vector(cfg)
    t0 = float(cfg["simulation"]["compare_from"] if compare_from is None else compare_from)

    t = runs[ids[0]]["t"]
    mask = t >= t0 - 1e-12
    n = len(ids)

    # Pre-normalise once
    Y = {k: (runs[k]["y"][mask] / sig) for k in ids}
    for k in ids:
        if Y[k].shape != Y[ids[0]].shape:
            raise ValueError(f"run {k} has inconsistent sample count -- cannot compare")

    D = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            diff = Y[ids[i]] - Y[ids[j]]
            d = float(np.sqrt(np.mean(diff * diff)))
            D[i, j] = D[j, i] = d
    return ids, D


def binary_matrix(D: np.ndarray, tau: float) -> np.ndarray:
    """Distinguishable (True) iff d > tau. Diagonal is False by definition."""
    B = D > tau
    np.fill_diagonal(B, False)
    return B


def _rankdata(a: np.ndarray) -> np.ndarray:
    """Average ranks, ties shared. Local implementation -- scipy is not a dependency."""
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(1, len(a) + 1, dtype=np.float64)
    # average tied ranks
    sorted_a = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sorted_a[j + 1] == sorted_a[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = np.mean(ranks[order[i:j + 1]])
        i = j + 1
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation. Returns nan if either input is constant."""
    ra, rb = _rankdata(a), _rankdata(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    den = np.sqrt(np.sum(ra * ra) * np.sum(rb * rb))
    if den == 0:
        return float("nan")
    return float(np.sum(ra * rb) / den)


def upper_triangle(M: np.ndarray) -> np.ndarray:
    iu = np.triu_indices(M.shape[0], k=1)
    return M[iu]


def summarise(ids: list[str], D: np.ndarray, tau: float, tol: float) -> dict:
    """Pre-declared quantitative summaries (experiment_spec.md 3.2)."""
    n = len(ids)
    B = binary_matrix(D, tau)
    off = upper_triangle(D)
    n_pairs = off.size

    distinguishable = int(np.sum(upper_triangle(B.astype(float)) > 0.5))
    identical = int(np.sum(off < tol))

    ambiguity_degree = {
        ids[i]: int(np.sum(~B[i]) - 1)          # exclude self
        for i in range(n)
    }
    amb_pairs = [(ids[i], ids[j], float(D[i, j]))
                 for i in range(n) for j in range(i + 1, n) if not B[i, j]]
    amb_pairs.sort(key=lambda p: p[2])

    return {
        "n_faults": n,
        "n_pairs": n_pairs,
        "threshold": tau,
        "n_distinguishable": distinguishable,
        "n_indistinguishable": n_pairs - distinguishable,
        "frac_distinguishable": distinguishable / n_pairs,
        "n_numerically_identical": identical,
        "min_distance": float(off.min()),
        "median_distance": float(np.median(off)),
        "max_distance": float(off.max()),
        "ambiguity_degree": ambiguity_degree,
        "indistinguishable_pairs": amb_pairs,
        "is_fully_diagonal": distinguishable == n_pairs,
        "is_fully_dense": distinguishable == 0,
    }


def compare_conditions(ids: list[str], D_by_cond: dict[str, np.ndarray],
                       tau: float) -> dict:
    """Cross-condition structure comparison.

    The rank correlation is THRESHOLD-FREE and is the primary evidence on whether
    the ambiguity structure reorders between conditions; the binary flip count
    depends on tau and is reported alongside it.
    """
    conds = list(D_by_cond.keys())
    out = {"conditions": conds, "pairwise": {}}
    for a in range(len(conds)):
        for b in range(a + 1, len(conds)):
            ca, cb = conds[a], conds[b]
            da = upper_triangle(D_by_cond[ca])
            db = upper_triangle(D_by_cond[cb])
            Ba = upper_triangle(binary_matrix(D_by_cond[ca], tau).astype(float)) > 0.5
            Bb = upper_triangle(binary_matrix(D_by_cond[cb], tau).astype(float)) > 0.5
            flips = int(np.sum(Ba != Bb))
            changed = [
                (ids[i], ids[j])
                for k, (i, j) in enumerate(zip(*np.triu_indices(len(ids), k=1)))
                if Ba[k] != Bb[k]
            ]
            out["pairwise"][f"{ca}|{cb}"] = {
                "spearman_rho": spearman(da, db),
                "binary_flips": flips,
                "binary_flip_fraction": flips / da.size,
                "changed_pairs": changed[:40],
                "n_changed_pairs_total": len(changed),
            }
    return out


def matrix_to_text(ids: list[str], D: np.ndarray, tau: float) -> str:
    """Compact rendering: '.' distinguishable, 'X' indistinguishable."""
    B = binary_matrix(D, tau)
    w = max(len(i) for i in ids)
    head = " " * (w + 1) + " ".join(f"{k:>2d}" for k in range(len(ids)))
    lines = [head]
    for i, name in enumerate(ids):
        cells = []
        for j in range(len(ids)):
            cells.append(" -" if i == j else ("  " if B[i, j] else " X"))
        lines.append(f"{name:<{w}} " + "".join(cells))
    lines.append("")
    lines.append("  X = indistinguishable (d <= tau)   blank = distinguishable   - = self")
    lines.append("  index: " + ", ".join(f"{k}={n}" for k, n in enumerate(ids)))
    return "\n".join(lines)

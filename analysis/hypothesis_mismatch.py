"""
Hypothesis-space mismatch analysis — EXP-0012.

Measures what a physics-based diagnostic system does when the true fault is absent from
its hypothesis library: which known fault it picks, how confident it is, and whether the
absolute goodness of fit already reveals the mismatch **without any machine learning**.

Two quantities are computed and must not be conflated:

  POSTERIOR  P(j | y) over H_known. Structurally incapable of expressing mismatch: a
             uniform lack of fit adds the same constant to every log-likelihood and
             cancels in the softmax. It is a probability CONDITIONAL on the hypothesis
             space containing the truth -- exactly the condition being violated here.

  RESIDUAL   R = min_j ||y - w_j||^2 / eta^2. A chi-square goodness-of-fit statistic
             with KN degrees of freedom. Unlike the posterior it IS sensitive to
             absolute misfit, so it can in principle say "none of the above".

Exact Monte Carlo. With y = w_u + eta*z in sigma units, write t_j = z.w_j for the
augmented template set (known templates plus the unseen one). Then t ~ N(0, G) with G
the augmented Gram matrix, and

    ||y - w_j||^2 / eta^2  =  D_uj/eta^2 + 2 (t_u - t_j)/eta + ||z||^2

where D_uj = ||w_u - w_j||^2. The noise norm splits exactly as
||z||^2 = t G^+ t^T + chi2(KN - r), the two parts independent, with r the rank of the
template span. Nothing is approximated except the chi-square tail, which uses a normal
approximation valid at these degrees of freedom.
"""

from __future__ import annotations

import numpy as np
from math import erf, sqrt


def _phi(x):
    x = np.asarray(x, dtype=np.float64)
    return 0.5 * (1.0 + np.vectorize(erf)(x / sqrt(2.0)))


def chi2_sf_normal(R, df):
    """Upper-tail probability of chi2(df), normal approximation. df is large here."""
    return 1.0 - _phi((np.asarray(R, dtype=np.float64) - df) / sqrt(2.0 * df))


def chi2_threshold(df, alpha=0.01):
    """Upper-tail critical value of chi2(df) at level alpha, normal approximation."""
    z = {0.05: 1.6449, 0.01: 2.3263, 0.001: 3.0902}[alpha]
    return df + z * sqrt(2.0 * df)


def diagnose_unseen(M_aug, u_index, class_of, prior_mask, eta, n_mc, rng,
                    n_dims, rank=None):
    """Monte Carlo diagnosis of an observation whose truth is OUTSIDE the library.

    M_aug      augmented Gram matrix, templates then the unseen template last
    u_index    row of the unseen template in M_aug
    class_of   list mapping template index -> class name (unseen index included)
    prior_mask boolean over templates: which are admissible hypotheses
    n_dims     K*N, the measurement dimension
    """
    n = M_aug.shape[0]
    diag = np.diag(M_aug)
    D_u = diag[u_index] + diag - 2.0 * M_aug[u_index]          # ||w_u - w_j||^2
    D_u = np.maximum(D_u, 0.0)

    evals, evecs = np.linalg.eigh(M_aug)
    evals_c = np.clip(evals, 0.0, None)
    A = evecs * np.sqrt(evals_c)
    r = int(rank if rank is not None else np.sum(evals_c > evals_c.max() * 1e-12))
    t = rng.standard_normal(size=(n_mc, n)) @ A.T              # t ~ N(0, M_aug)

    # ||z_par||^2 = t G^+ t^T  ; ||z_perp||^2 ~ chi2(KN - r), independent
    pinv = np.linalg.pinv(M_aug, rcond=1e-10)
    z_par = np.einsum("ij,jk,ik->i", t, pinv, t)
    z_par = np.maximum(z_par, 0.0)
    df_perp = max(n_dims - r, 1)
    z_perp = rng.chisquare(df_perp, size=n_mc)
    z_norm2 = z_par + z_perp

    # score_j = R_j - ||z||^2 ; the common ||z||^2 cancels in the posterior (FACT 1)
    score = D_u[None, :] / eta ** 2 + 2.0 * (t[:, [u_index]] - t) / eta

    cand = np.where(prior_mask)[0]
    classes = sorted({class_of[j] for j in cand})
    lls = np.full((n_mc, len(classes)), -np.inf)
    for ci, c in enumerate(classes):
        ks = [j for j in cand if class_of[j] == c]
        a = -score[:, ks] / 2.0
        amax = a.max(axis=1, keepdims=True)
        lls[:, ci] = amax[:, 0] + np.log(np.exp(a - amax).sum(axis=1) / len(ks))

    m = lls.max(axis=1, keepdims=True)
    post = np.exp(lls - m)
    post /= post.sum(axis=1, keepdims=True)

    win = np.argmax(post, axis=1)
    conf = post[np.arange(n_mc), win]
    srt = np.sort(post, axis=1)
    margin = srt[:, -1] - srt[:, -2] if post.shape[1] > 1 else np.ones(n_mc)

    R = score[:, cand].min(axis=1) + z_norm2
    pval = chi2_sf_normal(R, n_dims)

    names, counts = np.unique(np.array(classes)[win], return_counts=True)
    return {
        "classes": classes,
        "winner_counts": {str(a): int(b) for a, b in zip(names, counts)},
        "modal_winner": str(names[int(np.argmax(counts))]),
        "mean_confidence": float(conf.mean()),
        "median_confidence": float(np.median(conf)),
        "max_confidence": float(conf.max()),
        "mean_runner_up_margin": float(margin.mean()),
        "mean_residual": float(R.mean()),
        "normalised_residual": float(R.mean() / n_dims),
        "median_chi2_pvalue": float(np.median(pval)),
        "frac_chi2_rejects_at_01": float((pval < 0.01).mean()),
        "conf_ge_threshold": conf,          # returned for FC(t) at any threshold
        "n_dims": int(n_dims),
        "rank": r,
        "nearest_template_deflection": float(np.sqrt(D_u[cand].min())),
    }


def false_confidence(conf, tau):
    """FC = P(confidence >= tau) when NO correct hypothesis exists in the library."""
    return float((np.asarray(conf) >= float(tau)).mean())

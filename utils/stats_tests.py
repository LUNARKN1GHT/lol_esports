"""Non-parametric significance tests for cross-region playstyle comparison.

Kruskal-Wallis (group-level) + pairwise Mann-Whitney with Bonferroni
correction (post-hoc). Effect size reported as epsilon-squared.
"""

from itertools import combinations

import pandas as pd
import scipy.stats as stats


def kw_test(df: pd.DataFrame, group_col: str, metric_col: str, groups=None) -> dict | None:
    """Kruskal-Wallis on one metric across groups.

    Returns dict with H, p, eps2 and per-group sample sizes.
    Skips groups with <5 observations; returns None if fewer than 2 valid groups remain.
    """
    samples = []
    sizes = {}
    for g in groups or sorted(df[group_col].dropna().unique()):
        s = df.loc[df[group_col] == g, metric_col].dropna().values
        if len(s) >= 5:
            samples.append(s)
            sizes[g] = len(s)
    if len(samples) < 2:
        return None
    H, p = stats.kruskal(*samples)
    n_total = sum(sizes.values())
    eps2 = H / (n_total - 1)
    return {"H": H, "p": p, "eps2": eps2, **{f"n_{g}": v for g, v in sizes.items()}}


def kw_table(df: pd.DataFrame, group_col: str, metrics: list[str], groups=None) -> pd.DataFrame:
    """Run kw_test over a list of metrics; returns one row per metric."""
    rows = []
    for m in metrics:
        r = kw_test(df, group_col, m, groups)
        if r:
            rows.append({"metric": m, **r})
    return pd.DataFrame(rows).set_index("metric")


def pairwise_mwu(
    df: pd.DataFrame, group_col: str, metric: str, groups: list[str]
) -> pd.DataFrame:
    """Pairwise Mann-Whitney U with Bonferroni-adjusted p-values.

    Returns a symmetric DataFrame; diagonal is NaN.
    """
    n_pairs = len(list(combinations(groups, 2)))
    res = pd.DataFrame(index=groups, columns=groups, dtype=float)
    for a, b in combinations(groups, 2):
        sa = df.loc[df[group_col] == a, metric].dropna()
        sb = df.loc[df[group_col] == b, metric].dropna()
        if len(sa) >= 5 and len(sb) >= 5:
            _, p = stats.mannwhitneyu(sa, sb, alternative="two-sided")
            p_adj = min(p * n_pairs, 1.0)
            res.loc[a, b] = res.loc[b, a] = p_adj
    return res

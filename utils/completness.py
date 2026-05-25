"""Document data availability across years.

Missingness here is *descriptive*, not prescriptive: many "missing" values
correspond to game mechanics introduced in later years (e.g. Rift Herald,
objective bounties) rather than recording gaps. Use this module to know
*when* a field becomes usable; do not drop columns globally.
"""

import pandas as pd


def missing_rate_by_year(df: pd.DataFrame, year_col: str = "year") -> pd.DataFrame:
    """Per-year proportion of NaN values for every column."""
    return df.groupby(year_col).apply(lambda g: g.isna().mean())


def first_usable_year(miss: pd.DataFrame, threshold: float = 0.10) -> pd.Series:
    """Earliest year where a field's missing rate drops below `threshold`.

    Returns NaN if the field never reaches the threshold.
    """
    result = {}
    for col in miss.columns:
        good = miss.index[miss[col] < threshold]
        result[col] = int(good.min()) if len(good) else pd.NA
    return pd.Series(result, name="first_usable_year")

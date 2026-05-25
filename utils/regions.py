"""League regions mapping for regional style analysis."""

import pandas as pd

MAJOR_REGION_MAP = {
    "LPL": "LPL",
    "LCK": "LCK",
    "LCS": "LCS",
    "NA LCS": "LCS",
    "LEC": "LEC",
    "EU LCS": "LEC",
}

ACADEMY = frozenset(
    {
        "LDL",  # LPL 二级
        "LCKC",  # LCK Challengers
        "NACL",  # NA Challengers
        "LCSA",  # LCS Academy
        "LFL2",  # LFL 2
        "CBLOLA",  # CBLOL Academy
    }
)

INTERNATIONAL = frozenset(
    {"WLDs", "LCKC", "NACL", "LCSA", "LFL2", "CBLOLA", "LSPL", "EBLPA", "GLLPA", "TCS"}
)

REGION_ORDER = ["LPL", "LCK", "LCS", "LEC", "Others", "International", "Academy"]


def classify_league(league: str) -> str:
    if league in MAJOR_REGION_MAP:
        return MAJOR_REGION_MAP[league]
    if league in INTERNATIONAL:
        return "International"
    if league in ACADEMY:
        return "Academy"
    return "Others"


def add_region(df: pd.DataFrame, league_col: str = "league", out_col: str = "region"):
    """Return df with a new 'region' column derived from 'league'."""
    df = df.copy()
    df[out_col] = df[league_col].map(classify_league)
    return df

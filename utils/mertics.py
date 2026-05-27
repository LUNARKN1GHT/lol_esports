"""Per-(team, season, region) playstyle metrics.

All functions take the *raw merged* DataFrame and return a DataFrame
keyed by (teamname, year, region), with one or more metric columns.
They can be joined together to build the full playstyle table used
in regional comparison (M5).

Note on the `region` key: 一支队伍在同一年可能跨多个 region（如 LPL 队
打 Worlds），那些场次风格差异显著，因此分别聚合而不是混在一行。
"""

import pandas as pd

from .preprocess import get_team_rows, require_snapshots, standard_clean
from .regions import add_region

GROUP_KEYS = ["teamname", "year", "region"]


def _team_season_base(df: pd.DataFrame) -> pd.DataFrame:
    """Common base: cleaned team rows with region annotation."""
    return standard_clean(df).pipe(get_team_rows).pipe(add_region)


def aggression(df: pd.DataFrame) -> pd.DataFrame:
    """KPM, first-blood rate, mean gold diff at 15 - per (team, year, region)."""
    base = _team_season_base(df)

    grouped = base.groupby(GROUP_KEYS)
    out = pd.DataFrame(
        {
            "games": grouped.size(),
            "kpm": grouped["kills"].sum() / (grouped["gamelength"].sum() / 60),
            "fb_rate": grouped["firstblood"].mean(),
        }
    )

    snap = (
        require_snapshots(base)
        .groupby(GROUP_KEYS)["golddiffat15"]
        .mean()
        .rename("golddiff15_avg")
    )
    out = out.join(snap)

    return out.reset_index()

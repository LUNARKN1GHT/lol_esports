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
        require_snapshots(base).groupby(GROUP_KEYS)["golddiffat15"].mean().rename("golddiff15_avg")
    )
    out = out.join(snap)

    return out.reset_index()


def early_dominance(df: pd.DataFrame) -> pd.DataFrame:
    """Dominance in early 10 mins: mean CSD@10 / golddiff@10 / xpdiff@10

    Need snapshot data.
    """
    base = _team_season_base(df).pipe(require_snapshots)

    grouped = base.groupby(GROUP_KEYS)
    out = pd.DataFrame(
        {
            "games_snap": grouped.size(),
            "csd10_avg": grouped["csdiffat10"].mean(),
            "golddiff10_avg": grouped["golddiffat10"].mean(),
            "xpdiff10_avg": grouped["xpdiffat10"].mean(),
        }
    )
    return out.reset_index()


def vision_control(df: pd.DataFrame) -> pd.DataFrame:
    """Vision metrics per (team, year, region).

    数据策略：player 行聚合到 team-game（sum 5 个选手），
    再对 team-season 取均值 → 平均每场该队总视野投入。

    覆盖：wardsplaced / wardskilled / controlwardsbought 字段 LPL
    全年（2016+）覆盖良好；visionscore 在 LPL 2016-17 缺失。
    """
    from .preprocess import get_player_rows, standard_clean
    from .regions import add_region

    players = standard_clean(df).pipe(get_player_rows).pipe(add_region)
    vision_cols = ["visionscore", "wardsplaced", "wardskilled", "controlwardsbought"]

    team_game = players.groupby(["gameid", "teamname", "year", "region"], as_index=False)[
        vision_cols
    ].sum(min_count=1)

    grouped = team_game.groupby(GROUP_KEYS)
    out = pd.DataFrame(
        {
            "games_vision": grouped.size(),
            "vs_avg": grouped["visionscore"].mean(),
            "wards_placed_avg": grouped["wardsplaced"].mean(),
            "wards_killed_avg": grouped["wardskilled"].mean(),
            "ctrl_wards_avg": grouped["controlwardsbought"].mean(),
        }
    )
    return out.reset_index()


def objective_focus(df: pd.DataFrame) -> pd.DataFrame:
    """Objective control metrics per (team, year, region).

    主指标用 count 字段（dragons / barons / heralds），LPL 全年覆盖完整。
    First-X rate 字段在 LPL 2016-17 和 2022+ 部分缺失（采集口径），会有 NaN。
    """
    from .preprocess import get_team_rows, standard_clean
    from .regions import add_region

    teams = standard_clean(df).pipe(get_team_rows).pipe(add_region)

    grouped = teams.groupby(GROUP_KEYS)
    out = pd.DataFrame(
        {
            "games_obj": grouped.size(),
            # 数量：每场该队拿到多少
            "dragons_avg": grouped["dragons"].mean(),
            "barons_avg": grouped["barons"].mean(),
            "heralds_avg": grouped["heralds"].mean(),
            # 首拿率：mean(0/1) = 该队拿到首条 X 的比例
            "first_dragon_rate": grouped["firstdragon"].mean(),
            "first_baron_rate": grouped["firstbaron"].mean(),
            "first_herald_rate": grouped["firstherald"].mean(),
        }
    )
    return out.reset_index()


def build_playstyle_table(df: pd.DataFrame) -> pd.DataFrame:
    """合并四个维度的指标到一张 (team, year, region) 长表。"""
    agg = aggression(df)
    early = early_dominance(df)
    vis = vision_control(df)
    obj = objective_focus(df)

    merged = agg
    for other in [early, vis, obj]:
        merged = merged.merge(other, on=GROUP_KEYS, how="outer")
    return merged

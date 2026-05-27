"""League regions mapping for regional style analysis.

通用原则：
- MAJOR_REGION_MAP: 4 大赛区及其历史改名 / 国内杯赛 / 官方继任体系
- INTERNATIONAL: Riot 主办或跨赛区的国际邀请赛
- ACADEMY: 主赛区下属的二级 / 青训 / 升降赛体系
- 其余 → "Others"（包括 2025 新设的 LCP / LTA 合并区，因样本仅一年暂归 Others）
"""

import pandas as pd

MAJOR_REGION_MAP = {
    # LPL (China)
    "LPL": "LPL",
    "DCup": "LPL",  # Demacia Cup（中国国内杯赛）
    # LCK (Korea)
    "LCK": "LCK",
    "KeSPA": "LCK",  # KeSPA Cup（韩国国内杯赛）
    "OGN": "LCK",  # 2015 OnGameNet 主办的早期韩国顶级联赛
    # LCS (North America)
    "LCS": "LCS",
    "NA LCS": "LCS",
    "LTA N": "LCS",  # 2025 北美区合并后的官方继任
    # LEC (Europe)
    "LEC": "LEC",
    "EU LCS": "LEC",
}

ACADEMY = frozenset(
    {
        # China
        "LDL",  # LPL Development League
        "LSPL",  # LoL Secondary Pro League (LDL 前身)
        # Korea
        "LCKC",  # LCK Challengers
        "CK",  # Korea Challengers (LCKC 前身)
        # North America
        "NACL",  # NA Challengers
        "LCSA",  # LCS Academy
        "NA CS",  # NA Challenger Series
        # Europe
        "EU CS",  # EU Challenger Series
        "LFL2",  # LFL 二级
        "PRMP",  # Prime League Promotion
        "GLLPA",  # Greek/Balkan Promotion Amateur
        "EBLPA",  # Eastern Balkan Promotion Amateur
        # Other regional tier-2
        "CBLOLA",  # CBLOL Academy
        "OCS",  # Oceanic Challenger Series
        "LJLCS",  # LJL Challenger Series
        "LJLA",  # LJL Academy
    }
)

INTERNATIONAL = frozenset(
    {
        "WLDs",  # World Championship
        "MSI",  # Mid-Season Invitational
        "MSC",  # Mid-Season Cup (2020)
        "EWC",  # Esports World Cup
        "IEM",  # Intel Extreme Masters (LoL era)
        "IWCI",  # International Wildcard Invitational
        "ASI",  # Asian Games / All-Star series
        "Asia Master",
        "Riot",  # Riot 直办特殊赛事
    }
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

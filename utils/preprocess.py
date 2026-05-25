"""Row-subset selectors and filtering rules of the merged dataset

Data structure (12 rows for each game):
- participantid 1-10 (position {top, jng, mid, bot, sup})
- participantid 100, 200 (position == 'team)

datacompleteness:
- 'complete': all complete
- 'partial': partly missing

gamelength:
- seconds: < 900 are remake / forfeit / surrender. Should be ignored
"""

import pandas as pd

PLAYER_POSITIONS = ("top", "jng", "mid", "bot", "sup")
TEAM_POSITION = "team"


def get_player_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["position"].isin(PLAYER_POSITIONS)]


def get_team_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["position"] == TEAM_POSITION]


def filter_complete(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["datacompleteness"] == "complete"]


def filter_valid_gamelength(df: pd.DataFrame, min_seconds: int = 900) -> pd.DataFrame:
    valid_games = df.loc[df["gamelength"] >= min_seconds, "gameid"].unique()
    return df[df["gameid"].isin(valid_games)]


def standard_clean(df: pd.DataFrame, min_seconds: int = 900) -> pd.DataFrame:
    """Standard data processing pipeline"""
    return filter_valid_gamelength(filter_complete(df), min_seconds=min_seconds)

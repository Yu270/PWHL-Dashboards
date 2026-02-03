# Librairies
import os
import pandas as pd
from .util import (
    process_seasons,
    process_games,
    process_teams,
    process_standings,
    process_skaters,
    process_goalies,
    process_penalties,
    process_standings_advanced,
)


def get_seasons() -> pd.DataFrame:
    """
    """
    if os.path.exists("./cache/references/all_seasons.csv"):
        return pd.read_csv("./cache/references/all_seasons.csv",index_col=0).sort_values("start_date",ascending=False)
    return process_seasons().sort_values("start_date",ascending=False)


def get_teams(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        return pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0).sort_index()
    return process_teams(id_saison,nom_saison).sort_index()


def get_games_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/games_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/games_df.csv",index_col=0).sort_index()
    return process_games(id_saison,nom_saison).sort_index()


def get_standings_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/standings_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/standings_df.csv",index_col=0).sort_index()
    return process_standings(id_saison,nom_saison).sort_index()


def get_skaters_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/skaters_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/skaters_df.csv",index_col=0).sort_index()
    return process_skaters(id_saison,nom_saison).sort_index()


def get_goalies_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/goalies_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/goalies_df.csv",index_col=0).sort_index()
    return process_goalies(id_saison,nom_saison).sort_index()


def get_penalties_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/penalties_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/penalties_df.csv").sort_values(["game_id","event_id"])
    return process_penalties(id_saison,nom_saison).sort_values(["game_id","event_id"])


def get_standings_advanced_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/standings_advanced_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/standings_advanced_df.csv",index_col=0).sort_index()
    return process_standings_advanced(id_saison,nom_saison).sort_index()

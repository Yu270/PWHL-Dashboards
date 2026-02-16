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
    process_skaters_all_time,
    process_goalies_all_time,
    process_penalties_all_time,
    process_shots,
)


def get_seasons() -> pd.DataFrame:
    """
    Fonction qui retourne les données des saisons. 

    Sortie
        données des saisons
    """
    if os.path.exists("./cache/traitees/all_seasons.csv"):
        return pd.read_csv("./cache/traitees/all_seasons.csv",index_col=0).sort_values("start_date",ascending=False)
    return process_seasons().sort_values("start_date",ascending=False)


def get_teams(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des équipes d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des équipes
    """
    if os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        return pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0).sort_index()
    return process_teams(id_saison,nom_saison).sort_index()


def get_games_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des parties d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des parties
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/games_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/games_df.csv",index_col=0).sort_index()
    return process_games(id_saison,nom_saison).sort_index()


def get_standings_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données du classement d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données du classement
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/standings_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/standings_df.csv",index_col=0).sort_index()
    return process_standings(id_saison,nom_saison).sort_index()


def get_skaters_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des patineuses d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des patineuses
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/skaters_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/skaters_df.csv",index_col=0).sort_index()
    return process_skaters(id_saison,nom_saison).sort_index()


def get_goalies_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des gardiennes d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des gardiennes
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/goalies_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/goalies_df.csv",index_col=0).sort_index()
    return process_goalies(id_saison,nom_saison).sort_index()


def get_penalties_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des pénalités d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des pénalités
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/penalties_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/penalties_df.csv").sort_values(["game_id","event_id"])
    return process_penalties(id_saison,nom_saison).sort_values(["game_id","event_id"])


def get_standings_advanced_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données avancées du classement d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données avancées du classement
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/standings_advanced_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/standings_advanced_df.csv",index_col=0).sort_index()
    return process_standings_advanced(id_saison,nom_saison).sort_index()


def get_skaters_all_time_df() -> pd.DataFrame:
    """
    Fonction qui retourne les données des patineuses (toutes les saisons). 
    
    Sortie
        données des patineuses (toutes les saisons)
    """
    if os.path.exists("./cache/traitees/skaters_df.csv"):
        return pd.read_csv("./cache/traitees/skaters_df.csv",index_col=0).sort_index()
    return process_skaters_all_time().sort_index()


def get_goalies_all_time_df() -> pd.DataFrame:
    """
    Fonction qui retourne les données des gardiennes (toutes les saisons). 
    
    Sortie
        données des gardiennes (toutes les saisons)
    """
    if os.path.exists("./cache/traitees/goalies_df.csv"):
        return pd.read_csv("./cache/traitees/goalies_df.csv",index_col=0).sort_index()
    return process_goalies_all_time().sort_index()


def get_penalties_all_time_df() -> pd.DataFrame:
    """
    Fonction qui retourne les données des pénalités (toutes les saisons). 
    
    Sortie
        données des pénalités (toutes les saisons)
    """
    if os.path.exists("./cache/traitees/penalties_df.csv"):
        return pd.read_csv("./cache/traitees/penalties_df.csv").sort_values(["season_id","game_id","event_id"]).reset_index(drop=True)
    return process_penalties_all_time().sort_values(["season_id","game_id","event_id"]).reset_index(drop=True)


def get_shots_df(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui retourne les données des tirs d'une saison. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données des tirs
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/shots_df.csv"):
        return pd.read_csv(f"./cache/traitees/{nom_saison}/shots_df.csv",index_col=0).sort_values(["game_id","event_id"])
    return process_shots(id_saison,nom_saison).sort_values(["game_id","event_id"])

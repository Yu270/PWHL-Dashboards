import os
import json
import numpy as np
import pandas as pd
from .fetching import (
    fetch_seasons,
    fetch_games,
    fetch_teams,
    fetch_standings,
    fetch_skaters,
    fetch_goalies,
    fetch_game_events,
)


def process_seasons() -> pd.DataFrame:
    """
    Fonction qui traite les données des saisons.  
    Enregistre les données dans la cache en plus de les retourner. 

    Sortie
        données traitées des saisons
    """
    if not os.path.exists(f"./cache/traitees"):
        os.makedirs(f"./cache/traitees")
    
    if not os.path.exists("./cache/references/all_seasons.csv"):
        fetch_seasons()
    seasons = pd.read_csv("./cache/references/all_seasons.csv",index_col=0)
    seasons["games_played"] = None
    for id_saison in seasons.index:
        if not os.path.exists(f"./cache/brutes/{seasons.loc[id_saison,"season_name"]}/all_games.csv"):
            fetch_games(id_saison,seasons.loc[id_saison,"season_name"])
        games = pd.read_csv(f"./cache/brutes/{seasons.loc[id_saison,"season_name"]}/all_games.csv",index_col=0)
        seasons.loc[id_saison,"games_played"] = games[games.final==1].shape[0]
    seasons.to_csv("./cache/traitees/all_seasons.csv")
    return seasons


def process_games(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données des parties d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées des parties
    """
    if not os.path.exists(f"./cache/traitees/{nom_saison}"):
        os.makedirs(f"./cache/traitees/{nom_saison}")
    
    if not os.path.exists(f"./cache/brutes/{nom_saison}/all_games.csv"):
        fetch_games(id_saison,nom_saison)
    games = pd.read_csv(f"./cache/brutes/{nom_saison}/all_games.csv",index_col=0)
    games = games[games.final==1]
    columns = ["season_id","date_played","GameDateISO8601","home_team","visiting_team","home_goal_count","visiting_goal_count","period","overtime","game_number","shootout","attendance","final","venue_name","venue_location"]
    df = games[columns].copy()
    df.rename(columns={
        "date_played": "date",
        "GameDateISO8601": "datetime",
        "home_team": "home_team_id",
        "visiting_team": "visiting_team_id",
        "home_goal_count": "home_goals",
        "visiting_goal_count": "visiting_goals",
        "period": "last_period",
    },inplace=True)
    if "Regular" in nom_saison:
        winning_team = []
        losing_team = []
        home_points = []
        visiting_points = []
        for i in df.index:
            if df.loc[i,"home_goals"]>df.loc[i,"visiting_goals"]:
                winning_team.append(df.loc[i,"home_team_id"])
                losing_team.append(df.loc[i,"visiting_team_id"])
                if df.loc[i,"overtime"]==1 or df.loc[i,"shootout"]==1:
                    home_points.append(2)
                    visiting_points.append(1)
                else:
                    home_points.append(3)
                    visiting_points.append(0)
            elif df.loc[i,"visiting_goals"]>df.loc[i,"home_goals"]:
                winning_team.append(df.loc[i,"visiting_team_id"])
                losing_team.append(df.loc[i,"home_team_id"])
                if df.loc[i,"overtime"]==1 or df.loc[i,"shootout"]==1:
                    home_points.append(1)
                    visiting_points.append(2)
                else:
                    home_points.append(0)
                    visiting_points.append(3)
            else:
                winning_team.append(None)
                losing_team.append(None)
                home_points.append(0)
                visiting_points.append(0)
        df["winning_team"] = winning_team
        df["losing_team"] = losing_team
        df["home_points"] = home_points
        df["visiting_points"] = visiting_points
    else:
        df["winning_team"] = np.where(df.home_goals>df.visiting_goals,df.home_team_id,np.where(df.visiting_goals>df.home_goals,df.visiting_team_id,None))
        df["losing_team"] = np.where(df.home_goals>df.visiting_goals,df.visiting_team_id,np.where(df.visiting_goals>df.home_goals,df.home_team_id,None))
        df["home_points"] = 0
        df["visiting_points"] = 0
    df.to_csv(f"./cache/traitees/{nom_saison}/games_df.csv")
    return df


def process_teams(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données des équipes d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées des équipes
    """
    if not os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        fetch_teams(id_saison,nom_saison)
    return pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0)


def process_standings(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données du classement d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées du classement
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/games_df.csv"):
        games = pd.read_csv(f"./cache/traitees/{nom_saison}/games_df.csv",index_col=0)
    else:
        games = process_games(id_saison,nom_saison)
    if not os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        fetch_teams(id_saison,nom_saison)
    teams = pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0)
    all_teams = []
    for i in teams.index:
        home_games = games[games.home_team_id==i].copy()
        visiting_games = games[games.visiting_team_id==i].copy()
        data = {"team_id": i}
        data["home_games_played"] = home_games.shape[0]
        data["home_wins"] = home_games[home_games.winning_team==i].shape[0]
        data["home_reg_wins"] = home_games[(home_games.winning_team==i)*(home_games.overtime==0)*(home_games.shootout==0)].shape[0]
        data["home_ot_wins"] = home_games[(home_games.winning_team==i)*(home_games.overtime>0)*(home_games.shootout==0)].shape[0]
        data["home_so_wins"] = home_games[(home_games.winning_team==i)*(home_games.shootout>0)].shape[0]
        data["home_wins_pct"] = 100*data["home_wins"]/data["home_games_played"] if data["home_games_played"]>0 else 0.0
        data["home_losses"] = home_games[home_games.losing_team==i].shape[0]
        data["home_reg_losses"] = home_games[(home_games.losing_team==i)*(home_games.overtime==0)*(home_games.shootout==0)].shape[0]
        data["home_ot_losses"] = home_games[(home_games.losing_team==i)*(home_games.overtime>0)*(home_games.shootout==0)].shape[0]
        data["home_so_losses"] = home_games[(home_games.losing_team==i)*(home_games.shootout>0)].shape[0]
        data["home_goals_for"] = home_games.home_goals.sum()
        data["home_goals_against"] = home_games.visiting_goals.sum()
        data["home_goals_for_avg"] = data["home_goals_for"]/data["home_games_played"] if data["home_games_played"]>0 else 0.0
        data["home_goals_against_avg"] = data["home_goals_against"]/data["home_games_played"] if data["home_games_played"]>0 else float("inf")
        data["visiting_games_played"] = visiting_games.shape[0]
        data["visiting_wins"] = visiting_games[visiting_games.winning_team==i].shape[0]
        data["visiting_reg_wins"] = visiting_games[(visiting_games.winning_team==i)*(visiting_games.overtime==0)*(visiting_games.shootout==0)].shape[0]
        data["visiting_ot_wins"] = visiting_games[(visiting_games.winning_team==i)*(visiting_games.overtime>0)*(visiting_games.shootout==0)].shape[0]
        data["visiting_so_wins"] = visiting_games[(visiting_games.winning_team==i)*(visiting_games.shootout>0)].shape[0]
        data["visiting_wins_pct"] = 100*data["visiting_wins"]/data["visiting_games_played"] if data["visiting_games_played"]>0 else 0.0
        data["visiting_losses"] = visiting_games[visiting_games.losing_team==i].shape[0]
        data["visiting_reg_losses"] = visiting_games[(visiting_games.losing_team==i)*(visiting_games.overtime==0)*(visiting_games.shootout==0)].shape[0]
        data["visiting_ot_losses"] = visiting_games[(visiting_games.losing_team==i)*(visiting_games.overtime>0)*(visiting_games.shootout==0)].shape[0]
        data["visiting_so_losses"] = visiting_games[(visiting_games.losing_team==i)*(visiting_games.shootout>0)].shape[0]
        data["visiting_goals_for"] = visiting_games.visiting_goals.sum()
        data["visiting_goals_against"] = visiting_games.home_goals.sum()
        data["visiting_goals_for_avg"] = data["visiting_goals_for"]/data["visiting_games_played"] if data["visiting_games_played"]>0 else 0.0
        data["visiting_goals_against_avg"] = data["visiting_goals_against"]/data["visiting_games_played"] if data["visiting_games_played"]>0 else float("inf")
        data["home_tot_attendance"] = home_games.attendance.sum()
        data["home_avg_attendance"] = home_games.attendance.mean()
        data["games_played"] = data["home_games_played"]+data["visiting_games_played"]
        data["wins"] = data["home_wins"]+data["visiting_wins"]
        data["reg_wins"] = data["home_reg_wins"]+data["visiting_reg_wins"]
        data["ot_wins"] = data["home_ot_wins"]+data["visiting_ot_wins"]
        data["so_wins"] = data["home_so_wins"]+data["visiting_so_wins"]
        data["non_reg_wins"] = data["ot_wins"]+data["so_wins"]
        data["wins_pct"] = 100*data["wins"]/data["games_played"] if data["games_played"]>0 else 0.0
        data["losses"] = data["home_losses"]+data["visiting_losses"]
        data["reg_losses"] = data["home_reg_losses"]+data["visiting_reg_losses"]
        data["ot_losses"] = data["home_ot_losses"]+data["visiting_ot_losses"]
        data["so_losses"] = data["home_so_losses"]+data["visiting_so_losses"]
        data["non_reg_losses"] = data["ot_losses"]+data["so_losses"]
        data["goals_for"] = data["home_goals_for"]+data["visiting_goals_for"]
        data["goals_against"] = data["home_goals_against"]+data["visiting_goals_against"]
        data["goals_for_avg"] = data["goals_for"]/data["games_played"] if data["games_played"]>0 else 0.0
        data["goals_against_avg"] = data["goals_against"]/data["games_played"] if data["games_played"]>0 else float("inf")
        data["points"] = home_games.home_points.sum()+visiting_games.visiting_points.sum()
        all_teams.append(data)
    df_base = pd.DataFrame(all_teams)

    if not os.path.exists(f"./cache/brutes/{nom_saison}/standings.csv"):
        fetch_standings(id_saison,nom_saison)
    df_add = pd.read_csv(f"./cache/brutes/{nom_saison}/standings.csv")
    columns = ["team_id","name","team_code","penalty_minutes","power_play_goals","power_play_goals_against","shootout_goals","shootout_goals_against","shootout_attempts","shootout_attempts_against","short_handed_goals_for","short_handed_goals_against","power_play_pct","penalty_kill_pct","power_plays","times_short_handed","games_remaining"]
    df_add = df_add[columns].copy()
    df_add.rename(columns={"name": "team_name"},inplace=True)

    df = pd.merge(df_base,df_add,how="left",on="team_id")
    df.sort_values(["points","reg_wins","wins","team_code"],ascending=False,inplace=True)
    df["penalty_minutes_avg"] = np.where(df["games_played"]>0,df["penalty_minutes"]/df["games_played"],0.0)
    df["rank"] = range(1,df.shape[0]+1)
    df["season_id"] = id_saison
    df.set_index("rank",inplace=True)
    df.to_csv(f"./cache/traitees/{nom_saison}/standings_df.csv")
    return df


def process_skaters(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données des patineuses d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées des patineuses
    """
    if not os.path.exists(f"./cache/traitees/{nom_saison}"):
        os.makedirs(f"./cache/traitees/{nom_saison}")
    
    if not os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        fetch_teams(id_saison,nom_saison)
    teams = pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0)
    df = pd.DataFrame()
    columns = ["first_name","last_name","name","active","height","weight","shoots","position","rookie","jersey_number","team_id","birthdate","hometown","birthtown","birthprov","birthcntry","games_played","game_winning_goals","first_goals","empty_net_goals","overtime_goals","ice_time","goals","shots","hits","shots_blocked_by_player","assists","points","penalty_minutes","minor_penalties","major_penalties","power_play_goals","power_play_assists","power_play_points","short_handed_goals","short_handed_assists","short_handed_points","shootout_goals","shootout_attempts","faceoff_attempts","faceoff_wins","player_image"]
    for i in teams.index:
        if not os.path.exists(f"./cache/brutes/{nom_saison}/skaters_{teams.loc[i,"code"]}.csv"):
            fetch_skaters(i,teams.loc[i,"code"],id_saison,nom_saison)
        temp = pd.read_csv(f"./cache/brutes/{nom_saison}/skaters_{teams.loc[i,"code"]}.csv",index_col=0)
        if temp.shape[0]>0:
            temp = temp[columns].copy()
            temp.rename(columns={"name": "player_name", "shots_blocked_by_player": "shots_blocked"},inplace=True)
            df = pd.concat((df,temp))
    df["birthprov"] = df.birthprov.fillna("(unknown)")
    df["birthcntry"] = df.birthcntry.fillna("(unknown)")
    df["position"] = np.where(df.position.str.contains("D"),"D",np.where(df.position.str.contains("W")+df.position.str.contains("C"),"F",df.position))
    df["ice_time_min"] = df["ice_time"]/60
    df["min_for_point"] = np.where(df["points"]>0,df["ice_time_min"]/df["points"],float("inf"))
    df["min_for_shot"] = np.where(df["shots"]>0,df["ice_time_min"]/df["shots"],float("inf"))
    df["ice_time_avg"] = np.where(df["games_played"]>0,df["ice_time"]/df["games_played"],0.0)
    df["ice_time_min_avg"] = df["ice_time_avg"]/60
    df["goals_avg"] = np.where(df["games_played"]>0,df["goals"]/df["games_played"],0.0)
    df["shots_avg"] = np.where(df["games_played"]>0,df["shots"]/df["games_played"],0.0)
    df["hits_avg"] = np.where(df["games_played"]>0,df["hits"]/df["games_played"],0.0)
    df["shots_blocked_avg"] = np.where(df["games_played"]>0,df["shots_blocked"]/df["games_played"],0.0)
    df["assists_avg"] = np.where(df["games_played"]>0,df["assists"]/df["games_played"],0.0)
    df["points_avg"] = np.where(df["games_played"]>0,df["points"]/df["games_played"],0.0)
    df["penalty_minutes_avg"] = np.where(df["games_played"]>0,df["penalty_minutes"]/df["games_played"],0.0)
    df["minor_penalties_avg"] = np.where(df["games_played"]>0,df["minor_penalties"]/df["games_played"],0.0)
    df["goals_pct"] = np.where(df["shots"]>0,100*df["goals"]/df["shots"],0.0)
    df["shootout_pct"] = np.where(df["shootout_attempts"]>0,100*df["shootout_goals"]/df["shootout_attempts"],0.0)
    df["faceoff_pct"] = np.where(df["faceoff_attempts"]>0,100*df["faceoff_wins"]/df["faceoff_attempts"],0.0)
    df["first_goals_pct"] = np.where(df["games_played"]>0,100*df["first_goals"]/df["games_played"],0.0)
    df["birthyear"] = df.birthdate.str[-4:].astype(int)
    df["age"] = int(nom_saison[:4])-df["birthyear"]
    df["w_age"] = df["age"]*df["games_played"]
    df["feet"] = None
    df["inches"] = None
    df["height_cm"] = None
    df["w_height_cm"] = None
    df.reset_index(inplace=True)
    for i in df.index:
        if df.loc[i,"height"]==df.loc[i,"height"]:
            df.loc[i,"height"] = df.loc[i,"height"].replace("\"","")
            df.loc[i,"height"] = df.loc[i,"height"].replace("’","'")
            df.loc[i,"height"] = df.loc[i,"height"].replace("''","")
            df.loc[i,"height"] = df.loc[i,"height"].replace("”","")
            delim = df.loc[i,"height"].find("'")
            df.loc[i,"feet"] = int(df.loc[i,"height"][:delim])
            if len(df.loc[i,"height"])>delim+1:
                df.loc[i,"inches"] = int(df.loc[i,"height"][delim+1:])
            else:
                df.loc[i,"inches"] = 0
            df.loc[i,"height_cm"] = (12*df.loc[i,"feet"]+df.loc[i,"inches"])*2.54
            df.loc[i,"w_height_cm"] = df.loc[i,"height_cm"]*df.loc[i,"games_played"]
    df.drop(columns=["feet","inches","birthyear"],inplace=True)
    df["season_id"] = id_saison
    df["player_id"] = df.player_id.astype(str)+"-"+df.team_id.astype(str)
    df.set_index("player_id",inplace=True)
    df.to_csv(f"./cache/traitees/{nom_saison}/skaters_df.csv")
    return df


def process_goalies(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données des gardiennes d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées des gardiennes
    """
    if not os.path.exists(f"./cache/traitees/{nom_saison}"):
        os.makedirs(f"./cache/traitees/{nom_saison}")
    
    if not os.path.exists(f"./cache/references/{nom_saison}/all_teams.csv"):
        fetch_teams(id_saison,nom_saison)
    teams = pd.read_csv(f"./cache/references/{nom_saison}/all_teams.csv",index_col=0)
    df = pd.DataFrame()
    columns = ["rookie","first_name","last_name","name","active","height","weight","position","jersey_number","catches","team_id","birthdate","hometown","birthtown","birthprov","birthcntry","games_played","seconds_played","saves","shots","goals_against","shutouts","wins","total_losses","shootout_goals_against","shootout_saves","shootout_attempts","goals","assists","points","penalty_minutes","player_image"]
    for i in teams.index:
        if not os.path.exists(f"./cache/brutes/{nom_saison}/goalies_{teams.loc[i,"code"]}.csv"):
            fetch_goalies(i,teams.loc[i,"code"],id_saison,nom_saison)
        temp = pd.read_csv(f"./cache/brutes/{nom_saison}/goalies_{teams.loc[i,"code"]}.csv",index_col=0)
        if temp.shape[0]>0:
            temp = temp[columns].copy()
            temp.rename(columns={"name": "player_name","seconds_played": "ice_time","shots": "shots_against","total_losses": "losses"},inplace=True)
            df = pd.concat((df,temp))
    df["birthprov"] = df.birthprov.fillna("(unknown)")
    df["birthcntry"] = df.birthcntry.fillna("(unknown)")
    df["ice_time_min"] = df["ice_time"]/60
    df["ice_time_avg"] = np.where(df["games_played"]>0,df["ice_time"]/df["games_played"],0.0)
    df["saves_avg"] = np.where(df["games_played"]>0,df["saves"]/df["games_played"],0.0)
    df["shots_against_avg"] = np.where(df["games_played"]>0,df["shots_against"]/df["games_played"],0.0)
    df["goals_against_avg"] = np.where(df["games_played"]>0,df["goals_against"]/df["games_played"],float("inf"))
    df["saves_pct"] = np.where(df["shots_against"]>0,100*df["saves"]/df["shots_against"],0.0)
    df["wins_pct"] = np.where(df["games_played"]>0,100*df["wins"]/df["games_played"],0.0)
    df["shootout_pct"] = np.where(df["shootout_attempts"]>0,100*df["shootout_saves"]/df["shootout_attempts"],0.0)
    df["birthyear"] = df.birthdate.str[-4:].astype(int)
    df["age"] = int(nom_saison[:4])-df["birthyear"]
    df["w_age"] = df["age"]*df["games_played"]
    df["feet"] = None
    df["inches"] = None
    df["height_cm"] = None
    df["w_height_cm"] = None
    df.reset_index(inplace=True)
    for i in df.index:
        if df.loc[i,"height"]==df.loc[i,"height"]:
            df.loc[i,"height"] = df.loc[i,"height"].replace("\"","")
            df.loc[i,"height"] = df.loc[i,"height"].replace("’","'")
            df.loc[i,"height"] = df.loc[i,"height"].replace("''","")
            df.loc[i,"height"] = df.loc[i,"height"].replace("”","")
            delim = df.loc[i,"height"].find("'")
            df.loc[i,"feet"] = int(df.loc[i,"height"][:delim])
            if len(df.loc[i,"height"])>delim+1:
                df.loc[i,"inches"] = int(df.loc[i,"height"][delim+1:])
            else:
                df.loc[i,"inches"] = 0
            df.loc[i,"height_cm"] = (12*df.loc[i,"feet"]+df.loc[i,"inches"])*2.54
            df.loc[i,"w_height_cm"] = df.loc[i,"height_cm"]*df.loc[i,"games_played"]
    df.drop(columns=["feet","inches","birthyear"],inplace=True)
    df["season_id"] = id_saison
    df["player_id"] = df.player_id.astype(str)+"-"+df.team_id.astype(str)
    df.set_index("player_id",inplace=True)
    df.to_csv(f"./cache/traitees/{nom_saison}/goalies_df.csv")
    return df


def process_penalties(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui traite les données des pénalités d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données traitées des pénalités
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/games_df.csv"):
        games = pd.read_csv(f"./cache/traitees/{nom_saison}/games_df.csv",index_col=0)
    else:
        games = process_games(id_saison,nom_saison)

    all_penalties = []
    for id_partie in games.index:
        if not os.path.exists(f"./cache/brutes/{nom_saison}/games/{id_partie}.json"):
            fetch_game_events(id_partie,nom_saison)
        f = open(f"./cache/brutes/{nom_saison}/games/{id_partie}.json","r")
        events = json.load(f)
        f.close()
        penalties = [i for i in events if i.get("event")=="penalty"]
        for i in penalties:
            i["game_id"] = id_partie
        all_penalties += penalties.copy()
    df = pd.DataFrame(all_penalties)
    columns = ["event","id","game_id","player_id","player_served","time_off_formatted","minutes","penalty_class","lang_penalty_description","period_id","team_id"]
    df = df[columns].copy()
    df.rename(columns={"id": "event_id","player_served": "player_served_id","time_off_formatted": "time_off","lang_penalty_description": "penalty_description", "period_id": "period"},inplace=True)
    df["season_id"] = id_saison
    df["player_id"] = df.player_id.astype(str)+"-"+df.team_id.astype(str)
    df["player_served_id"] = df.player_served_id.astype(str)+"-"+df.team_id.astype(str)
    df.to_csv(f"./cache/traitees/{nom_saison}/penalties_df.csv",index=False)
    return df


def process_standings_advanced(id_saison: int, nom_saison: str) -> pd.DataFrame:
    """
    Fonction qui ajoute des données au classement d'une saison.  
    Enregistre les données dans la cache en plus de les retourner. 

    Entrées
        id_saison: identifiant d'une saison
        nom_saison: nom d'une saison
    
    Sortie
        données avancées traitées du classement
    """
    if os.path.exists(f"./cache/traitees/{nom_saison}/standings_df.csv"):
        standings = pd.read_csv(f"./cache/traitees/{nom_saison}/standings_df.csv")
    else:
        standings = process_standings(id_saison,nom_saison).reset_index()
    if os.path.exists(f"./cache/traitees/{nom_saison}/skaters_df.csv"):
        skaters = pd.read_csv(f"./cache/traitees/{nom_saison}/skaters_df.csv")
    else:
        skaters = process_skaters(id_saison,nom_saison).reset_index()
    if os.path.exists(f"./cache/traitees/{nom_saison}/goalies_df.csv"):
        goalies = pd.read_csv(f"./cache/traitees/{nom_saison}/goalies_df.csv")
    else:
        goalies = process_goalies(id_saison,nom_saison).reset_index()

    agg_skaters = skaters[["team_id","shots","hits","shots_blocked","first_goals"]].groupby("team_id").sum().reset_index()
    agg_goalies = goalies[["team_id","shots_against"]].groupby("team_id").sum().reset_index()
    df = pd.merge(standings,agg_skaters,how="left",on="team_id")
    df = pd.merge(df,agg_goalies,how="left",on="team_id")
    df["shots_avg"] = np.where(df["games_played"]>0,df["shots"]/df["games_played"],0.0)
    df["hits_avg"] = np.where(df["games_played"]>0,df["hits"]/df["games_played"],0.0)
    df["shots_blocked_pct"] = np.where(df["shots_against"]+df["shots_blocked"]>0,100*df["shots_blocked"]/(df["shots_against"]+df["shots_blocked"]),0.0)
    df["goals_pct"] = np.where(df["shots"]>0,100*df["goals_for"]/df["shots"],0.0)
    df["first_goals_pct"] = np.where(df["games_played"]>0,100*df["first_goals"]/df["games_played"],0.0)
    players = pd.concat((skaters[["team_id","w_age","w_height_cm","games_played"]],goalies[["team_id","w_age","w_height_cm","games_played"]]))
    agg_temp = players.groupby("team_id").sum().reset_index().rename(columns={"games_played": "weights"})
    df = pd.merge(df,agg_temp,how="left",on="team_id")
    df["age_avg"] = np.where(df["weights"]>0,df["w_age"]/df["weights"],0.0)
    df["height_avg"] = np.where(df["weights"]>0,df["w_height_cm"]/df["weights"],0.0)
    df.drop(columns=["w_age","w_height_cm","weights"],inplace=True)
    df.set_index("rank",inplace=True)
    df.to_csv(f"./cache/traitees/{nom_saison}/standings_advanced_df.csv")
    return df

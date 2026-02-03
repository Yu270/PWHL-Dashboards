import os
import json
import requests
import pandas as pd


def fetch_seasons():
    """
    """
    if not os.path.exists("./cache/references"):
        os.makedirs("./cache/references")
    
    response = requests.get("https://lscluster.hockeytech.com/feed/index.php?feed=modulekit&view=seasons&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        seasons = response.json().get("SiteKit",{}).get("Seasons",[])
        deb, fin = len(seasons), 0
        for i in range(len(seasons)):
            if isinstance(seasons[i],dict) and "season_id" in seasons[i]:
                deb = i
                break
        for i in range(len(seasons),0,-1):
            if isinstance(seasons[i-1],dict) and "season_id" in seasons[i-1]:
                fin = i
                break
        df = pd.DataFrame(seasons[deb:fin])
        if df.shape[0]>0:
            df.set_index("season_id",inplace=True)
        df.to_csv("./cache/references/all_seasons.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_games(id_saison: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/brutes/{nom_saison}"):
        os.makedirs(f"./cache/brutes/{nom_saison}")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/?feed=modulekit&view=schedule&season_id={id_saison}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        games = response.json().get("SiteKit",{}).get("Schedule",[])
        deb, fin = len(games), 0
        for i in range(len(games)):
            if isinstance(games[i],dict) and "game_id" in games[i]:
                deb = i
                break
        for i in range(len(games),0,-1):
            if isinstance(games[i-1],dict) and "game_id" in games[i-1]:
                fin = i
                break
        df = pd.DataFrame(games[deb:fin])
        if df.shape[0]>0:
            df.set_index("game_id",inplace=True)
        df.to_csv(f"./cache/brutes/{nom_saison}/all_games.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_teams(id_saison: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/references/{nom_saison}"):
        os.makedirs(f"./cache/references/{nom_saison}")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/index.php?feed=modulekit&view=teamsbyseason&season_id={id_saison}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        teams = response.json().get("SiteKit",{}).get("Teamsbyseason",[])
        deb, fin = len(teams), 0
        for i in range(len(teams)):
            if isinstance(teams[i],dict) and "id" in teams[i]:
                deb = i
                break
        for i in range(len(teams),0,-1):
            if isinstance(teams[i-1],dict) and "id" in teams[i-1]:
                fin = i
                break
        df = pd.DataFrame(teams[deb:fin])
        if df.shape[0]>0:
            df.set_index("id",inplace=True)
        df.to_csv(f"./cache/references/{nom_saison}/all_teams.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_standings(id_saison: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/brutes/{nom_saison}"):
        os.makedirs(f"./cache/brutes/{nom_saison}")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/index.php?feed=modulekit&view=statviewtype&stat=conference&type=standings&season_id={id_saison}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        standings = response.json().get("SiteKit",{}).get("Statviewtype",[])
        deb, fin = len(standings), 0
        for i in range(len(standings)):
            if isinstance(standings[i],dict) and "team_id" in standings[i]:
                deb = i
                break
        for i in range(len(standings),0,-1):
            if isinstance(standings[i-1],dict) and "team_id" in standings[i-1]:
                fin = i
                break
        df = pd.DataFrame(standings[deb:fin])
        if df.shape[0]>0:
            df.set_index("team_id",inplace=True)
        df.to_csv(f"./cache/brutes/{nom_saison}/standings.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_skaters(id_equipe: int, code_equipe: str, id_saison: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/brutes/{nom_saison}"):
        os.makedirs(f"./cache/brutes/{nom_saison}")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/index.php?feed=modulekit&view=statviewtype&type=skaters&league_id=1&team_id={id_equipe}&season_id={id_saison}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        skaters = response.json().get("SiteKit",{}).get("Statviewtype",[])
        deb, fin = len(skaters), 0
        for i in range(len(skaters)):
            if isinstance(skaters[i],dict) and "player_id" in skaters[i]:
                deb = i
                break
        for i in range(len(skaters),0,-1):
            if isinstance(skaters[i-1],dict) and "player_id" in skaters[i-1]:
                fin = i
                break
        df = pd.DataFrame(skaters[deb:fin])
        if df.shape[0]>0:
            df.set_index("player_id",inplace=True)
        df.to_csv(f"./cache/brutes/{nom_saison}/skaters_{code_equipe}.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_goalies(id_equipe: int, code_equipe: str, id_saison: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/brutes/{nom_saison}"):
        os.makedirs(f"./cache/brutes/{nom_saison}")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/index.php?feed=modulekit&view=statviewtype&type=goalies&league_id=1&team_id={id_equipe}&season_id={id_saison}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        goalies = response.json().get("SiteKit",{}).get("Statviewtype",[])
        deb, fin = len(goalies), 0
        for i in range(len(goalies)):
            if isinstance(goalies[i],dict) and "player_id" in goalies[i]:
                deb = i
                break
        for i in range(len(goalies),0,-1):
            if isinstance(goalies[i-1],dict) and "player_id" in goalies[i-1]:
                fin = i
                break
        df = pd.DataFrame(goalies[deb:fin])
        if df.shape[0]>0:
            df.set_index("player_id",inplace=True)
        df.to_csv(f"./cache/brutes/{nom_saison}/goalies_{code_equipe}.csv")
    else:
        raise Exception(f"{response.status_code}, {response.reason}")


def fetch_game_events(id_partie: int, nom_saison: str):
    """
    """
    if not os.path.exists(f"./cache/brutes/{nom_saison}/games"):
        os.makedirs(f"./cache/brutes/{nom_saison}/games")
    
    response = requests.get(f"https://lscluster.hockeytech.com/feed/index.php?feed=gc&tab=pxpverbose&game_id={id_partie}&key=446521baf8c38984&client_code=pwhl")
    if response.status_code==200:
        events = response.json().get("GC",{}).get("Pxpverbose",[])
        f = open(f"./cache/brutes/{nom_saison}/games/{id_partie}.json","w")
        json.dump(events,f)
        f.close()
    else:
        raise Exception(f"{response.status_code}, {response.reason}")

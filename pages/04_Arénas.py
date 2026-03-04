import numpy as np
import pandas as pd
import streamlit as st
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_games_df, get_games_all_time_df

st.set_page_config(page_title="Arénas",page_icon="🏟️")

st.title("Arénas")


def show_visuals(base_df: pd.DataFrame, variable: str, name: str, aggregation: str, rounding: int, percent: bool = False):
    """
    Fonction qui affiche le classement des arénas selon une variable. 
    
    Entrées
        base_df: données à utiliser
        variable: variable à utiliser
        name: nom de la variable à utiliser
        aggregation: type d'aggrégation ('total' ou 'moyenne')
        rounding: arrondissement
        percent: pourcentage?
    """
    if aggregation=="total":
        agg_df = base_df[["venue",variable]].groupby("venue").sum().reset_index()
    elif aggregation=="moyenne":
        agg_df = base_df[["venue",variable]].groupby("venue").mean().reset_index()
    else:
        raise Exception("Type d'aggrégation invalide!")
    new_df = pd.merge(agg_df,base_df[["venue","venue_cntry"]].drop_duplicates(["venue","venue_cntry"]),how="left",on="venue")
    if percent:
        new_df[variable] = 100*new_df[variable]

    new_df.sort_values(variable,ascending=False,inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    cols = st.columns(min(3,new_df.shape[0]))
    for i, col in enumerate(cols):
        with col:
            value = round(new_df.loc[i,variable],rounding) if rounding>0 else int(new_df.loc[i,variable])
            if percent:
                product_card(new_df.loc[i,"venue"],price=f"{value}%",product_image=flags[new_df.loc[i,"venue_cntry"]],picture_position="left",enable_animation=False,key=f"{i+1}_{variable}_{aggregation}")
            else:
                product_card(new_df.loc[i,"venue"],price=value,product_image=flags[new_df.loc[i,"venue_cntry"]],picture_position="left",enable_animation=False,key=f"{i+1}_{variable}_{aggregation}")
    if new_df.shape[0]>3:
        reste = new_df.loc[3:].copy()
        reste["Rang"] = range(4,reste.shape[0]+4)
        reste.rename(columns={"venue": "Aréna", "venue_cntry": "Pays", variable: name},inplace=True)
        st.dataframe(reste.set_index("Rang")[["Aréna","Pays",name]])

def show_visuals2(base_df: pd.DataFrame, variable: str, name: str, rounding: int, percent: bool = False):
    """
    Fonction qui affiche le classement des équipes selon une variable. 
    
    Entrées
        base_df: données à utiliser
        variable: variable à utiliser
        name: nom de la variable à utiliser
        rounding: arrondissement
        percent: pourcentage?
    """
    new_df = base_df[base_df.games_played>0].copy()
    new_df.sort_values(variable,ascending=False,inplace=True)
    new_df.reset_index(inplace=True)
    cols = st.columns(min(3,new_df.shape[0]))
    for i, col in enumerate(cols):
        with col:
            value = round(new_df.loc[i,variable],rounding) if rounding>0 else int(new_df.loc[i,variable])
            if percent:
                product_card(new_df.loc[i,"name"],price=f"{value}%",product_image=new_df.loc[i,"team_logo_url"],picture_position="left",enable_animation=False,key=f"{i+1}_{variable}")
            else:
                product_card(new_df.loc[i,"name"],price=value,product_image=new_df.loc[i,"team_logo_url"],picture_position="left",enable_animation=False,key=f"{i+1}_{variable}")
    if new_df.shape[0]>3:
        reste = new_df.loc[3:].copy()
        reste["Rang"] = range(4,reste.shape[0]+4)
        reste.rename(columns={"name": "Équipe", variable: name},inplace=True)
        st.dataframe(reste.set_index("Rang")[["Équipe",name]])

if not ("arena" in st.session_state):
    st.session_state.arena = None

@st.fragment
def show_teams(base_df: pd.DataFrame, data_df: pd.DataFrame):
    """
    Fonction qui affiche les statistiques des équipes selon l'aréna. 

    Entrée
        base_df: données de base (équipes)
        data_df: données à utiliser (parties)
    """
    base_copy = base_df[["name","team_logo_url"]].copy()
    new_df = data_df[["home_team_id","visiting_team_id","home_goals","visiting_goals","venue","winning_team","Count"]].copy()
    arenas_list = new_df["venue"].unique().tolist()
    arenas_list.sort()
    st.session_state.arena = st.selectbox("Aréna",options=arenas_list,placeholder="Choisissez un aréna")
    new_df = new_df[new_df.venue==st.session_state.arena].copy()
    
    base_copy["games_played"] = 0
    base_copy["goals"] = 0
    base_copy["wins"] = 0
    for team_id in base_copy.index:
        home_games = new_df[new_df.home_team_id==team_id]
        visiting_games = new_df[new_df.visiting_team_id==team_id]
        base_copy.loc[team_id,"games_played"] = home_games.shape[0]+visiting_games.shape[0]
        base_copy.loc[team_id,"goals"] = home_games.home_goals.sum()+visiting_games.visiting_goals.sum()
        base_copy.loc[team_id,"wins"] = new_df[new_df.winning_team==team_id].shape[0]
    base_copy["goals_avg"] = np.where(base_copy["games_played"]>0,base_copy["goals"]/base_copy["games_played"],0.0)
    base_copy["wins_pct"] = np.where(base_copy["games_played"]>0,100*base_copy["wins"]/base_copy["games_played"],0.0)
    
    st.subheader("Parties jouées")
    show_visuals2(base_copy,"games_played","Parties jouées",0)

    st.subheader("Victoires")
    show_visuals2(base_copy,"wins","Victoires",0)

    st.subheader("Pourcentage de victoires")
    show_visuals2(base_copy,"wins_pct","% de victoires",1,True)

    st.subheader("Buts totaux")
    show_visuals2(base_copy,"goals","Buts",0)

    st.subheader("Buts par partie")
    show_visuals2(base_copy,"goals_avg","Buts",2)

if not ("team" in st.session_state):
    st.session_state.team = None

@st.fragment
def show_arenas(base_df: pd.DataFrame):
    """
    Fonction qui affiche les statistiques des arénas selon l'équipe. 

    Entrée
        base_df: données à utiliser
    """
    st.session_state.team = st.selectbox("Équipe",options=teams.name.to_list(),placeholder="Choisissez un équipe")
    id_equipe = teams[teams.name==st.session_state.team].index.to_list()[0]
    new_df = base_df[["home_team_id","visiting_team_id","home_goals","visiting_goals","venue","venue_cntry","winning_team","Count"]].copy()
    new_df = new_df[(new_df.home_team_id==id_equipe)+(new_df.visiting_team_id==id_equipe)].copy()
    
    new_df["team_goals"] = np.where(new_df.home_team_id==id_equipe,new_df.home_goals,new_df.visiting_goals)
    new_df["team_wins"] = np.where(new_df.winning_team==id_equipe,1,0)
    
    st.subheader("Parties jouées")
    show_visuals(new_df,"Count","Parties jouées","total",0)

    st.subheader("Victoires")
    show_visuals(new_df,"team_wins","Victoires","total",0)

    st.subheader("Pourcentage de victoires")
    show_visuals(new_df,"team_wins","% de victoires","moyenne",1,True)

    st.subheader("Buts totaux")
    show_visuals(new_df,"team_goals","Buts","total",0)

    st.subheader("Buts par partie")
    show_visuals(new_df,"team_goals","Buts","moyenne",2)


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list()+["(Toutes)"],placeholder="Choisissez une saison")
    if saison!="(Toutes)":
        id_saison = seasons[seasons.season_name==saison].index.to_list()[0]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            if saison=="(Toutes)":
                last_id = max(seasons[seasons.career==1].index)
                last_name = seasons.loc[last_id,"season_name"]
                teams = get_teams(last_id,last_name)
                games = get_games_all_time_df()
            else:
                teams = get_teams(id_saison,saison)
                games = get_games_df(id_saison,saison)
            games["Count"] = 1
            flags = {
                "CAN": "https://cdn.quanthockey.com/img/country-flags/Canada-Flag-48.png",
                "USA": "https://cdn.quanthockey.com/img/country-flags/United-States-Flag-48.png",
                "(unknown)": "https://img.freepik.com/premium-photo/white-natural-paper-texture-clean-square-background-wallpaper_118047-7127.jpg?w=360",
            }


@st.fragment
def arenas():
    """
    """
    st.toggle("Afficher",key="arenas")
    if st.session_state.get("arenas",False):
        st.subheader("Parties accueillies")
        show_visuals(games,"Count","Parties","total",0)

        st.subheader("Spectateurs totaux")
        show_visuals(games,"attendance","Spectateurs","total",0)

        st.subheader("Spectateurs par partie")
        show_visuals(games,"attendance","Spectateurs","moyenne",0)


with st.container(border=True):
    st.header("Arénas")
    if go:
        arenas()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def par_arena():
    """
    """
    st.toggle("Afficher",key="par_arena")
    if st.session_state.get("par_arena",False):
        show_teams(teams,games)

with st.container(border=True):
    st.header("Par aréna")
    if go:
        par_arena()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def par_equipe():
    """
    """
    st.toggle("Afficher",key="par_equipe")
    if st.session_state.get("par_equipe",False):
        show_arenas(games)

with st.container(border=True):
    st.header("Par équipe")
    if go:
        par_equipe()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

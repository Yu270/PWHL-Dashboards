import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy.ndimage import gaussian_filter
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_standings_advanced_df, get_skaters_df, get_goalies_df, get_shots_df, get_skaters_all_time_df, get_goalies_all_time_df, get_shots_all_time_df

st.set_page_config(page_title="Analyse des tirs",page_icon="🥅")

st.title("Analyse des tirs")


def get_shot_pct(base_df: pd.DataFrame, n_bins: int = 50) -> np.ndarray:
    """
    Fonction qui calcule le pourcentage de tir par emplacement. 

    Entrées
        base_df: données à utiliser
        n_bins: nombre de bins

    Sortie
        pourcentage de tir par emplacement
    """
    hist = np.histogram2d(base_df.xCoord,base_df.yCoord,bins=(np.linspace(0,296,n_bins+1),np.linspace(0,296,n_bins+1)))[0]
    return hist.T / base_df.shape[0]

def show_shot_comparison(raw_data: np.ndarray, sigma: float = 2, n_bins: int = 50, raw_data2: np.ndarray = np.array([])):
    """
    Fonction qui affiche un graphique de comparaison. 

    Entrées
        raw_data: données à utiliser (différence avec le reste de la ligue)
        sigma: paramètre de lissage
        n_bins: nombre de bins
        raw_data: autre ensemble de données à utiliser (différence avec le reste de la ligue)
    """
    diff_smooth = gaussian_filter(raw_data,sigma=sigma)
    max_abs = np.max(np.abs(diff_smooth))
    if raw_data2.size>0:
        diff_smooth2 = gaussian_filter(raw_data2,sigma=sigma)
        max_abs2 = np.max(np.maximum(np.abs(diff_smooth),np.abs(diff_smooth2)))
    img = mpimg.imread("./cache/nhl_half_rink.jpeg")
    if raw_data2.size>0:
        A, B = st.columns(2)
        with A:
            fig1, ax1 = plt.subplots()
            ax1.imshow(img,extent=[0,296,0,296])
            ax1.set_xticks(np.arange(0,296,296/6))
            ax1.set_yticks(np.arange(0,296,296/6))
            ax1.contour(np.linspace(0,296,n_bins),np.linspace(0,296,n_bins),diff_smooth,cmap="seismic",vmin=-max_abs,vmax=max_abs)
            ax1.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
            st.pyplot(fig1)
        with B:
            fig2, ax2 = plt.subplots()
            ax2.imshow(img,extent=[0,296,0,296])
            ax2.set_xticks(np.arange(0,296,296/6))
            ax2.set_yticks(np.arange(0,296,296/6))
            ax2.contour(np.linspace(0,296,n_bins),np.linspace(0,296,n_bins),diff_smooth2,cmap="seismic",vmin=-max_abs2,vmax=max_abs2)
            ax2.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
            st.pyplot(fig2)
    else:
        fig, ax = plt.subplots()
        ax.imshow(img,extent=[0,296,0,296])
        ax.set_xticks(np.arange(0,296,296/6))
        ax.set_yticks(np.arange(0,296,296/6))
        ax.contour(np.linspace(0,296,n_bins),np.linspace(0,296,n_bins),diff_smooth,cmap="seismic",vmin=-max_abs,vmax=max_abs)
        ax.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
        st.pyplot(fig)

@st.fragment
def show_team_shot_density(base_df: pd.DataFrame, shot_type: str, bw_adjust: float = 0.5, sigma: float = 2):
    """
    Fonction qui affiche la répartition des tirs d'une équipe (densité 2D).  
    S'il y a assez de données, affiche aussi une comparaison avec le reste de la ligue. 
    
    Entrées
        base_df: données à utiliser
        shot_type: type de tir à afficher
        bw_adjust: paramètre de la densité
        sigma: paramètre de lissage
    """
    assert shot_type in ["shot","goal","blocked","save","goal_against"], "Le type de tir doit être 'shot', 'goal', 'blocked', 'save' ou 'goal_against'"
    if shot_type=="shot":
        id_col = "player_team_id"
        ctrl_col = "shots"
    elif shot_type=="goal":
        id_col = "player_team_id"
        ctrl_col = "goals_for"
    elif shot_type=="blocked":
        id_col = "blocker_team_id"
        ctrl_col = "shots_blocked"
    elif shot_type=="save":
        id_col = "goalie_team_id"
        ctrl_col = "saves"
    else:
        id_col = "goalie_team_id"
        ctrl_col = "goals_against"
    
    temp = base_df[base_df[id_col]==id_equipe]
    img = mpimg.imread("./cache/nhl_half_rink.jpeg")
    fig, ax = plt.subplots()
    ax.imshow(img,extent=[0,296,0,296])
    ax.set_xticks(np.arange(0,296,296/6))
    ax.set_yticks(np.arange(0,296,296/6))
    if temp.shape[0]>=30:
        sns.kdeplot(temp,x="xCoord",y="yCoord",cmap="Reds",bw_adjust=bw_adjust,ax=ax)
    else:
        ax.scatter(temp.xCoord,temp.yCoord,color="b",marker="o")
    ax.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
    st.pyplot(fig)

    if temp.shape[0]>=30:
        st.text("Comparaison avec le reste de la ligue")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Équipe 1",options=[equipe],placeholder="Choisissez une équipe",key=f"team1_{shot_type}")
        with col2:
            st.selectbox("Équipe 2",options=[None]+teams[teams[ctrl_col]>=30].sort_values("name").name.to_list(),placeholder="Choisissez une équipe",key=f"team2_{shot_type}")
        shot_pct = get_shot_pct(temp)
        if st.session_state.get(f"team2_{shot_type}",None)!=None:
            team_id = teams[teams.name==st.session_state.get(f"team2_{shot_type}",None)].index.to_list()[0]
            temp2 = base_df[base_df[id_col]==team_id]
            shot_pct2 = get_shot_pct(temp2)
            show_shot_comparison(shot_pct-league_pct,sigma,raw_data2=shot_pct2-league_pct)
        else:
            show_shot_comparison(shot_pct-league_pct,sigma)

@st.fragment
def show_skater_shot_density(base_df: pd.DataFrame, shot_type: str, bw_adjust: float = 0.5, sigma: float = 2):
    """
    Fonction qui affiche la répartition des tirs d'une patineuse (densité 2D).  
    S'il y a assez de données, affiche aussi une comparaison avec le reste de la ligue. 
    
    Entrées
        base_df: données à utiliser
        shot_type: type de tir à afficher
        bw_adjust: paramètre de la densité
        sigma: paramètre de lissage
    """
    assert shot_type in ["shot","goal","blocked"], "Le type de tir doit être 'shot', 'goal' ou 'blocked'"
    if shot_type=="shot":
        id_col = "player_id"
        ctrl_col = "shots"
    elif shot_type=="goal":
        id_col = "player_id"
        ctrl_col = "goals"
    else:
        id_col = "blocker_id"
        ctrl_col = "shots_blocked"

    temp = base_df[base_df[id_col]==id_joueuse]
    img = mpimg.imread("./cache/nhl_half_rink.jpeg")
    fig, ax = plt.subplots()
    ax.imshow(img,extent=[0,296,0,296])
    ax.set_xticks(np.arange(0,296,296/6))
    ax.set_yticks(np.arange(0,296,296/6))
    if temp.shape[0]>=30:
        sns.kdeplot(temp,x="xCoord",y="yCoord",cmap="Reds",bw_adjust=bw_adjust,ax=ax)
    else:
        ax.scatter(temp.xCoord,temp.yCoord,color="b",marker="o")
    ax.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
    st.pyplot(fig)

    if temp.shape[0]>=30:
        st.text("Comparaison avec le reste de la ligue")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Joueuse 1",options=[joueuse],placeholder="Choisissez une joueuse",key=f"player1_{shot_type}")
        with col2:
            st.selectbox("Joueuse 2",options=[None]+skaters[skaters[ctrl_col]>=30].sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse",key=f"player2_{shot_type}")
        shot_pct = get_shot_pct(temp)
        if st.session_state.get(f"player2_{shot_type}",None)!=None:
            player_id = skaters[skaters.player_name==st.session_state.get(f"player2_{shot_type}",None)].index.to_list()[0]
            temp2 = base_df[base_df[id_col]==player_id]
            shot_pct2 = get_shot_pct(temp2)
            show_shot_comparison(shot_pct-league_pct,sigma,raw_data2=shot_pct2-league_pct)
        else:
            show_shot_comparison(shot_pct-league_pct,sigma)

@st.fragment
def show_goalie_shot_density(base_df: pd.DataFrame, shot_type: str, bw_adjust: float = 0.5, sigma: float = 2):
    """
    Fonction qui affiche la répartition des tirs sur une gardienne (densité 2D).  
    S'il y a assez de données, affiche aussi une comparaison avec le reste de la ligue. 
    
    Entrées
        base_df: données à utiliser
        shot_type: type de tir à afficher
        bw_adjust: paramètre de la densité
        sigma: paramètre de lissage
    """
    assert shot_type in ["save","goal_against"], "Le type de tir doit être 'save' ou 'goal_against'"
    if shot_type=="save":
        id_col = "goalie_id"
        ctrl_col = "saves"
    else:
        id_col = "goalie_id"
        ctrl_col = "goals_against"
    
    temp = base_df[base_df[id_col]==id_joueuse]
    img = mpimg.imread("./cache/nhl_half_rink.jpeg")
    fig, ax = plt.subplots()
    ax.imshow(img,extent=[0,296,0,296])
    ax.set_xticks(np.arange(0,296,296/6))
    ax.set_yticks(np.arange(0,296,296/6))
    if temp.shape[0]>=30:
        sns.kdeplot(temp,x="xCoord",y="yCoord",cmap="Reds",bw_adjust=bw_adjust,ax=ax)
    else:
        ax.scatter(temp.xCoord,temp.yCoord,color="b",marker="o")
    ax.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
    st.pyplot(fig)

    if temp.shape[0]>=30:
        st.text("Comparaison avec le reste de la ligue")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Joueuse 1",options=[joueuse],placeholder="Choisissez une joueuse",key=f"player1_{shot_type}")
        with col2:
            st.selectbox("Joueuse 2",options=[None]+goalies[goalies[ctrl_col]>=30].sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse",key=f"player2_{shot_type}")
        shot_pct = get_shot_pct(temp)
        if st.session_state.get(f"player2_{shot_type}",None)!=None:
            player_id = goalies[goalies.player_name==st.session_state.get(f"player2_{shot_type}",None)].index.to_list()[0]
            temp2 = base_df[base_df[id_col]==player_id]
            shot_pct2 = get_shot_pct(temp2)
            show_shot_comparison(shot_pct-league_pct,sigma,raw_data2=shot_pct2-league_pct)
        else:
            show_shot_comparison(shot_pct-league_pct,sigma)


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list()+["(Toutes)"],placeholder="Choisissez une saison")
    if saison!="(Toutes)":
        id_saison = seasons[seasons.season_name==saison].index.to_list()[0]
        teams = get_teams(id_saison,saison)
        standings = get_standings_advanced_df(id_saison,saison)
        teams = pd.merge(teams,standings[["team_id","games_played","shots","goals_for","shots_blocked","shots_against","goals_against"]],how="left",left_index=True,right_on="team_id")
        teams["saves"] = np.maximum(0,teams.shots_against-teams.goals_against)
        equipe = st.selectbox("Équipe",options=teams.sort_values("name").name.to_list(),placeholder="Choisissez une équipe")
        id_equipe = teams[teams.name==equipe].index.to_list()[0]
        skaters = get_skaters_df(id_saison,saison)
        skaters = skaters[skaters.team_id==id_equipe].copy()
        goalies = get_goalies_df(id_saison,saison)
        goalies = goalies[goalies.team_id==id_equipe].copy()
        players = pd.concat((skaters[["player_name","position","player_image","games_played"]],goalies[["player_name","position","player_image","games_played"]]))
        joueuse = st.selectbox("Joueuse",options=[None]+players.sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse")
    else:
        skaters = get_skaters_all_time_df()
        goalies = get_goalies_all_time_df()
        players = pd.concat((skaters[["player_name","position","player_image","games_played"]],goalies[["player_name","position","player_image","games_played"]]))
        joueuse = st.selectbox("Joueuse",options=players.sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse")
    if joueuse!=None:
        id_joueuse = players[players.player_name==joueuse].index.to_list()[0]
        pos_joueuse = players.loc[id_joueuse,"position"]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            if saison!="(Toutes)":
                shots = get_shots_df(id_saison,saison)
            else:
                shots = get_shots_all_time_df()
            league_pct = get_shot_pct(shots)


with st.container():
    st.header("Informations")
    if go:
        if joueuse==None:
            team_stats = f"{teams.loc[id_equipe,"games_played"]} parties jouées, {shots[(shots["type"].isin(["shot","goal"]))*(shots.player_team_id==id_equipe)].shape[0]} tirs, {shots[(shots["type"]=="goal")*(shots.player_team_id==id_equipe)].shape[0]} buts, {shots[shots.blocker_team_id==id_equipe].shape[0]} tirs bloqués, {shots[(shots["type"].isin(["shot","goal"]))*(shots.goalie_team_id==id_equipe)].shape[0]} tirs arrêtés, {shots[(shots["type"]=="goal")*(shots.goalie_team_id==id_equipe)].shape[0]} buts accordés"
            product_card(equipe,price=team_stats,product_image=teams.loc[id_equipe,"team_logo_url"],picture_position="left",enable_animation=False,key="Equipe")
        else:
            if pos_joueuse=="G":
                player_stats = f"{players.loc[id_joueuse,"games_played"]} parties jouées, {shots[(shots["type"].isin(["shot","goal"]))*(shots.goalie_id==id_joueuse)].shape[0]} tirs reçus, {shots[(shots["type"]=="goal")*(shots.goalie_id==id_joueuse)].shape[0]} buts accordés"
            else:
                player_stats = f"{players.loc[id_joueuse,"games_played"]} parties jouées, {shots[(shots["type"].isin(["shot","goal"]))*(shots.player_id==id_joueuse)].shape[0]} tirs, {shots[(shots["type"]=="goal")*(shots.player_id==id_joueuse)].shape[0]} buts, {shots[shots.blocker_id==id_joueuse].shape[0]} tirs bloqués"
            if saison!="(Toutes)":
                product_card(joueuse+f" ({players.loc[id_joueuse,"position"]})",description=equipe,price=player_stats,product_image=players.loc[id_joueuse,"player_image"],picture_position="left",enable_animation=False,key="Joueuse")
            else:
                product_card(joueuse,description=f"({players.loc[id_joueuse,"position"]})",price=player_stats,product_image=players.loc[id_joueuse,"player_image"],picture_position="left",enable_animation=False,key="Joueuse")
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def offensive():
    """
    """
    st.toggle("Afficher",key="offensive")
    if st.session_state.get("offensive",False):
        st.subheader("Tirs au but")
        if joueuse==None:
            st.text(f"Répartition des tirs au but de {equipe}")
            show_team_shot_density(shots[shots["type"]=="shot"],"shot")
        elif pos_joueuse!="G":
            st.text(f"Répartition des tirs au but de {joueuse}")
            show_skater_shot_density(shots[shots["type"]=="shot"],"shot")
        else:
            st.error("Il n'y a aucune donnée de tirs au but pour cette joueuse.")
        
        st.subheader("Buts")
        if joueuse==None:
            st.text(f"Répartition des buts de {equipe}")
            show_team_shot_density(shots[shots["type"]=="goal"],"goal")
        elif pos_joueuse!="G":
            st.text(f"Répartition des buts de {joueuse}")
            show_skater_shot_density(shots[shots["type"]=="goal"],"goal")
        else:
            st.error("Il n'y a aucune donnée de buts pour cette joueuse.")

with st.container(border=True):
    st.header("Offensive")
    if go:
        offensive()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def defensive():
    """
    """
    st.toggle("Afficher",key="defensive")
    if st.session_state.get("defensive",False):
        st.subheader("Tirs bloqués")
        if joueuse==None:
            st.text(f"Répartition des tirs bloqués de {equipe}")
            show_team_shot_density(shots[shots["type"]=="blocked"],"blocked")
        elif pos_joueuse!="G":
            st.text(f"Répartition des tirs bloqués de {joueuse}")
            show_skater_shot_density(shots[shots["type"]=="blocked"],"blocked")
        else:
            st.error("Il n'y a aucune donnée de tirs bloqués pour cette joueuse.")

with st.container(border=True):
    st.header("Défensive")
    if go:
        defensive()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def gardienne():
    """
    """
    st.toggle("Afficher",key="gardienne")
    if st.session_state.get("gardienne",False):
        st.subheader("Tirs arrêtés")
        if joueuse==None:
            st.text(f"Répartition des tirs arrêtés de {equipe}")
            show_team_shot_density(shots[shots["type"]=="shot"],"save")
        elif pos_joueuse=="G":
            st.text(f"Répartition des tirs arrêtés de {joueuse}")
            show_goalie_shot_density(shots[shots["type"]=="shot"],"save")
        else:
            st.error("Il n'y a aucune donnée de tirs arrêtés pour cette joueuse.")
        
        st.subheader("Buts accordés")
        if joueuse==None:
            st.text(f"Répartition des buts accordés de {equipe}")
            show_team_shot_density(shots[shots["type"]=="goal"],"goal_against")
        elif pos_joueuse=="G":
            st.text(f"Répartition des buts accordés de {joueuse}")
            show_goalie_shot_density(shots[shots["type"]=="goal"],"goal_against")
        else:
            st.error("Il n'y a aucune donnée de buts accordés pour cette joueuse.")

with st.container(border=True):
    st.header("Gardienne")
    if go:
        gardienne()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

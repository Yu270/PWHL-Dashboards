import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_skaters_df, get_goalies_df, get_shots_df, get_skaters_all_time_df, get_goalies_all_time_df, get_shots_all_time_df

st.set_page_config(page_title="Analyse des tirs",page_icon="🥅")

st.title("Analyse des tirs")


def show_shot_density(base_df: pd.DataFrame, density_param: float = 0.5):
    """
    Fonction qui affiche la répartition des tirs (densité 2D). 
    
    Entrées
        base_df: données à utiliser
        density_param: paramètre de la densité
    """
    img = mpimg.imread("./cache/nhl_half_rink.jpeg")
    fig, ax = plt.subplots()
    ax.imshow(img,extent=[0,296,0,296])
    ax.set_xticks(np.arange(0,296,296/6))
    ax.set_yticks(np.arange(0,296,296/6))
    if base_df.shape[0]>=30:
        sns.kdeplot(base_df,x="xCoord",y="yCoord",cmap="Reds",bw_adjust=density_param,ax=ax)
    else:
        ax.scatter(base_df.xCoord,base_df.yCoord,color="b",marker="o")
    ax.set(xticklabels=[],xlabel=None,yticklabels=[],ylabel=None)
    st.pyplot(fig)


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list()+["(Toutes)"],placeholder="Choisissez une saison")
    if saison!="(Toutes)":
        id_saison = seasons[seasons.season_name==saison].index.to_list()[0]
        teams = get_teams(id_saison,saison)
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


with st.container():
    st.header("Informations")
    if go:
        if joueuse==None:
            team_stats = f"{shots[(shots["type"].isin(["shot","goal"]))*(shots.player_team_id==id_equipe)].shape[0]} tirs, {shots[(shots["type"]=="goal")*(shots.player_team_id==id_equipe)].shape[0]} buts, {shots[shots.blocker_team_id==id_equipe].shape[0]} tirs bloqués, {shots[(shots["type"].isin(["shot","goal"]))*(shots.goalie_team_id==id_equipe)].shape[0]} tirs arrêtés, {shots[(shots["type"]=="goal")*(shots.goalie_team_id==id_equipe)].shape[0]} buts accordés"
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
        st.dataframe(shots)
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
            show_shot_density(shots[(shots["type"]=="shot")*(shots.player_team_id==id_equipe)])
        elif pos_joueuse!="G":
            st.text(f"Répartition des tirs au but de {joueuse}")
            show_shot_density(shots[(shots["type"]=="shot")*(shots.player_id==id_joueuse)])
        else:
            st.error("Il n'y a aucune donnée de tirs au but pour cette joueuse.")
        
        st.subheader("Buts")
        if joueuse==None:
            st.text(f"Répartition des buts de {equipe}")
            show_shot_density(shots[(shots["type"]=="goal")*(shots.player_team_id==id_equipe)],0.25)
        elif pos_joueuse!="G":
            st.text(f"Répartition des buts de {joueuse}")
            show_shot_density(shots[(shots["type"]=="goal")*(shots.player_id==id_joueuse)],0.25)
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
            show_shot_density(shots[(shots["type"]=="blocked")*(shots.blocker_team_id==id_equipe)])
        elif pos_joueuse!="G":
            st.text(f"Répartition des tirs bloqués de {joueuse}")
            show_shot_density(shots[(shots["type"]=="blocked")*(shots.blocker_id==id_joueuse)])
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
            show_shot_density(shots[(shots["type"]=="shot")*(shots.goalie_team_id==id_equipe)])
        elif pos_joueuse=="G":
            st.text(f"Répartition des tirs arrêtés de {joueuse}")
            show_shot_density(shots[(shots["type"]=="shot")*(shots.goalie_id==id_joueuse)])
        else:
            st.error("Il n'y a aucune donnée de tirs arrêtés pour cette joueuse.")
        
        st.subheader("Buts accordés")
        if joueuse==None:
            st.text(f"Répartition des buts accordés de {equipe}")
            show_shot_density(shots[(shots["type"]=="goal")*(shots.goalie_team_id==id_equipe)])
        elif pos_joueuse=="G":
            st.text(f"Répartition des buts accordés de {joueuse}")
            show_shot_density(shots[(shots["type"]=="goal")*(shots.goalie_id==id_joueuse)])
        else:
            st.error("Il n'y a aucune donnée de buts accordés pour cette joueuse.")

with st.container(border=True):
    st.header("Gardienne")
    if go:
        gardienne()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

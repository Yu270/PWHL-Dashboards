import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_skaters_df, get_goalies_df, get_shots_df

st.set_page_config(page_title="Tirs au but",page_icon="🥅")

st.title("Tirs au but")

plt.style.use('dark_background')


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list(),placeholder="Choisissez une saison")
    id_saison = seasons[seasons.season_name==saison].index.to_list()[0]
    teams = get_teams(id_saison,saison)
    equipe = st.selectbox("Équipe",options=teams.sort_values("name").name.to_list(),placeholder="Choisissez une équipe")
    id_equipe = teams[teams.name==equipe].index.to_list()[0]
    skaters = get_skaters_df(id_saison,saison)
    skaters = skaters[skaters.team_id==id_equipe].copy()
    goalies = get_goalies_df(id_saison,saison)
    goalies = goalies[goalies.team_id==id_equipe].copy()
    players = pd.concat((skaters[["player_name","position","team_id","player_image"]],goalies[["player_name","position","team_id","player_image"]]))
    joueuse = st.selectbox("Joueuse",options=[None]+players.sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse")
    if joueuse!=None:
        id_joueuse = players[players.player_name==joueuse].index.to_list()[0]
        pos_joueuse = players.loc[id_joueuse,"position"]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            shots = get_shots_df(id_saison,saison)


with st.container():
    st.header("Informations")
    if go:
        team_stats = f"{shots[(shots["type"].isin(["shot","goal"]))*(shots.player_team_id==id_equipe)].shape[0]} tirs, {shots[(shots["type"]=="goal")*(shots.player_team_id==id_equipe)].shape[0]} buts, {shots[shots.blocker_team_id==id_equipe].shape[0]} tirs bloqués"
        product_card(equipe,price=team_stats,product_image=teams.loc[id_equipe,"team_logo_url"],picture_position="left",enable_animation=False,key="Equipe")
        if joueuse!=None:
            if pos_joueuse=="G":
                player_stats = f"{shots[(shots["type"].isin(["shot","goal"]))*(shots.goalie_id==id_joueuse)].shape[0]} tirs reçus, {shots[(shots["type"]=="goal")*(shots.goalie_id==id_joueuse)].shape[0]} buts accordés"
            else:
                player_stats = f"{shots[(shots["type"].isin(["shot","goal"]))*(shots.player_id==id_joueuse)].shape[0]} tirs, {shots[(shots["type"]=="goal")*(shots.player_id==id_joueuse)].shape[0]} buts, {shots[shots.blocker_id==id_joueuse].shape[0]} tirs bloqués"
            product_card(joueuse,description=f"({players.loc[id_joueuse,"position"]})",price=player_stats,product_image=players.loc[id_joueuse,"player_image"],picture_position="left",enable_animation=False,key="Joueuse")
        st.dataframe(shots)
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

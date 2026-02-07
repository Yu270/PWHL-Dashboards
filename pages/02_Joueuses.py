import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_skaters_df, get_goalies_df, get_penalties_df

st.set_page_config(page_title="Joueuses",page_icon="⛸️")

st.title("Joueuses")

plt.style.use('dark_background')


if not ("select" in st.session_state):
    st.session_state.select = None

@st.fragment
def show_visuals(base_df: pd.DataFrame, column: str, name: str, ascending: bool, rounding: int, title: str = None, percent: bool = False):
    """
    Fonction qui affiche le classement des joueuses selon une variable. 
    
    Entrées
        base_df: données à utiliser
        column: variable à utiliser
        name: nom de la variable à afficher
        ascending: si on classe en ordre croissant
        rounding: arrondissement des données
        title: titre du classement
        percent: si on affiche le symbole de %
    """
    new_df = base_df[["player_name","player_image","team_id","position",column]].reset_index(drop=True)
    new_df["Équipe"] = ""
    for i in new_df.index:
        new_df.loc[i,"Équipe"] = teams.loc[new_df.loc[i,"team_id"],"name"]
    new_df.sort_values([column,"player_name"],ascending=ascending,inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    if title!=None:
        st.text(title)
    if new_df.shape[0]>3:
        col1, col2, col3 = st.columns(3)
        with col1:
            if percent:
                product_card(f"{new_df.loc[0,"player_name"]} ({new_df.loc[0,"position"]})",description=new_df.loc[0,"Équipe"],price=f"{round(new_df.loc[0,column],rounding)}%",product_image=new_df.loc[0,"player_image"],picture_position="left",enable_animation=False,key="1_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[0,"player_name"]} ({new_df.loc[0,"position"]})",description=new_df.loc[0,"Équipe"],price=round(new_df.loc[0,column],rounding),product_image=new_df.loc[0,"player_image"],picture_position="left",enable_animation=False,key="1_"+column+"_"+str(base_df.shape[0]))
        with col2:
            if percent:
                product_card(f"{new_df.loc[1,"player_name"]} ({new_df.loc[1,"position"]})",description=new_df.loc[1,"Équipe"],price=f"{round(new_df.loc[1,column],rounding)}%",product_image=new_df.loc[1,"player_image"],picture_position="left",enable_animation=False,key="2_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[1,"player_name"]} ({new_df.loc[1,"position"]})",description=new_df.loc[1,"Équipe"],price=round(new_df.loc[1,column],rounding),product_image=new_df.loc[1,"player_image"],picture_position="left",enable_animation=False,key="2_"+column+"_"+str(base_df.shape[0]))
        with col3:
            if percent:
                product_card(f"{new_df.loc[2,"player_name"]} ({new_df.loc[2,"position"]})",description=new_df.loc[2,"Équipe"],price=f"{round(new_df.loc[2,column],rounding)}%",product_image=new_df.loc[2,"player_image"],picture_position="left",enable_animation=False,key="3_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[2,"player_name"]} ({new_df.loc[2,"position"]})",description=new_df.loc[2,"Équipe"],price=round(new_df.loc[2,column],rounding),product_image=new_df.loc[2,"player_image"],picture_position="left",enable_animation=False,key="3_"+column+"_"+str(base_df.shape[0]))
        reste = new_df.loc[3:].copy()
        reste["Rang"] = range(4,reste.shape[0]+4)
        reste.rename(columns={"player_name": "Nom", "position": "Position", column: name},inplace=True)
        st.dataframe(reste.loc[:9].set_index("Rang")[["Nom","Position","Équipe",name]])
        if reste.shape[0]>7:
            others = reste.Nom.to_list()
            others.sort()
            st.session_state.select = st.selectbox("Voir une autre joueuse",options=[None]+others,placeholder="Choisissez une joueuse",key="select_"+column+"_"+str(base_df.shape[0]))
            if st.session_state.select!=None:
                idx = reste[reste.Nom==st.session_state.select].index.to_list()[0]
                if percent:
                    product_card(f"{reste.loc[idx,"Nom"]} ({reste.loc[idx,"Position"]})",description=reste.loc[idx,"Équipe"],price=f"{round(reste.loc[idx,name],rounding)}%",product_image=reste.loc[idx,"player_image"],picture_position="left",enable_animation=False,key="0_"+column+"_"+str(base_df.shape[0]))
                else:
                    product_card(f"{reste.loc[idx,"Nom"]} ({reste.loc[idx,"Position"]})",description=reste.loc[idx,"Équipe"],price=round(reste.loc[idx,name],rounding),product_image=reste.loc[idx,"player_image"],picture_position="left",enable_animation=False,key="0_"+column+"_"+str(base_df.shape[0]))
    else:
        cols = st.columns(new_df.shape[0])
        for i,col in enumerate(cols):
            with col:
                if percent:
                    product_card(f"{new_df.loc[i,"player_name"]} ({new_df.loc[i,"position"]})",description=new_df.loc[i,"Équipe"],price=f"{round(new_df.loc[i,column],rounding)}%",product_image=new_df.loc[i,"player_image"],picture_position="left",enable_animation=False,key=str(i+1)+"_"+column+"_"+str(base_df.shape[0]))
                else:
                    product_card(f"{new_df.loc[i,"player_name"]} ({new_df.loc[i,"position"]})",description=new_df.loc[i,"Équipe"],price=round(new_df.loc[i,column],rounding),product_image=new_df.loc[i,"player_image"],picture_position="left",enable_animation=False,key=str(i+1)+"_"+column+"_"+str(base_df.shape[0]))

if not ("team" in st.session_state):
    st.session_state.team = None

if not ("player" in st.session_state):
    st.session_state.player = None

@st.fragment
def show_penalty_types(base_df: pd.DataFrame):
    """
    Fonction qui affiche la distribution des types de pénalité pour une joueuse + comparaison avec le reste de son équipe. 
    
    Entrées
        base_df: données à utiliser
    """
    with st.container(horizontal=True):
        if equipe!="Toutes":
            st.session_state.team = st.selectbox("Équipe",options=[equipe],placeholder="Choisissez une équipe")
        else:
            st.session_state.team = st.selectbox("Équipe",options=teams.name.to_list(),placeholder="Choisissez une équipe")
        team_id = teams[teams.name==st.session_state.team].index.to_list()[0]
        st.session_state.player = st.selectbox("Joueuse",options=skaters[skaters.team_id==team_id].player_name.to_list(),placeholder="Choisissez une joueuse")
        id_joueuse = skaters[skaters.player_name==st.session_state.player].index.to_list()[0]
    new_df = base_df[base_df.player_id==id_joueuse].copy()
    if new_df.shape[0]>0:
        new_df["Count_player"] = 1
        agg_player = new_df[["penalty_description","Count_player"]].groupby("penalty_description").sum().reset_index()
        agg_player.sort_values("Count_player",inplace=True)
        fig1, ax1 = plt.subplots()
        ax1.barh(agg_player.penalty_description.to_list()[-10:],agg_player.Count_player.to_list()[-10:])
        ax1.set_title(f"Pénalités de {st.session_state.player}")
        ax1.set_xlabel("Fréquence")
        st.pyplot(fig1)
    else:
        st.error("Il n'y a aucune donnée de pénalités pour cette joueuse.")
    new_df2 = base_df[(base_df.team_id==team_id)*(base_df.player_id!=id_joueuse)].copy()
    if new_df2.shape[0]>0:
        new_df2["Count_players"] = 1
        agg_players = new_df2[["penalty_description","Count_players"]].groupby("penalty_description").sum().reset_index()
        agg_players.sort_values("Count_players",inplace=True)
        fig2, ax2 = plt.subplots()
        ax2.barh(agg_players.penalty_description.to_list()[-10:],agg_players.Count_players.to_list()[-10:])
        ax2.set_title(f"Pénalités des autres joueuses de {st.session_state.team}")
        ax2.set_xlabel("Fréquence")
        st.pyplot(fig2)
    else:
        st.error("Il n'y a aucune donnée de pénalités pour les autres joueuses.")


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list(),placeholder="Choisissez une saison")
    id_saison = seasons[seasons.season_name==saison].index.to_list()[0]
    teams = get_teams(id_saison,saison)
    equipe = st.selectbox("Équipe",options=["Toutes"]+teams.name.to_list(),placeholder="Choisissez une équipe")
    if equipe!="Toutes":
        id_equipe = teams[teams.name==equipe].index.to_list()[0]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            skaters = get_skaters_df(id_saison,saison)
            goalies = get_goalies_df(id_saison,saison)
            penalties = get_penalties_df(id_saison,saison)
            if equipe!="Toutes":
                skaters = skaters[skaters.team_id==id_equipe].copy()
                goalies = goalies[goalies.team_id==id_equipe].copy()
                penalties = penalties[penalties.team_id==id_equipe].copy()


@st.fragment
def offensive():
    """
    """
    st.toggle("Afficher",key="offensive")
    if st.session_state.get("offensive",False):
        st.subheader("Buts")
        show_visuals(skaters,"goals","Nombre de buts",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"goals_avg","Moyenne de buts",False,2,"Moyenne (au moins 5 parties jouées)")

        st.subheader("Assistances")
        show_visuals(skaters,"assists","Nombre d'assistances",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"assists_avg","Moyenne d'assistances",False,2,"Moyenne (au moins 5 parties jouées)")

        st.subheader("Points")
        show_visuals(skaters,"points","Nombre de points",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"points_avg","Moyenne de points",False,2,"Moyenne (au moins 5 parties jouées)")
        show_visuals(skaters[skaters.games_played>=5],"min_for_point","Minutes jouées pour 1 point",True,2,"Minutes de jeu pour 1 point (au moins 5 parties jouées)")

        st.subheader("Tirs au but")
        show_visuals(skaters,"shots","Nombre de tirs",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"shots_avg","Moyenne de tirs",False,2,"Moyenne (au moins 5 parties jouées)")
        show_visuals(skaters[skaters.games_played>=5],"min_for_shot","Minutes jouées pour 1 tir",True,2,"Minutes de jeu pour 1 tir (au moins 5 parties jouées)")

        st.subheader("Pourcentage de buts")
        show_visuals(skaters[skaters.shots>=5],"goals_pct","% de buts",False,1,"(au moins 5 tirs au but effectués)",True)

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
        st.subheader("Mises en échec")
        show_visuals(skaters,"hits","Nombre de mises en échec",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"hits_avg","Moyenne de mises en échec",False,2,"Moyenne (au moins 5 parties jouées)")

        st.subheader("Tirs bloqués")
        show_visuals(skaters,"shots_blocked","Nombre de tirs bloqués",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"shots_blocked_avg","Moyenne de tirs bloqués",False,2,"Moyenne (au moins 5 parties jouées)")

with st.container(border=True):
    st.header("Défensive")
    if go:
        defensive()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def gardiennes():
    """
    """
    st.toggle("Afficher",key="gardiennes")
    if st.session_state.get("gardiennes",False):
        st.subheader("Arrêts")
        show_visuals(goalies,"saves","Nombre d'arrêts",False,0,"Total")
        show_visuals(goalies[goalies.games_played>=3],"saves_pct","% d'arrêts",False,1,"% d'arrêts (au moins 3 parties jouées)",True)

        st.subheader("Buts accordés")
        show_visuals(goalies[goalies.games_played>=3],"goals_against_avg","Moyenne de buts accordés",True,2,"Moyenne (au moins 3 parties jouées)")

        st.subheader("Victoires")
        show_visuals(goalies,"wins","Nombre de victoires",False,0,"Total")
        show_visuals(goalies[goalies.games_played>=3],"wins_pct","% de victoires",False,1,"% de victoires (au moins 3 parties jouées)",True)

        st.subheader("Jeux blancs")
        show_visuals(goalies,"shutouts","Nombre de jeux blancs",False,0,"Total")

with st.container(border=True):
    st.header("Gardiennes")
    if go:
        gardiennes()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def sup_inf_num():
    """
    """
    st.toggle("Afficher",key="sup_inf_num")
    if st.session_state.get("sup_inf_num",False):
        st.subheader("Buts en supériorité numérique")
        show_visuals(skaters,"power_play_goals","Nombre de buts en supériorité numérique",False,0)

        st.subheader("Buts en infériorité numérique")
        show_visuals(skaters,"short_handed_goals","Nombre de buts en infériorité numérique",False,0)

with st.container(border=True):
    st.header("Supériorité et infériorité numérique")
    if go:
        sup_inf_num()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def penalites():
    """
    """
    st.toggle("Afficher",key="penalites")
    if st.session_state.get("penalites",False):
        st.subheader("Minutes de pénalité")
        show_visuals(skaters,"penalty_minutes","Minutes de pénalité",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=5],"penalty_minutes_avg","Moyenne de minutes de pénalité",False,2,"Moyenne (au moins 5 parties jouées)")

        st.subheader("Types de pénalité")
        if penalties.shape[0]>0:
            show_penalty_types(penalties)
        else:
            st.error("Il n'y a aucune donnée de pénalités pour cette saison.")

with st.container(border=True):
    st.header("Pénalités")
    if go:
        penalites()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def autres():
    """
    """
    st.toggle("Afficher",key="autres")
    if st.session_state.get("autres",False):
        st.subheader("Temps sur la glace (patineuses)")
        show_visuals(skaters,"ice_time_min","Temps de jeu total (min)",False,1,"Total")
        show_visuals(skaters[skaters.games_played>=5],"ice_time_min_avg","Temps de jeu moyen (min)",False,2,"Moyenne (au moins 5 parties jouées)")
        
        st.subheader("Temps sur la glace (gardiennes)")
        show_visuals(goalies,"ice_time_min","Temps de jeu total (min)",False,1)

        st.subheader("Mises au jeu")
        show_visuals(skaters[skaters.faceoff_attempts>=5],"faceoff_pct","% de mises au jeu gagnées",False,1,"(au moins 5 mises au jeu effectuées)",True)

        st.subheader("Marque le premier but d'une partie")
        show_visuals(skaters[skaters.games_played>=5],"first_goals_pct","% de premier but d'une partie",False,1,"(au moins 5 parties jouées)",True)

with st.container(border=True):
    st.header("Autres statistiques")
    if go:
        autres()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

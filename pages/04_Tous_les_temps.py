import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
from streamlit_product_card import product_card
from data import get_skaters_all_time_df, get_goalies_all_time_df, get_penalties_all_time_df, get_shots_all_time_df

st.set_page_config(page_title="Tous les temps",page_icon="🏆")

st.title("Joueuses (tous les temps)")

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
    new_df = base_df[["player_name","player_image","position",column]].reset_index(drop=True)
    new_df.sort_values([column,"player_name"],ascending=ascending,inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    if title!=None:
        st.text(title)
    if new_df.shape[0]>3:
        col1, col2, col3 = st.columns(3)
        with col1:
            if percent:
                product_card(f"{new_df.loc[0,"player_name"]}",description=f"({new_df.loc[0,"position"]})",price=f"{round(new_df.loc[0,column],rounding)}%",product_image=new_df.loc[0,"player_image"],picture_position="left",enable_animation=False,key="1_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[0,"player_name"]}",description=f"({new_df.loc[0,"position"]})",price=round(new_df.loc[0,column],rounding),product_image=new_df.loc[0,"player_image"],picture_position="left",enable_animation=False,key="1_"+column+"_"+str(base_df.shape[0]))
        with col2:
            if percent:
                product_card(f"{new_df.loc[1,"player_name"]}",description=f"({new_df.loc[1,"position"]})",price=f"{round(new_df.loc[1,column],rounding)}%",product_image=new_df.loc[1,"player_image"],picture_position="left",enable_animation=False,key="2_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[1,"player_name"]}",description=f"({new_df.loc[1,"position"]})",price=round(new_df.loc[1,column],rounding),product_image=new_df.loc[1,"player_image"],picture_position="left",enable_animation=False,key="2_"+column+"_"+str(base_df.shape[0]))
        with col3:
            if percent:
                product_card(f"{new_df.loc[2,"player_name"]}",description=f"({new_df.loc[2,"position"]})",price=f"{round(new_df.loc[2,column],rounding)}%",product_image=new_df.loc[2,"player_image"],picture_position="left",enable_animation=False,key="3_"+column+"_"+str(base_df.shape[0]))
            else:
                product_card(f"{new_df.loc[2,"player_name"]}",description=f"({new_df.loc[2,"position"]})",price=round(new_df.loc[2,column],rounding),product_image=new_df.loc[2,"player_image"],picture_position="left",enable_animation=False,key="3_"+column+"_"+str(base_df.shape[0]))
        reste = new_df.loc[3:].copy()
        reste["Rang"] = range(4,reste.shape[0]+4)
        reste.rename(columns={"player_name": "Nom", "position": "Position", column: name},inplace=True)
        st.dataframe(reste.loc[:9].set_index("Rang")[["Nom","Position",name]])
        if reste.shape[0]>7:
            others = reste.Nom.to_list()
            others.sort()
            st.session_state.select = st.selectbox("Voir une autre joueuse",options=[None]+others,placeholder="Choisissez une joueuse",key="select_"+column+"_"+str(base_df.shape[0]))
            if st.session_state.select!=None:
                idx = reste[reste.Nom==st.session_state.select].index.to_list()[0]
                if percent:
                    product_card(f"{reste.loc[idx,"Nom"]}",description=f"({reste.loc[idx,"Position"]})",price=f"{round(reste.loc[idx,name],rounding)}%",product_image=reste.loc[idx,"player_image"],picture_position="left",enable_animation=False,key="0_"+column+"_"+str(base_df.shape[0]))
                else:
                    product_card(f"{reste.loc[idx,"Nom"]}",description=f"({reste.loc[idx,"Position"]})",price=round(reste.loc[idx,name],rounding),product_image=reste.loc[idx,"player_image"],picture_position="left",enable_animation=False,key="0_"+column+"_"+str(base_df.shape[0]))
    else:
        cols = st.columns(new_df.shape[0])
        for i,col in enumerate(cols):
            with col:
                if percent:
                    product_card(f"{new_df.loc[i,"player_name"]}",description=f"({new_df.loc[i,"position"]})",price=f"{round(new_df.loc[i,column],rounding)}%",product_image=new_df.loc[i,"player_image"],picture_position="left",enable_animation=False,key=str(i+1)+"_"+column+"_"+str(base_df.shape[0]))
                else:
                    product_card(f"{new_df.loc[i,"player_name"]}",description=f"({new_df.loc[i,"position"]})",price=round(new_df.loc[i,column],rounding),product_image=new_df.loc[i,"player_image"],picture_position="left",enable_animation=False,key=str(i+1)+"_"+column+"_"+str(base_df.shape[0]))

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
        st.session_state.player = st.selectbox("Joueuse",options=skaters.sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse",key="choix_joueuse_penalite")
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
    new_df2 = base_df[base_df.player_id!=id_joueuse].copy()
    if new_df2.shape[0]>0:
        new_df2["Count_players"] = 1
        agg_players = new_df2[["penalty_description","Count_players"]].groupby("penalty_description").sum().reset_index()
        agg_players.sort_values("Count_players",inplace=True)
        fig2, ax2 = plt.subplots()
        ax2.barh(agg_players.penalty_description.to_list()[-10:],agg_players.Count_players.to_list()[-10:])
        ax2.set_title(f"Pénalités des autres joueuses")
        ax2.set_xlabel("Fréquence")
        st.pyplot(fig2)
    else:
        st.error("Il n'y a aucune donnée de pénalités pour les autres joueuses.")

@st.fragment
def show_shot_types(base_df: pd.DataFrame):
    """
    Fonction qui affiche la distribution des types de tir pour une joueuse + comparaison avec le reste de son équipe. 
    
    Entrées
        base_df: données à utiliser
    """
    with st.container(horizontal=True):
        st.session_state.player = st.selectbox("Joueuse",options=skaters.sort_values("player_name").player_name.to_list(),placeholder="Choisissez une joueuse",key="choix_joueuse_tir")
        id_joueuse = skaters[skaters.player_name==st.session_state.player].index.to_list()[0]
    new_df = base_df[base_df.player_id==id_joueuse].copy()
    if new_df.shape[0]>0:
        new_df["Count_player"] = 1
        agg_player = new_df[["shot_type","Count_player"]].groupby("shot_type").sum().reset_index()
        agg_player.sort_values("Count_player",inplace=True)
        fig1, ax1 = plt.subplots()
        ax1.barh(agg_player.shot_type.to_list()[-10:],agg_player.Count_player.to_list()[-10:])
        ax1.set_title(f"Tirs au but de {st.session_state.player}")
        ax1.set_xlabel("Fréquence")
        st.pyplot(fig1)
    else:
        st.error("Il n'y a aucune donnée de tirs au but pour cette joueuse.")
    new_df2 = base_df[base_df.player_id!=id_joueuse].copy()
    if new_df2.shape[0]>0:
        new_df2["Count_players"] = 1
        agg_players = new_df2[["shot_type","Count_players"]].groupby("shot_type").sum().reset_index()
        agg_players.sort_values("Count_players",inplace=True)
        fig2, ax2 = plt.subplots()
        ax2.barh(agg_players.shot_type.to_list()[-10:],agg_players.Count_players.to_list()[-10:])
        ax2.set_title(f"Tirs au but des autres joueuses")
        ax2.set_xlabel("Fréquence")
        st.pyplot(fig2)
    else:
        st.error("Il n'y a aucune donnée de tirs au but pour les autres joueuses.")

def show_distribution(base_df: pd.DataFrame, column: str, name: str, title: str):
    """
    Fonction qui affiche la distribution d'une variable. 
    
    Entrées
        base_df: données à utiliser
        column: variable à utiliser
        name: nom de la variable à afficher
        title: titre du graphique
    """
    mean, median = base_df[column].mean(), base_df[column].median()
    fig, ax = plt.subplots()
    ax.hist(base_df[column],bins=10,align="mid",rwidth=0.8)
    ax.axvline(mean,color="blue",label=f"Moyenne: {round(mean,2)}")
    ax.axvline(median,color="red",label=f"Médiane: {round(median,2)}")
    ax.set_title(title)
    ax.set_xlabel(name)
    ax.set_ylabel("Nombre de joueuses")
    ax.legend()
    st.pyplot(fig)


with st.sidebar:
    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            skaters = get_skaters_all_time_df()
            goalies = get_goalies_all_time_df()
            penalties = get_penalties_all_time_df()
            shots = get_shots_all_time_df()


@st.fragment
def games():
    """
    """
    st.toggle("Afficher",key="games")
    if st.session_state.get("games",False):
        show_visuals(skaters,"games_played","Parties jouées",False,0)

with st.container(border=True):
    st.header("Parties jouées")
    if go:
        games()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def offensive():
    """
    """
    st.toggle("Afficher",key="offensive")
    if st.session_state.get("offensive",False):
        st.subheader("Buts")
        show_visuals(skaters,"goals","Nombre de buts",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=10],"goals_avg","Moyenne de buts",False,2,"Moyenne (au moins 10 parties jouées)")

        st.subheader("Assistances")
        show_visuals(skaters,"assists","Nombre d'assistances",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=10],"assists_avg","Moyenne d'assistances",False,2,"Moyenne (au moins 10 parties jouées)")

        st.subheader("Points")
        show_visuals(skaters,"points","Nombre de points",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=10],"points_avg","Moyenne de points",False,2,"Moyenne (au moins 10 parties jouées)")
        show_visuals(skaters[skaters.games_played>=10],"min_for_point","Minutes jouées pour 1 point",True,2,"Minutes de jeu pour 1 point (au moins 10 parties jouées)")

        st.subheader("Tirs au but")
        show_visuals(skaters,"shots","Nombre de tirs",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=10],"shots_avg","Moyenne de tirs",False,2,"Moyenne (au moins 10 parties jouées)")
        show_visuals(skaters[skaters.games_played>=10],"min_for_shot","Minutes jouées pour 1 tir",True,2,"Minutes de jeu pour 1 tir (au moins 10 parties jouées)")

        st.subheader("Pourcentage de buts")
        show_visuals(skaters[skaters.shots>=10],"goals_pct","% de buts",False,1,"(au moins 10 tirs au but effectués)",True)

        st.subheader("Types de tir")
        show_shot_types(shots)

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
        show_visuals(skaters[skaters.games_played>=10],"hits_avg","Moyenne de mises en échec",False,2,"Moyenne (au moins 10 parties jouées)")

        st.subheader("Tirs bloqués")
        show_visuals(skaters,"shots_blocked","Nombre de tirs bloqués",False,0,"Total")
        show_visuals(skaters[skaters.games_played>=10],"shots_blocked_avg","Moyenne de tirs bloqués",False,2,"Moyenne (au moins 10 parties jouées)")

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
        show_visuals(goalies[goalies.games_played>=10],"saves_pct","% d'arrêts",False,1,"% d'arrêts (au moins 10 parties jouées)",True)

        st.subheader("Buts accordés")
        show_visuals(goalies[goalies.games_played>=10],"goals_against_avg","Moyenne de buts accordés",True,2,"Moyenne (au moins 10 parties jouées)")

        st.subheader("Victoires")
        show_visuals(goalies,"wins","Nombre de victoires",False,0,"Total")
        show_visuals(goalies[goalies.games_played>=10],"wins_pct","% de victoires",False,1,"% de victoires (au moins 10 parties jouées)",True)

        st.subheader("Jeux blancs")
        show_visuals(goalies,"shutouts","Nombre de jeux blancs",False,0,"Total")

        st.subheader("Arrêts en tirs de barrage")
        show_visuals(goalies,"shootout_saves","Nombre d'arrêts en tirs de barrage",False,0,"Total")
        if goalies[goalies.shootout_attempts>=5].shape[0]>0:
            show_visuals(goalies[goalies.shootout_attempts>=5],"shootout_pct","% d'arrêts en tirs de barrage",False,1,"% d'arrêts (au moins 5 tirs de barrage reçus)",True)
        else:
            st.error("Il y a très peu de données de tirs de barrage.")

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
        
        st.subheader("Points en supériorité numérique")
        show_visuals(skaters,"power_play_points","Nombre de points en supériorité numérique",False,0)

        st.subheader("Points en infériorité numérique")
        show_visuals(skaters,"short_handed_points","Nombre de points en infériorité numérique",False,0)

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
        show_visuals(skaters[skaters.games_played>=10],"penalty_minutes_avg","Moyenne de minutes de pénalité",False,2,"Moyenne (au moins 10 parties jouées)")

        st.subheader("Types de pénalité")
        show_penalty_types(penalties)

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
        show_visuals(skaters[skaters.games_played>=10],"ice_time_min_avg","Temps de jeu moyen (min)",False,2,"Moyenne (au moins 10 parties jouées)")
        
        st.subheader("Temps sur la glace (gardiennes)")
        show_visuals(goalies,"ice_time_min","Temps de jeu total (min)",False,1)

        st.subheader("Mises au jeu")
        show_visuals(skaters[skaters.faceoff_attempts>=10],"faceoff_pct","% de mises au jeu gagnées",False,1,"(au moins 10 mises au jeu effectuées)",True)

        st.subheader("Buts en tirs de barrage")
        show_visuals(skaters,"shootout_goals","Nombre de buts en tirs de barrage",False,0,"Total")
        if skaters[skaters.shootout_attempts>=5].shape[0]>0:
            show_visuals(skaters[skaters.shootout_attempts>=5],"shootout_pct","% de buts en tirs de barrage",False,1,"% de buts (au moins 5 tirs de barrage effectués)",True)
        else:
            st.error("Il y a très peu de données de tirs de barrage.")

        st.subheader("Marque le premier but d'une partie")
        show_visuals(skaters[skaters.games_played>=10],"first_goals_pct","% de premier but d'une partie",False,1,"(au moins 10 parties jouées)",True)

with st.container(border=True):
    st.header("Autres statistiques")
    if go:
        autres()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def infos():
    """
    """
    st.toggle("Afficher",key="infos")
    if st.session_state.get("infos",False):
        players = pd.concat((skaters[["player_name","player_image","position","birthyear","height_cm"]],goalies[["player_name","player_image","position","birthyear","height_cm"]]))
        players["age"] = date.today().year-players["birthyear"]
        st.subheader("Âge")
        st.toggle("Ordre croissant",value=True,key="age")
        show_visuals(players,"age","Âge",st.session_state.get("age",True),0)
        show_distribution(players,"age","Âge","Distribution de l'âge des joueuses")
        
        st.subheader("Taille")
        st.toggle("Ordre croissant",key="taille")
        show_visuals(players,"height_cm","Taille (cm)",st.session_state.get("taille",False),2)
        show_distribution(players,"height_cm","Taille (cm)","Distribution de la taille des joueuses")

with st.container(border=True):
    st.header("Informations sur les joueuses")
    if go:
        infos()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_games_df, get_standings_advanced_df, get_penalties_df


st.set_page_config(page_title="Équipes",page_icon="🥅")

st.title("Équipes")

plt.style.use('dark_background')


def show_visuals(base_df: pd.DataFrame, column: str, name: str, ascending: bool, rounding: int, title: str = None, percent: bool = False):
    """
    Fonction qui affiche le classement des équipes selon une variable. 
    
    Entrées
        base_df: données à utiliser
        column: variable à utiliser
        name: nom de la variable à afficher
        ascending: si on classe en ordre croissant
        rounding: arrondissement des données
        title: titre du classement
        percent: si on affiche le symbole de %
    """
    new_df = base_df[["team_id",column]].reset_index(drop=True)
    new_df["Équipe"] = ""
    for i in new_df.index:
        new_df.loc[i,"Équipe"] = teams.loc[new_df.loc[i,"team_id"],"name"]
    new_df.sort_values([column,"Équipe"],ascending=ascending,inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    if title!=None:
        st.text(title)
    col1, col2, col3 = st.columns(3)
    with col1:
        if percent:
            product_card(new_df.loc[0,"Équipe"],price=f"{round(new_df.loc[0,column],rounding)}%",product_image=teams.loc[new_df.loc[0,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="1_"+column)
        else:
            product_card(new_df.loc[0,"Équipe"],price=round(new_df.loc[0,column],rounding),product_image=teams.loc[new_df.loc[0,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="1_"+column)
    with col2:
        if percent:
            product_card(new_df.loc[1,"Équipe"],price=f"{round(new_df.loc[1,column],rounding)}%",product_image=teams.loc[new_df.loc[1,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="2_"+column)
        else:
            product_card(new_df.loc[1,"Équipe"],price=round(new_df.loc[1,column],rounding),product_image=teams.loc[new_df.loc[1,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="2_"+column)
    with col3:
        if percent:
            product_card(new_df.loc[2,"Équipe"],price=f"{round(new_df.loc[2,column],rounding)}%",product_image=teams.loc[new_df.loc[2,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="3_"+column)
        else:
            product_card(new_df.loc[2,"Équipe"],price=round(new_df.loc[2,column],rounding),product_image=teams.loc[new_df.loc[2,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key="3_"+column)
    reste = new_df.loc[3:].copy()
    reste["Rang"] = range(4,reste.shape[0]+4)
    reste.rename(columns={column: name},inplace=True)
    st.dataframe(reste.set_index("Rang")[["Équipe",name]])

if not ("team" in st.session_state):
    st.session_state.team = None

@st.fragment
def show_penalty_types(base_df: pd.DataFrame):
    """
    Fonction qui affiche la distribution des types de pénalité pour une équipe + comparaison avec le reste de la ligue. 
    
    Entrées
        base_df: données à utiliser
    """
    st.session_state.team = st.selectbox("Équipe",options=teams.name.to_list(),placeholder="Choisissez une équipe")
    id_equipe = teams[teams.name==st.session_state.team].index.to_list()[0]
    new_df = base_df[base_df.team_id==id_equipe].copy()
    if new_df.shape[0]>0:
        new_df["Count_team"] = 1/new_df.shape[0]
        agg_team = new_df[["penalty_description","Count_team"]].groupby("penalty_description").sum().reset_index()
        agg_team.sort_values("Count_team",inplace=True)
        fig1, ax1 = plt.subplots()
        ax1.barh(agg_team.penalty_description.to_list()[-10:],agg_team.Count_team.to_list()[-10:])
        ax1.set_title(f"Distribution des pénalités de {st.session_state.team}")
        ax1.set_xlabel("Fréquence relative")
        st.pyplot(fig1)
    else:
        st.error("Il n'y a aucune donnée de pénalités pour cette équipe.")
    new_df2 = base_df[base_df.team_id!=id_equipe].copy()
    if new_df2.shape[0]>0:
        new_df2["Count_teams"] = 1/new_df2.shape[0]
        agg_teams = new_df2[["penalty_description","Count_teams"]].groupby("penalty_description").sum().reset_index()
        agg_teams.sort_values("Count_teams",inplace=True)
        fig2, ax2 = plt.subplots()
        ax2.barh(agg_teams.penalty_description.to_list()[-10:],agg_teams.Count_teams.to_list()[-10:])
        ax2.set_title("Distribution des pénalités des autres équipes")
        ax2.set_xlabel("Fréquence relative")
        st.pyplot(fig2)
    else:
        st.error("Il n'y a aucune donnée de pénalités pour les autres équipes.")


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list(),placeholder="Choisissez une saison")
    id_saison = seasons[seasons.season_name==saison].index.to_list()[0]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            teams = get_teams(id_saison,saison)
            games = get_games_df(id_saison,saison)
            standings = get_standings_advanced_df(id_saison,saison)
            penalties = get_penalties_df(id_saison,saison)


if go:
    point_diff_all = pd.DataFrame()
    goal_diff_all = pd.DataFrame()
    # diff_all = pd.DataFrame()
    for i in teams.index:
        point_diff = [0]
        goal_diff = [0]
        # diff = [0]
        for j in games.index:
            if games.loc[j,"home_team_id"]==i:
                prev_pd = point_diff[-1]
                point_diff.append(prev_pd+games.loc[j,"home_points"])
                prev_gd = goal_diff[-1]
                curr_gd = games.loc[j,"home_goals"]-games.loc[j,"visiting_goals"]
                goal_diff.append(prev_gd+curr_gd)
            elif games.loc[j,"visiting_team_id"]==i:
                prev_pd = point_diff[-1]
                point_diff.append(prev_pd+games.loc[j,"visiting_points"])
                prev_gd = goal_diff[-1]
                curr_gd = games.loc[j,"visiting_goals"]-games.loc[j,"home_goals"]
                goal_diff.append(prev_gd+curr_gd)
            # if games.loc[j,"winning_team"]==i:
            #     prev = diff[-1]
            #     diff.append(prev+1)
            # elif games.loc[j,"losing_team"]==i:
            #     prev = diff[-1]
            #     diff.append(prev-1)
        point_diff_all = pd.concat((point_diff_all,pd.DataFrame(point_diff,columns=[teams.loc[i,"code"]])),axis=1)
        goal_diff_all = pd.concat((goal_diff_all,pd.DataFrame(goal_diff,columns=[teams.loc[i,"code"]])),axis=1)
        # diff_all = pd.concat((diff_all,pd.DataFrame(diff,columns=[teams.loc[i,"code"]])),axis=1)


with st.container():
    st.header("Classement")
    if go:
        classement = standings[["team_id","games_played","reg_wins","non_reg_wins","non_reg_losses","reg_losses","wins_pct","points"]].reset_index()
        classement["Équipe"] = ""
        for i in classement.index:
            classement.loc[i,"Équipe"] = teams.loc[classement.loc[i,"team_id"],"name"]
        classement.rename(columns={"rank": "Rang", "games_played": "PJ", "reg_wins": "V", "non_reg_wins": "VP", "non_reg_losses": "DP", "reg_losses": "D", "wins_pct": "%", "points": "PTS"},inplace=True)
        st.dataframe(classement.set_index("Rang")[["Équipe","PJ","PTS","V","VP","DP","D","%"]])
        fig, ax = plt.subplots()
        for col in point_diff_all.columns:
            ax.plot(point_diff_all[col],label=col)
        ax.set_title("Classement au fil de la saison")
        ax.set_xlabel("Parties jouées")
        ax.set_ylabel("Points")
        fig.legend()
        st.pyplot(fig)
        # fig, ax = plt.subplots()
        # for col in diff_all.columns:
        #     ax.plot(diff_all[col],label=col)
        # ax.set_title("Différentiel au fil de la saison")
        # ax.set_xlabel("Parties jouées")
        # ax.set_ylabel("Différentiel")
        # fig.legend()
        # st.pyplot(fig)
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def offensive():
    """
    """
    st.toggle("Afficher",key="offensive")
    if st.session_state.get("offensive",False):
        st.subheader("Buts marqués")
        show_visuals(standings,"goals_for","Nombre de buts",False,0,"Total")
        show_visuals(standings,"goals_for_avg","Moyenne de buts",False,2,"Moyenne")

        st.subheader("Tirs au but")
        show_visuals(standings,"shots","Nombre de tirs",False,0,"Total")
        show_visuals(standings,"shots_avg","Moyenne de tirs",False,2,"Moyenne")

        st.subheader("Pourcentage de buts")
        show_visuals(standings,"goals_pct","% de buts",False,1,percent=True)

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
        st.subheader("Buts accordés")
        show_visuals(standings,"goals_against","Nombre de buts accordés",True,0,"Total")
        show_visuals(standings,"goals_against_avg","Moyenne de buts accordés",True,2,"Moyenne")

        st.subheader("Tirs bloqués")
        show_visuals(standings,"shots_blocked","Nombre de tirs bloqués",False,0,"Total")
        show_visuals(standings,"shots_blocked_pct","% de tirs bloqués",False,1,"Pourcentage",True)

        st.subheader("Mises en échec")
        show_visuals(standings,"hits","Nombre de mises en échec",False,0,"Total")
        show_visuals(standings,"hits_avg","Moyenne de mises en échec",False,2,"Moyenne")

with st.container(border=True):
    st.header("Défensive")
    if go:
        defensive()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def sup_inf_num():
    """
    """
    st.toggle("Afficher",key="sup_inf_num")
    if st.session_state.get("sup_inf_num",False):
        st.subheader("Supériorité numérique")
        show_visuals(standings,"power_play_pct","% d'avantage numérique",False,1,percent=True)

        st.subheader("Infériorité numérique")
        show_visuals(standings,"penalty_kill_pct","% d'écoulement de pénalité",False,1,percent=True)

with st.container(border=True):
    st.header("Supériorité et infériorité numérique")
    if go:
        sup_inf_num()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def domicile():
    """
    """
    st.toggle("Afficher",key="domicile")
    if st.session_state.get("domicile",False):
        st.subheader("Pourcentage de victoires")
        show_visuals(standings,"home_wins_pct","% de victoires",False,1,percent=True)

        st.subheader("Buts marqués")
        show_visuals(standings,"home_goals_for_avg","Moyenne de buts marqués",False,2,"Moyenne")

        st.subheader("Buts accordés")
        show_visuals(standings,"home_goals_against_avg","Moyenne de buts accordés",True,2,"Moyenne")

with st.container(border=True):
    st.header("À domicile")
    if go:
        domicile()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def etranger():
    """
    """
    st.toggle("Afficher",key="etranger")
    if st.session_state.get("etranger",False):
        st.subheader("Pourcentage de victoires")
        show_visuals(standings,"visiting_wins_pct","% de victoires",False,1,percent=True)

        st.subheader("Buts marqués")
        show_visuals(standings,"visiting_goals_for_avg","Moyenne de buts marqués",False,2,"Moyenne")

        st.subheader("Buts accordés")
        show_visuals(standings,"visiting_goals_against_avg","Moyenne de buts accordés",True,2,"Moyenne")

with st.container(border=True):
    st.header("À l'étranger")
    if go:
        etranger()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def penalites():
    """
    """
    st.toggle("Afficher",key="penalites")
    if st.session_state.get("penalites",False):
        st.subheader("Minutes de pénalité")
        show_visuals(standings,"penalty_minutes","Minutes de pénalité",False,0,"Total")
        show_visuals(standings,"penalty_minutes_avg","Moyenne de minutes de pénalité",False,2,"Moyenne")

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
        st.subheader("Spectateurs")
        show_visuals(standings,"home_tot_attendance","Nombre de spectateurs à domicile",False,0,"Total")
        show_visuals(standings,"home_avg_attendance","Moyenne de spectateurs à domicile",False,1,"Moyenne")

        st.subheader("Marquer le premier but")
        show_visuals(standings,"first_goals_pct","% de premiers buts marqués",False,1,"Pourcentage",True)

        st.subheader("Différentiel de buts")
        fig, ax = plt.subplots()
        for col in goal_diff_all.columns:
            ax.plot(goal_diff_all[col],label=col)
        ax.set_title("Différentiel de buts au fil de la saison")
        ax.set_xlabel("Parties jouées")
        ax.set_ylabel("Différentiel de buts")
        fig.legend()
        st.pyplot(fig)

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
        st.subheader("Âge")
        show_visuals(standings,"age_avg","Âge moyen",True,2,"(pondéré par le nombre de parties jouées)")

        st.subheader("Taille")
        show_visuals(standings,"height_avg","Taille moyenne (cm)",False,2,"(pondérée par le nombre de parties jouées)")

with st.container(border=True):
    st.header("Informations sur les joueuses")
    if go:
        infos()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

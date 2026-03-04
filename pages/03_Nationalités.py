import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_product_card import product_card
from data import get_seasons, get_teams, get_skaters_df, get_goalies_df

st.set_page_config(page_title="Nationalités",page_icon="🚩")

st.title("Nationalités")

plt.style.use('dark_background')


def show_visuals(base_df: pd.DataFrame, country: str):
    """
    Fonction qui affiche le classement des équipes selon leur nombre de joueuses d'un pays. 
    
    Entrées
        base_df: données à utiliser
        country: pays à utiliser
    """
    new_df = base_df[["team_id",f"count_{country}",f"freq_{country}"]].copy()
    new_df["Équipe"] = ""
    for i in new_df.index:
        new_df.loc[i,"Équipe"] = teams.loc[new_df.loc[i,"team_id"],"name"]

    new_df.sort_values([f"freq_{country}","Équipe"],ascending=False,inplace=True)
    new_df.reset_index(drop=True,inplace=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        product_card(new_df.loc[0,"Équipe"],price=f"{round(new_df.loc[0,f"freq_{country}"],1)}% ({round(new_df.loc[0,f"count_{country}"],0)})",product_image=teams.loc[new_df.loc[0,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key=f"1_freq_{country}")
    with col2:
        product_card(new_df.loc[1,"Équipe"],price=f"{round(new_df.loc[1,f"freq_{country}"],1)}% ({round(new_df.loc[1,f"count_{country}"],0)})",product_image=teams.loc[new_df.loc[1,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key=f"2_freq_{country}")
    with col3:
        product_card(new_df.loc[2,"Équipe"],price=f"{round(new_df.loc[2,f"freq_{country}"],1)}% ({round(new_df.loc[2,f"count_{country}"],0)})",product_image=teams.loc[new_df.loc[2,"team_id"],"team_logo_url"],picture_position="left",enable_animation=False,key=f"3_freq_{country}")
    reste = new_df.loc[3:].copy()
    reste["Rang"] = range(4,reste.shape[0]+4)
    reste.rename(columns={f"freq_{country}": "%", f"count_{country}": "Nombre"},inplace=True)
    st.dataframe(reste.set_index("Rang")[["Équipe","%","Nombre"]])

if not ("nation" in st.session_state):
    st.session_state.nation = None

@st.fragment
def show_list(base_df: pd.DataFrame):
    """
    Fonction qui affiche la liste des joueuses selon leur nationalité. 

    Entrée
        base_df: données à utiliser
    """
    new_df = base_df[["player_id","player_name","team_id","birthcntry"]].copy()
    new_df.drop_duplicates("player_id",inplace=True)
    new_df.set_index("player_id",inplace=True)
    new_df["Équipe"] = ""
    for i in new_df.index:
        new_df.loc[i,"Équipe"] = teams.loc[new_df.loc[i,"team_id"],"name"]
    new_df.rename(columns={"player_name": "Nom", "birthcntry": "Nationalité"},inplace=True)
    nations = new_df["Nationalité"].unique().tolist()
    nations.sort()
    
    st.session_state.nation = st.selectbox("Nationalité",options=nations,index=nations.index("Canada"),placeholder="Choisissez une nationalité")
    new_df = new_df[new_df["Nationalité"]==st.session_state.nation].copy()
    new_df.sort_values(["Équipe","Nom"],inplace=True)
    st.dataframe(new_df.reset_index(drop=True)[["Nom","Équipe","Nationalité"]])

def show_plots(id_equipe: int, base_df: pd.DataFrame):
    """
    Fonction qui affiche la distribution des nationalités des joueuses d'une équipe. 

    Entrées
        id_equipe: identifiant de l'équipe
        base_df: données à utiliser
    """
    st.subheader(teams.loc[id_equipe,"name"])
    new_df = base_df[base_df.team_id==id_equipe].copy()
    if new_df.shape[0]>0:
        new_df["Count"] = 1/new_df.shape[0]
        agg_team = new_df[["birthcntry","Count"]].groupby("birthcntry").sum().reset_index()
        agg_team.sort_values("Count",inplace=True)
        fig, ax = plt.subplots()
        ax.barh(agg_team.birthcntry.to_list(),agg_team.Count.to_list())
        ax.set_title(f"Nationalité des joueuses de {teams.loc[id_equipe,"name"]}")
        ax.set_xlabel("Fréquence relative")
        st.pyplot(fig)


seasons = get_seasons()

with st.sidebar:
    st.header("Options")

    saison = st.selectbox("Saison",options=seasons[seasons.career==1].season_name.to_list(),placeholder="Choisissez une saison")
    id_saison = seasons[seasons.season_name==saison].index.to_list()[0]

    go = st.button("Récupérer les données")
    if go:
        with st.spinner("Récupération en cours..."):
            teams = get_teams(id_saison,saison)
            skaters = get_skaters_df(id_saison,saison)
            goalies = get_goalies_df(id_saison,saison)
            players = pd.concat((skaters.reset_index()[["player_id","player_name","team_id","birthprov","birthcntry"]],goalies.reset_index()[["player_id","player_name","team_id","birthprov","birthcntry"]]))
            players["Count"] = 1
            players["%"] = 1/players.shape[0]


with st.container():
    st.header("Ligue")
    if go:
        if players.shape[0]>0:
            agg = players[["birthcntry","%"]].groupby("birthcntry").sum().reset_index()
            agg.sort_values("%",inplace=True)
            fig, ax = plt.subplots()
            ax.barh(agg.birthcntry.to_list(),agg["%"].to_list())
            ax.set_title("Nationalité des joueuses de la LPHF")
            ax.set_xlabel("Fréquence relative")
            st.pyplot(fig)
        else:
            st.error("Il n'y a aucune donnée sur la nationalité des joueuses.")
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def can_vs_usa():
    """
    """
    st.toggle("Afficher",key="can_vs_usa")
    if st.session_state.get("can_vs_usa",False):
        all_teams = []
        for i in teams.index:
            data = {"team_id": i}
            n = players[players.team_id==i].shape[0]
            data["count_can"] = players[(players.team_id==i)*(players.birthcntry=="Canada")].shape[0]
            data["freq_can"] = 100*data["count_can"]/n if n>0 else 0.0
            data["count_usa"] = players[(players.team_id==i)*(players.birthcntry=="United States")].shape[0]
            data["freq_usa"] = 100*data["count_usa"]/n if n>0 else 0.0
            data["count_oth"] = players[(players.team_id==i)*(players.birthcntry!="Canada")*(players.birthcntry!="United States")].shape[0]
            data["freq_oth"] = 100*data["count_oth"]/n if n>0 else 0.0
            all_teams.append(data)
        df = pd.DataFrame(all_teams)
        st.subheader("Canada 🇨🇦")
        show_visuals(df,"can")

        st.subheader("États-Unis 🇺🇸")
        show_visuals(df,"usa")

        st.subheader("Autres 🏳️")
        show_visuals(df,"oth")

with st.container(border=True):
    st.header("Canada vs États-Unis")
    if go:
        can_vs_usa()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def par_nationalite():
    """
    """
    st.toggle("Afficher",key="par_nationalite")
    if st.session_state.get("par_nationalite",False):
        show_list(players)

with st.container(border=True):
    st.header("Par nationalité")
    if go:
        par_nationalite()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")


@st.fragment
def par_equipe():
    """
    """
    st.toggle("Afficher",key="par_equipe")
    if st.session_state.get("par_equipe",False):
        for i in teams.index:
            show_plots(i,players)

with st.container(border=True):
    st.header("Par équipe")
    if go:
        par_equipe()
    else:
        st.info("Cliquez sur le bouton pour récupérer les données.")

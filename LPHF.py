import streamlit as st

st.set_page_config(page_title="LPHF",page_icon="🏒")

st.title("Ligue professionnelle de hockey féminin")

with st.container():
    st.subheader("Tableaux de bord de la LPHF")
    st.text("Cette application comprend 6 tableaux de bord pour visualiser les performances des équipes et des joueuses de la LPHF.")
    st.text("")
    st.markdown("Source des données : API HockeyTech ([référence](https://github.com/IsabelleLefebvre97/PWHL-Data-Reference))")
    st.markdown("Récupération et traitement des données : repo [GitHub](https://github.com/Yu270/PWHL-Dashboards/tree/main/data)")

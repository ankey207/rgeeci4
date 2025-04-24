# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import function
from datetime import datetime, timedelta,time, timezone
import numpy as np
import plotly.express as px
import requests
from io import StringIO


st.set_page_config(page_title="RGEE-CI",layout="wide", initial_sidebar_state="auto", page_icon="logo_rgeeci.jpg")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.header("RGEE-CI: REPORTING COLLECTE")
function.load_styles()

url = "https://kf.kobotoolbox.org/api/v2/assets/azR3wHzm3BK4YKbrrrSfFo/export-settings/esw25ALnhMxzoshajCy4hGm/data.csv"

username = "amanyankey2"
password = "L@ScXi7TFhKWrN5"

# Effectuer une requête HTTP avec authentification basique
response = requests.get(url, auth=(username, password))

# Vérifier que la requête a réussi
if response.status_code == 200:
    df = function.get_data_from_forms(StringIO(response.text))
else:
    st.warning("Aucune data")

st.write(df)
st.write(function.liste_equipe )
#Chargement du fichier d'attribution des ZD par équipes et merge avec les geodf
#df_attribution_zd = function.get_data_attribution_eq_xlsx("Attribution_zd.xlsx")
#chargement des ZDs
#geo_df = function.load_geozd("Contour_NAWA_GBOKLE.geojson")
#geo_df = geo_df.merge(df_attribution_zd[['NumZD', "NOM CHEF D'EQUIPE"]], on='NumZD', how='left')
#st.write(geo_df[["NomSp",'NumZD', "NOM CHEF D'EQUIPE"]])

#Coordonnées initiales pour l'affichage de la carte (Soubre)
#latitude_centre = 5.788289
#longitude_centre = -6.594167

with st.sidebar:
    if st.button("ACTUALISER", type="primary"):
        function.get_data_from_forms.clear()

    CE =df["Chef d'equipe"].sort_values().unique()
    CE_SELECT = st.selectbox("CHEFS D'EQUIPE:",CE,index=None)

    SUP =df["Superviseur"].sort_values().unique()
    SUP_SELECT = st.selectbox("SUPERVISEUR:",SUP,index=None)


if len(df)!= 0 :
    try:
        if CE_SELECT:
            df = df.loc[df["Chef d'equipe"]==CE_SELECT]
        if SUP_SELECT:
            df = df.loc[df["Superviseur"]==SUP_SELECT]
    except:
        pass
    
def split_and_collect(column):
    result = []
    for item in column:
        if isinstance(item, str):  # Vérifie si l'élément est une chaîne de caractères
            result.extend(item.split(','))
        elif pd.notna(item):  # Vérifie si l'élément n'est pas NaN (valeurs manquantes)
            result.append(str(item))  # Convertit les autres types en chaîne de caractères et les ajoute à la liste
    return result


#recupeeration coordonnees cnetroide en fonction de la zone geographique


# Appliquer la fonction à la colonne
liste_zd = split_and_collect(df['NumZD'])
liste_zd = list(set(liste_zd))
liste_zd = [s for s in liste_zd if "0000" not in s]

#Identification des ZDs traiteees
#geo_df["Statut ZD"] = geo_df["NumZD"].apply(lambda x: function.statut_zd(x, liste_zd))

# Obtenez l'heure actuelle en GMT+0
current_time = datetime.now(timezone.utc).time()
current_date = pd.to_datetime(datetime.now().date())
cutoff_time = time(17, 30)  # 17:30 in 24-hour format

UET = df[['UEF_complet_agent1','UEI_complet_agent1',"UEF_partiel_agent1","UEI_partiel_agent1","UEP_sans_statut_agent1","UE_refus_agent1",'UEF_complet_agent1','UEI_complet_agent2',"UEF_partiel_agent2","UEI_partiel_agent2","UEP_sans_statut_agent2","UE_refus_agent2",'UEF_complet_agent3','UEI_complet_agent3',"UEF_partiel_agent3","UEI_partiel_agent3","UEP_sans_statut_agent3","UE_refus_agent3"]].sum(axis=1).sum()
UEI = df[['UEI_complet_agent1', 'UEI_partiel_agent1','UEI_complet_agent2', 'UEI_partiel_agent2','UEI_complet_agent3', 'UEI_partiel_agent3']].sum(axis=1).sum()
UEF = df[['UEF_complet_agent1', 'UEF_partiel_agent1','UEF_complet_agent2', 'UEF_partiel_agent2','UEF_complet_agent3', 'UEF_partiel_agent3']].sum(axis=1).sum()
REFUS = df[["UE_refus_agent1","UE_refus_agent2","UE_refus_agent3"]].sum(axis=1).sum()
UE_partiels = df[["UEF_partiel_agent1","UEI_partiel_agent1","UEP_sans_statut_agent1","UEF_partiel_agent2","UEI_partiel_agent2","UEP_sans_statut_agent2","UEF_partiel_agent3","UEI_partiel_agent3","UEP_sans_statut_agent3"]].sum(axis=1).sum()-df[['UEPF_trans_complet_agent1','UEPI_trans_complet_agent1','UEPF_trans_complet_agent2','UEPI_trans_complet_agent2','UEPF_trans_complet_agent3','UEPI_trans_complet_agent3']].sum(axis=1).sum()
Nb_rdv_h = df["Nb_rdv_h"].sum()
Nb_rdv = df["Nb_rdv"].sum()
Nb_rdv_attente = Nb_rdv-Nb_rdv_h

ZD_total = len(liste_zd)
container =st.container()
with container:
    col1, col2, col3, col3a = st.columns(4)
    col1.metric("UE", f"{UET:,}")
    col2.metric("Formelle", f"{UEF:,}")
    col3.metric("Informelle", f"{UEI:,}")
    col3a.metric("Partiels", f"{UE_partiels:,}")
with container:
    col4, col5, col6,col7, col8 = st.columns(5)
    col4.metric("ZDs traités", f"{ZD_total:,}")
    col5.metric("Refus", f"{REFUS:,}")
    col6.metric("Total RDV", f"{Nb_rdv:,}")
    col7.metric("RDV honoré", f"{Nb_rdv_h:,}")
    col8.metric("RDV en attente", f"{Nb_rdv_attente:,}")

#RESULTAT PAR EQUIPE SUR LES 5 DERNIERS JOURS
st.markdown("<h5 style='text-align: center;color: #3a416c;'>RESULTAT PAR EQUIPE SUR LES 5 DERNIERS JOURS</h5>", unsafe_allow_html=True)
pivot_df =  df[["date_reporting","Chef d'equipe","UE_total"]]
pivot_df = pivot_df.pivot_table(index="Chef d'equipe", columns='date_reporting',values='UE_total', aggfunc='sum', fill_value=0)
pivot_df["Total depuis le debut"] = pivot_df.sum(axis=1)

sum_row = pivot_df.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
pivot_df = pd.concat([pivot_df, sum_row_df])

ensemble_col = pivot_df['Total depuis le debut']
date_columns = pd.to_datetime(pivot_df.columns.drop('Total depuis le debut'))

today = datetime.now()
five_days_ago = today - timedelta(days=5)
filtered_columns = date_columns[date_columns >= five_days_ago]
pivot_df = pivot_df[filtered_columns.strftime('%Y-%m-%d').tolist()+['Total depuis le debut']]
st.table(function.style_dataframe(pivot_df))


#classement des AGENTS
df["UE_agent1"] = df[['UEF_complet_agent1','UEI_complet_agent1',"UEF_partiel_agent1","UEI_partiel_agent1","UEP_sans_statut_agent1","UE_refus_agent1",'UEF_complet_agent1']].sum(axis=1)
df["UE_agent2"] = df[['UEF_complet_agent2','UEI_complet_agent2',"UEF_partiel_agent2","UEI_partiel_agent2","UEP_sans_statut_agent2","UE_refus_agent2",'UEF_complet_agent2']].sum(axis=1)
df["UE_agent3"] = df[['UEF_complet_agent3','UEI_complet_agent3',"UEF_partiel_agent3","UEI_partiel_agent3","UEP_sans_statut_agent3","UE_refus_agent3",'UEF_complet_agent3']].sum(axis=1)

st.markdown("<h5 style='text-align: center;color: #3a416c;'>RESULTATS AGENTS RECENSEURS</h5>", unsafe_allow_html=True)
stat_agent_lastday = df[["date_reporting","Chef d'equipe","nom_CE","UE_agent1","UE_agent2","UE_agent3"]]
stat_agent_lastday = stat_agent_lastday.melt(id_vars=['date_reporting', 'Chef d\'equipe', "nom_CE"], 
                                             value_vars=['UE_agent1', 'UE_agent2', 'UE_agent3'], 
                                             var_name='Nom_Agent', 
                                             value_name='Value')

stat_agent_lastday = stat_agent_lastday.pivot_table(index=['Chef d\'equipe', "nom_CE", 'Nom_Agent'], 
                                                    columns='date_reporting', 
                                                    values='Value').reset_index()
numeric_columns = stat_agent_lastday.select_dtypes(include=[np.number]).columns.tolist()
# Remplir les NaN avec 0
stat_agent_lastday[numeric_columns] = stat_agent_lastday[numeric_columns].fillna(0)

# Calculer la somme pour la colonne "Total depuis le debut"
stat_agent_lastday["Total depuis le debut"] = stat_agent_lastday[numeric_columns].sum(axis=1)# Remplacer les NaN par une valeur par défaut (par exemple 0)
stat_agent_lastday[filtered_columns.strftime('%Y-%m-%d').tolist()] = stat_agent_lastday[filtered_columns.strftime('%Y-%m-%d').tolist()].fillna(0).astype(int)

stat_agent_lastday['Nom_Agent'] = stat_agent_lastday['nom_CE'].str.replace('Ce', 'Agt') + stat_agent_lastday['Nom_Agent'].str[-1]
stat_agent_lastday = function.add_agent_name(stat_agent_lastday)
stat_agent_lastday = stat_agent_lastday[['Chef d\'equipe',"nom_CE", 'Nom_Agent']+filtered_columns.strftime('%Y-%m-%d').tolist()+['Total depuis le debut']]
stat_agent_lastday['Total depuis le debut'] = stat_agent_lastday['Total depuis le debut'].astype(int)
stat_agent_lastday.drop(columns=["nom_CE"], inplace=True)
stat_agent_lastday.sort_values(by=['Chef d\'equipe', 'Nom_Agent'], ascending=True, inplace=True)
stat_agent_lastday = stat_agent_lastday.reset_index(drop=True)
stat_agent_lastday.index = stat_agent_lastday.index + 1
st.table(function.style_dataframe(stat_agent_lastday))




#liste des ZD deja acheves
st.markdown("<h5 style='text-align: center;color: #3a416c;'>LISTES DES ZD TRAITEES</h5>", unsafe_allow_html=True)
df_zd = df[["Chef d'equipe","NumZD"]]
df_zd = df_zd.groupby("Chef d'equipe").agg({"NumZD": function.concat_list_zd}).reset_index()
df_zd["NumZD"] = df_zd["NumZD"].apply(function.delete_doublon_and_sort_from_list_zd)
df_zd.set_index("Chef d'equipe",inplace=True)

st.table(function.style_dataframe(df_zd))

#DIFFICULTES DU JOUR
yesterday = datetime.now().date()-timedelta(days=1)
st.markdown("<h5 style='text-align: center;color: #3a416c;'>DIFFICULTES DU JOUR</h5>", unsafe_allow_html=True)
df_difficultes_obs = df[["Chef d'equipe","difficultes","date_reporting","observations"]]
df_difficultes_obs["date_reporting"] = df_difficultes_obs["date_reporting"].apply(function.convert_to_datetime)
df_difficultes_obs = df_difficultes_obs[df_difficultes_obs["date_reporting"] >=yesterday]

df_difficultes = df_difficultes_obs[~df_difficultes_obs['difficultes'].isna()]
df_difficultes = df_difficultes.groupby("Chef d'equipe")['difficultes'].agg('/'.join).reset_index()
st.table(function.style_dataframe(df_difficultes))

st.markdown("<h5 style='text-align: center;color: #3a416c;'>OBSERVATIONS DU JOUR</h5>", unsafe_allow_html=True)
df_obs = df_difficultes_obs[~df_difficultes_obs['observations'].isna()]
df_obs = df_obs.groupby("Chef d'equipe")['observations'].agg('/'.join).reset_index()
st.table(function.style_dataframe(df_obs))







footer="""<style>
    a:link , a:visited{
    color: blue;
    background-color: transparent;
    text-decoration: underline;
    }

    a:hover,  a:active {
    color: red;
    background-color: transparent;
    text-decoration: underline;
    }

    .footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: transparent;
    color: black;
    text-align: center;
    }
</style>
<div class="footer">
    <p>Developed by <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/nsi%C3%A9ni-kouadio-eli%C3%A9zer-amany-613681185" target="_blank">Nsiéni Amany Kouadio</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

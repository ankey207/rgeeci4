# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import function
from datetime import datetime, timedelta,time, timezone
import numpy as np
import plotly.express as px

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

url = "https://kf.kobotoolbox.org/api/v2/assets/awexhpC92q5Xo3oA7G9DZg/export-settings/es7DwtyTCa6oPdBmbPsr8m8/data.csv"
df = function.get_data_from_forms(url)

#Chargement du fichier d'attribution des ZD par équipes et merge avec les geodf
df_attribution_zd = function.get_data_attribution_eq("Attribution_zd.csv")
#chargement des ZDs
geo_df = function.load_geozd("Contour_NAWA.geojson")
geo_df = geo_df.merge(df_attribution_zd[['NumZD', "NOM CHEF D'EQUIPE"]], on='NumZD', how='inner')

#Coordonnées initiales pour l'affichage de la carte (Soubre)
latitude_centre = 5.788289
longitude_centre = -6.594167

with st.sidebar:
    if st.button("ACTUALISER", type="primary"):
        function.get_data_from_forms.clear()

    st.title("Filtre")
    SUP =df["Superviseur"].sort_values().unique()
    SUP_SELECT = st.selectbox("SUPERVISEURS:",SUP,index=None)

    CE =df["Chef d'equipe"].sort_values().unique()
    CE_SELECT = st.selectbox("CHEFS D'EQUIPE:",CE,index=None)

    REG =df["NomReg"].sort_values().unique()
    REG_SELECT = st.selectbox("REGION:",REG,index=None)

    DEP =df["NomDep"].sort_values().unique()
    DEP_SELECT = st.selectbox("DEPARTEMENT:",DEP,index=None)

    SP =df["NomSp"].sort_values().unique()
    SP_SELECT = st.selectbox("SOUS-PREFECTURE:",SP,index=None)

if len(df)!= 0 :
    try:
        if SUP_SELECT:
            df = df.loc[df['Superviseur']==SUP_SELECT]
            latitude_centre = function.coords_superviseur[SUP_SELECT][0]
            longitude_centre = function.coords_superviseur[SUP_SELECT][1]

        if CE_SELECT:
            df = df.loc[df["Chef d'equipe"]==CE_SELECT]
            geo_df = geo_df.loc[geo_df["NOM CHEF D'EQUIPE"]==CE_SELECT]

        if REG_SELECT:
            df = df.loc[df["NomReg"]==REG_SELECT]
            latitude_centre = function.coords_region[REG_SELECT][0]
            longitude_centre = function.coords_region[REG_SELECT][1]

        if DEP_SELECT:
            df = df.loc[df["NomDep"]==DEP_SELECT]
            latitude_centre = function.coords_departement[DEP_SELECT][0]
            longitude_centre = function.coords_departement[DEP_SELECT][1]

        if SP_SELECT:
            df = df.loc[df["NomSp"]==SP_SELECT]
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
geo_df["Statut ZD"] = geo_df["NumZD"].apply(lambda x: function.statut_zd(x, liste_zd))

# Obtenez l'heure actuelle en GMT+0
current_time = datetime.now(timezone.utc).time()
current_date = pd.to_datetime(datetime.now().date())
cutoff_time = time(17, 30)  # 17:30 in 24-hour format

if current_time < cutoff_time:
    df.loc[df['date_2']!=current_date-timedelta(days=1), 'partiels'] = 0
    df.loc[df['date_2']!= current_date-timedelta(days=1), 'refus'] = 0
else:
    df.loc[df['date_2'] < current_date, 'partiels'] = 0
    df.loc[df['date_2'] < current_date, 'refus'] = 0

df['partiels'] = df['partiels'].astype(int)
df['refus'] = df['refus'].astype(int)


UET = df["UE_total"].sum()
UEI = df["UE I"].sum()
UEF = df["UE F"].sum()
REFUS = df["refus"].sum()
UE_partiels = df["partiels"].sum()

ZD_total = len(liste_zd)
container =st.container()
with container:
    col1, col2, col3, col3a = st.columns(4)
    col1.metric("UE", f"{UET:,}")
    col2.metric("Formelle", f"{UEF:,}")
    col3.metric("Informelle", f"{UEI:,}")
    col3a.metric("Partiels", f"{UE_partiels:,}")
with container:
    col4, col5, col6 = st.columns([2,3,2])
    col4.metric("ZDs traités", f"{ZD_total:,}")
    col5.metric("Taux de réalisation ZD", f"{(ZD_total/569)*100:.2f}%")
    col6.metric("Refus", f"{REFUS:,}")

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

#STATISTIQUE EQUIPE
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR EQUIPES</h5>", unsafe_allow_html=True)
stat_ce = df[["Chef d'equipe","UE F","UE I","UE_total","partiels","refus","NbZD","NumZD","ZD_affectees"]]
stat_ce = stat_ce.groupby("Chef d'equipe").agg({
    "UE F": "sum",
    "UE I": "sum",
    "UE_total": "sum",
    "partiels": "sum",
    "refus": "sum",
    "NbZD": "sum",
    "NumZD": function.concat_list_zd,
    "ZD_affectees": "first"
}).reset_index()

stat_ce["NumZD"] = stat_ce["NumZD"].apply(function.delete_doublon_and_sort_from_list_zd)
stat_ce["NbZD"] = stat_ce["NumZD"].apply(function.count_unique_zd)
stat_ce["ZD_affectees"] =stat_ce["ZD_affectees"].astype("int")
stat_ce.drop(columns="NumZD",inplace=True)
stat_ce.sort_values(by="UE_total",ascending=False,inplace=True)
stat_ce.set_index("Chef d'equipe",inplace=True)
st.table(function.style_dataframe(stat_ce))

#STATISTIQUES PAR DEPARTEMENT
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR DEPARTEMENT</h5>", unsafe_allow_html=True)
stat_departement = df[["NomDep","UE F","UE I","UE_total","partiels","refus","NbZD","NumZD"]]
#stat_departement = stat_departement.groupby("NomDep").sum()
stat_departement = stat_departement.groupby("NomDep").agg({
    "UE F": "sum",
    "UE I": "sum",
    "UE_total": "sum",
    "partiels": "sum",
    "refus": "sum",
    "NbZD": "sum",
    "NumZD": function.concat_list_zd
}).reset_index()
stat_departement["NumZD"] = stat_departement["NumZD"].apply(function.delete_doublon_and_sort_from_list_zd)
stat_departement["NbZD"] = stat_departement["NumZD"].apply(function.count_unique_zd)
stat_departement.drop(columns="NumZD",inplace=True)
stat_departement.set_index("NomDep",inplace=True)
sum_row = stat_departement.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
stat_departement = pd.concat([stat_departement, sum_row_df])
st.table(function.style_dataframe(stat_departement))

#STATISTIQUES PAR SUPERVISEUR
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR SUPERVISEUR</h5>", unsafe_allow_html=True)
stat_sup = df[["Superviseur","UE F","UE I","UE_total","partiels","refus","NbZD","NumZD"]]
#stat_sup = stat_sup.groupby("Superviseur").sum()

stat_sup = stat_sup.groupby("Superviseur").agg({
    "UE F": "sum",
    "UE I": "sum",
    "UE_total": "sum",
    "partiels": "sum",
    "refus": "sum",
    "NbZD": "sum",
    "NumZD": function.concat_list_zd
}).reset_index()
stat_sup["NumZD"] = stat_sup["NumZD"].apply(function.delete_doublon_and_sort_from_list_zd)
stat_sup["NbZD"] = stat_sup["NumZD"].apply(function.count_unique_zd)
stat_sup.drop(columns="NumZD",inplace=True)
stat_sup.set_index("Superviseur",inplace=True)
st.table(function.style_dataframe(stat_sup))

#classement des AGENTS
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
st.markdown("<h5 style='text-align: center;color: #3a416c;'>LISTES DES ZD TRAITES</h5>", unsafe_allow_html=True)
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

# Création de la carte Folium

fig = px.choropleth_mapbox(geo_df,
    geojson=geo_df.geometry,
    locations=geo_df.index,
    #center={'lat':5.788289, 'lon':-6.594167},
    center={'lat':latitude_centre, 'lon':longitude_centre},
    mapbox_style="open-street-map",
    zoom=11,opacity=0.2,color="Statut ZD",
    color_discrete_map = {"Traité": "green", "Non traité": "red"},
    hover_data = ["LibQtierCp","NumZD","NOM CHEF D'EQUIPE"]
    )
fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
st.plotly_chart(fig, theme="streamlit", use_container_width=True)



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
# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import function
from datetime import datetime, timedelta


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

        if CE_SELECT:
            df = df.loc[df["Chef d'equipe"]==CE_SELECT]

        if REG_SELECT:
            df = df.loc[df["NomReg"]==REG_SELECT]

        if DEP_SELECT:
            df = df.loc[df["NomDep"]==DEP_SELECT]

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

# Appliquer la fonction à la colonne
liste_zd = split_and_collect(df['NumZD'])
liste_zd = list(set(liste_zd))
try:
    liste_zd.remove("0000")
except:
    pass

UET = df["UE_total"].sum()
REFUS = df["refus"].sum()
UEI = df["UE informelle"].sum()
UEF = df["UE formelle"].sum()

ZD_total = len(liste_zd)
container =st.container()
with container:
    col1, col2, col3 = st.columns(3)
    col1.metric("UE", f"{UET:,}")
    col2.metric("UE formelle", f"{UEF:,}")
    col3.metric("UE informelle", f"{UEI:,}")
with container:
    col4, col5, col6 = st.columns([2,3,2])
    col4.metric("ZDs traités", f"{ZD_total:,}")
    col5.metric("Taux de réalisation ZD", f"{(ZD_total/569)*100:.2f}%")
    col6.metric("Refus", f"{REFUS:,}")

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

# Obtenir la date actuelle
today = datetime.now()
five_days_ago = today - timedelta(days=5)
filtered_columns = date_columns[date_columns >= five_days_ago]
pivot_df = pivot_df[filtered_columns.strftime('%Y-%m-%d').tolist()+['Total depuis le debut']]
st.table(function.style_dataframe(pivot_df))

#STATISTIQUE EQUIPE
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR EQUIPES</h5>", unsafe_allow_html=True)
stat_ce = df[["Chef d'equipe","UE formelle","UE informelle","UE_total","refus","Nombre ZD"]]
stat_ce = stat_ce.groupby("Chef d'equipe").sum()
stat_ce.sort_values(by="UE_total",ascending=False,inplace=True)
st.table(function.style_dataframe(stat_ce))

#STATISTIQUES PAR DEPARTEMENT
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR DEPARTEMENT</h5>", unsafe_allow_html=True)
stat_departement = df[["NomDep","UE formelle","UE informelle","UE_total","refus","Nombre ZD"]]
stat_departement = stat_departement.groupby("NomDep").sum()

sum_row = stat_departement.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
stat_departement = pd.concat([stat_departement, sum_row_df])
st.table(function.style_dataframe(stat_departement))

#STATISTIQUES PAR SUPERVISEUR
st.markdown("<h5 style='text-align: center;color: #3a416c;'>STATISTIQUES PAR SUPERVISEUR</h5>", unsafe_allow_html=True)
stat_sup = df[["Superviseur","UE formelle","UE informelle","UE_total","refus","Nombre ZD"]]
stat_sup = stat_sup.groupby("Superviseur").sum()
st.table(function.style_dataframe(stat_sup))

#classement des AGENTS
st.markdown("<h5 style='text-align: center;color: #3a416c;'>CLASSEMENT AGENTS RECENSEURS</h5>", unsafe_allow_html=True)
stat_agent = df[["nom_CE","UE_agent1","UE_agent2","UE_agent3"]]
stat_agent =stat_agent.groupby("nom_CE").sum()
stat_agent = stat_agent.reset_index()
stat_agent = stat_agent.melt(id_vars=['nom_CE'], var_name='Agent', value_name='UE_Total')
stat_agent['Nom_Agent'] = stat_agent['nom_CE'].str.replace('Ce', 'Agt')+stat_agent['Agent'].str[-1]
stat_agent = stat_agent[["Nom_Agent","UE_Total"]]
stat_agent.sort_values(by="UE_Total",ascending=False,inplace=True)
stat_agent = function.add_agent_name(stat_agent)
stat_agent = stat_agent.reset_index(drop=True)
stat_agent.index = stat_agent.index + 1
st.table(function.style_dataframe(stat_agent))

#liste des ZD deja acheves
st.markdown("<h5 style='text-align: center;color: #3a416c;'>LISTES DES ZD TRAITES</h5>", unsafe_allow_html=True)
df_zd = df[["Chef d'equipe","NumZD"]]
df_zd['ZD traites'] = df_zd['NumZD'].astype(str)
df_zd = df_zd[(df_zd['ZD traites'] != '0000') & (df_zd['ZD traites'] != 'nan')]
df_zd = df_zd.groupby("Chef d'equipe")['ZD traites'].agg(', '.join).reset_index()
df_zd['ZD traites'] = df_zd['ZD traites'].apply(function.remove_duplicates_and_sort)
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
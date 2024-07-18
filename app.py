# Importation des modules nécessaires
import streamlit as st
import pandas as pd
import time
import os
import function
import plotly.express as px
import geopandas as gpd
import datetime


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


st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR EQUIPE</h5>", unsafe_allow_html=True)
pivot_df =  df[["date_reporting","Chef d'equipe","UE_total"]]
#pivot_df = pivot_df.rename(columns={'s0q10':"date",'s0q9':"Agent"})
pivot_df = pivot_df.pivot_table(index="Chef d'equipe", columns='date_reporting',values='UE_total', aggfunc='sum', fill_value=0)
pivot_df["Ensemble"] = pivot_df.sum(axis=1)

sum_row = pivot_df.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
pivot_df = pd.concat([pivot_df, sum_row_df])
st.table(function.style_dataframe(pivot_df))
#st.table(pivot_df.style.applymap(function.cooling_highlight,subset=['Ensemble']))

st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR DEPARTEMENT</h5>", unsafe_allow_html=True)
df_depart = df[["NomDep","UE formelle","UE informelle","UE_total","refus","Nombre ZD"]]
df_depart = df_depart.groupby("NomDep").sum()

sum_row = df_depart.sum(axis=0)
sum_row_df = pd.DataFrame(sum_row).T
sum_row_df.index = ['Total']
df_depart = pd.concat([df_depart, sum_row_df])
st.table(function.style_dataframe(df_depart))

#st.write(df_depart)


st.markdown("<h5 style='text-align: center;color: #3a416c;'>TABLEAU DE SUIVI PAR SUPERVISEUR</h5>", unsafe_allow_html=True)
df_sup = df[["Superviseur","UE formelle","UE informelle","UE_total","refus","Nombre ZD"]]
df_sup = df_sup.groupby("Superviseur").sum()
st.table(function.style_dataframe(df_sup))

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
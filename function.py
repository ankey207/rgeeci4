import pandas as pd
from io import StringIO
import requests
import streamlit as st
import geopandas as gpd
import regex as re
from datetime import datetime

liste_equipe = {
    "RGEECI_Ce0130": "DJELI CLAVER KEVIN",
    "RGEECI_Ce0131": "TRAORE ISSIAKA KY",
    "RGEECI_Ce0132": "OUREGA JONAS CAMPBEL",
    "RGEECI_Ce0133": "OREGA KADI JEPHTHE",
    "RGEECI_Ce0134": "BLE GONDO FULGENCE",
    "RGEECI_Ce0135": "AGO TOGBEDJI JACQUES",
    "RGEECI_Ce0136": "FOFANA LACINE",
    "RGEECI_Ce0137": "SOUNAN BERTIN JEAN CYRILLE",
    "RGEECI_Ce0138": "N'GOTTA KOFFI FULGENCE ALAIN",
    "RGEECI_Ce0139": "ASSI YAPO CONSTANT",
    "RGEECI_Ce0140": "DANSI GEOFFROY FABIEN",
    "RGEECI_Ce0141": "CAMARA LIATCHIN",
    "RGEECI_Ce0142": "OUATTARA BAMADOU"
}

liste_sup = {
    "RGEECI_Ce0130": "COULIBALY",
    "RGEECI_Ce0131": "COULIBALY",
    "RGEECI_Ce0132": "COULIBALY",
    "RGEECI_Ce0133": "ADOU",
    "RGEECI_Ce0134": "ADOU",
    "RGEECI_Ce0135": "AMANY",
    "RGEECI_Ce0136": "ADOU",
    "RGEECI_Ce0137": "AMANY",
    "RGEECI_Ce0138": "AMANY",
    "RGEECI_Ce0139": "ADOU",
    "RGEECI_Ce0140": "AMANY",
    "RGEECI_Ce0141": "AMANY",
    "RGEECI_Ce0142": "AMANY"
}


def cooling_highlight(val):
    color = '#aaf6aa' if val else 'white'
    return f'background-color: {color}'

def convert_to_datetime(date_str):
    if date_str is None:
        return None
    if isinstance(date_str, float):
        return 
    else:
        return datetime.strptime(str(date_str), "%d/%m/%Y")

@st.cache_data
def get_data_from_forms(url):
    df = pd.read_csv(url,sep=';', dtype={"NumZD":"object"})
    df["Chef d'equipe"] = df["nom_CE"].map(liste_equipe)
    df["Superviseur"] = df["nom_CE"].map(liste_sup)
    df = df.rename(columns={"UEF_total":"UE formelle","UEI_total":"UE informelle","NbZD":"Nombre ZD","refus_total":"refus"})
    return df

@st.cache_resource
def load_styles():
    with open('style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Appliquer la fonction à chaque ligne du DataFrame pour créer une nouvelle colonne
def style_dataframe(df):
    # Créer un DataFrame de style
    styled_df = df.style
    
    # Colorier les entêtes, les index et les lignes du corps en bleu nuit
    styled_df.set_table_styles([
        {'selector': 'td:hover','props': [('background-color', '#7dbef4')]},
        {'selector': '.index_name','props': 'font-style: italic; color: darkgrey; font-weight:normal;'},
        {'selector': 'th:not(.index_name)','props': 'background-color: #3a416c; color: white;'},
    ], overwrite=False)

    # Colorier les lignes du corps en alternance en gris et blanc
    def row_style(row):
        # Convertir row.name en entier si possible
        try:
            row_index = int(row.name)
        except ValueError:
            row_index = hash(row.name)
        
        if row_index % 2 == 0:
            return ['background-color: #ebecf0'] * len(row)
        else:
            return ['background-color: #f9fafd'] * len(row)

    styled_df.apply(row_style, axis=1)

    return styled_df

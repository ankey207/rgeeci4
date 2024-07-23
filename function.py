import pandas as pd
import streamlit as st
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
liste_ar = {
    "RGEECI_Agt01301": "KOUASSI KOFFI JULIEN",
    "RGEECI_Agt01302": "DAGOU DAZE THIERRY",
    "RGEECI_Agt01303": "GNAMBA LANDRY",
    "RGEECI_Agt01311": "OUATTARA MAMADOU",
    "RGEECI_Agt01312": "KOUASSI KOUADIO ANGE GAUTHIER",
    "RGEECI_Agt01313": "AMANI AYA BENEDICTE",
    "RGEECI_Agt01321": "AMANY YATCHIA STÉPHANIE",
    "RGEECI_Agt01322": "BROU KOUAME NOKAN PACOME",
    "RGEECI_Agt01323": "AHIZI YABA GISÈLE",
    "RGEECI_Agt01331": "YOBOUET KONAN LEOPOLD",
    "RGEECI_Agt01332": "KOUAKOU KONAN JEAN-LUC",
    "RGEECI_Agt01333": "KOUASSI KOUADIO STEVEN",
    "RGEECI_Agt01341": "AKAMOU N'DA EMMANUEL",
    "RGEECI_Agt01342": "BOGUI JEAN-YVES",
    "RGEECI_Agt01343": "ME N'GORAN HENRIETTE",
    "RGEECI_Agt01351": "ISSIAKA BAYOUE",
    "RGEECI_Agt01352": "DISSIA MONSIBBLE STÉPHANE CHARLY",
    "RGEECI_Agt01353": "SERI GBALE ATTOUBE DÉBORAH",
    "RGEECI_Agt01361": "KONAN YAO BLAISE",
    "RGEECI_Agt01362": "KOUKOUGNON ISAAC ALAIN CHARLES",
    "RGEECI_Agt01363": "GOGUI ANGE FRANCKY",
    "RGEECI_Agt01371": "DIARRASSOUBA YOUSSOUF N'GOLO ANSELME",
    "RGEECI_Agt01372": "KONE METAN GRÂCE SCHELA",
    "RGEECI_Agt01373": "SYLLA ISSOUF",
    "RGEECI_Agt01381": "MAVOU ZONRE FRANCOIS JOSUE",
    "RGEECI_Agt01382": "AHOUTOU FRANCK WILLIAMS LE ROY",
    "RGEECI_Agt01383": "SILUE LASSINA",
    "RGEECI_Agt01391": "BINDE FRANCK ANICET",
    "RGEECI_Agt01392": "DIABAGATE BASSORY",
    "RGEECI_Agt01393": "OUATTARA AZOUMANA",
    "RGEECI_Agt01401": "ÀMANI N'GORAN AUGUSTIN",
    "RGEECI_Agt01402": "KOFFI KOUAME AIME CESAR",
    "RGEECI_Agt01403": "BANON ROMARIC",
    "RGEECI_Agt01411": "YOUAN BI GOURE SEBASTIEN",
    "RGEECI_Agt01412": "GNEHO DOH PIERRE",
    "RGEECI_Agt01413": "SIDIBÉ AWA TATIANA FELICIENNE",
    "RGEECI_Agt01421": "KAMBIRE SANKABANAN MARCELIN",
    "RGEECI_Agt01422": "SOM TOHO TECHLE",
    "RGEECI_Agt01423": "COULIBALY PELEOULE JUNIOR MALICK"
}

def add_agent_name(df):
    df['Nom_Agent'] = df['Nom_Agent'].map(liste_ar)
    return df

def cooling_highlight(val):
    color = '#aaf6aa' if val else 'white'
    return f'background-color: {color}'

def convert_to_datetime(date_str):
    if date_str is None:
        return None
    if isinstance(date_str, float):
        return 
    else:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()

@st.cache_data
def get_data_from_forms(url):
    df = pd.read_csv(url,sep=';', dtype={"NumZD":'str'})
    df["Chef d'equipe"] = df["nom_CE"].map(liste_equipe)
    df["Superviseur"] = df["nom_CE"].map(liste_sup)
    df['difficultes'] = df['difficultes'].str.upper()
    df['observations'] = df['observations'].str.upper()
    df = df.rename(columns={"UEF_total":"UE formelle","UEI_total":"UE informelle","NbZD":"Nombre ZD","refus_total":"refus"})
    return df

#@st.cache_resource
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

def remove_duplicates_and_sort(zds):
    zds_list = zds.split(', ')
    zds_list_unique = sorted(list(dict.fromkeys(zds_list)))
    return ', '.join(zds_list_unique)
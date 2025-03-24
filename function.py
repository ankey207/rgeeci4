import pandas as pd
import streamlit as st
from datetime import datetime
import geopandas as gpd

liste_equipe = {
    "CE0361": "DJATO ATTA KOUAME",
    "CE0358": "KLARROU DIENOU JEAN JACQUES",
    "CE0363": "AHOSSI ALLA ENOCH BLELEDJAN",
    'CE0360':"KONE ANOKOUA RENÉ GUILLAUME",
    'CE0359':"ALLIALI LORRAINE DESIRÉE",
    'CE0362':"COULIBALY NARNOUNG AFFOUSSIATA",
    'CE0357':"IRIE BI BOTTY FIACRE-ARTHUR",
}

coords_region = {"NAWA":[5.788289, -6.594167],"GBOKLE":[4.950852, -6.089824]}
coords_superviseur = {"AMANY":[5.788289, -6.594167],"ADOU":[5.409237, -6.557446],"COULIBALY":[4.950852, -6.089824]}
coords_departement = {"BUYO":[6.248728, -7.005931],"GUEYO":[5.686322, -6.073239],"MEAGUI":[5.409237, -6.557446],"SOUBRE":[5.788289, -6.594167],"SASSANDRA":[4.950852, -6.089824],"FRESCO":[5.110777, -5.586933]}

zd_par_equipe = {
    "CE0361": 11,
    "CE0358": 10,
    "CE0363": 10
}

liste_sup={'CE0360':"SIAGOUE",
'CE0359':"SIAGOUE",
'CE0362':"SIAGOUE",
'CE0357':"SIAGOUE",
'CE0361':"AMANY",
'CE0363':"AMANY",
'CE0358':"AMANY"}

liste_ar = {
    "CE03611": "BEUGRE N’DA YAO OLIVIER",
    "CE03612": "KOUABENAN YAO ISMAEL",
    "CE03613": "N'DOLI NIAMIEN JULIANA EDWIGE",
    "CE03581": "TAH ISAAC FAHD FADDHY ALASSANE",
    "CE03582": "KOUASSI KOUADIO CYRILLE",
    "CE03583": "KOUASSI KOUASSI ROMARIC",
    "CE03631": "MAHI DAGBO DIEUDONNE",
    "CE03632": "KONE LEGNMIN AIME",
    "CE03633": "DIA AKA KOUASSI MATHIEU",
    "CE03571": "DIOMANDE BLONDE",
    "CE03572": "N'GUESSAN KHAN ARTHUR ARMAND",
    "CE03573": "DIABY MAÏMOUNA",
    "CE03591": "NGUESSAN KOFFI BOUTINOH",
    "CE03592": "OUATTARA YAYA",
    "CE03593": "Atse Anin Victoire",
    "CE03601": "ASSE ADIBO ANTOINE JUNIOR",
    "CE03602": "SILUE DOUFOUNGOGNON MARCEL WILFRIED",
    "CE03603": "OUATTARA KADI ESTHER",
    "CE03621": "DJAH AKRÉ",
    "CE03622": "TIETIE HONTO JENNIFER",
    "CE03623": "KOUASSI KOUADIO PRIVAT"
}

def add_agent_name(df):
    df['Nom_Agent'] = df['Nom_Agent'].replace(liste_ar)
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
    
def concatenate_zd_nomsp(row):
    # Assurer que la valeur de NumZD est une chaîne de caractères
    if pd.isna(row['NumZD']):
        return "0000"
    if not isinstance(row['NumZD'], str):
        zds = str(row['NumZD']).split(',')
    else:
        zds = row['NumZD'].split(',')
    
    # Filtrer les chaînes vides
    zds = [zd for zd in zds if zd != '']
    
    # Concaténer chaque ZD avec NomSp
    concatenated_values = [f"{zd}" for zd in zds]
    
    return ','.join(concatenated_values)


@st.cache_data
def get_data_from_forms(url):
    df = pd.read_csv(url,sep=';', dtype={"NumZD":'str'})
    df["Chef d'equipe"] = df["nom_CE"].map(liste_equipe)
    df["ZD_affectees"] = df["nom_CE"].map(zd_par_equipe)
    df['difficultes'] = df['difficultes'].str.upper()
    df['observations'] = df['observations'].str.upper()
    df = df.rename(columns={"UEF_total":"UE F","UEI_total":"UE I","refus_total":"refus","partiels_total":"partiels"})
    df["date_2"] =pd.to_datetime(df["date_reporting"])
    df["NumZD"] = df.apply(concatenate_zd_nomsp, axis=1)
    df["Superviseur"] = df["nom_CE"].map(liste_sup)


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
        row_index = df.index.get_loc(row.name)  # Obtenir la position de la ligne
        
        if row_index % 2 == 0:
            return ['background-color: #ebecf0'] * len(row)
        else:
            return ['background-color: #f9fafd'] * len(row)

    styled_df.apply(row_style, axis=1)

    return styled_df

def concat_list_zd(series):
    # Utiliser un ensemble pour éliminer les doublons et conserver l'unicité
    unique_elements = set(series.astype(str))
    unique_elements = set(unique_elements)
    # Convertir l'ensemble en liste pour assurer l'ordre si nécessaire
    unique_list = list(unique_elements)
    # Concaténer les valeurs uniques en une seule chaîne de caractères
    return ','.join(unique_list)

def delete_doublon_and_sort_from_list_zd(input_string):
    # Séparer la chaîne en une liste d'éléments
    elements = input_string.split(',')
    
    # Utiliser un ensemble pour éliminer les doublons et filtrer les éléments indésirables
    unique_elements = {element for element in elements if "0000" not in str(element) and element.lower() != "nan"}
    
    # Convertir l'ensemble en liste et trier les éléments
    sorted_elements = sorted(unique_elements)
    
    # Joindre les éléments triés en une seule chaîne
    result = ','.join(sorted_elements)
    
    return result

def count_unique_zd(input_string):
    # Séparer la chaîne en une liste d'éléments
    elements = input_string.split(',')    
    # Retourner le nombre d'éléments uniques
    return len(elements)

def statut_zd(zd,liste_zd):
    if zd in liste_zd:
        return "Traité"
    else:
        return "Non traité"



@st.cache_data
def get_data_attribution_eq(xpath):
    return pd.read_csv(xpath, sep=';')

@st.cache_data
def get_data_attribution_eq_xlsx(xpath):
    return pd.read_excel(xpath)

zd_departement = {
    "BUYO": 74,
    "GUEYO": 39,
    "MEAGUI": 165,
    "SOUBRE": 306,
    "FRESCO": 35,
    "SASSANDRA": 85
}

zd_sous_prefecture = {
    "BUYO": 53,
    "DABOUYO": 18,
    "DAPEOUA": 21,
    "GNAMANGUI": 19,
    "GRAND-ZATTRY": 36,
    "GUEYO": 21,
    "LILIYO": 36,
    "MEAGUI": 110,
    "OKROUYO": 11,
    "OUPOYO": 32,
    "SOUBRE": 223,
    "DAHIRI": 5,
    "DAKPADOU": 12,
    "FRESCO": 21,
    "GBAGBAM": 9,
    "GRIHIRI": 9,
    "LOBAKUYA": 4,
    "MEDON": 6,
    "SAGO": 12,
    "SASSANDRA": 42
}

zd_region = {
    "NAWA": 584,
    "GBOKLE": 120
}

zd_sup = {
    "AMANY": 345,
    "ADOU": 239,
    "COULIBALY": 120
}

soubre_list = [
    "SOUBRE 0038",
    "SOUBRE 0049",
    "SOUBRE 0050",
    "SOUBRE 0080",
    "SOUBRE 0101",
    "SOUBRE 0081",
    "SOUBRE 0086",
    "SOUBRE 0074",
    "SOUBRE 0090",
    "SOUBRE 0091",
    "SOUBRE 0130",
    "SOUBRE 0120",
    "SOUBRE 0104",
    "SOUBRE 0105",
    "SOUBRE 0106",
    "SOUBRE 0118",
    "SOUBRE 0119",
    "SOUBRE 0110",
    "SOUBRE 0062",
    "SOUBRE 0077"
]


@st.cache_data
def load_geozd(xpath):
    geo_df = gpd.read_file(xpath,dtype={'NUM_ZD_NEW':'str'})
    geo_df["NumZD"] = geo_df["NomSp"] +" "+geo_df["NUM_ZD_NEW"]
    #geo_df = geo_df[geo_df["NumZD"].isin(soubre_list)]
    #geo_df = geo_df.set_index("CONTOUR")
    return geo_df
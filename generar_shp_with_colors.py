import pandas as pd
import numpy as np
import geopandas as gpd

# solamente para leer shp creado by crear_eje_carretera_by_pk
nombre_carretera ="AP-41"
sentidopk = 2
distance_delta = 5

path_zonas = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\ZONA_HOMOGENEA_UNE_41250_4.xlsx" 
path_tramos =  nombre_carretera+'_sentido_'+str(int(sentidopk))+'_tramificada_'+str(int(distance_delta))+'m.shp'



""" INPUT """
codigo_carretera= "01AP4111"
PK_HIT_INI = 11
PK_HIT_FIN = 47
id_tramo =  4

df_zonas = pd.read_excel(path_zonas)
df_zonas_tramo = df_zonas[( df_zonas.idtramo == id_tramo) &(df_zonas.PKIHito >=PK_HIT_INI) &(df_zonas.PKIHito <PK_HIT_FIN)]


# establecer los limites entre grupos
limites = df_zonas_tramo.DFK.quantile([.25, .75])


limite1 = limites.iloc[0]
limite2 = limites.iloc[1]

# GRUPO 1
df_zonas_tramo.loc[df_zonas_tramo["DFK"] <= limite1, 'color'] = 'verde'

# GRUPO 2
df_zonas_tramo.loc[(df_zonas_tramo["DFK"] >limite1 ) & (df_zonas_tramo["DFK"] <= limite2 ) , 'color'] = 'amarillo'

# GRUPO 3
df_zonas_tramo.loc[df_zonas_tramo["DFK"] > limite2, 'color'] = 'rojo'


df_zonas_tramo.sort_values(by=["PKIHito","PKIDist"])
df_zonas_tramo["PKI"] = df_zonas_tramo["PKIHito"] *1000 +df_zonas_tramo["PKIDist"] 



# PASO 1. Cargar datos del shp al df
df_tramos= gpd.read_file(path_tramos)
df_tramos["PKI"] = df_tramos["PK_HITO_IN"] *1000 +df_tramos["PK_DIST_IN"] 


merged_df = pd.merge(
    df_tramos,
    df_zonas_tramo,
    how="left",
    on="PKI",
    left_index=False,
    right_index=False,
    sort=True,
    suffixes=("_x", "_y"),
    copy=True,
    indicator=False,
    validate=None,
)


merged_df[["PKI","color","DFK"]] = merged_df[["PKI","color","DFK"]].ffill()

merged_df = merged_df.rename(columns={"C_Variación": "C_Variacion"})

merged_df.to_file(codigo_carretera+"_sentido_"+str(int(sentidopk))+"_tramificada.shp")

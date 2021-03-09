import pandas as pd
import numpy as np
import geopandas as gpd
import tramificacion

# solamente para leer shp creado by crear_eje_carretera_by_pk


""" INPUT """
PK_HIT_INI = 11
PK_HIT_FIN = 47

nombre_carretera ="AP-41"
sentidopk = 2
distance_delta = 5

path_tramos= r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-tramo.xlsx"
path_carreteras = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-Carretera.xlsx"
path_zonas = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\ZONA_HOMOGENEA_UNE_41250_4.xlsx" 
path_tramos_shp =  nombre_carretera+'_sentido_'+str(int(sentidopk))+'_tramificada_'+str(int(distance_delta))+'m.shp'



# read data to dataframe
df_carreteras= pd.read_excel(path_carreteras)
df_tramos = pd.read_excel(path_tramos)
df_zonas = pd.read_excel(path_zonas)

# get id of carretera with specific name
IdCarretera = tramificacion.get_id_carretera(nombre_carretera,df_carreteras)

# get id of tramo based on IdCarretera y SentidoPK (1-creciente, 2 -decresciente) 
id_tramo =  tramificacion.get_id_tramo(IdCarretera,sentidopk,df_tramos)

# seleccionar df del tramo de estudio
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


#  Cargar datos del shp al df
df_tramos_shp= gpd.read_file(path_tramos_shp)
df_tramos_shp["PKI"] = df_tramos_shp["PK_HITO_IN"] *1000 +df_tramos_shp["PK_DIST_IN"] 

# merge data from SHP and Visor Multiparametrico
merged_df = pd.merge(df_tramos_shp,df_zonas_tramo,how="left",on="PKI")

# cada tramos asociar a un color en funcion del valor DFK
merged_df[["PKI","color","DFK"]] = merged_df[["PKI","color","DFK"]].ffill()

# renombrar la columna con acento español a uno sin acento
merged_df = merged_df.rename(columns={"C_Variación": "C_Variacion"})

# guardar el archivo a un nuevo shp
merged_df.to_file(nombre_carretera+"_sentido_"+str(int(sentidopk))+"_tramificada_por_dfk.shp")

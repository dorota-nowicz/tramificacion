#!/usr/bin/python
# -*- coding: latin-1 -*-
import os 
import crear_eje_carretera_by_pk
import generar_shp_with_colors
import shp_2_cad
import pandas as pd

# turn off warning : "A value is trying to be set on a copy of a slice from a DataFrame. Try using .loc[row_indexer,col_indexer] = value instead"
pd.options.mode.chained_assignment = None  # default='warn'

""" INPUT 

NOMBRE_CARRETERA: nombre de la carretera el cual debe aparecer dentro de la columna "nombre" de la capa  definida en la variable PATH_CARRETERA
SENTIDO_PK: 1 significa el tramo con los PK crecientes, 2 significa el tramo con los PK decrecientes según la columna sentido de la capa definida en la variable PATH_CARRETERA
PK_HIT_INI: el kilometraje del inicio de la carretera ( cada 1000 m) pe. si nesesitamos desde PK 11+300  PK_HIT_INI= "11"
PK_HIT_FIN: el kilometraje del final de la carretera ( cada 1000 m) pe. si nesesitamos hast PK 11+300  PK_HIT_FIN= "12"
TIPO_TRAMD: tipo de tramo para sacar la eje de la carretera. Debe coincidir con un tipo enumerado dentro de la columna tipo_tramD" de la capa definida en la variable PATH_CARRETERA
PATH_CARRETERA: la ruta hacia shp con la carreteras ( polilineas) la cual se puede descargar desde la siguiente pagina web http://centrodedescargas.cnig.es/CentroDescargas/buscar.do?filtro.codFamilia=REDTR#
PATH_PK: la ruta hacia shp con los PKs de las carreteras ( pùntos) la cual se puede descargar desde la siguiente pagina web http://centrodedescargas.cnig.es/CentroDescargas/buscar.do?filtro.codFamilia=REDTR#
BUFFER: el buffer en metros para insertar los puntos de PK dentro de la eje de carretera. No siempre los PK insertan la eje
EPSG_INPUT: Sistema de referencia de la capa del input (PATH_CARRETERA,PATH_PK ). En 10/03/2021 ha sido EPSG:4326 (coordenadas en grados)
EPSG_OUTPUT: Sistema de referencia de la capa del output para hacer los planos. EPSG:25830 ETRS_1989_UTM_Zone30N (coordenadas en metros)
LONG_TRAMO: Longitud de tramo para tramificar por defecto damos 5 metros
PATH_TRAMO_XLSX : ruta del archivo de Excel exportado de MsAccess del Visor Multiparametro (La tabla se llama A-tramo)
PATH_CARRETERA_XLSX:  ruta del archivo de Excel exportado de MsAccess del Visor Multiparametro (La tabla se llama A-Carretera)
PATH_ZONA_HOMOGENEA_XLSX:  ruta del archivo de Excel exportado de MsAccess del Visor Multiparametro (La tabla se llama A-ZONA_HOMOGENEA_UNE_41250_4)
PATH_DXF: ruta del archivo de cad (*dxf, *dwg) donde ceremos dibujar la eje con los PK (no es obligatorio)
NOMBRE_BLOCK_PK100: nombre del bloque para el PK100 si no existe en el archivo definido en PATH_DXF se generará uno por defecto
NOMBRE_BLOCK_PK20: nombre del bloque para el PK20 si no existe en el archivo definido en PATH_DXF se generará uno por defecto
NOMBRE_CAPA_EJE: nombre de la capa para los bloques NOMBRE_BLOCK_PK100 y NOMBRE_BLOCK_PK20 si no existe en el archivo definido en PATH_DXF se generará uno por defecto
NUEVO_ARCHIVO: si queremos dibujar la eje con los PK en un nuevo archivo "1", si ya tenemos un archivo "0". Si seleccionamos "0", es muy importante definir la variable PATH_DXF

"""
os.environ["CIUDAD"] = "Toledo"
os.environ["NOMBRE_CARRETERA"] = "AP-41"
os.environ["SENTIDO_PK"] = "2" #  1- PK crecientes, 2 -PK decrecientes HANDEL WHEN IT IS DIFF THAN 1 and 2
os.environ["PK_HIT_INI"] = "10" # HANDEL ERROR WHEN PK IS NOT IN THE SHAPE !!!!!!
os.environ["PK_HIT_FIN"] = "48" # HANDEL ERROR WHEN PK IS NOT IN THE SHAPE !!!!!!
os.environ["TIPO_TRAMD"] = "Troncal"
os.environ["PATH_CARRETERA"] = "C:/PROYECTOS/ESP_P_SEITT FIRMES AP-41 A-40 TO-22/GIS/CAPAS/SHP/ejeCarretera/RT_"+os.environ["CIUDAD"]+"/RT_VIARIA/rt_tramo_vial.shp"
os.environ["PATH_PK"] = "C:/PROYECTOS/ESP_P_SEITT FIRMES AP-41 A-40 TO-22/GIS/CAPAS/SHP/ejeCarretera/RT_"+os.environ["CIUDAD"]+"/RT_VIARIA/rt_portalpk_p.shp"
os.environ["BUFFER"] = "0.01" # en metros
os.environ["EPSG_INPUT"] = "EPSG:4326"
os.environ["EPSG_OUTPUT"] = "EPSG:25830"
os.environ["LONG_TRAMO"] = "5"
os.environ["PATH_TRAMO_XLSX"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-tramo.xlsx"
os.environ["PATH_CARRETERA_XLSX"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-Carretera.xlsx"
os.environ["PATH_ZONA_HOMOGENEA_XLSX"] =  r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\ZONA_HOMOGENEA_UNE_41250_4.xlsx" 
os.environ["PATH_DXF"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\PYTHON\test.dxf" 
os.environ["NOMBRE_BLOCK_PK100_1"] = "pk100_1"  # PARA SENTIDO 1
os.environ["NOMBRE_BLOCK_PK100_2"] = "pk100_2"  # PARA SENTIDO 2
os.environ["NOMBRE_BLOCK_PK20"] = "pk20" 
os.environ["NOMBRE_CAPA_EJE"] = "eje" 
os.environ["NUEVO_ARCHIVO"] = "0" # 1- creamos nuevo archivo, 0 - usamos archivo definido en PATH_DXF


# comenta los scripts los cuales no quieres usar
if __name__ == '__main__':

    print("START")


    # 1. crear_eje_carretera_by_pk.py
    print()
    print("INICIO DE LA GENERACIÓN DE LA EJE DE LA CARRETERA. Este proceso puede tardar unos minutos en función del tamaño del dataset con los polilineas de ejes de carreteras y los pk de los mismos.")
    crear_eje_carretera_by_pk.run_script()

    # 2. generar_shp_with_colors.py
    print()
    print("INICIO DE LA CORRECCIÓN DEL SHP (RELLENAR CADA TRAMO CON UN COLOR PREDEFINIDO) " )
    generar_shp_with_colors.run_script()

    # 3. shp_2_cad.py
    print()
    print("INICIO DE LA CONVERSIÓN DEL SHP AL ARCHIVO DXF INCLUYENDO LOS PKS")
    shp_2_cad.run_script()

    print("THE END")



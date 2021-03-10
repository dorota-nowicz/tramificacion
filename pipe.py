#!/usr/bin/python
# -*- coding: latin-1 -*-
import os 
import subprocess
import crear_eje_carretera_by_pk
import generar_shp_with_colors
import shp_2_cad

""" INPUT 
NOMBRE_CARRETERA: nombre de la carretera el cual debe aparecer dentro de la columna "nombre" de la capa  definida en la variable PATH_CARRETERA
TIPO_TRAMD: tipo de tramo para sacar la eje de la carretera. Debe coincidir con un tipo enumerado dentro de la columna tipo_tramD" de la capa definida en la variable PATH_CARRETERA
PATH_CARRETERA: la ruta hacia shp con la carreteras ( polilineas) la cual se puede descargar desde la siguiente pagina web http://centrodedescargas.cnig.es/CentroDescargas/buscar.do?filtro.codFamilia=REDTR#
PATH_PK: la ruta hacia shp con los PKs de las carreteras ( pùntos) la cual se puede descargar desde la siguiente pagina web http://centrodedescargas.cnig.es/CentroDescargas/buscar.do?filtro.codFamilia=REDTR#
SENTIDO_PK: 1 significa el tramo con los PK crecientes, 2 significa el tramo con los PK decrecientes según la columna sentido de la capa definida en la variable PATH_CARRETERA
PK_HIT_INI: el kilometraje del inicio de la carretera ( cada 1000 m) pe. si nesesitamos desde PK 11+300  PK_HIT_INI= "11"
PK_HIT_FIN: el kilometraje del final de la carretera ( cada 1000 m) pe. si nesesitamos hast PK 11+300  PK_HIT_FIN= "12"
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


os.environ["NOMBRE_CARRETERA"] = "AP-41"
os.environ["TIPO_TRAMD"] ="Troncal"
os.environ["PATH_CARRETERA"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\GIS\CAPAS\SHP\ejeCarretera\RT_TOLEDO\RT_VIARIA\rt_tramo_vial.shp"
os.environ["PATH_PK"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\GIS\CAPAS\SHP\ejeCarretera\RT_TOLEDO\RT_VIARIA\rt_portalpk_p.shp"
os.environ["SENTIDO_PK"] = "2" 
os.environ["PK_HIT_INI"] = "11"
os.environ["PK_HIT_FIN"] = "47"
os.environ["BUFFER"] = "0.0001"
os.environ["EPSG_INPUT"] = "EPSG:4326"
os.environ["EPSG_OUTPUT"] = "EPSG:25830"
os.environ["LONG_TRAMO"] = "5"

os.environ["PATH_TRAMO_XLSX"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-tramo.xlsx"
os.environ["PATH_CARRETERA_XLSX"] = r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\A-Carretera.xlsx"
os.environ["PATH_ZONA_HOMOGENEA_XLSX"] =  r"C:\PROYECTOS\ESP_P_SEITT FIRMES AP-41 A-40 TO-22\DATOS_CARRETERA\xlsx_MadridToledo\ZONA_HOMOGENEA_UNE_41250_4.xlsx" 
os.environ["PATH_DXF"] = "" 
os.environ["NOMBRE_BLOCK_PK100"] = "pk100" 
os.environ["NOMBRE_BLOCK_PK20"] = "pk20" 
os.environ["NOMBRE_CAPA_EJE"] = "eje" 

os.environ["NUEVO_ARCHIVO"] ="1"

if __name__ == '__main__':

    # 1. crear_eje_carretera_by_pk.py
    crear_eje_carretera_by_pk.run_script()

    # 2. generar_shp_with_colors.py
    generar_shp_with_colors.run_script()

    # 3. shp_2_cad.py
    shp_2_cad.run_script()



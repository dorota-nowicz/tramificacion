#!/usr/bin/python
# -*- coding: latin-1 -*-
import numpy as np
import geopandas as gpd
import pandas as pd
import re
from shapely.ops import linemerge, unary_union, split,snap

from osgeo import ogr
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, MultiLineString, LineString, MultiPoint, Point
from shapely.wkt import loads, dumps


def generate_df_tramo(pk, splitted_line):

    PK_HITO_ALL = []
    PK_DIST_ALL = []

    pk_hito = [pk for i in range(len(splitted_line))]
    pk_dist = [i*5 for i in range(len(splitted_line))]

    df_tramo = pd.DataFrame(list(zip(pk_hito, pk_dist)),columns= ["PK_HITO_INI","PK_DIST_INI"])

    return df_tramo


def generate_gdf_tramo(crs,splitted_line,df_tramo):
    
    geometry = [l for l in splitted_line] 
    gdf = gpd.GeoDataFrame(df_tramo, crs=crs, geometry = geometry)
    return gdf


def get_pk_by_line(line,distance_delta):
    distances = np.arange(0, line.length, distance_delta)
    points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]
    multipoint = unary_union(points)   
    return multipoint

def get_road_from_PK(line,PK):
    segements = split(line,PK)
    length_segments = [i.length for i in segements]
    index_max= np.argmax(length_segments)
    line = segements[index_max]
    return line

def filtr_road(df_carreteras, nombre_carretera,tipo_tramD):
    # coger datos de la carretera con un nombre concreto y tipo_TramD concreto
    df_carretera = df_carreteras[(df_carreteras.nombre == nombre_carretera) &
                                 (df_carreteras.tipo_tramD ==tipo_tramD)]
    return df_carretera

def join_touching_lines(df_carretera):
    #conectar las lineas (tramos de carretera) seleccionadas en una eje
    list_geom = df_carretera['geometry'].tolist()
    inlines = MultiLineString( [ i for i in list_geom] )
    multiline = linemerge(inlines)
    
    return multiline

def generate_points_on_line(distance_delta,multiline):
    #cada X distancia ( en grados!) crear un PK
    line_length = multiline.length
    distances = np.arange(0, multiline.length, distance_delta)
    points = [line.interpolate(distance) for distance in distances] + [multiline.boundary[1]]
    multipoint = unary_union(points)  # or new_line = LineString(points)
    return multipoint

def correct_road_by_PK(PK, line, buffer):
    ### Create a buffer polygon around the interpolated point
    buff = PK.buffer(buffer) # 

    ### Split the line on the buffer
    if len(split(line,buff)) == 3:
        first_seg, buff_seg, last_seg = split(line,buff)

        ### Stitch together the first segment, the interpolated point, and the last segment 
        line = LineString(list(first_seg.coords) + list(PK.coords) + list(last_seg.coords))

    return line

def tranform_geom(geom,epsg_input,epsg_output):
    # TRANSFORM from degrees (4326) to m in projection  (25830) ETRS_1989_utm_ZONE_30N
    from pyproj import Proj, Transformer
    import shapely.ops as sp_ops
    my_transformer = Transformer.from_crs(epsg_input,epsg_output, always_xy=True)
    geom_transformed = sp_ops.transform(my_transformer.transform, geom)
    return geom_transformed

def find_the_closest_line(point, lines):
    # get the closest line to point
    distances = [point.distance(line) for line in lines]
    min_dist = min(distances)
    min_index = distances.index(min_dist)
    # line of interest: 
    line = lines[min_index]
    return line




def get_id_carretera(Codigo,df_carreteras):
    """
    descrp:
    devuelve el id de la carretera según de los datos del Visor Multiparametro de la carretera basando en su codigo
    
    input: 
    Codigo -  codigo de la carretera pe AP-41,debe estar dentro de la carretera!
    df_carreteras - tabla  A-Carretera  de Visor Multiparametro
    
    output: 
    sentido - 1 creciente;  2 decreciente formato int
    """
    df_carretera = df_carreteras[df_carreteras['Codigo'] == Codigo ]
    if df_carretera.empty:
        idCarretera = None
    else:
        idCarretera = df_carretera.iloc[0]['IdCarretera']
    
    return idCarretera

def check_sentido(PK_INI,PK_FIN):
    """
    descrp:
    devuelve el sentido de la carretera basando en sus pk ( pk inicial y pk final)
    
    input: 
    PK_INI -  pk inicial del tramo de la carretera formato int pe. 15100 (PK15+100)
    PK_FIN - pk final del tramo de la carretera formato int pe. 15100 (PK15+100)
    
    output:
    sentido - 1 creciente;  2 decreciente formato int
    """
    if PK_INI-PK_FIN < 0:
        sentido =  1
    elif PK_INI-PK_FIN > 0:
        sentido = 2
        
    return sentido
        

def get_id_tramo(IdCarretera,sentido,df_tramos):
    """
    input: 
    idCarretera -  id correspondiente al id de la carretera la tabla A-Carretera
    sentido - 1 creciente;  2 decreciente
    
    output:
    idTramo - id del tramo correspondiente al tramo en deflexiones y las zonas homogeneas
    """
    df_tramos_de_carretera = df_tramos[df_tramos["IdCarretera"] == IdCarretera]
    df_tramos_de_carretera["PK_INI"] = df_tramos_de_carretera.apply(lambda row: row["PKIHito"]*1000 + row["PKIDist"],axis=1)
    df_tramos_de_carretera["PK_FIN"] = df_tramos_de_carretera.apply(lambda row: row["PKFHito"]*1000 + row["PKFDist"],axis=1)
    
    df_tramos_de_carretera["Sentido"] =df_tramos_de_carretera.apply(lambda row: check_sentido(row["PK_INI"],row["PK_FIN"]),axis=1)
    
    df_tramo= df_tramos_de_carretera[df_tramos_de_carretera['Sentido'] == sentido ]
    if df_tramo.empty:
        IdTramo = None
    else:
        IdTramo = df_tramo.iloc[0]['IdTramo']
        
    
    return IdTramo


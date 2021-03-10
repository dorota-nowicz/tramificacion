import win32com.client
import ezdxf # https://anaconda.org/conda-forge/ezdxf
import os
import geopandas as gpd
import numpy as np
import math 

def prepare_PK_DIST_IN(PK_DIST_IN):
    """
    Esta funcion prepara formato de los metros de pk.
    Pe., cuando tenemos un pk 1+000 el PK_DIST_IN es igual a 0 y lo cambiamos a 000
    
    input: PK_DIST_IN metros del PK en formato int
    
    output: PK_DIST_IN en formato string con una longitud minima de 3 caracteres
    """
    len_PK_DIST_IN = len(str(PK_DIST_IN))
    if len_PK_DIST_IN == 1:
        PK_DIST_IN = "00"+str(PK_DIST_IN)
    elif len_PK_DIST_IN == 2:
        PK_DIST_IN = "0"+str(PK_DIST_IN)
        
    return str(PK_DIST_IN)

def create_new_block_pk100(dxf,block_name):
    """
    Esta funcion crea un blocke en autocad  con una linia y el atributo de texto llamado "PK"
    
    input: block_name (str) - nombre del blocke en cad 
    
    output: pk100 - blocke de cad
    """
    pk100 = dxf.blocks.new(name=block_name)
    pk100.add_lwpolyline([( -1.5,0), (8,0)])  # the pk100 symbol as 2D line
    pk100.add_attdef('PK', (8.5, -2.5), dxfattribs={'height': 5, 'color': 5})
    return  pk100


def prepare_df_for_block_pk(df_tramos_shp,intervalo):
    """
    Esta funcion prepara dataframe para insertar al archivo de dxf un block PK cada intervalo con una rotación adecuada 
    la cual genera y guarda en el campo "rotacion"
    
    input: df_tramos_shp ( geodataframe del shp creado por el script generar_shp_with_colors)
    intervalo: intervalo entre PK en metros
    
    output: df_tramos_shp_intervalo 
    """
    # 1. vector base con la direccion de eje X para calcular la rotacion de los tramos de carretera ( clockwise)
    vector_base = [0, 1]
    
    # 2. select pks every intervalo m
    df_tramos_shp_intervalo = df_tramos_shp[df_tramos_shp["PKI"]%intervalo== 0]

    # 3. get pk coordinate ( first point of line)
    df_tramos_shp_intervalo["pk_geom"] = df_tramos_shp_intervalo.geometry.apply(  lambda row: extract_first_poit(row) )

    # 4. Get vector of all segments
    df_tramos_shp_intervalo["vector"] = df_tramos_shp_intervalo.apply(  lambda row: find_vector(row) , axis=1)

    # 5. calculate angle between v0 [1, 0] and  v1[putno_tramo1,punto_tramo[-1]]
    df_tramos_shp_intervalo["rotation"] = df_tramos_shp_intervalo.apply(  lambda row: angle_between_two_vectors(vector_base, row.vector) , axis=1)
    
    return df_tramos_shp_intervalo


def create_new_block_pk20(dxf,block_name):
    """
    Esta funcion crea un blocke en autocad  con una linia
    
    input: block_name (str) - nombre del blocke en cad 
    
    output: pk20 - blocke de cad
    """
    pk20 = dxf.blocks.new(name=block_name)
    pk20.add_lwpolyline([( -2,0),(2,0)])  # the pk20 symbol as 2D line
    
    return pk20

def create_layer(dxf, layer_name, id_color):
    """
    Esta funcion crea una capa en autocad  con una nombre layer_name y color  id_color
    
    input: 
    layer_name (str) - nombre de la capa
    id_color (int) - id del color segun AutoCad   # https://gohtx.com/acadcolors.php green 3, yellow 2, red 1
    
    output: en el archivo dxf creamos la capa nueva
    """
    g1_layer = dxf.layers.new(layer_name)
    g1_layer.color = id_color
    return 


def add_tramos_by_group(layer_name,color,df_tramos_shp,msp):
    """
    Esta funcion añade los tramos del data_frame (df_tramos_shp) a la  capa en autocad (layer_name) 
    Es decir, tramo de un color concreto corresponde a una capa de cad
    
    input: 
    layer_name (str) - nombre de la capa en el archivo dxf
    color (str) - nombre de color que coincide con los valores dentro de df_tramos_shp["color"]
    df_tramos_shp (gdf) - dataframe con los tramos de interes. Debe poseer la columna "color"
    msp  (modelspace) - modelspace del dxf   # https://gohtx.com/acadcolors.php green 3, yellow 2, red 1
    
    output: msp actualizado con los tramos de un grupo agregados
    """
    
    # get tramos de tramos de un  grupo predefinido
    df_grupo = df_tramos_shp[df_tramos_shp["color"] == color]

    # add every polyline of road into msp
    for index, row in df_grupo.iterrows():
        linestring = row.geometry
        x, y = linestring.coords.xy
        points = [ i for i in zip(x,y)]
        msp.add_lwpolyline(points, dxfattribs={'layer': layer_name})
        
    return msp

def find_vector(row):
    """
    Esta funcion extrae el vector de una polilinea 
    
    input: 
    row (pandas df row) - fila del df con la geometría de una polilinea
    
    output:
    vector(lista) : vector [x1, x2]
    """
    
    x_line,y_line = row.geometry.coords.xy
    vector = [x_line[-1] - x_line[0], y_line[-1] - y_line[0]]
    return vector


def extract_first_poit(linestring):
    """
    Esta funcion extrae el primer punto de una polilinea
    
    input: 
    linestring (shapely linestring) 
    
    output:
    point  : coordenadas del punto en formato (x1, x2)
    """
    x,y = linestring.coords.xy
    point= (x[0],y[0])
    return point
    
def angle_between_two_vectors(vector_1, vector_2):
    """
    Esta funcion calcula el angulo entre dos vectores ( clockwise)
    
    input: 
    vector_1 (lista)-  lista con dos numeros que marcan el vactor [x, y]
    vector_2 (lista)-  lista con dos numeros que marcan el vactor [x, y]
    
    output:
    angle (int)  : angulo en grados
    
    """
    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)

    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    
    x2,y2 =unit_vector_2
    x1, y1 =unit_vector_1

    radians=math.atan2(x1*y2 - y1*x2, x1*x2+y1*y2)

    angle = math.degrees(radians)

    return angle


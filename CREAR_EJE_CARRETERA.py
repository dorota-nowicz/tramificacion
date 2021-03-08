import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.ops import linemerge, unary_union, split


from osgeo import ogr
import fiona
from fiona.crs import from_epsg
from shapely.geometry import mapping, MultiLineString, LineString, MultiPoint
from shapely.wkt import loads



def get_pk_by_line(line,distance_delta):
    distances = np.arange(0, line.length, distance_delta)
    points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]
    multipoint = unary_union(points)   
    return multipoint


def correct_road_by_PK(PK, line):
    ### Create a buffer polygon around the interpolated point
    buff = PK.buffer(0.0001)

    ### Split the line on the buffer
    if len(split(line,buff)) == 3:
        first_seg, buff_seg, last_seg = split(line,buff)

        ### Stitch together the first segment, the interpolated point, and the last segment 
        line = LineString(list(first_seg.coords) + list(PK.coords) + list(last_seg.coords))

    return line
    
def get_road_from_PK(line,PK):
    segements = split(line,PK)
    length_segments = [i.length for i in segements]
    index_max= np.argmax(length_segments)
    line = segements[index_max]
    return line
    
def correct_road_by_PK(PK, line):
    ### Create a buffer polygon around the interpolated point
    buff = PK.buffer(0.0001)

    ### Split the line on the buffer
    if len(split(line,buff)) == 3:
        first_seg, buff_seg, last_seg = split(line,buff)

        ### Stitch together the first segment, the interpolated point, and the last segment 
        line = LineString(list(first_seg.coords) + list(PK.coords) + list(last_seg.coords))

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


""" INPUT """
nombre_carretera ="AP-41"
tipo_tramD = "Troncal"
path_carretera =  r"..\GIS\CAPAS\SHP\ejeCarretera\RT_TOLEDO\RT_VIARIA\rt_tramo_vial.shp"
path_pk=  r"..\GIS\CAPAS\SHP\ejeCarretera\RT_TOLEDO\RT_VIARIA\rt_portalpk_p.shp"
sentidopk = 1

# guardar capas to shp
crs = 'GEOGCS["WGS 89",DATUM["WGS_1989",' \
       'SPHEROID["WGS 89",6378137,298.257223563,' \
       'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],' \
       'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],' \
       'UNIT["degree",0.01745329251994328,' \
       'AUTHORITY["EPSG","9122"]],' \
       'AUTHORITY["EPSG","4326"]]'     # Works


# PASO 1. Cargar datos del shp al df
df_carreteras = gpd.read_file(path_carretera)
df_pk = gpd.read_file(path_pk)
df_carretera = filtr_road(df_carreteras,nombre_carretera,tipo_tramD)




# los tramos de carretera en orden del PK 
df_pk_carretera = df_pk[df_pk['id_tramo'].isin(df_carretera.id_tramo)].sort_values(by=["sentidopk","numero"])
# limpiar los PK ( no existe sentido -998)
df_pk_carretera = df_pk_carretera[df_pk_carretera['sentidopk']!=-998].drop_duplicates(subset=['id_tramo'], keep='first')

# sleccionar calzada para 1 setnido de PK
tramos_calzada = df_pk_carretera[df_pk_carretera["sentidopk"] == sentidopk]["id_tramo"] 
df_calzada = df_carretera[df_carretera.id_tramo.isin(tramos_calzada)]


# join carretera with PK
df_carretera_and_pk = pd.merge(df_pk_carretera,
         df_calzada, 
         left_on ='id_tramo',
         right_on= 'id_tramo',
         how="inner").sort_values(by="numero")


# merge touching line on road. ( di tienes dos calzadas, te saldrán dos lineas)
multiline = join_touching_lines(df_carretera)




# ENCONTRAR PK INICIO Y PK FIN PARA CORTAR LA EJE ENTRE ESOS DOS PUNTOS
pk_ini_row = df_carretera_and_pk[["numero", "geometry_x"]].iloc[0]
pk_fin_row = df_carretera_and_pk[["numero", "geometry_x"]].iloc[-1]

PK_INI = pk_ini_row.numero
PK_FIN = pk_fin_row.numero

PK_INI_geom = pk_ini_row.geometry_x
PK_FIN_geom = pk_fin_row.geometry_x




""" ASEGURARNOS QUE EL PK ESTÁ EN LA CARRETERA PARA PODER CORTARLA EN ESOS PK"""

lines =[ i for i in multiline]
line = lines[0]

for PK in [PK_INI_geom,PK_FIN_geom]:
    correct_road_by_PK(PK, line)
    
""" CORTAR LA CARRETERA ENTRE DOS PK"""

line = get_road_from_PK(line,PK_INI_geom)

line = get_road_from_PK(line,PK_FIN_geom)


""" TRAMIFICAR LA CARRETERA EN CADA KM EN tramos de 5 m """
# correct line para poder split line at every PK
df_pk_carretera = df_pk[df_pk['id_tramo'].isin(df_carretera.id_tramo)].sort_values(by=["sentidopk","numero"])

for index, row in df_pk_carretera.iterrows():
    line = correct_road_by_PK(row.geometry,line)
    
points = MultiPoint(df_pk_carretera.geometry.tolist()) 
splitted = split(line, points) 
 
 
print(" Nº de tramos %s " % len(splitted))


distance_delta =  5/111000 *1.25944584382#  5 m --> 5/111000 degree ????????????????????????
collections= []
for segment in splitted:
    collections.append(get_pk_by_line(segment,distance_delta))
    
   



""" GUARDAR EJES DE CARRETERAS AL SHP """

lines =splitted
#creation of the resulting shapefile
schema_line = {'geometry': 'LineString','properties': {'id': 'int'},}
with fiona.open(nombre_carretera+'_tramificada.shp', 'w', 'ESRI Shapefile', schema_line, crs)  as output:
    for i, line in enumerate(lines):
        output.write({'geometry':mapping(line),'properties': {'id':i}})
        
        
    
""" GUARDAR PKS DE CARRETERAS AL SHP """
    
points = [point for collection in collections for point in collection]
#creation of the resulting shapefile
schema_point = {'geometry': 'Point','properties': {'id': 'int'},}
with fiona.open(nombre_carretera+'_pk.shp', 'w', 'ESRI Shapefile', schema_point, crs)  as output:
    for i, point in enumerate(points):
        output.write({'geometry':mapping(point),'properties': {'id':i}})
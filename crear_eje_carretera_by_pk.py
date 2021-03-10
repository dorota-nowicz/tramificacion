""" IMPORTAR MODULOS """
from tramificacion import *
import geopandas as gpd
import time
import os



def run_script():
    """ INPUT """
    nombre_carretera = os.environ["NOMBRE_CARRETERA"]
    tipo_tramD = os.environ["TIPO_TRAMD"]  # el tipo de la capa rt_tramo_vial. Mejor no cambiarlo
    path_carretera = os.environ["PATH_CARRETERA"] 
    path_pk=  os.environ["PATH_PK"]
    sentidopk = int(os.environ["SENTIDO_PK"] )
    pk_hit_ini_input = int(os.environ["PK_HIT_INI"])
    pk_hit_fin_intput = int(os.environ["PK_HIT_FIN"])
    buffer = float(os.environ["BUFFER"]) # m
    epsg_input = os.environ["EPSG_INPUT"] 
    epsg_output = os.environ["EPSG_OUTPUT"]


    # PASO 1. Cargar datos del shp al df
    start_time = time.time()
    df_carreteras = gpd.read_file(path_carretera)
    df_pk = gpd.read_file(path_pk)
    df_carretera = filtr_road(df_carreteras,nombre_carretera,tipo_tramD)
    print("Tiempo de cargar las capas--- %s seconds ----" % (time.time() - start_time))



    # los tramos de carretera en orden del PK 
    df_pk_carretera = df_pk[df_pk['id_tramo'].isin(df_carretera.id_tramo)].sort_values(by=["sentidopk","numero"])
    # limpiar los PK ( no existe sentido -998)
    df_pk_carretera = df_pk_carretera[df_pk_carretera['sentidopk']!=-998]#.drop_duplicates(subset=['id_tramo'], keep='first')

    # sleccionar calzada para 1 setnido de PK
    df_pk_calzada = df_pk_carretera[df_pk_carretera["sentidopk"] == sentidopk]
    tramos_calzada = df_pk_calzada["id_tramo"] 
    df_calzada = df_carretera[df_carretera.id_tramo.isin(tramos_calzada)]

    ### transformar
    df_pk_carretera["geometry"] = [ tranform_geom(geom,epsg_input,epsg_output) for geom in df_pk_carretera["geometry"] ]
    df_pk_calzada["geometry"] = [ tranform_geom(geom,epsg_input,epsg_output) for geom in df_pk_calzada["geometry"] ]
    df_calzada["geometry"] = [ tranform_geom(geom,epsg_input,epsg_output) for geom in df_calzada["geometry"] ]
    df_carretera["geometry"] =  [ tranform_geom(geom,epsg_input,epsg_output) for geom in df_carretera["geometry"] ]

    ### update exactitud
    simpledec = re.compile(r"\d*\.\d+")
    df_pk_carretera["geometry"] = df_pk_carretera["geometry"].apply(lambda x: loads(re.sub(simpledec, mround, x.wkt)))
    df_pk_calzada["geometry"] = df_pk_calzada["geometry"].apply(lambda x: loads(re.sub(simpledec, mround, x.wkt)))
    df_calzada["geometry"] = df_calzada["geometry"].apply(lambda x: loads(re.sub(simpledec, mround, x.wkt)))
    df_carretera["geometry"] = df_carretera["geometry"].apply(lambda x: loads(re.sub(simpledec, mround, x.wkt)))

    # join carretera with PK
    df_carretera_and_pk = pd.merge(df_pk_carretera,
            df_calzada, 
            left_on ='id_tramo',
            right_on= 'id_tramo',
            how="inner").sort_values(by="numero")


    # merge touching line on road. ( di tienes dos calzadas, te saldran dos lineas)
    multiline = join_touching_lines(df_carretera)

    # guardar capas to shp
    print("Tramo se compone de %s PKs " % len(df_pk_calzada) )


    ### hay que definir pk
    pk_ini_row = df_carretera_and_pk[df_carretera_and_pk["numero"]==pk_hit_ini_input][["numero", "geometry_x"]]
    pk_ini_row =  df_carretera_and_pk[["numero", "geometry_x"]].iloc[0] if pk_ini_row.empty else pk_ini_row.iloc[0]

    pk_fin_row =df_carretera_and_pk[df_carretera_and_pk["numero"]==pk_hit_fin_intput][["numero", "geometry_x"]]
    pk_fin_row = df_carretera_and_pk[["numero", "geometry_x"]].iloc[-1] if pk_fin_row.empty else pk_fin_row.iloc[0]

    PK_INI = pk_ini_row.numero
    PK_FIN = pk_fin_row.numero

    PK_INI_geom = pk_ini_row.geometry_x
    PK_FIN_geom = pk_fin_row.geometry_x

    print("PK_INI %s" % PK_INI)
    print("PK_FIN %s" % PK_FIN)


    """
    hay que encontrar la linea para la carretera correspondiente.
    Buscamos la linea mas cercana al PK_INI_geom
    """
    line =  find_the_closest_line(PK_INI_geom, multiline)

    """ ASEGURARNOS QUE LOS PK ESTAN EN LA CARRETERA PARA PODER CORTARLA EN ESOS PK"""

    for PK in [PK_INI_geom,PK_FIN_geom]:
        line = correct_road_by_PK(PK, line,buffer)
        
    # GET THE LONGEst TRAMO ( hay que asegurarnos qu es asi)
    line = get_road_from_PK(line,PK_INI_geom)
    line = get_road_from_PK(line,PK_FIN_geom)



    """ DIVIDE LINE BY ALL PKS """
    # correct line para poder split line at every PK
    df_pk_carretera = df_pk[df_pk['id_tramo'].isin(df_carretera.id_tramo)].sort_values(by=["sentidopk","numero"])
    line_pk1000 = line
    for index, row in df_pk_calzada.iterrows():
        line_pk1000 = correct_road_by_PK(row.geometry,line_pk1000, buffer)
        
    points = MultiPoint(df_pk_calzada.geometry.tolist()) 
    splitted_pk1000 = split(line_pk1000, points) 

    print("Numero de tramos entre PK de 1000 m es de %s " % len(splitted_pk1000))
    print("Ese NUMERO deberIa coincidir con %s " % int(len(df_pk_calzada)-1))



    """CADA TRAMO DE 1000 m dividir en X tramos de 5 m """

    from shapely.ops import unary_union
    #distance_delta =  5/111000 *1.259 #5/111000 *1.25944584382#  5 m --> 5/111000 degree ????????????????????????
    distance_delta = 5 # estamos en la projeccion EPSG 25830

    collections= []

    def get_pk_by_line(line,distance_delta):
        distances = np.arange(0, line.length, distance_delta)
        points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]
        multipoint = unary_union(points)   
        return multipoint

    # collection is a set of multiple points. It is like a mask to divde segment of road
    for segment in splitted_pk1000:
        collections.append(get_pk_by_line(segment,distance_delta))

    pk = PK_INI
    frames = []

    #buffer = 0.0001 # m

    for (points_segment,segement ) in zip(collections,splitted_pk1000):
        
        # we are goijng to try to split line by all points ( we want to get 194 lines)
        corrected_segment = segement
        for p in points_segment:
            corrected_segment = correct_road_by_PK(p, corrected_segment, buffer)
        
        splitted_segment = split(corrected_segment, MultiPoint(points_segment) )
        #convert_geom  = tranform_geom(splitted_segment,epsg_input,epsg_output)
        if len(splitted_segment)!= len(points_segment)-1:
            print("Disminuyr el buffer e intenta otra vez")
        df_tramo = generate_df_tramo(pk, splitted_segment)
        gdf_tramo = generate_gdf_tramo(None,splitted_segment,df_tramo)
        pk+=1
        frames.append(gdf_tramo)
        
    gdf_tramos = pd.concat(frames)
    gdf_tramos["PK_HITO_FIN"] = gdf_tramos["PK_HITO_INI"].shift(-1)
    gdf_tramos["PK_DIST_FIN"] = df_tramo["PK_DIST_INI"].shift(-1)
    gdf_tramos["id"] = [i+1 for i in range(len(gdf_tramos))]

    gdf_tramos["id"] = [i+1 for i in range(len(gdf_tramos))]

    gdf_tramos.to_file(nombre_carretera+'_sentido_'+str(int(sentidopk))+'_tramificada_'+str(int(distance_delta))+'m.shp')
    return




if __name__ == '__main__':
    # crear_eje_carretera_by_pk.py executed as script
    run_script()
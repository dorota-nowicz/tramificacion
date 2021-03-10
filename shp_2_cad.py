import cad
import ezdxf
import os
import geopandas as gpd




def run_script():
    #folder = './examplesCAD/'
    #filename = 'Rx_Eje_2000'
    #dxf_path = os.path.join(folder, filename + '.dxf')

    """ INPUT """
    NUEVO_ARCHIVO = int(os.environ["NUEVO_ARCHIVO"])  # 1- partimos desede 0, 2 - ya tenemos un archivo
    path_cad = os.environ["PATH_DXF"]
    sentidopk = int(os.environ["SENTIDO_PK"] )
    distance_delta = int(os.environ["LONG_TRAMO"] )
    nombre_carretera =  os.environ["NOMBRE_CARRETERA"]
    block_name_20 = os.environ["NOMBRE_BLOCK_PK20"]
    block_name_100 = os.environ["NOMBRE_BLOCK_PK100"]
    dxf_path = os.environ["PATH_DXF"] 
    path_tramos_shp = nombre_carretera+"_sentido_"+str(int(sentidopk))+"_tramificada_por_dfk.shp"


    eje_layer = os.environ["NOMBRE_CAPA_EJE"]
    layer_names = ["G1","G2","G3",eje_layer]
    colors = ["verde","amarillo","rojo","azul"]
    id_colors = [3,2,1,5]

    head, tail = os.path.split(path_tramos_shp)
    output_name = tail.split(".")[0]

    if NUEVO_ARCHIVO== 1:
        dxf = ezdxf.new('R2010')  # create a new DXF R2010 drawing, official DXF version name: 'AC1024'
    elif NUEVO_ARCHIVO== 0:
        
        dxf = ezdxf.readfile(dxf_path)


    msp = dxf.modelspace()

    # leer shp con tramos al gdf
    df_tramos_shp= gpd.read_file(path_tramos_shp)


    """ AGREGAR TRAMOS PER GRUPO AL ARCHIVO CAD """

    for layer_name, color, id_color in zip(layer_names,colors, id_colors):
        if  not layer_name in dxf.layers:
            cad.create_layer(dxf, layer_name, id_color) # añadir capas al archivo dxf si no exsisten aún
        cad.add_tramos_by_group(layer_name,color,df_tramos_shp,msp)
        

    """ BLOQUE PK100  """

    #definir blocke pk100
    pk100 = dxf.blocks[block_name_100] if  block_name_100 in dxf.blocks else cad.create_new_block_pk100(dxf,block_name_100)
    intervalo100 = 100

    # calculate rotation for all PK every 100 m
    df_tramos_shp_100m = cad.prepare_df_for_block_pk(df_tramos_shp,intervalo100)


    for index, row in df_tramos_shp_100m.iterrows():

        blockref = msp.add_blockref(block_name_100, row.pk_geom,dxfattribs={
            'rotation': row.rotation+180,
            'layer': eje_layer
        })
        
        PK_HITO_IN = int(row.PK_HITO_IN)
        PK_DIST_IN = cad.prepare_PK_DIST_IN(row.PK_DIST_IN)
        values = {'PK': "%s+%s" % (PK_HITO_IN, PK_DIST_IN ) }
        blockref.add_auto_attribs(values)
        
        
    """ BLOQUE PK20  """

    # definir blocke pk20
    pk20 = dxf.blocks[block_name_20] if  block_name_20 in dxf.blocks else cad.create_new_block_pk20(dxf,block_name_20)
    intervalo20 = 20

    # calculate rotation for all PK every 20 m
    df_tramos_shp_20m = cad.prepare_df_for_block_pk(df_tramos_shp,intervalo20)

    # remove PK every 100 m they have alredy their own block
    df_tramos_shp_20m = df_tramos_shp_20m[ df_tramos_shp_20m["PKI"]%intervalo100 != 0 ]

    # 6. insert block pk 20 with rotation
    for index, row in df_tramos_shp_20m.iterrows():
        msp.add_blockref(block_name_20, row.pk_geom,dxfattribs={
            'rotation': row.rotation,
            'layer': eje_layer
        })


    """ Save file """
    dxf.saveas(output_name+".dxf")

    return

if __name__ =="__main__":
    run_script()
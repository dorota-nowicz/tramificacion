# Tramificación de la carretera

Herramienta para automatizar la generación de los planos de la renovación de las carreteras en función de deflexiones en NanoCAD


## Descripción

La herramienta importa las capas vectoriales procedentes de CNIG para extraer la eje y los puntos kilometricos (PK) de una carretera predefinida. 
Posteriormente, se tramifica la carretera cada X metros, y, a cada tramo se le asocia su PK y los valores tales como deflexiones y/o CRT.
Al final, se automatiza la generación de los planos en el formato .dxf en función de los parametros predefinidos.


## Empezamos

### Dependencias

* Python
* Librerías de python: pandas, ezdxf, numpy, geopandas...

### Ejecución del programa
```
python pipe.py
```

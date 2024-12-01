import unidecode
import re

def determinar_provincia(ubicacion):
    # Palabras clave para cada provincia
    provincias = {
        "Caba": ["capital federal", "ciudad de buenos aires", "caba", "buenos aires caba"],
        "Buenos Aires": ["buenos aires", "bs.as.", "g.b.a.", "gba", "buenos aires provincia", "g.b.a. norte", "g.b.a. sur", "g.b.a. oeste"],
        "Córdoba": ["córdoba", "cordoba"],
        "Santa Fe": ["santa fe", "rosario"],
        "Mendoza": ["mendoza"],
        "Tucumán": ["tucumán", "tucuman"],
        "Salta": ["salta"],
        "Neuquén": ["neuquén", "neuquen"],
        "Río Negro": ["río negro", "rio negro", "bariloche"],
        "Chubut": ["chubut"],
        "Entre Ríos": ["entre ríos", "entre rios"],
        "San Juan": ["san juan"],
        "Misiones": ["misiones"],
        # Agregar más provincias y palabras clave según sea necesario
    }

    # Normalizar la ubicación eliminando acentos y convirtiendo a minúsculas
    ubicacion_normalizada = unidecode.unidecode(ubicacion).lower()

    # Buscar coincidencias utilizando una expresión regular para verificar si alguna palabra clave aparece
    for provincia, palabras in provincias.items():
        for keyword in palabras:
            if re.search(r'\b' + re.escape(keyword) + r'\b', ubicacion_normalizada):
                return provincia
    return 'Otros'

# Pruebas
ubicaciones = [
    "San Fernando, Bs.As. G.B.A. Norte",
    "Barrio Parque Gral San Martin, General San Martin, Bs.As. G.B.A. Norte",
    "Haedo, Moron, Bs.As. G.B.A. Oeste",
    "Lomas Del Mirador, La Matanza, Bs.As. G.B.A. Oeste",
    "Villa Adelina, San Isidro, Bs.As. G.B.A. Norte",
    "Quilmes, Bs.As. G.B.A. Sur"
]

for ubicacion in ubicaciones:
    print(f"Provincia de '{ubicacion}': {determinar_provincia(ubicacion)}")

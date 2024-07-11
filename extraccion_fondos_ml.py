import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import unidecode

# Función para obtener los títulos, ubicaciones, precios y rubros de las publicaciones en una página de Mercado Libre
def obtener_datos_pagina(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articulos = soup.find_all('li', class_='ui-search-layout__item')
    
    datos = []
    for articulo in articulos:
        titulo_elem = articulo.find('h2', class_='ui-search-item__title')
        ubicacion_elem = articulo.find('span', class_='ui-search-item__location-label')
        precio_elem = articulo.find('span', class_='andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript')
        
        if titulo_elem:
            titulo = titulo_elem.text.strip()
        else:
            titulo = 'No encontrado'
        
        if ubicacion_elem:
            ubicacion = ubicacion_elem.text.strip()
        else:
            ubicacion = 'No especificada'
        
        if precio_elem:
            precio = precio_elem.text.strip()
        else:
            precio = 'No especificado'
        
        # Determinar el rubro basado en palabras clave en el título
        rubro = determinar_rubro(titulo)
        
        datos.append([titulo, ubicacion, precio, rubro])
    
    return datos

# Función para determinar el rubro basado en palabras clave en el título
def determinar_rubro(titulo):
    # Lista de palabras clave y sus rubros correspondientes
    palabras_clave = {
        'autoservicio': 'Supermercado',
        'barberia': 'Barbería',
        'biciclet': 'Bicicletería',
        'bulonera': 'Ferretería',
        'cabaña': 'Hotelería',
        'cafe': 'Cafetería',
        'cafeteria': 'Cafetería',
        'carniceria': 'Carnicería',
        'catering': 'Eventos',
        'cervecer': 'Cervecería',
        'churreria': 'Panadería',
        'complejo': 'Hotelería',
        'confiteria': 'Panadería',
        'cotillon': 'Cotillón',
        'depilacion': 'Salón de belleza',
        'despensa': 'Almacén',
        'dietetica': 'Dietética',
        'estetica': 'Salón de belleza',
        'fabrica': 'Fábrica',
        'fast food': 'Hamburguesería',
        'ferreteria': 'Ferretería',
        'fiambre': 'Fiambrería',
        'fiesta': 'Eventos',
        'futbol': 'Cancha de futbol',
        'geriatri': 'Geriátrico',
        'gimnasio': 'Gimnasio',
        'gomeria': 'Gomería',
        'gym': 'Gimnasio',
        'hamburgueseria': 'Hamburguesería',
        'heladeria': 'Heladería',
        'hostel': 'Hotelería',
        'hotel': 'Hotelería',
        'indumentaria': 'Indumentaria',
        'kiosco': 'Kiosco',
        'kiosko': 'Kiosco',
        'lavadero autos': 'Lavadero de autos',
        'lavadero de autos': 'Lavadero de autos',
        'libreria': 'Librería',
        'local ind': 'Indumentaria',
        'loteria': 'Lotería',
        'maxikiosco': 'Kiosco',
        'maxiquiosco': 'Kiosco',
        'minimarket': 'Supermercado',
        'minimercado': 'Supermercado',
        'nails': 'Salón de belleza',
        'odontologico': 'Salud',
        'panaderia': 'Panadería',
        'papelera': 'Papelera',
        'parrilla': 'Parrilla',
        'peluqueria': 'Peluquería',
        'pet shop': 'Pet shop',
        'pizza': 'Pizzería',
        'pizzeria': 'Pizzería',
        'prendas de vestir': 'Indumentaria',
        'quiniela': 'Lotería',
        'quiosco': 'Kiosco',
        'restaurant': 'Restaurante',
        'resto bar': 'Restaurante',
        'restobar': 'Restaurante',
        'ropa': 'Indumentaria',
        'salon de belleza': 'Salón de belleza',
        'salon de fiesta': 'Eventos',
        'salon de uñas': 'Salón de belleza',
        'supermercado': 'Supermercado',
        'verduleria': 'Verdulería',
        'veterinaria': 'Veterinaria',
        'vivero': 'Vivero'
        # Agregar más palabras clave según sea necesario
    }
    
    # Normalizar el título eliminando acentos y convirtiendo a minúsculas
    titulo_normalizado = unidecode.unidecode(titulo).lower()
    
    # Buscar palabras clave en el título normalizado y asignar el rubro correspondiente
    for palabra, rubro in palabras_clave.items():
        if palabra in titulo_normalizado:
            return rubro
    
    return 'Otros'  # Si ninguna palabra clave coincide, asignar 'Otros'

# Función para obtener la cantidad total de páginas disponibles basada en el número total de resultados
def obtener_cantidad_paginas(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Busca el elemento que contiene la cantidad total de resultados
    resultados_elem = soup.find('span', class_='ui-search-search-result__quantity-results')
    
    if resultados_elem:
        # Extrae el texto que contiene el número de resultados y lo convierte a entero
        cantidad_resultados = int(resultados_elem.text.strip().split()[0])
        
        # Calcula la cantidad de páginas necesarias, asumiendo 48 resultados por página
        cantidad_paginas = math.ceil(cantidad_resultados / 48)
    else:
        cantidad_paginas = 1  # En caso de no encontrar resultados, se asume una sola página
    
    return cantidad_paginas

# URL de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta/dueno-directo/'
cantidad_paginas = obtener_cantidad_paginas(url_base)

datos_totales = []

# Iterar sobre todas las páginas de resultados disponibles
for pagina in range(1, cantidad_paginas + 1):
    url = url_base + f'_Desde_{(pagina-1)*48+1}'
    datos_totales.extend(obtener_datos_pagina(url))

# Crear un DataFrame con los datos obtenidos
columnas = ['Titulo', 'Ubicacion', 'Precio', 'Rubro']
df = pd.DataFrame(datos_totales, columns=columnas)

# Guardar el DataFrame en un archivo CSV
df.to_csv('fondos_de_comercio_datos.csv', index=False)
print(f'Se han recogido datos de {cantidad_paginas} páginas.')
print(df)

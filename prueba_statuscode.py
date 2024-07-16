import requests
from bs4 import BeautifulSoup
import time
import logging
import random
import math

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def verificar_carga_completa(response, soup):
    # Verificar el status code
    logging.info(f'Status code: {response.status_code}')
    
    # Verificar si el número esperado de artículos está presente en la página
    articulos = soup.find_all('li', class_='ui-search-layout__item')
    return len(articulos) > 0

def procesar_paginas(url_base):
    cantidad_paginas = obtener_cantidad_paginas(url_base)

    # Iterar sobre todas las páginas de resultados disponibles
    for pagina in range(1, cantidad_paginas + 1):
        url = url_base + f'_Desde_{(pagina-1)*48+1}'
        logging.info(f'Procesando página: {url}')
        
        response = requests.get(url)
        #time.sleep(random.uniform(2, 5))  # Esperar entre 2 y 5 segundos antes de procesar la página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if not verificar_carga_completa(response, soup):
            logging.error(f'Página {url} no cargó completamente.')

# URL de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta/dueno-directo/'

procesar_paginas(url_base)

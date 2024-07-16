import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def obtener_valor_etiqueta(articulo, etiquetas_clases):
    for etiqueta, clase in etiquetas_clases:
        elemento = articulo.find(etiqueta, class_=clase)
        if elemento:
            return elemento.text.strip()
    return 'No encontrado'

def obtener_datos_pagina(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articulos = soup.find_all('li', class_='ui-search-layout__item')
    
    datos = []
    for articulo in articulos:
        # Intentar obtener el título de varias maneras
        titulo = obtener_valor_etiqueta(articulo, [
            ('h2', 'ui-search-item__title'),
            ('h2', 'poly-box')
        ])
        
        # Intentar obtener el precio de varias maneras
        precio = obtener_valor_etiqueta(articulo, [
            ('span', 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript')
            # agregar mas tuplas si es necesario verificar mas etiquetas
        ])
        
        datos.append([titulo, precio])
    
    return datos

def main(url_base, total_paginas):
    datos_totales = []
    for pagina in range(1, total_paginas + 1):
        url = url_base + f'_Desde_{(pagina-1)*48+1}'
        datos_pagina = obtener_datos_pagina(url)
        datos_totales.extend(datos_pagina)
        time.sleep(1)  # Esperar 1 segundo entre cada solicitud
    
    # Crear un DataFrame con los datos obtenidos
    columnas = ['Titulo', 'Precio']
    df = pd.DataFrame(datos_totales, columns=columnas)
    
    # Guardar el DataFrame en un archivo CSV
    df.to_csv('fondos_de_comercio_datos.csv', index=False)
    print(f'Se han recogido datos de {total_paginas} páginas.')
    print(df)
    # Contar cuántos registros tienen "No encontrado" como título
    registros_no_encontrados = df[df['Titulo'] == 'No encontrado'].shape[0]
    print(f'Registros con título "No encontrado": {registros_no_encontrados}')

# URL base de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta/dueno-directo/'
total_paginas = 5  # Número total de páginas a verificar

if __name__ == "__main__":
    main(url_base, total_paginas)

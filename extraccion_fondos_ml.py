import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import time
import unidecode

def obtener_valor_etiqueta(articulo, etiquetas):
    intentos = 0
    while intentos < 3:
        for etiqueta, clase in etiquetas:
            elemento = articulo.find(etiqueta, class_=clase)
            if elemento:
                return elemento.text.strip()
        intentos += 1
        time.sleep(0.5)  # Esperar medio segundo antes de intentar nuevamente
        print(f'Intento {intentos} fallido para etiquetas {etiquetas}. Reintentando...')
    return 'No encontrado'

def obtener_datos_pagina(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articulos = soup.find_all('li', class_='ui-search-layout__item')
    
    datos = []
    for articulo in articulos:
        # Obtener título (verificar ambas clases posibles)
        titulo = obtener_valor_etiqueta(articulo, [('h2', 'ui-search-item__title'), ('h2', 'poly-box')]) # las 2 etiquetas que son titulo
        if titulo == 'No encontrado':
            continue  # Saltar este artículo si no se encontró el título
        
        # Obtener moneda y precio
        moneda = obtener_valor_etiqueta(articulo, [('span', 'andes-money-amount__currency-symbol')])    
        precio = int(obtener_valor_etiqueta(articulo, [('span', 'andes-money-amount__fraction')]).split()[0].replace('.', ''))

        datos.append([titulo, moneda, precio])
    
    return datos

def obtener_cantidad_paginas(url_base):
    response = requests.get(url_base)
    soup = BeautifulSoup(response.text, 'html.parser')
    resultados_elem = soup.find('span', class_='ui-search-search-result__quantity-results')
    
    if resultados_elem:
        cantidad_resultados = int(resultados_elem.text.strip().split()[0].replace('.', ''))
        cantidad_paginas = math.ceil(cantidad_resultados / 48)
    else:
        cantidad_paginas = 1
    
    return cantidad_paginas

def determinar_rubro(titulo):
    # Definir las palabras clave y sus rubros correspondientes
    rubros = {
        'autoservicio': 'Supermercado',
        'barberia': 'Barbería',
        'bebida': 'Bebidas',
        'vinoteca': 'Bebidas',
        'vineria': 'Bebidas',
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
        'farmacia': 'Farmacia',
        'fast food': 'Hamburguesería',
        'ferreteria': 'Ferretería',
        'fiambre': 'Fiambrería',
        'fiesta': 'Eventos',
        'franquicia': 'Franquicia',
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
        'lenceria': 'Indumentaria',
        'libreria': 'Librería',
        'local ind': 'Indumentaria',
        'loteria': 'Lotería',
        'maxikiosco': 'Kiosco',
        'maxiquiosco': 'Kiosco',
        'maxikisoco': 'Kiosco',
        'minimarket': 'Supermercado',
        'minimercado': 'Supermercado',
        'nails': 'Salón de belleza',
        'odontologico': 'Salud',
        'panaderia': 'Panadería',
        'papelera': 'Papelera',
        'pañalera': 'Pañalera',
        'parrilla': 'Parrilla',
        'peluqueria': 'Peluquería',
        'pet shop': 'Pet shop',
        'pelotero': 'Eventos',
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
        'salon masculino': 'Barbería',
        'salon de fiesta': 'Eventos',
        'salon de eventos': 'Eventos',
        'salon de uñas': 'Salón de belleza',
        'supermercado': 'Supermercado',
        'verduleria': 'Verdulería',
        'veterinaria': 'Veterinaria',
        'vivero': 'Vivero'
        # Agregar más palabras clave según sea necesario
    }
    
    # Normalizar el título eliminando acentos y convirtiendo a minúsculas
    titulo_normalizado = unidecode.unidecode(titulo).lower()
    
    # Buscar la primera palabra clave que coincida
    for palabra, rubro in rubros.items():
        if palabra in titulo_normalizado:
            return rubro
    return 'Otros'      # Si no se encuentra ninguna palabra clave, devolver "Otros"

def main(url_base):
    cantidad_paginas = obtener_cantidad_paginas(url_base)
    datos_totales = []
    for pagina in range(1, cantidad_paginas + 1):
        url = url_base + f'_Desde_{(pagina-1)*48+1}'
        print(f'Cargando página {pagina} de {cantidad_paginas}')
        datos_pagina = obtener_datos_pagina(url)
        datos_totales.extend(datos_pagina)
        time.sleep(1)  # Esperar 1 segundo entre cada solicitud
    
    # Crear un DataFrame con los datos obtenidos
    columnas = ['Titulo', 'Moneda', 'Precio']
    df = pd.DataFrame(datos_totales, columns=columnas)
    
    # Calcular el rubro y agregarlo como una nueva columna
    df['Rubro'] = df['Titulo'].apply(determinar_rubro)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv('fondos_de_comercio_datos.csv', index=False)
    print(f'Se han recogido datos de {cantidad_paginas} páginas.')
    print(df)

# URL base de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta/dueno-directo/'

if __name__ == "__main__":
    main(url_base)

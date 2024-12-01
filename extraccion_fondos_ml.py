import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import time
import unidecode
import datetime
import re

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

def obtener_metro_cuadrado(articulo):
    # Buscar todos los elementos con la clase correspondiente
    elementos_m2 = articulo.find_all('li', class_='poly-attributes-list__item poly-attributes-list__separator')
    for elemento in elementos_m2:
        texto = elemento.get_text()
        # Verificar si contiene "m²"
        if "m²" in texto:
            # Extraer el número antes de "m²" usando regex
            match = re.search(r'(\d+)\s*m²', texto)
            if match:
                return int(match.group(1))
    return None  # Si no encuentra "m²" en ninguno de los elementos, devolver None


def determinar_ciudad(ubicacion):
        # Dividir la ubicación por comas
    componentes = [componente.strip() for componente in ubicacion.split(',')]
    
    # Determinar la ciudad según la cantidad de componentes
    if len(componentes) == 1:
        ciudad = componentes[0]  # Solo hay un componente
    elif len(componentes) == 2:
        ciudad = componentes[0]  # Extraer el principio
    else:
        ciudad = componentes[-2]  # Extraer el anteúltimo
    
    return ciudad.title()  # Capitalizar la ciudad


def determinar_provincia(ubicacion):
    # Palabras clave para cada provincia
    provincias = {
        "Caba": ["capital federal", "ciudad de buenos aires", "caba", "buenos aires caba"],
        "Buenos Aires": ["buenos aires", "bs.as.", "g.b.a.", "gba", "buenos aires provincia"],
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
            if keyword in ubicacion_normalizada:
                return provincia
    return 'Otros'


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

        # Obtener ubicación
        ubicacion = obtener_valor_etiqueta(articulo, [('span', 'poly-component__location'), ('span', 'ui-search-item__location-label')]) 
        if ',' in ubicacion: ubicacion = ubicacion.split(',', 1)[1].strip()   # Limpia la direccion y altura, lo que esta antes de la 1er coma.

        # Obtener metros cuadrados (M2)
        m2 = obtener_metro_cuadrado(articulo)
        
        # Agregar los datos a la lista
        datos.append([titulo, moneda, precio, ubicacion, m2])
    
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
        "Deco": ["alfombras", "bazar", "decoracion", "decoración"],
        "Gastronómico": ["alimentos", "comida", "comidas", "catering", "cheddar", "gourmet", "sushi", "viandas"],
        "Almacén": ["almacen", "almacén", "despensa"],
        "Panadería": ["panaderia", "medialunas", "churreria", "confiteria"],
        "Antigüedad": ["antguedad", "antiguas", "antiguedad", "antigüedad", "antigüedades"],
        "Taller automovil": ["automotor", "escapes", "lubricentro", "mecanico", "mecánico", "motos"],
        "Supermercado": ["autoservicio", "minimarket", "minimercado"],
        "Barbería": ["barberia", "salon masculino"],
        "Bebidas": ["bebida", "vineria", "vinoteca"],
        "Bicicletería": ["biciclet"],
        "Blanquería": ["blanqueria"],
        "Ferretería": ["bulonera", "ferreteria"],
        "Hotelería": ["cabaña", "complejo", "hostel", "hotel"],
        "Cafetería": ["cafe", "cafeteria"],
        "Canchas": ["canchas", "futbol", "padel"],
        "Carnicería": ["carne", "carniceria", "cerdo", "frigorífico", "granja", "pollo"],
        "Eventos": ["fiesta", "pelotero", "salon de eventos", "salon de fiesta", "gazebos"],
        "Salón de belleza": ["cejas", "cosmetica", "depilacion", "estetica", "maquillajes", "nails", "pestañas", "solarium", "uñas"],
        "Tecnología": ["celular", "celulares", "computacion", "informatica", "informática", "telefonia", "telefonía", "teleonia"],
        "Dietética": ["dietarios", "dietetica"],
        "Diarios y revistas": ["diarios", "piarios", "revistas"],
        "Fábrica": ["fabrica"],
        "Farmacia": ["farmacia"],
        "Hamburguesería": ["fast food", "hamburgueseria"],
        "Heladería": ["heladeria"],
        "Indumentaria": ["indumentaria", "lenceria", "prendas de vestir", "ropa", "textiles", "zapatería"],
        "Kiosco": ["golosinas", "kiosco", "kiosko", "maxikiosco", "maxikisoco", "maxiquiosco"],
        "Limpieza": ["limpieza", "quimica"],
        "Lotería": ["loteria", "quiniela"],
        "Mercería": ["merceria"],
        "Papelera": ["papelera"],
        "Perfumería": ["perfumería", "perfumerie"],
        "Pescadería": ["marisqueria", "pescaderia"],
        "Pet shop": ["mascotas", "pet shop"],
        "Pizzería": ["empanada", "pizeria", "pizza", "pizzeria"],
        "Restaurante": ["restaurant", "resto bar", "restó", "restobar"],
        "Rotisería": ["rotiseria", "rotisería"],
        "Salud": ["laboratorio", "medico", "odontologico"],
        "Veterinaria": ["veterinaria"],
        "Vivero": ["vivero"],
        "Vidriería": ["vidriería"]
    }
    
    # Normalizar el título eliminando acentos y convirtiendo a minúsculas
    titulo_normalizado = unidecode.unidecode(titulo).lower()
    print(f'Titulo normalizado: "{titulo_normalizado}"')  # Imprimir el título normalizado
    
    # Buscar el rubro correspondiente
    for rubro, palabras in rubros.items():
        if any(keyword in titulo_normalizado for keyword in palabras):  # Buscar cualquier palabra clave del rubro
            return rubro  # Devolver el nombre del rubro, no la lista de palabras
    
    return 'Otros'  # Si no se encuentra ninguna palabra clave, devolver "Otros"



def main(url_base):
    cantidad_paginas = 1  # Forzar a analizar solo la primera página durante pruebas
    datos_totales = []
    for pagina in range(1, cantidad_paginas + 1):
        url = url_base + f'_Desde_{(pagina-1)*48+1}'
        print(f'Cargando página {pagina} de {cantidad_paginas}')
        datos_pagina = obtener_datos_pagina(url)
        datos_totales.extend(datos_pagina)
        time.sleep(1)  # Esperar 1 segundo entre cada solicitud
    
    # Crear un DataFrame con los datos obtenidos
    columnas = ['Fecha Scrapping', 'Titulo', 'Moneda', 'Precio', 'Ubicacion', 'M2']
    fecha_hoy = datetime.datetime.now().strftime('%Y-%m-%d')  # Obtiene la fecha actual
    df = pd.DataFrame(datos_totales, columns=columnas[1:])  # Ignorar la primera columna temporalmente
    df.insert(0, 'Fecha Scrapping', fecha_hoy)  # Agregar la fecha como primera columna

    # Agregar columna "Plataforma"
    df.insert(1, 'Plataforma', 'Mercado Libre')  # Agregar como segunda columna
    
    # Calcular el rubro y agregarlo como una nueva columna
    df['Rubro'] = df['Titulo'].apply(determinar_rubro)

    # Aplicamos la nueva función a la columna 'Ubicacion'
    df['Ciudad'] = df['Ubicacion'].apply(determinar_ciudad)

    # Agregar columna Provincia
    df['Provincia'] = df['Ubicacion'].apply(determinar_provincia)

    df['Pais'] = 'Argentina'    # Agregar columna Pais

    # Concatenar las columnas 'Ciudad', 'Provincia' y 'Pais' para crear 'Ubicacion mapa'
    df['Ubicacion mapa'] = df['Ciudad'] + ', ' + df['Provincia'] + ', ' + df['Pais']

    # Definir la cotización manual del dólar en Argentina
    cotizacion_dolar = 1100  # Cambia este valor según la cotización actual
    # Crear la columna 'Precio en U$s' según la condición, asegurando números enteros
    df['Precio en U$s'] = df.apply(
    lambda row: int(row['Precio']) if row['Moneda'] == 'US$' else int(round(row['Precio'] / cotizacion_dolar)) if row['Moneda'] == '$' else None, axis=1)
    
    # Crear la columna 'Precio x m2' asegurando que se eviten errores de división
    df['Precio x m2'] = df.apply(
        lambda row: int(round(row['Precio en U$s'] / row['M2'])) if row['M2'] and row['Precio en U$s'] else None, axis=1)

    # Reordenar las columnas para que 'M2' sea la última
    columnas_reordenadas = ['Fecha Scrapping', 'Plataforma', 'Titulo', 'Moneda', 'Precio', 'Ubicacion', 'Rubro', 'M2', 'Ciudad', 'Provincia', 'Pais', 'Ubicacion mapa', 'Precio en U$s', 'Precio x m2']
    df = df[columnas_reordenadas]

    # Guardar el DataFrame en un archivo CSV con la fecha del día que se genera
    nombre_archivo = f'/home/eze-ubuntu/Documents/data_projects/partnerds/fondos_ml/fondos_de_comercio_datos_{fecha_hoy}.csv'
    df.to_csv(nombre_archivo, index=False)
    print(f'Se han recogido datos de {cantidad_paginas} página(s).')
    print(df)

# URL base de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta'

if __name__ == "__main__":
    main(url_base)

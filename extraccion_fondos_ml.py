import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import time
import unidecode
import datetime

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

        # Obtener ubicación
        ubicacion = obtener_valor_etiqueta(articulo, [('span', 'poly-component__location'), ('span', 'ui-search-item__location-label')]) 
        if ',' in ubicacion: ubicacion = ubicacion.split(',', 1)[1].strip()   # Limpia la direccion y altura, lo que esta antes de la 1er coma.

        datos.append([titulo, moneda, precio, ubicacion])
    
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
        'Alfombras': 'Deco',
        'Alimentos': 'Gastronómico',
        'Almacen': 'Almacen',
        'Almacén': 'Almacen',
        'Anadería,': 'Panadería',
        'Antguedad': 'Antigüedad',
        'Antiguas': 'Antigüedad',
        'Antiguedad': 'Antigüedad',
        'Antigüedad': 'Antigüedad',
        'Antigüedades': 'Antigüedad',
        'Automotor': 'Taller automovil',
        'autoservicio': 'Supermercado',
        'barberia': 'Barbería',
        'Bazar': 'Deco',
        'bebida': 'Bebidas',
        'biciclet': 'Bicicletería',
        'Blanqueria': 'Blanquería',
        'bulonera': 'Ferretería',
        'cabaña': 'Hotelería',
        'cafe': 'Cafetería',
        'cafeteria': 'Cafetería',
        'Canchas': 'Canchas',
        'Carne': 'Carnicería',
        'carne': 'Carnicería',
        'carniceria': 'Carnicería',
        'catering': 'Eventos',
        'Cejas': 'Salón de belleza',
        'Celular': 'Tecnología',
        'Celulares,': 'Tecnología',
        'Celulares': 'Tecnología',
        'Cerdo': 'Carnicería',
        'Cerrajería': 'Cerrajería',
        'cervecer': 'Cervecería',
        'Cheddar': 'Gastronómico',
        'churreria': 'Panadería',
        'Comida': 'Gastronómico',
        'comida': 'Gastronómico',
        'Comidas': 'Gastronómico',
        'complejo': 'Hotelería',
        'Computacion': 'Tecnología',
        'confiteria': 'Panadería',
        'Cosmetica': 'Salón de belleza',
        'cotillon': 'Cotillón',
        'Deco': 'Deco',
        'Decoracion': 'Deco',
        'Decoración': 'Deco',
        'depilacion': 'Salón de belleza',
        'despensa': 'Almacén',
        'detailing': 'Lavadero de autos',
        'Diarios': 'Diarios y revistas',
        'Dietarios': 'Dietética',
        'dietetica': 'Dietética',
        'empanada': 'Pizzería',
        'Enseñanza': 'Educación',
        'Escapes': 'Taller automovil',
        'Estacionamiento': 'Estacionamiento',
        'estetica': 'Salón de belleza',
        'fabrica': 'Fábrica',
        'farmacia': 'Farmacia',
        'fast food': 'Hamburguesería',
        'ferreteria': 'Ferretería',
        'fiambre': 'Fiambrería',
        'fiesta': 'Eventos',
        'franquicia': 'Franquicia',
        'Frigorífico': 'Carnicería',
        'futbol': 'Canchas',
        'Gaonómico': 'Gastronómico',
        'gastronom': 'Gastronómico',
        'Gastronomía': 'Gastronómico',
        'Gastronomica': 'Gastronómico',
        'Gastronomíco': 'Gastronómico',
        'Gastronómico': 'Gastronómico',
        'Gazebos': 'Eventos',
        'geriatri': 'Geriátrico',
        'gimnasio': 'Gimnasio',
        'Golosinas': 'Kiosco',
        'gomeria': 'Gomería',
        'Gourmet': 'Gastronómico',
        'Gráfica': 'Gráfica',
        'Granja': 'Carnicería',
        'granja': 'Carnicería',
        'gym': 'Gimnasio',
        'hamburgueseria': 'Hamburguesería',
        'heladeria': 'Heladería',
        'hostel': 'Hotelería',
        'hotel': 'Hotelería',
        'indumentaria': 'Indumentaria',
        'Informatica': 'Tecnología',
        'Informática': 'Tecnología',
        'Inglés': 'Educación',
        'Instituto': 'Educación',
        'Joyería,': 'Joyería',
        'jugueteria': 'Juguetería',
        'Juguetería': 'Juguetería',
        'kiosco': 'Kiosco',
        'kiosko': 'Kiosco',
        'Laboratorio': 'Salud',
        'lavadero autos': 'Lavadero de autos',
        'lavadero de autos': 'Lavadero de autos',
        'Lavadero': 'Lavadero de autos',
        'Lavanderia': 'Lavandería',
        'Lavandería': 'Lavandería',
        'lenceria': 'Indumentaria',
        'libreria': 'Librería',
        'Limpieza': 'Limpieza',
        'local ind': 'Indumentaria',
        'loteria': 'Lotería',
        'Lubricentro': 'Taller automovil',
        'Maquillajes': 'Salón de belleza',
        'Marisqueria': 'Pescadería',
        'Mascotas': 'Pet shop',
        'maxikiosco': 'Kiosco',
        'maxikisoco': 'Kiosco',
        'maxiquiosco': 'Kiosco',
        'Mecanico': 'Taller automovil',
        'Mecánico': 'Taller automovil',
        'Medialunas': 'Panadería',
        'Medico': 'Salud',
        'Merceria': 'Mercería',
        'Mercería': 'Mercería',
        'minimarket': 'Supermercado',
        'minimercado': 'Supermercado',
        'Motos': 'Taller automovil',
        'nails': 'Salón de belleza',
        'odontologico': 'Salud',
        'Padel': 'Canchas',
        'panaderia': 'Panadería',
        'Pañalera': 'Pañalera',
        'pañalera': 'Pañalera',
        'papelera': 'Papelera',
        'parrilla': 'Parrilla',
        'pelotero': 'Eventos',
        'peluqueria': 'Peluquería',
        'perfumería': 'Perfumería',
        'Perfumería': 'Perfumería',
        'Perfumerie': 'Perfumería',
        'Pescaderia': 'Pescadería',
        'Pestañas': 'Salón de belleza',
        'pet shop': 'Pet shop',
        'Piarios': 'Diarios y revistas',
        'Pizeria': 'Pizzería',
        'pizeria': 'Pizzería',
        'pizza': 'Pizzería',
        'pizzeria': 'Pizzería',
        'Pollo': 'Carnicería',
        'prendas de vestir': 'Indumentaria',
        'Quesería': 'Fiambrería',
        'Quimica': 'Limpieza',
        'quiniela': 'Lotería',
        'quiosco': 'Kiosco',
        'Regalería': 'Regalería',
        'Regalos': 'Regalería',
        'Relojería,': 'Relojería',
        'Repuestos': 'Repuestos',
        'restaurant': 'Restaurante',
        'resto bar': 'Restaurante',
        'Restó': 'Restaurante',
        'restobar': 'Restaurante',
        'Retacería': 'Retacería',
        'Revistas': 'Diarios y revistas',
        'ropa': 'Indumentaria',
        'Rotiseria': 'Rotisería',
        'rotiseria': 'Rotisería',
        'Rotisería': 'Rotisería',
        'salon de belleza': 'Salón de belleza',
        'salon de eventos': 'Eventos',
        'salon de fiesta': 'Eventos',
        'salon de uñas': 'Salón de belleza',
        'Salón De Uñas': 'Salón de belleza',
        'salon masculino': 'Barbería',
        'Solarium': 'Salón de belleza',
        'supermercado': 'Supermercado',
        'Sushi': 'Gastronómico',
        'Taller': 'Taller automovil',
        'Tecnología': 'Tecnología',
        'Telefonia': 'Tecnología',
        'Telefonía': 'Tecnología',
        'Teleonia': 'Tecnología',
        'Textiles': 'Indumentaria',
        'Tintoreria': 'Tintoreria',
        'Uñas': 'Salón de belleza',
        'verduleria': 'Verdulería',
        'veterinaria': 'Veterinaria',
        'Viandas': 'Gastronómico',
        'Vidriería': 'Vidriería',
        'vineria': 'Bebidas',
        'vinoteca': 'Bebidas',
        'vivero': 'Vivero',
        'Zapatería': 'Indumentaria'
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
    columnas = ['Titulo', 'Moneda', 'Precio', 'Ubicacion']
    df = pd.DataFrame(datos_totales, columns=columnas)
    
    # Calcular el rubro y agregarlo como una nueva columna
    df['Rubro'] = df['Titulo'].apply(determinar_rubro)

    # Guardar el DataFrame en un archivo CSV con la fecha del dia que se genera.
    fecha_hoy = datetime.datetime.now().strftime('%Y-%m-%d')    # Obtiene la fecha actual.
    nombre_archivo = f'/home/eze-ubuntu/Documents/data_projects/partnerds/fondos_ml/fondos_de_comercio_datos_{fecha_hoy}.csv'
    df.to_csv(nombre_archivo, index=False)
    print(f'Se han recogido datos de {cantidad_paginas} páginas.')
    print(df)

# URL base de ejemplo (modificar según las necesidades)
url_base = 'https://inmuebles.mercadolibre.com.ar/fondo-de-comercio/venta/dueno-directo/'

if __name__ == "__main__":
    main(url_base)

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import folium
from datetime import datetime


# In[14]:


import requests

url = 'http://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/resource/80ac25de-a44a-4445-9215-090cf55cfda5/download/precios-en-surtidor-resolucin-3142016.csv'

# Descargar el archivo
response = requests.get(url)

if response.status_code == 200:
    # Obtener la fecha de hoy
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Nombre del archivo con la fecha de hoy
    nombre_archivo = f'resolución_314_{fecha_hoy}.csv'

    # Guardar el contenido descargado en un archivo
    with open(nombre_archivo, 'wb') as file:
        file.write(response.content)

    # Cargar el archivo CSV en un DataFrame
    reso = pd.read_csv(nombre_archivo)

    print('Descarga completa y archivo guardado como:', nombre_archivo)
else:
    print('Error al descargar el archivo')


# In[15]:


reso = reso[(reso['idtipohorario']==2)&(reso['fecha_vigencia']>'2024-03-06')]
# Crear un diccionario de mapeo para reemplazar los valores
mapeo_empresas = {
    "YPF": "YPF",
    "SHELL C.A.P.S.A.": "SHELL",
    "AXION": "AXION",
    "BLANCA": "BLANCA",
    "PUMA": "PUMA"
}

# Crear una lista de las empresas que no se cambiarán y agregarlas al diccionario
empresas_a_mantener = ["YPF", "SHELL C.A.P.S.A.", "AXION", "BLANCA", "PUMA"]
for empresa in reso["empresabandera"].unique():
    if empresa not in empresas_a_mantener:
        mapeo_empresas[empresa] = "OTRAS"

# Reemplazar los valores en la columna 'empresabandera' utilizando el diccionario de mapeo
reso["empresabandera"] = reso["empresabandera"].replace(mapeo_empresas)
reso.dropna(subset='latitud',inplace=True)


# In[21]:


import folium

def mapa(producto):
    from folium.plugins import MarkerCluster
    # Filtramos por el producto
    res = reso[reso['producto'] == producto]
    mt2 = folium.Map(location=[-34.6, -58.2], zoom_start=7)

    # Definimos las capas como un diccionario
    layers = {
        'YPF': folium.FeatureGroup(name='YPF'),
        'SHELL': folium.FeatureGroup(name='SHELL'),
        'AXION': folium.FeatureGroup(name='AXION'),
        'BLANCA': folium.FeatureGroup(name='BLANCA'),
        'PUMA': folium.FeatureGroup(name='PUMA'),
        'OTRAS': folium.FeatureGroup(name='OTRAS')
    }

    # Seteamos los colores que queremos
    color_scale = {
        'SHELL': {'border': 'orange', 'fill': 'yellow'},
        'YPF': {'border': 'blue', 'fill': 'lightblue'},
        'AXION': {'border': 'purple', 'fill': 'lavender'},
        'PUMA': {'border': 'green', 'fill': 'lightgreen'},
        'BLANCA': {'border': 'black', 'fill': 'white'},
        'OTRAS': {'border': 'grey', 'fill': 'lightgrey'}
    }

    #armo función para que cuando pasemos el mouse por el mapa encima de cada estación se vea la fecha de ese precio
    def create_hover_popup_content(fecha):
        return f'{str(fecha)}</div>'

    def create_popup_content(marca, precio):
        colors = color_scale.get(marca, {'border': 'purple', 'fill': 'lavender'})
        style = f'style="font-size: 7pt; color: black; background-color: {colors["fill"]}; padding: 1px; border-radius: 3px; border: 1px solid {colors["border"]}; margin-top: -10px; width: 28px; font-weight: bold;"'
        return f'<div {style}>{str(precio)}</div>'

    for bandera in res['empresabandera'].unique():
        df = res[res['empresabandera'] == bandera]
        for lat, lon, fv, ps in zip(df['latitud'], df['longitud'], df['fecha_vigencia'], df['precio']):
            popup_content = create_popup_content(bandera, ps)
            hover_popup_content = create_hover_popup_content(fv)
            marker = folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f'<div style="max-width: 300px;">{popup_content}</div>')
            )
            marker.add_child(folium.Tooltip(hover_popup_content))
            layers[bandera].add_child(marker)

    for layer_name, layer in layers.items():
        mt2.add_child(layer)

    folium.LayerControl().add_to(mt2)

    # Guardar el mapa como un archivo HTML
    mt2.save(f'mapa_{producto}.html')
    import webbrowser
    webbrowser.open(f'mapa_{producto}.html')  # Abrir el archivo HTML en una nueva pestaña del navegador


# In[ ]:





# In[7]:


#ejecuto la función para cada producto
for producto in reso['producto'].unique():
    mapa(producto)


# In[ ]:





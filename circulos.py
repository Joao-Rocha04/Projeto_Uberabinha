from geopy.distance import geodesic
import math
from geopy.distance import geodesic
import math
import folium
from folium.plugins import MarkerCluster
import requests
import pandas
from geopy.geocoders import Nominatim

# Função para gerar círculos menores sobrepostos
def gerar_circulos_menores_sobrepostos(raio_maior, centro_lat, centro_lon, raio_menor):
    # Lista para armazenar as latitudes e longitudes dos círculos menores
    circulos = []
    
    # Diâmetro do círculo menor
    diametro_menor = 2 * raio_menor
    
    # Cálculo do número de linhas e colunas de círculos menores
    num_linhas = math.ceil(raio_maior / diametro_menor)+5
    num_colunas = math.ceil(raio_maior / diametro_menor)+5
    
    # Espaçamento entre os centros dos círculos menores
    espacamento_lat = (raio_menor+80) / 111000  # Aproximação: 1 grau de latitude = 111 km
    espacamento_lon = (raio_menor+80) / (111000 * math.cos(math.radians(centro_lat)))  # Correção para longitude
    for z in range(1,5):
        for i in range(num_linhas):
            for j in range(num_colunas):
                # Cálculo da posição do centro do círculo menor
                if z ==1:
                    novo_centro_lat = centro_lat + (i * espacamento_lat)
                    novo_centro_lon = centro_lon + (j * espacamento_lon)
                if z ==2:
                    novo_centro_lat = centro_lat - (i * espacamento_lat)
                    novo_centro_lon = centro_lon - (j * espacamento_lon)
                if z ==3:
                    novo_centro_lat = centro_lat - (i * espacamento_lat)
                    novo_centro_lon = centro_lon + (j * espacamento_lon)
                if z ==4:
                    novo_centro_lat = centro_lat + (i * espacamento_lat)
                    novo_centro_lon = centro_lon - (j * espacamento_lon)
                # Adicionando as coordenadas do círculo menor à lista

                # Verificando se o centro do círculo menor está dentro do círculo maior
                if geodesic((centro_lat, centro_lon), (novo_centro_lat, novo_centro_lon)).meters <= raio_maior:
                    # Verificando se o círculo menor já está na lista
                    if (novo_centro_lat, novo_centro_lon) not in circulos:
                        # Adicionando as coordenadas do círculo menor à lista
                        circulos.append((novo_centro_lat, novo_centro_lon))
    return circulos

# Coordenadas do centro do círculo maior
centro_lat = -23.59843  # Latitude
centro_lon = -46.67646  # Longitude

# Raio do círculo maior em metros
raio_maior = 5000

# Raio dos círculos menores em metros
raio_menor = 200

# Chamando a função para gerar os círculos menores
coordenadas_circulos = gerar_circulos_menores_sobrepostos(raio_maior, centro_lat, centro_lon, raio_menor)

# Imprimindo as coordenadas dos círculos menores
for i, coord in enumerate(coordenadas_circulos, 1):
    print(f'Círculo {i}: Latitude {coord[0]}, Longitude {coord[1]}')


# Criando o mapa com folium
m = folium.Map(location=[centro_lat, centro_lon], zoom_start=12)

# Adicionando o círculo maior ao mapa
folium.Circle(
    location=[centro_lat, centro_lon],
    radius=raio_maior,
    color='blue',
    fill=True,
    fill_opacity=0.3,
).add_to(m)

# Adicionando os círculos menores ao mapa
for coord in coordenadas_circulos:
    folium.Circle(
        location=[coord[0], coord[1]],
        radius=raio_menor,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.6,
    ).add_to(m)

# Exibindo o mapa
m.save('mapa_circulos.html')


# URL da api
URL = 'https://places.googleapis.com/v1/places:searchNearby'
# Tipos de oportunidades necessarios de realizar 
tipos_para_fazer = ["restaurant","car_dealer","store","gas_station","car_repair","supermarket","farm","school",
  "university","accounting","bank","cafe","bar","fire_station","police","hospital",
  "beauty_salon","market","shopping_mall","supermarket","gym"]

#Sua api
API_KEY = 'YOUR_API_KEY'
#Header necessário para realizar a requisição 
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': API_KEY,
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.types,places.location'
}
#lista para a conderencia de nomes já repetidos 
nomes_ja_vistos = []

#Iterar para realizar todas as requisiçôes, para todos os tipos
for tipo in tipos_para_fazer:
    data = []
    places = []

    #Realizar a requisição para cada circulo menor retornado da função criada 
    for centro in coordenadas_circulos:
        LATITUDE = centro[0]
        LONGITUDE = centro[1]
        payload = {
        "includedTypes": tipo,
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
            "center": {
                "latitude": LATITUDE,
                "longitude": LONGITUDE
            },
            "radius": raio_menor
            }
        },
        "rankPreference": "DISTANCE"
            }
        # Faz a requisição 
        response = requests.post(URL, json=payload,headers=headers) 
        if response.status_code != 200:
            print('Erro:', response.status_code)

        #Caso a requisição não de falhas, adiciona na lista places
        if 'places' in response.json():
            places.extend(response.json()['places'])
    for place in places:
        #Confere caso já não tenha aparecido anteriormente 
        if place['displayName']['text'] not in nomes_ja_vistos:
            #Salvo as informações 
            endereco = place['formattedAddress']
            nome = place['displayName']['text']
            lat = place['location']['latitude']
            long = place['location']['longitude']
            #Adiociona o lugar a lista de já vistos
            nomes_ja_vistos.append(nome)
            todos_tipos = ''
            for tipo1 in place['types']:
                todos_tipos += tipo1 + '/'
            data.append([nome,endereco,lat,long,todos_tipos])
    df = pandas.DataFrame(data, columns=['Nome','Endereço','Latitude','Longitude','Tipos'])
    df.to_excel(f'Oportunidades_{tipo}.xlsx', index=False)


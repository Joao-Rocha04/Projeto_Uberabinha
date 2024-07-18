# Importe as bibliotecas necessárias, caso necessário instale as bibliotecas
import requests
import pandas as pd
from geopy.distance import geodesic

# Sua chave de API
API_KEY = 'YOUR_API_KEY'
# Função para obter o place_id de um local possuindo somente suas coordenadas,utiliza de uma requisição GET para a API do Google Maps
def get_place_id(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json() # Converte a resposta para JSON
        if 'results' in data and len(data['results']) > 0: # Verifica se há resultados, caso contrário retorna None
            return data['results'][0]['place_id'] # Retorna o place_id do primeiro resultado
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None
    
# Função para obter a avaliação de um local possuindo seu place_id, utiliza de uma requisição GET para a API do Google Maps
def get_place_rating(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200: # Verifica se a requisição foi bem sucedida
        data = response.json()
        if 'result' in data: # Verifica se há um resultado
            rating = data['result'].get('rating', 'Rating not available') # Obtém a avaliação do local, caso não haja, retorna 'Rating not available'
            return rating
        else:
            return 'Rating not available'
    else:
        print(f"Error: {response.status_code}")
        return 'Rating not available'

# Realiza a leitura do arquivo excel onde possuimos as oportunidades e suas respectivas coordenadas
dados = pd.read_excel('oportunidades.xlsx')
latitude_insper_p2, longitude_insper_p2 = -23.599284777838378, -46.67564352329625

# Cria uma lista para armazenar os locais que estão a menos de 1km do Insper P2 e são restaurantes
lista_locais = []

for index,row in dados.iterrows():
    if row['restaurant'] == 1: #Verifica se o local é um restaurante
        latitude = row['Latitude']
        longitude = row['Longitude']
        if geodesic((latitude_insper_p2,longitude_insper_p2), (latitude, longitude)).meters <= 1000: #Verifica se a distância entre o Insper P2 e o local é menor ou igual a 1km
            place_id = get_place_id(latitude, longitude, API_KEY) #Obtém o place_id do local
            if place_id: #Verifica se o place_id foi obtido
                rating = get_place_rating(place_id, API_KEY) #Obtém a avaliação do local
                lista_locais.append({ #Adiciona o local à lista de locais
                    'Nome': row['Nome'],
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'Rating': rating,
                    'PlaceId': place_id
                })

# Cria um DataFrame com os locais e suas avaliações e salva em um arquivo excel
df_resultados = pd.DataFrame(lista_locais)
df_resultados.to_excel('Restaurantes_com_avaliação.xlsx',index=False)
            
            





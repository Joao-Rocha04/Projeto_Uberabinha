#Realizando a importação das bibliotecas necessárias, caso necessário é preciso instalar as bibliotecas
from geopy.distance import geodesic
import math
from geopy.distance import geodesic
import math
import folium
from folium.plugins import MarkerCluster
import requests
import pandas
from geopy.geocoders import Nominatim
from datetime import timezone, datetime


#Definindo as coordenadas dos prédios do Insper
latitude_insper_p2, longitude_insper_p2 = -23.599284777838378, -46.67564352329625
latitude_insper_p1, longitude_insper_p1 = -23.598875446728382, -46.676490128284335
API_KEY = 'YOUR_API_KEY'

#Realizando a leitura do arquivo excel onde possuimos as oportunidades e suas respectivas coordenadas
dados = pandas.read_excel('Oportunidades.xlsx')

#Definindo a lista de modos de transporte que serão utilizados para realizar as requisições e preencher o arquivo excel com as colunas de requisições
lista_modos = ['driving', 'walking', 'bicycling']
dados['Requisição_com_Uberabinha'] = ''
dados['Requisição_sem_Uberabinha'] = ''
dados['Requisição_com_Uberabinha_pessimista'] = '' 
dados['Requisição_sem_Uberabinha_pessimista'] = ''

#Definindo a data de partida para realizar a requisição com o trânsito
departure_date = datetime(2024, 5, 28, 10, 15, 0)  # Ano, mês, dia, hora, minuto, segundo
departure_timestamp = int(departure_date.replace(tzinfo=timezone.utc).timestamp())
quantidade_oportunidades_raio = 0

for modo in lista_modos:
    #Realizando a iteração sobre as linhas do arquivo excel para realizar as requisições
    for index,row in dados.iterrows():
        latitude_destino, longitude_destino = row['Latitude'], row['Longitude']
        #Verificando se a distância entre o Insper P2 e o destino é menor ou igual a 3km
        if geodesic((latitude_insper_p2,longitude_insper_p2), (latitude_destino, longitude_destino)).meters <= 3000:
            quantidade_oportunidades_raio += 1
            #Realizando a requisição para o modo de transporte escolhido, sem transito e com a Uberabinha
            url_com_uberabinha = f'https://maps.googleapis.com/maps/api/directions/json?origin={latitude_insper_p2},{longitude_insper_p2}&destination={latitude_destino},{longitude_destino}&mode={modo}&key={API_KEY}'
            response_com_uberabinha = requests.post(url_com_uberabinha) #Faço a requisição
            response_json_com_uberabinha = response_com_uberabinha.json() #Pego o json da resposta
            if response_com_uberabinha.status_code != 200: #Se o status code não for 200, imprimo o erro
                print('Erro:', response_com_uberabinha.status_code)
            else:
                dados.at[index, 'Requisição_com_Uberabinha'] = response_json_com_uberabinha #Preencho a coluna com o json da resposta
            
            #Para o modo de transporte driving, realizo tambem a requisição com o transito pessimista e sem a Uberabinha
            if modo == 'driving':
                #Requisição sem a Uberabinha, saindo do Insper P1, para não passar pela Uberabinha
                url_sem_uberabinha = f'https://maps.googleapis.com/maps/api/directions/json?origin={latitude_insper_p1},{longitude_insper_p1}&destination={latitude_destino},{longitude_destino}&mode=driving&key={API_KEY}'
                response_sem_uberabinha = requests.post(url_sem_uberabinha)
                response_json_sem_uberabinha = response_sem_uberabinha.json()
                if response_sem_uberabinha.status_code != 200:
                    print('Erro:', response_sem_uberabinha.status_code)
                else:
                    dados.at[index, 'Requisição_sem_Uberabinha'] = response_json_sem_uberabinha
                #Requisição sem a Uberabinha, saindo do Insper P1, para não passar pela Uberabinha, mas com o trânsito pessimista
                url_sem_uberabinha_pessimista = f'https://maps.googleapis.com/maps/api/directions/json?origin={latitude_insper_p1},{longitude_insper_p1}&destination={latitude_destino},{longitude_destino}&mode=driving&departure_time={departure_timestamp}&traffic_model=pessimistic&key={API_KEY}'
                response_sem_uberabinha_pessimista = requests.post(url_sem_uberabinha_pessimista)
                response_json_sem_uberabinha_pessimista = response_sem_uberabinha_pessimista.json()
                if response_sem_uberabinha_pessimista.status_code != 200:
                    print('Erro:', response_sem_uberabinha_pessimista.status_code)
                else:
                    dados.at[index, 'Requisição_sem_Uberabinha_pessimista'] = response_json_sem_uberabinha_pessimista  
                #Requisição com a Uberabinha, saindo do Insper P2, para passar pela Uberabinha e com o trânsito pessimista
                url_com_uberabinha_pessimista = f'https://maps.googleapis.com/maps/api/directions/json?origin={latitude_insper_p2},{longitude_insper_p2}&destination={latitude_destino},{longitude_destino}&mode=driving&departure_time={departure_timestamp}&traffic_model=pessimistic&key={API_KEY}'
                response_com_uberabinha_pessimista = requests.post(url_com_uberabinha_pessimista)
                response_json_com_uberabinha_pessimista = response_com_uberabinha_pessimista.json()
                if response_com_uberabinha_pessimista.status_code != 200:
                    print('Erro:', response_com_uberabinha_pessimista.status_code)
                else:
                    dados.at[index, 'Requisição_com_Uberabinha_pessimista'] = response_json_com_uberabinha_pessimista
    #Salva o arquivo excel com as requisições preenchidas        
    dados.to_excel(f'Oportunidades_Atualizado_{modo}.xlsx', index=False)
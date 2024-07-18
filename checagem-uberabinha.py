#Faz a impotação das bibliotecas necessarias para o código
import pandas as pd

# Caminho dos arquivos
file_bicycling = 'Oportunidades_Atualizado_bicycling.xlsx'
file_driving = 'Oportunidades_Atualizado_driving.xlsx'
file_walking = 'Oportunidades_Atualizado_walking.xlsx'

# Carregar os arquivos
df_bicycling = pd.read_excel(file_bicycling)
df_driving = pd.read_excel(file_driving)
df_walking = pd.read_excel(file_walking)

# A frase a ser procurada
frase_procura =  'Turn <b>right</b> onto <b>R. Uberabinha</b>'

# Inicializar a nova base de dados
checagem_uberabinha = []

# Iterar sobre os dataframes para verificar a presença da frase
for idx in range(len(df_bicycling)):
    # Informações do local
    nome = df_bicycling.loc[idx, 'Nome']
    endereco = df_bicycling.loc[idx, 'Endereço']
    latitude = df_bicycling.loc[idx, 'Latitude']
    longitude = df_bicycling.loc[idx, 'Longitude']
    
    # Garantir que as células são strings e salvar a resposta com os passos para cada modalidade
    req_bike = str(df_bicycling.loc[idx, 'Requisição_com_Uberabinha'])
    req_car = str(df_driving.loc[idx, 'Requisição_com_Uberabinha'])
    req_pe = str(df_walking.loc[idx, 'Requisição_com_Uberabinha'])
    
    if req_bike != 'nan': # Caso não possua frase na base de dados, significa que esta fora do raio de 3Km, logo não precisamos conferir
        # Procura em cada um, se a frase desejada está presente 
        virou_bike = frase_procura in req_bike
        virou_carro = frase_procura in req_car
        virou_pe = frase_procura in req_pe
        
        checagem_uberabinha.append({
            'Nome': nome,
            'Endereço': endereco,
            'Latitude': latitude,
            'Longitude': longitude,
            'Virou_bike': virou_bike,
            'Virou_carro': virou_carro,
            'Virou_pé': virou_pe
        })

# Converter para DataFrame
df_checagem_uberabinha = pd.DataFrame(checagem_uberabinha)

# Salvar a nova base de dados
output_file = 'Checagem_Uberabinha.xlsx'
df_checagem_uberabinha.to_excel(output_file, index=False)

output_file

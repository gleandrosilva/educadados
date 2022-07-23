import requests
import os

def download(url, directory):

    file = requests.get(url)
    if file.status_code == requests.codes.OK:
        with open(directory, 'wb') as new_file:
            new_file.write(file.content)
        print('Download do arquivo realizado com sucesso.')
    else:
        print(file.raise_for_status())
    
if __name__ == "__main__":
    URL = 'https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2020.zip'
    FOLDER = '../data'
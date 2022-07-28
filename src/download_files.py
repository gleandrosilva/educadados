from datetime import date
import requests
import os

def download(url: str, directory: str) -> None:
    """_Função que faz o download de um arquivo_

    Args:
        url (str): _arquivo a se baixado_
        directory (str): _pasta onde o arquivo vai ser baixado_
    """

    file = requests.get(url, verify=False)
    if file.status_code == requests.codes.OK:
        with open(directory, 'wb') as new_file:
            new_file.write(file.content)
        print(f'Download do arquivo realizado com sucesso. Salvo em {directory}')
    else:
        print(f'[ERRO] URL {url} não existe')
        print(file.raise_for_status())
    
if __name__ == "__main__":
    URL = 'https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{}.zip'
    FOLDER = '../data'

    last_year = date.today().year
    first_year = last_year - 10

    for year in range(first_year, last_year):
        file_name = os.path.join(FOLDER, f'microdados_censo_da_educacao_superior_{year}.zip')
        download(URL.format(year), file_name)
      
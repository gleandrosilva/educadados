import os
import zipfile as zip

import pandas as pd

from sqlalchemy import create_engine, Table, schema
from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv

#configurações de database mysql
load_dotenv()
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DBNAME = 'EDUCADADOS'

class DataBase:
    """_summary_
    """
    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def execute_query(self, query_or_dataframe: str, table_name: str = None) -> object:
        """Exucuta uma query no banco de dados, para CREATE, UPDATEM SELECT e DELETE.

        Args:
            query_or_dataframe (str): query a ser executada
            table_name (str, optional): tabela que recebe o insert. Defaults to None.

        Returns:
            object: execução da query
        """

        def connect_db() -> object:
            """Faz a conexão com o bando de dados MySql

            Args:
                user (str): usuário de conexão com o db
                password (str): senha de conexão
                host (str): endereço do db
                port (str): porta de conexão
                database (str): nome do db

            Returns:
                object: retorna o objeto de conexão do db
            """
            url_db = f'mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
            
            try:
                engine = create_engine(url_db)
                if not database_exists(engine.url):
                    create_database(engine.url)
                print('Conexão ao banco de dados estabelecida com sucesso!')            
            except Exception as error:
                print('Erro ao conectar ao banco de dados')
                print(error)                    
            return engine if engine else None

        def insert_dataframe(dataframe: object, table_name: str, engine: object) -> None:
            """Inserir dados no banco de dados

            Args:
                dataframe (object): Datafrane a ser inserido no banco de dados
                table_name (str): Nome da tabela no banco de dados
                engine (object): Objeto de conexão com o banco de dados

            Returns:
                None: Não retorna nenhum valor, apenas o resultado da query
            """
            # insert dos dados na tabela FT_OFERTA_CURSO
            metadata = schema.MetaData(bind=engine)
            table = Table(table_name, metadata, autoload=True)
            insert_rows_dict = dataframe.to_dict(orient='records')
            engine.execute(table.insert(), insert_rows_dict)
            return None

        engine = connect_db()
        engine.connect()
        if type(query_or_dataframe) != pd.core.frame.DataFrame:
            engine.execute(query_or_dataframe)
        elif type(query_or_dataframe) == pd.core.frame.DataFrame and table_name is not None:
            insert_dataframe(query_or_dataframe, table_name, engine)
        else:
            raise Exception('O tipo de dados passado não está correto ou não foi informado o nome da tabela!')
        return print('Query executada com sucesso!') if True else print('Erro ao executar a query')


if __name__ == "__main__":

    # criar objeto de conexão com o banco de dados
    new_data = DataBase(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DBNAME)

    # create table
    with open('../scripts/create_table_ft_oferta_curso.sql', 'r') as file:
        create_table_str = str(file.read())    

    # converte csv em dataframe
    folder = '../data/censo-educacao-superior/'
    files = os.listdir(folder)
    df = pd.DataFrame()

    for file in files:
        with zip.ZipFile(folder + file, 'r') as zip_file:
            for name in zip_file.namelist():
                if name.find('MICRODADOS_CADASTRO_CURSOS') > 0:
                    with zip_file.open(name) as csv_file:
                        df_tmp = pd.read_csv(csv_file, encoding='latin1', sep=';')
                        df = df.append(df_tmp)
                else:
                    pass         

    columns = ['NU_ANO_CENSO','CO_IES','CO_MUNICIPIO','CO_CINE_ROTULO','NO_CINE_ROTULO','TP_GRAU_ACADEMICO','TP_MODALIDADE_ENSINO','TP_NIVEL_ACADEMICO',
               'QT_VG_TOTAL','QT_INSCRITO_TOTAL','QT_ING','QT_MAT','QT_CONC']

    ft_oferta_curso = df[columns]
    name_columns = {'NU_ANO_CENSO': 'NR_ANO',
                    'CO_IES': 'CD_IES',
                    'CO_MUNICIPIO': 'CD_MUNICIPIO',
                    'CO_CINE_ROTULO': 'CD_CURSO',
                    'NO_CINE_ROTULO': 'NM_CURSO',
                    'TP_GRAU_ACADEMICO': 'CD_GRAU_ACADEMICO',
                    'TP_MODALIDADE_ENSINO': 'CD_MODALIDADE_ENSINO',
                    'TP_NIVEL_ACADEMICO': 'CD_NIVEL_ACADEMICO',
                    'QT_VG_TOTAL': 'QT_OFERTA_TOTAL',
                    'QT_INSCRITO_TOTAL': 'QT_INSCRITO_TOTAL',
                    'QT_ING': 'QT_INGRESSANTE_TOTAL',
                    'QT_MAT': 'QT_MATRICULA_TOTAL',
                    'QT_CONC': 'QT_CONCLUINTE_TOTAL'}

    ft_oferta_curso.rename(columns=name_columns, inplace=True)
    ft_oferta_curso.fillna(0, inplace=True)

    new_data.execute_query(ft_oferta_curso, 'FT_OFERTA_CURSO')

    # limpa a tabela antes de inserir os dados
    # engine.execute('DELETE FROM `EDUCADADOS`.`FT_OFERTA_CURSO`;')
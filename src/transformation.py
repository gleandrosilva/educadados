import os
import zipfile as zip

import pandas as pd

from sqlalchemy import create_engine, Table, schema, true
from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv


folder = '../data/censo-educacao-superior/'

files = os.listdir(folder)
df = pd.DataFrame()

for file in files:
    with zip.ZipFile(folder + file, 'r') as zip_file:
        for name in zip_file.namelist():
            if name.find('MICRODADOS_CADASTRO_CURSOS_{}') > 0:
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

#configurações de database mysql
load_dotenv()
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DBNAME = 'EDUCADADOS'

url_db = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DBNAME}'

engine = create_engine(url_db)
if not database_exists(engine.url):
    create_database(engine.url)

engine.connect()

# criando a tabela FT_OFERTA_CURSO
engine.execute(
    """
    CREATE TABLE IF NOT EXISTS FT_OFERTA_CURSO (
        `ID` INT KEY AUTO_INCREMENT,
        `NR_ANO` INT NULL,
        `CD_IES` INT NULL,
        `CD_MUNICIPIO` INT NULL,
        `CD_CURSO` VARCHAR(80) NULL,
        `CD_GRAU_ACADEMICO` INT NULL,
        `CD_MODALIDADE_ENSINO` INT NULL,
        `CD_NIVEL_ACADEMICO` INT NULL,
        `QT_OFERTA_TOTAL` INT NULL,
        `QT_INSCRITO_TOTAL` INT NULL,
        `QT_INGRESSANTE_TOTAL` INT NULL,
        `QT_MATRICULA_TOTAL` INT NULL,
        `QT_CONCLUINTE_TOTAL` INT NULL
    );
    """
)

# insert dos dados na tabela FT_OFERTA_CURSO
metadata = schema.MetaData(bind=engine)
table = Table('FT_OFERTA_CURSO', metadata, autoload=true)
insert_rows_dict = ft_oferta_curso.to_dict(orient='records')
engine.execute(table.insert(), insert_rows_dict)
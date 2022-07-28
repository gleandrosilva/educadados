import os
import zipfile as zip
import pandas as pd

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
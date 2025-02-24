import pandas as pd
import os
from typing import Dict
import xlwings as xw
from dependencies.functions import Functions
from time import sleep

class TratarDados:
    @staticmethod
    def sep_dados_por_empresas(path:str) -> list:
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado!")
        
        df = pd.read_excel(path)
        try:    
            df = df[['Empresa', 'Nº documento', 'Banco da empresa']]
        except KeyError as err:
            raise KeyError(f"Colunas não encontradas! -> {err}")

        
        
        
        empresas = df['Empresa'].dropna().unique().tolist()
        bancos = df['Banco da empresa'].dropna().unique().tolist()

        docs = []
        for empresa in empresas:
            for banco in bancos:
                temp = {}
                temp['docs'] = df[(df['Empresa'] == empresa) & (df['Banco da empresa'] == banco)]['Nº documento'].dropna().astype(int).tolist()
                if not temp['docs']:
                    continue
                temp['empresa'] = empresa
                temp['banco'] = banco
                docs.append(temp)
        
        return docs
    
    @staticmethod
    def load_previReceita(path:str) -> pd.DataFrame:
        app = xw.App(visible=False)
        wb = app.books.open(path)
        del wb.sheets[0]
        wb.save()
        wb.close()
        app.kill()
        
        Functions.fechar_excel(path)

        return pd.read_excel(path)
            
    
if __name__ == "__main__":
    pass

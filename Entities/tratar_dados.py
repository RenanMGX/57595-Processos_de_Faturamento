import pandas as pd
import os
from typing import Dict
import xlwings as xw
from dependencies.functions import Functions, P
from time import sleep
from typing import List


class TratarDados:
    @staticmethod
    def sep_dados_por_empresas(path:str, *, remover_empresas:List[str]=[]) -> list:
        remover_empresas = [empresa.upper() for empresa in remover_empresas]
        
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
            if empresa.upper() in remover_empresas:
                print(P(f"{empresa} foi removido", color='magenta'))
                continue
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
        
        ws = wb.sheets[1]
        
        table = ws.range('A1').expand('table').value        
        df = pd.DataFrame(table)
        
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        
        wb.close()
        app.kill()
        
        sleep(1)
        Functions.fechar_excel(path)

        return df
            
    
if __name__ == "__main__":
    pass

import pandas as pd
import os
from typing import Dict

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
                temp['empresa'] = empresa
                temp['banco'] = banco
                temp['docs'] = df[(df['Empresa'] == empresa) & (df['Banco da empresa'] == banco)]['Nº documento'].dropna().astype(int).tolist()
                docs.append(temp)
        
        return docs
            
    
if __name__ == "__main__":
    pass

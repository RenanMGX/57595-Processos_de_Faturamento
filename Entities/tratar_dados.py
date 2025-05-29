import pandas as pd
import os
from typing import Dict, Union
import xlwings as xw
from dependencies.functions import Functions, P
from time import sleep
from typing import List, Tuple
from formulas import formulas
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class TratarDados:
    @staticmethod
    def sep_dados_por_empresas(path:str, *, remover_empresas:List[str]=[]) -> list:
        remover_empresas = [empresa.upper() for empresa in remover_empresas]
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado!")
        
        df = pd.read_excel(path)
        try:    
            df = df[['Empresa', 'Nº documento', 'Banco da empresa', 'Solicitação de L/C']]
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
                temp['docs'] = df[
                    (df['Empresa'] == empresa) &
                    (df['Banco da empresa'] == banco) &
                    (df['Solicitação de L/C'].isna())
                    ]['Nº documento'].dropna().astype(int).tolist()
                #import pdb; pdb.set_trace()
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
    
    @staticmethod
    def generate_df_with_emails(*, df_clientes:pd.DataFrame, df_previsaoReceita:pd.DataFrame):
        df_previsaoReceita = df_previsaoReceita[
            ~df_previsaoReceita['Documento'].isna()
        ]
        
        df = df_previsaoReceita
        df['Email'] = df_previsaoReceita.apply(lambda row: formulas.get_email_principal(row, df_clientes), axis=1)
                
        return df[
                    [
                        "Código SPE",
                        "Empreendimento",
                        "Código Principal",
                        "Cliente Principal",
                        "Código Empreendimento",
                        "Código Bloco",
                        "Bloco",
                        "Unidade",
                        "Data Vencimento",
                        "Série",
                        "Parcela",
                        "Documento",
                        "Email"
                    ]
                ]
        
    @staticmethod
    def generate_files_to_send(*, df:pd.DataFrame, path:str) -> tuple:
        emails_to_send:Dict[str, Dict[str, Union[str,list]]] = {}
        #files_not_found:Dict[str, list] = {}

        df_files_not_found = pd.DataFrame()


        #print(type(emails_to_send), emails_to_send)
        count = 1
        for row, value in df.iterrows():
            print(P(f"Processando {count}/{len(df)}"), end="\r")
            count += 1
            
            bloco:str = str(value['Código Bloco'])
            bloco2 = bloco[1:] if bloco.startswith('0') else bloco.zfill(2)

            mes = str(value['Data Vencimento'].month).zfill(2)
            ano = str(value['Data Vencimento'].year)
            
            parcela = value['Parcela']
            parcela = str(int(parcela)) if isinstance(parcela, float) else parcela
            
            temp_file = f"{value['Código Empreendimento']}-{bloco}-{value['Unidade']}-{mes}-{ano}-{value['Série']}-{parcela}-{int(value['Documento'])}.pdf"
            temp_file_path = os.path.join(path, temp_file)
            temp_file2 = f"{value['Código Empreendimento']}-{bloco2}-{value['Unidade']}-{mes}-{ano}-{value['Série']}-{parcela}-{int(value['Documento'])}.pdf"
            temp_file2_path = os.path.join(path, temp_file2)    

            #import pdb; pdb.set_trace()
            
            if os.path.exists(temp_file_path):
                file = temp_file_path
            elif os.path.exists(temp_file2_path):
                file = temp_file2_path
            else:
                file = None
                
            if file:
                    
                    
                try:
                    emails_to_send[value['Email']]
                except KeyError:
                    emails_to_send[value['Email']] = {}    
                
                try:
                    emails_to_send[value['Email']]["files"].append(file) #type: ignore
                except KeyError:
                    emails_to_send[value['Email']]["files"] = [file] 
                
                emails_to_send[value['Email']]["nome"] = value['Cliente Principal']
                emails_to_send[value['Email']]["empreendimento"] = value['Empreendimento']
                emails_to_send[value['Email']]["date"] = value['Data Vencimento'].strftime('%B/%Y').capitalize()
                emails_to_send[value['Email']]["bloco"] = value['Bloco']
                emails_to_send[value['Email']]["unidade"] = str(value['Unidade'])
                emails_to_send[value['Email']]["empresa"] = value['Código SPE']
                
            else:
                value['file'] = temp_file_path
                df_files_not_found = pd.concat([df_files_not_found, value.to_frame().T])
        
        print()      
        return emails_to_send, df_files_not_found
    
if __name__ == "__main__":
    pass

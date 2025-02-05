from Entities.imobme import Imobme, datetime, P
from Entities.etapas import Etapa
from Entities.dependencies.functions import Functions
import Entities.utils as utils
from Entities.sap import SAP
from Entities.tratar_dados import TratarDados, pd
from typing import List, Dict
from time import sleep

import os
import json

lista_indices = [
    r'0,8% a.m.',
    r'0,5% a.m.',
    r'JUROS 1%',
    r'JUROS 0,5%',
    r'INCC',
    r'CDI',
    r'CDI 3% a.a.',
    r'IPCA',
    r'IPCA 12a.a.',
    r'IPCA 1%',
    r'POUPA 12',
    r'POUPA 15',
    r'POUPA 28',
    r'IGPM',
    r'IGPM 0,5%',
    r'IGPM 1%',
]

etapa = Etapa()

def primeiro_imobme_cobranca_global(date:datetime=datetime.now()) -> bool:
    print(P(f"Executando Imobme cobrança global em {date.strftime('%d/%m/%Y')}", color='yellow'))
    
    if not etapa.executed_month('imobme_cobranca_global'):
        bot = Imobme()
        if bot.verificar_indices(date=utils.primeiro_dia_ultimo_mes(date), lista_indices=lista_indices):
            if bot.cobranca(utils.primeiro_dia_proximo_mes(date), tamanho_mini_lista=12):
                etapa.save('imobme_cobranca_global')
                print(P("    Imobme Cobrança global executada com sucesso!", color='green'))
                return True
            else:
                print(P("    Erro ao executar Imobme cobrança global!", color='red'))
        else:
            print(P("    Erro ao verificar indices!", color='red'))
    else:
        print(P("    Imobme Cobrança global já foi executada este mês!", color='cyan'))
    return False
        
def segundo_rel_partidas_individuais(date: datetime=datetime.now()):
    print(P(f"Executando relatório partidas individuais em {date.strftime('%d/%m/%Y')}", color='yellow'))
    
    if etapa.executed_month('imobme_cobranca_global'):
        if not etapa.executed_month('rel_partidas_individuais'):
            sap = SAP()
            try:
                file_path = sap.relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
            except Exception as err:
                print(P(f"    Erro ao executar o processo! -> {err}", color='red'))
                return False
            
            if file_path:
                docs:list = TratarDados.sep_dados_por_empresas(file_path)
                sleep(3)
                Functions.fechar_excel(file_path)
                os.unlink(file_path)
                
                docs_path = os.path.join(os.getcwd(), 'docs.json')
                if os.path.exists(docs_path):
                    os.unlink(docs_path)
                    
                with open(docs_path, 'w') as file:
                    json.dump(docs, file)
                
                etapa.save('rel_partidas_individuais')
                print(P("    Relatório partidas individuais executado com sucesso!", color='green'))
                return True
            else:
                print(P("    Erro ao executar relatório partidas individuais!", color='red'))
        else:
            print(P("    Relatório partidas individuais já foi executado este mês!", color='cyan'))
    else:
        print(P("    Imobme Cobrança global não foi executada este mês!", color='magenta'))
        
def terceiro_gerar_arquivos_de_remessa():
    print(P("Executando geração de arquivos de remessa", color='yellow'))
    
    if etapa.executed_month('rel_partidas_individuais'):
        if not etapa.executed_month('gerar_arquivos_de_remessa'):
            sap = SAP()
            with open('docs.json', 'r') as file:
                data:List[Dict[str,object]] = json.load(file)
                
            for dado in data:
                try:
                    sap.gerar_arquivos_de_remessa(data=dado)
                except Exception as err:
                    print(P(f"    Erro ao executar o processo! -> {err}", color='red'))
                    continue
            sap.fechar_sap()
            etapa.save('gerar_arquivos_de_remessa')
            print(P("    Geração de arquivos de remessa executada com sucesso!", color='green'))
            return True
        else:
            print(P("    Geração de arquivos de remessa já foi executada este mês!", color='cyan'))
    else:
        print(P("    Relatório partidas individuais não foi executado este mês!", color='magenta'))
        
def quarto_verificar_lancamentos(date: datetime):
    print(P(f"Executando verificação de lançamentos em {date.strftime('%d/%m/%Y')}", color='yellow'))
    
    if etapa.executed_month('gerar_arquivos_de_remessa'):
        if not etapa.executed_month('verificar_lancamentos'):

            for _ in range(5):
                path = SAP().relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
                df = pd.read_excel(path)
                os.unlink(path)
                df = df.dropna(subset=['Conta'])
                if df[df['Solicitação de L/C'].isna()].empty:
                   etapa.save('verificar_lancamentos')
                   print(P("    Verificação de lançamentos executada com sucesso!", color='green'))
                   return True
                
                sleep(15)
            
            print(P("    Erro ao executar verificação de lançamentos!", color='red'))
        else:
            print(P("    Verificação de lançamentos já foi executada este mês!", color='cyan'))
    else:
        print(P("    Geração de arquivos de remessa não foi executada este mês!", color='magenta'))
    
    return False

def quinto_verificar_retorno_do_banco(date:datetime):
    print(P(f"Executando verificação de retorno do banco em {date.strftime('%d/%m/%Y')}", color='yellow'))
    
    if etapa.executed_month('verificar_lancamentos'):
        if not etapa.executed_month('verificar_retorno_do_banco'):
            path = SAP().relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
            df = pd.read_excel(path)
            os.unlink(path)
            df = df.dropna(subset=['Conta'])
            filtro = df[
                df['Chave referência 3'].isna()
            ]
            if not filtro.empty:
                empty_files_path = os.path.join(f"C:\\Users\\{os.getlogin()}\\Downloads", datetime.now().strftime("%Y%m%d%H%M%S_empty_files.xlsx"))
                filtro.to_excel(empty_files_path, index=False)
            
            etapa.save('verificar_retorno_do_banco')
            print(P("    Verificação de retorno do banco executada com sucesso!", color='green'))
            return True
               
        else:
            print(P("    Verificação de retorno do banco já foi executada este mês!", color='cyan'))
    else:  
        print(P("    Verificação de lançamentos não foi executada este mês!", color='magenta'))

if __name__ == "__main__":
    pass

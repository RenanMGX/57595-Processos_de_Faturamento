from Entities.imobme import Imobme, datetime, P
from Entities.etapas import Etapa
from Entities.dependencies.functions import Functions
import Entities.utils as utils
from Entities.sap import SAP
from Entities.tratar_dados import TratarDados
from typing import List, Dict
from time import sleep

import os
import json

lista_indices = [
    r'0,8% a.m.',
    r'0,5% a.m.',
    r'JUROS 1%',
    r'JUROS 0,5%',
    'INCC',
    'CDI',
    r'CDI 3% a.a.',
    'IPCA',
    'IPCA 12a.a.',
    'IPCA 1%',
    'POUPA 12',
    'POUPA 15',
    'POUPA 28',
    'IGPM',
    'IGPM 0,5%',
    'IGPM 1%',
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
            file_path = sap.relatorio_partidas_individuais_cliente(datetime(2024, 11, 1))
            
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
                    print(P(f"Erro ao executar o processo! -> {err}", color='red'))
                    continue
            sap.fechar_sap()
            etapa.save('gerar_arquivos_de_remessa')
            print(P("    Geração de arquivos de remessa executada com sucesso!", color='green'))
            return True
        else:
            print(P("    Geração de arquivos de remessa já foi executada este mês!", color='cyan'))
    else:
        print(P("    Relatório partidas individuais não foi executado este mês!", color='magenta'))

if __name__ == "__main__":
    pass

from Entities.imobme import Imobme, datetime
from  processos import Processos
#from datetime import datetime
from Entities.sap import SAP
from Entities.dependencies.functions import P
from Entities.dependencies.logs import Logs, traceback

if __name__ == "__main__":
    try:
        date = datetime.now()
        
        #processos = Processos(date, pasta=r'W:\BOLETOS_SEGUNDA_VIA_HML')
        processos = Processos(date)

        
        print(P('  ---> Iniciando Automação <---  \n', color='green'))
        
        # Etapa 1
        processos.imobme_cobranca_global(date=date, finalizar=True, etapa='1.imobme_cobranca_global') # ETAPA 1 OK
        
        # Etapa 2       
        processos.rel_partidas_individuais(date=date, etapa='2.rel_partidas_individuais', ultima_etapa='1.imobme_cobranca_global', remover_empresas=["P027"]) # ETAPA 2 OK
        
        # Etapa 3
        processos.gerar_arquivos_de_remessa(finalizar=True ,etapa='3.gerar_arquivos_de_remessa', ultima_etapa='2.rel_partidas_individuais')# ETAPA 3 OK
        
        # Etapa 4
        processos.verificar_lancamentos(date=date, etapa="4.verificar_lancamentos", ultima_etapa='3.gerar_arquivos_de_remessa') # ETAPA 4 OK
        
        # Etapa 5   
        processos.verificar_retorno_do_banco(date=date, etapa='5.verificar_retorno_do_banco', ultima_etapa='4.verificar_lancamentos') # ETAPA 5 OK
        
        # Etapa 6
        processos.gerar_boletos(finalizar=True, date=date, etapa='6.gerar_boletos', ultima_etapa='5.verificar_retorno_do_banco') # ETAPA 6 OK
        
        # Etapa 7  repetindo etapa 5 
        processos.verificar_retorno_do_banco(date=date, etapa='7.verificar_retorno_do_banco', ultima_etapa='6.gerar_boletos')
        
        # Etapa 8 repetindo etapa 6
        processos.gerar_boletos(date=date, etapa='8.gerar_boletos', ultima_etapa='7.verificar_retorno_do_banco')
        
        
        # Etapa 8
        ###processos.criptografar_boletos() # Esperar liberação do Financeiro
    except Exception as err:
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
        print(traceback.format_exc())
    
    # sap = SAP()
    # sap.gerar_boletos_no_sap(date)
    # sap.fechar_sap()
    
    
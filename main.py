from Entities.imobme import Imobme, datetime
from  processos import Processos
#from datetime import datetime
from Entities.sap import SAP
from Entities.dependencies.functions import P
from Entities.dependencies.logs import Logs, traceback

if __name__ == "__main__":
    try:
        date = datetime.now()
        
        processos = Processos(date)
        
        print(P('  ---> Iniciando Automação <---  \n', color='green'))
        
        processos.primeiro_imobme_cobranca_global(date=date, finalizar=True)
        
        processos.pre_segundo_verificar_documentos_imobme_para_sap(date=date)
        
        processos.segundo_rel_partidas_individuais(date=date) # para ser executado 1 dia depois
        
        processos.terceiro_gerar_arquivos_de_remessa()
        
        processos.quarto_verificar_lancamentos(date=date, finalizar=True) # para ser executado 1 dia depois
            
        processos.quinto_verificar_retorno_do_banco(date=date) # para ser executado 2 dia depois
        
        processos.sexto_gerar_boletos(date=date) # para ser executado 2 dia depois
        
        #processos.setimo_criptografar_boletos() # Esperar liberação do Financeiro
    except Exception as err:
        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
        print(traceback.format_exc())
    
    # sap = SAP()
    # sap.gerar_boletos_no_sap(date)
    # sap.fechar_sap()
    
    
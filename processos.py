from Entities.imobme import Imobme, datetime, P
from Entities.etapas import Etapa
import Entities.utils as utils

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

def imobme_cobranca_global(bot:Imobme, date:datetime=datetime.now()):
    print(P(f"Executando Imobme cobrança global em {date.strftime('%d/%m/%Y')}", color='yellow'))
    
    if not etapa.executed_month('imobme_cobranca_global'):
        if bot.verificar_indices(date=utils.primeiro_dia_ultimo_mes(date), lista_indices=lista_indices):
            if bot.cobranca(utils.primeiro_dia_proximo_mes(date), tamanho_mini_lista=12):
                etapa.save('imobme_cobranca_global')
                print(P("Imobme Cobrança global executada com sucesso!", color='green'))
                return True
            else:
                print(P("Erro ao executar Imobme cobrança global!", color='red'))
        else:
            print(P("Erro ao verificar indices!", color='red'))
    else:
        print(P("Imobme Cobrança global já foi executada este mês!", color='yellow'))

if __name__ == "__main__":
    pass

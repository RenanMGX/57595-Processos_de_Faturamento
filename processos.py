from Entities.imobme import Imobme, datetime
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

def cobranca_global(date:datetime=datetime.now()):
    bot = Imobme()
    if bot.verificar_indices(date=utils.primeiro_dia_ultimo_mes(date), lista_indices=lista_indices):
        return bot.cobranca(utils.primeiro_dia_proximo_mes(date), tamanho_mini_lista=12)

if __name__ == "__main__":
    pass

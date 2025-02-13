from copy import deepcopy
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta

def criar_listas_de_mini_listas(*, lista:list, tamanho_mini_lista:int) -> List[list]:
    lista = deepcopy(lista)
    result = []
    tamanho = int(len(lista)/tamanho_mini_lista)
    for _ in range(tamanho):
        lista_temporaria = []
        for _ in range(tamanho_mini_lista):
            lista_temporaria.append(lista.pop(0))
        result.append(lista_temporaria)
    if lista:
        result.append(lista)
    return result

def primeiro_dia_ultimo_mes(date:datetime) -> datetime:
    return (date - relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def primeiro_dia_proximo_mes(date:datetime) -> datetime:
    return (date + relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def primeiro_dia_mes(date:datetime) -> datetime:
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def ultimo_dia_mes(date:datetime) -> datetime:
    return (date + relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=1)


if __name__ == "__main__":
    print(ultimo_dia_mes(datetime.now()))
    print(type(datetime.now().year))
    
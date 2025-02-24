from copy import deepcopy
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Union
import os
import re
import shutil
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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

def ultimo_dia_proximo_mes(date:datetime) -> datetime:
    return (date + relativedelta(months=2)).replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=1)

def get_date_from_pdf(path:str) -> List[Dict[str, Union[str, datetime]]]:
    lista:List[Dict[str, Union[str, datetime]]] = []
    for file in os.listdir(path):
        file_path:str = os.path.join(path, file)
        if os.path.isfile(file_path):
            if file_path.lower().endswith('.pdf'):
                if (dateSTR:=re.search(r'-[0-9]{1,2}-[0-9]{4}-', file)):
                    dateSTR = dateSTR.group().strip('-').split('-')
                    mes, ano = dateSTR[0], dateSTR[1]
                    try:
                        date = datetime(int(ano), int(mes), 1)
                        lista.append({'file_path':file_path, 'date':date})
                    except Exception as err:
                        #print(type(err), err)
                        continue
    return lista

def mover_pdfs(path:str, *, pasta:str="Boletos"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} not found")
    files = get_date_from_pdf(path)
    for file in files:
        path_target = os.path.join(path, pasta, str(file['date'].year), str(file['date'].strftime("%B")).title()) #type: ignore
        if not os.path.exists(path_target):
            os.makedirs(path_target)
        
        path_target = os.path.join(path_target,os.path.basename(file['file_path'])) # type: ignore
        if os.path.exists(path_target):
            os.remove(path_target)
        shutil.move(file['file_path'], path_target) #type: ignore
        
        
if __name__ == "__main__":
    print(ultimo_dia_mes(datetime.now()))
    print(type(datetime.now().year))
    
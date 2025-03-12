from copy import deepcopy
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Union
import os
import re
import shutil
import locale
import json
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

def get_date_from_pdf(*, path:str, _date: datetime) -> List[Dict[str, Union[str, datetime]]]:
    lista:List[Dict[str, Union[str, datetime]]] = []
    for file in os.listdir(path):
        file_path:str = os.path.join(path, file)
        if os.path.isdir(file_path):
            continue
        
        try:
            file_date = os.path.basename(file_path)
            file_date = f"{file_date.split('-')[3]}/{file_date.split('-')[4]}"
        except:
            continue
        try:
            file_date = datetime.strptime(file_date, '%m/%Y') 
        except ValueError:
            continue
        #import pdb; pdb.set_trace()
        if (_date - file_date).days < 120:
            #print(f"{file} é menor que 90 dias  -- {(_date - file_date).days}")
            continue
        #print(f"{file} é maior que 30 dias  -- {(_date - file_date).days}")
        
        
        if os.path.isfile(file_path):
            if file_path.lower().endswith('.pdf'):
                _file_path = os.path.basename(file_path)
                if (dateSTR:=f"{_file_path.split('-')[3]}-{_file_path.split('-')[4]}"):
                    dateSTR = dateSTR.split('-')
                    mes, ano = dateSTR[0], dateSTR[1]
                    try:
                        date = datetime(int(ano), int(mes), 1)
                        lista.append({'file_path':file_path, 'date':date})
                    except Exception as err:
                        #print(type(err), err)
                        continue
    return lista

def mover_pdfs(path:str, *, pasta:str="Boletos", _date: datetime=datetime.now()):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} not found")
    files = get_date_from_pdf(path=path, _date=_date)
    #import pdb; pdb.set_trace()
    for file in files:
        continue
        path_target = os.path.join(path, pasta, str(file['date'].year), str(file['date'].strftime("%B")).title()) #type: ignore
        if not os.path.exists(path_target):
            os.makedirs(path_target)
        
        path_target = os.path.join(path_target,os.path.basename(file['file_path'])) # type: ignore
        if os.path.exists(path_target):
            os.remove(path_target)
        shutil.move(file['file_path'], path_target) #type: ignore
        
class jsonFile:
    @staticmethod
    def read(path:str):
        if not path.lower().endswith('.json'):
            raise Exception(f"File {path} is not a json file")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found")
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def write(path:str, data:dict|list) -> None:
        if not path.lower().endswith('.json'):
            raise Exception(f"File {path} is not a json file")
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file)
    
    @staticmethod
    def append(path:str, data:dict|list) -> None:
        if not path.lower().endswith('.json'):
            raise Exception(f"File {path} is not a json file")
        with open(path, 'a', encoding='utf-8') as file:
            json.dump(data, file)
            
    @staticmethod
    def delete(path:str) -> None:
        os.remove(path)
        
    @staticmethod
    def read_qualquer_arquivo(path:str) -> str:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()


if __name__ == "__main__":
    print(ultimo_dia_mes(datetime.now()))
    print(type(datetime.now().year))
    
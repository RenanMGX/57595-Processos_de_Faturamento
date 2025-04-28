from datetime import datetime
from dateutil.relativedelta import relativedelta
from dependencies.config import Config
import os
import json
from typing import Dict


class Etapa:
    @property
    def date(self):
        return self.__date
    
    @property
    def file_path(self):
        return self.__file_path
    
    def __init__(self) -> None:
        self.__date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if self.date.day <= int(Config()['param']['dias_ate_virar_mes']):
            self.__date = self.date - relativedelta(months=1)
        
        self.__file_path = os.path.join(os.getcwd(), 'etapas.json')
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as _file:
                json.dump({}, _file)
                
    def load(self):
        with open(self.file_path) as _file:
            return json.load(_file)
            
    def save(self, etapa:str):
        if not etapa:
            print("Sem Etapa para salvar")
            return
        data = self.load()
        
        if datetime.now().day <= int(Config()['param']['dias_ate_virar_mes']):
            data[etapa] = (datetime.now() - relativedelta(months=1)).isoformat()
        else:
            data[etapa] = datetime.now().isoformat()
        
        with open(self.file_path, 'w') as _file:
            json.dump(data, _file)
            
    def executed_today(self, etapa:str):
        data = self.load()
        if etapa in data:
            return self.date.date() == datetime.fromisoformat(data[etapa]).date()
        return False
    
    def executed_month(self, etapa:str):
        data = self.load()
        if etapa in data:
            return (self.date.month == datetime.fromisoformat(data[etapa]).month) and (self.date.year == datetime.fromisoformat(data[etapa]).year)
        return False
    
    
    def reset_etapa(self, etapa:str):
        data = self.load()
        if etapa in data:
            data.pop(etapa)
            
            with open(self.file_path, 'w') as _file:
                json.dump(data, _file)
        
        
if __name__ == "__main__":
    etapa = Etapa()
    #etapa._Etapa__date = datetime(2025, 2, 1)
    #etapa.save('teste')
    print(etapa.save('teste'))
    print(etapa.load())
    print(etapa.date)
    #etapa.reset_etapa('teste')
    #pass

import os
from getpass import getuser
import json

class SharepointFolders:
    @property
    def value(self):
        if self.__value:
            if os.path.exists(self.__value):
                return self.__value
            else:
                raise Exception(f"não foi possivel encontrar o caminho '{self.__value}'")
        raise Exception("value esta vazio")
            
    
    def __init__(self, target:str , *, initial_path:str=f'C:\\Users\\{getuser()}') -> None:
        self.__file_register_path = os.path.join(os.getcwd(), 'register.json')
        if not os.path.exists(self.__file_register_path):
            with open(self.__file_register_path, 'w', encoding='utf-8') as _file:
                json.dump({}, _file)
                
        self.__value = ""
        if (value:=self.__read().get(target)):
            self.__value = value
        else:
            self.__value = self.find_path(target=target, initial_path=initial_path)
            self.__register(target, self.__value)
        
    
    def __read(self) -> dict:
        with open(self.__file_register_path, 'r', encoding='utf-8')as _file:
            return json.load(_file)
        
    def __register(self, key, value):
        with open(self.__file_register_path, 'w', encoding='utf-8') as _file:
            json.dump({key:value}, _file)

    def find_path(self, *, target,  initial_path):
        base_path = initial_path
        for path, file, folder in os.walk(base_path):
            if target in path:
                return path
            
    def __repr__(self) -> str:
        return self.value
    
    def __str__(self) -> str:
        return self.value
    
if __name__ == "__main__":
    SharepointFolders("RPA - Dados\\Relatorios Auditoria\\KPMG").value
    
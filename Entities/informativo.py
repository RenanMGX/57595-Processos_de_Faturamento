from Entities.dependencies.logs import Logs, traceback
from Entities.dependencies.functions import P
from Entities.emails import Email
from typing import Literal
import os

class Informativo:
    def __init__(self, *, email:str="", assunto:str="") -> None:
        self.email = email
        self.assunto = assunto
        
    def sucess(
        self,
        msg:str,
        *,
        send_logs:bool = True,
        send_email:bool = True,
        anexo:list=[]
    ):
        print(P(msg, color='green'))
        
        if send_logs:
            Logs().register(status='Concluido', description=msg)
        
        if send_email: 
            if self.email:
                mandar_email = Email('email_debug')
                mandar_email.mensagem(
                        Destino=self.email,
                        Assunto=self.assunto,
                        Corpo_email=msg,
                        _type='plain'
                    )
                for a in anexo:
                    if os.path.exists(a):
                        mandar_email.Anexo(a)
                mandar_email.send()
                
    def error(
        self,
        msg:str,
        *,
        send_logs:bool = True,
        send_email:bool = True,
        anexo:list=[]
    ):
        print(P(msg, color='red'))
        
        if send_logs:
            Logs().register(status='Error', description=msg, exception=traceback.format_exc())
            
        if send_email: 
            if self.email:
                mandar_email = Email('email_debug')
                mandar_email.mensagem(
                        Destino=self.email,
                        Assunto=self.assunto,
                        Corpo_email=msg,
                        _type='plain'
                    )
                for a in anexo:
                    if os.path.exists(a):
                        mandar_email.Anexo(a)
                mandar_email.send()
    
if __name__ == "__main__":
    pass

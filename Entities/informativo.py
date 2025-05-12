from Entities.dependencies.logs import Logs, traceback
from Entities.dependencies.functions import P
from Entities.emails import Email
from typing import Literal
import os
from Entities.dependencies.gemini_ia import GeminiIA
from Entities.dependencies.credenciais import Credential


class  Informativo:
    def __init__(self, *, email:str="", cc:str="", assunto:str="") -> None:
        self.email = email
        self.assunto = assunto
        self.cc = cc
        
        self.ia = GeminiIA(
            token=Credential('GeminiIA-Token-Default').load()['token'],
            instructions="vc vai receber a atualização de status de uma automação analise o texto e deixe ele melhor e mais completo e coeso e formate para ser incluido apenas no corpo do email ignorando os outros campos, não coloque campos com sugestão para alteração seu texto tem que ser final pq ele sera entregue direto ao destinatario sem passar por revisão",
            temperature=0.5,
            )
        
    def sucess(
        self,
        msg:str,
        *,
        send_logs:bool = True,
        send_email:bool = True,
        anexo:list=[]
    ):
        print(P(msg, color='green'))
        
        try:
            email_melhorado = self.ia.perguntar(msg)
            if email_melhorado.text:
                msg = email_melhorado.text
        except:
            pass
        
        
        if send_logs:
            Logs().register(status='Concluido', description=msg)
        
        if send_email: 
            if self.email:
                mandar_email = Email('email_debug')
                mandar_email.mensagem(
                        Destino=self.email,
                        Assunto=self.assunto,
                        CC= self.cc if self.cc else "",
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
        try:
            email_melhorado = self.ia.perguntar(msg)
            if email_melhorado.text:
                msg = email_melhorado.text
        except:
            pass
        
        if send_logs:
            Logs().register(status='Error', description=msg, exception=traceback.format_exc())
            
        if send_email: 
            if self.email:
                mandar_email = Email('email_debug')
                mandar_email.mensagem(
                        Destino=self.email,
                        Assunto=self.assunto,
                        CC= self.cc if self.cc else "",
                        Corpo_email=msg,
                        _type='plain'
                    )
                for a in anexo:
                    if os.path.exists(a):
                        mandar_email.Anexo(a)
                mandar_email.send()
    
if __name__ == "__main__":
    mail = Informativo(email='renan.oliveira@patrimar.com', assunto='Teste')
    mail.sucess("Teste de email")

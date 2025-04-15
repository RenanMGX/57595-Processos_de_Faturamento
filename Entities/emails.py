import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders
from Entities.dependencies.config import Config
from Entities.dependencies.credenciais import Credential
from Entities.dependencies.functions import P
from typing import Literal
import os
import re
import utils
from multiprocessing import Lock
import traceback


class Email:
    def __init__(self, crd_email:Literal['email', 'email_debug']|str) -> None:
        self.__smtp_server = 'smtp-mail.outlook.com'
        self.__smtp_port = 587
        
        crd:dict = Credential(Config()['credenciais'][crd_email]).load()
        self.__username = crd['email']
        self.__password = crd['password']
        
        
    def mensagem(
                self, *,
                Destino:str|list,
                CC:str|list="",
                Assunto:str= "",
                Corpo_email:str,
                _type:Literal['plain', 'html']='plain'
            ):
        
        msg = MIMEMultipart()
        msg['From'] = self.__username
        msg['To'] = Destino if isinstance(Destino, str) else ','.join(Destino)
        if CC:
            msg['CC'] = CC if isinstance(CC, str) else ','.join(CC)
        msg['Subject'] = Assunto
        
        msg.attach(MIMEText(Corpo_email, _type, 'utf-8'))

        self.__msg = msg
        return self
        
    def Anexo(self, Attachment_path:str):
        try:
            self.__msg
            if not os.path.exists(Attachment_path):
                raise FileNotFoundError(f"Arquivo não encontrado '{Attachment_path}'")
            
            filename = os.path.basename(Attachment_path)
            with open(Attachment_path, 'rb') as _file:
                part = MIMEApplication(_file.read(), Name=filename)
                # part = MIMEBase('application', 'octet-stream')
                # part.set_payload(_file.read())
                # encoders.encode_base64(part)
                # part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            part['Content-Disposition'] = f'attachment; filename="{filename}"'        
            self.__msg.attach(part)
            
            return self
        except KeyError:
            raise Exception(f"Crie um corpo de email primeiro usando '.mensagem'")
    
    def addImagemCid(self, *, Attachment_path:str, tag:str):
        try:
            self.__msg
            if not os.path.exists(Attachment_path):
                raise FileNotFoundError(f"Arquivo não encontrado '{Attachment_path}'")
                
            filename = os.path.basename(Attachment_path)
            with open(Attachment_path, 'rb') as _file:
                img_data = _file.read()
            
            imagem = MIMEImage(img_data)
            imagem.add_header('Content-ID', f'<{tag}>')
            
            self.__msg.attach(imagem)
            return self
        except KeyError:
            raise Exception(f"Crie um corpo de email primeiro usando '.mensagem'")
          
    
    def send(self, *, msg_envio:str=""):
        try:
            self.__msg
        except KeyError:
            print(P("Crie um corpo para o email primeiro usando '.mensagem'", color='red'))
        
        destinatarios = []
        for campo in ['To', 'CC']:
            emails = self.__msg.get(campo, '')
            if emails:
                # Separa os endereços por vírgula ou ponto e vírgula e remove espaços em branco
                enderecos = re.split(r'[;,]', emails)
                destinatarios += [email.strip() for email in enderecos if email.strip()]

        with smtplib.SMTP(self.__smtp_server, self.__smtp_port) as server:
            server.starttls()
            server.login(self.__username, self.__password)
            server.sendmail(self.__msg['From'], destinatarios, self.__msg.as_string())
            
        if msg_envio:
            print(P(f"{msg_envio} - Emai enviado", color='green'))
        else:
            print(P("Emai enviado", color='green'))
            
        del self.__msg

lock = None

def set_lock(l):
    global lock
    lock = l

        
class EmailToClient:
    @staticmethod
    def send(_file: tuple, mensagem_html_path:str, emails_to_delete_path:str, email_origin:Literal['email', 'email_debug'] = 'email'):
        email:str = _file[0]
        dados:dict = _file[1]
        
        for _ in range(5):
            try:
                
                send_email:Email = Email(email_origin)
                
                empresa:str = dados['empresa']
                                
                empresa = "Patrimar" if empresa.upper().startswith("P") else "Novolar" if empresa.upper().startswith("N") else ""
                                
                assunto = f"Boleto {empresa} - {dados['date']} - {dados['empreendimento']} - {dados['bloco']} - Unidade {dados['unidade']}"
                                
                                
                msg = utils.jsonFile.read_qualquer_arquivo(os.path.join(mensagem_html_path, f'{empresa.lower()}.html'))

                msg = msg.replace("{{teste}}", "")
                                    
                msg = msg.replace("{{nome_empreendimento}}", dados['empreendimento'])
                msg = msg.replace("{{bloco}}", dados['bloco'])
                msg = msg.replace("{{unidade}}", f"Unidade {dados['unidade']}")
                msg = msg.replace("{{nome_cliente}}", dados['nome'].title())
                msg = msg.replace("{{data}}", dados['date'])
                
                target_email:str|list = ""                                         
                if email.startswith('1'):
                    target_email = [
                        email,
                        email[1:]
                    ]
                else:
                    target_email = email
                                       
                send_email.mensagem(
                    Destino=target_email,
                    #Destino='renan.oliveira@patrimar.com.br',
                    Assunto=assunto,
                    CC = "",
                    Corpo_email=msg,
                    _type='html'
                )
                                
                for file in dados['files']:
                    send_email.Anexo(
                        Attachment_path=file
                    )
                                
                                
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', f'emp_{empresa.lower()}.png'), tag="emp_header")  
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', f'logo_{empresa.lower()}.png'), tag="logo_header")
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', f'patrimar_vertical.png'), tag='patrimar_vertical')
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', f'novolar_vertical.png'), tag='novolar_vertical')
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', f'bt_portal_{empresa.lower()}.png'), tag='botao')
                                
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', 'icons', f'email.png'), tag='icon-email')
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', 'icons', f'tel.png'), tag='icon-tel')
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', 'icons', f'whatsapp.png'), tag='icon-whatsapp')
                send_email.addImagemCid(Attachment_path=os.path.join(mensagem_html_path, 'img', 'icons', f'internet.png'), tag='icon-internet')
                                
                send_email.send(msg_envio=f"    Email enviado para {email} - assunto: {assunto}")    
                
                with lock: #type: ignore
                    emails_to_delete:list = utils.jsonFile.read(emails_to_delete_path)
                    emails_to_delete.append(email)
                    utils.jsonFile.write(emails_to_delete_path, emails_to_delete)
                return
            except smtplib.SMTPDataError:
                print(P(f"    Erro ao enviar email para {email} tentando novamente!", color='yellow'))
                continue
            except Exception as err:
                print(P(f"    Erro ao enviar email para {email} - {type(err)}", color='red'))
                print(traceback.format_exc())
                return
        
        print(P(f"    Erro ao enviar email para {email} - Timeout", color='red'))
        
if __name__ == "__main__":
    pass

from selenium.webdriver.chrome.options import Options
from dependencies.navegador_chrome import NavegadorChrome as Nav
from dependencies.navegador_chrome import By, Keys, P, Select, WebElement
from dependencies.config import Config
from dependencies.credenciais import Credential
from time import sleep
from datetime import datetime
from typing import List, Dict, Union
from copy import deepcopy
import exceptions
import re
import os
import Entities.utils as utils
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


class Imobme(Nav):
    """
    Classe que representa interações com o sistema Imobme.
    """    
    @property
    def base_url(self) -> str:
        """
        Retorna a parte inicial (base) da URL do sistema.

        Returns:
            str: URL base do sistema.
        """
        if (url:=re.search(r'[A-z]+://[A-z0-9.]+/', self.__crd['url'])):
            return url.group()
        raise exceptions.UrlError("URL inválida!")
    
    @staticmethod
    def verify_login(func):
        """
        Decorator que verifica se o usuário está logado antes de executar a função.

        Args:
            func (Callable): Função a ser decorada.

        Returns:
            Callable: Função decorada.
        """
        def wrap(*args, **kwargs):
            self:Imobme = args[0]
            
            tag_html = self.find_element(By.TAG_NAME, 'html').text
            if "Imobme - Autenticação" in tag_html:
                print(P("Efetuando login...", color='yellow'))
                sleep(1)
                self.find_element(By.ID, 'login').send_keys(self.__crd['login'])
                t_password = self.find_element(By.ID, 'password')
                t_password.send_keys(self.__crd['password'])
                
                print(P("Aguardando resposta...", color='yellow'))
                t_password.send_keys(Keys.ENTER)                
                
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if "\nLogin não encontrado.\n" in self.find_element(By.TAG_NAME, 'html').text:
                    print(P("Login não encontrado!", color='red'))
                    raise exceptions.LoginError("Login não encontrado!")
                
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if (t_senha_invalida:=re.search(r'Senha Inválida. Número de Tentativas Restantes: [0-9]', tag_html)):
                    print(P(t_senha_invalida.group(), color='red'))
                    raise exceptions.LoginError(t_senha_invalida.group())
                
                tag_html = self.find_element(By.TAG_NAME, 'html').text
                if "\nUsuário já logado!\n" in self.find_element(By.TAG_NAME, 'html').text:
                    self.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/button[1]').click()
                
                #import pdb;pdb.set_trace()
                print(P("Login efetuado com sucesso!", color='green'))
                sleep(1)

            result = func(*args, **kwargs)

            return result
        return wrap
    
    def __init__(self):
        self.__crd:dict = Credential(Config()['credenciais']['imobme']).load()
        
        super().__init__(download_path=Config()['path']['download'], save_user=True)
        
        self.__load_page('Autenticacao/Login')
        
    
    def __load_page(self, endpoint:str):
        """
        Constrói a URL final e carrega a página solicitada.

        Args:
            endpoint (str): Caminho adicional a ser anexado à URL base.

        Returns:
            None
        """
        if not endpoint.endswith('/'):
            endpoint += '/'
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        url = os.path.join(self.base_url, endpoint)
        print(P(f"Carregando página: {url}...          ", color='yellow'))  
        self.get(url)
        
    def __esperar_carregamento(self, *, initial_wait:Union[int, float]=1):
        """
        Aguarda o carregamento de elementos na página.

        Args:
            initial_wait (float): Tempo inicial de espera.

        Returns:
            None
        """
        sleep(initial_wait)
        while self._find_element(By.ID, 'feedback-loader').text == 'Carregando':
            print(P("Aguardando carregar página...                ", color='yellow'), end='\r')
            sleep(1)
        print(end='\r')
    
    @verify_login     
    def _find_element(self, by=By.ID, value: str | None = None, *, timeout: int = 10, force: bool = False, wait_before: int | float = 0, wait_after: int | float = 0) -> WebElement:
        """
        Envolve find_element com verificação de login.

        Args:
            by: Tipo de busca (ex: By.ID, By.XPATH).
            value (str | None): Valor para busca do elemento.
            timeout (int): Tempo de tentativas em segundos.
            force (bool): Retorna elemento HTML se não for encontrado.
            wait_before (float): Intervalo antes da busca.
            wait_after (float): Intervalo após a busca.

        Returns:
            WebElement: Elemento encontrado ou o HTML.
        """
        return super().find_element(by, value, timeout=timeout, force=force, wait_before=wait_before, wait_after=wait_after)
    
    @verify_login  
    def cobranca(self, date: datetime, *, tamanho_mini_lista=10) -> bool:
        """
        Executa rotinas de cobrança para uma data específica.

        Args:
            date (datetime): Data para a qual será realizada a cobrança.
            tamanho_mini_lista (int): Tamanho de cada lista de empreendimentos.

        Returns:
            bool: True se a cobrança for realizada com sucesso.
        """
        self.__load_page('CalculoMensal/Cobranca')
        print(P("Aguardando carregar página...                           ", color='yellow'))
        
        #import pdb;pdb.set_trace()
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/button').click()
        t_ul = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/ul')
        lista_empreendimentos:List[str] = [element.text for element in t_ul.find_elements(By.TAG_NAME, 'li') if (element.text != '') and (element.text != 'Todos')]
        
        empreendimentos:List[List[str]] = utils.criar_listas_de_mini_listas(lista=lista_empreendimentos, tamanho_mini_lista=tamanho_mini_lista)
        
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/button').click()
        
        cont = 0   
        for empreendimento in empreendimentos:
            cont += 1
            for _ in range(5):
                try:
                    self.__load_page('CalculoMensal/Cobranca')
                    self.__esperar_carregamento()
                    self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/button').click()
                    
                    t_ul = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/ul')
                    for element in [element for element in t_ul.find_elements(By.TAG_NAME, 'li') if (element.text != '') and (element.text != 'Todos')]:
                        if element.text in empreendimento:
                            element.click()
                    
                    
                    #elemento_empreendimento['element'].click() #type: ignore
                    #self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/ul/li[2]/a/label/input').click() # selecionar todos
                    #self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/ul/li[3]/a/label').click() # selecionar primeiro empreendimento
                    self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[4]/div[1]/div/button').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Empreendimentos Selecionado...                  ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)        
                    self._find_element(By.ID, 'Mes_chzn').click()
                    t_buscar_mes = self._find_element(By.XPATH, '//*[@id="Mes_chzn"]/div/div/input')
                    t_buscar_mes.clear()
                    t_buscar_mes.send_keys(date.strftime('%B').capitalize())
                    t_buscar_mes.send_keys(Keys.ENTER)
                    print(P(f"[{cont}/{len(empreendimentos)}] | Mês Selecionado...                 ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)
                    t_ano = self._find_element(By.ID, 'ano')
                    t_ano.clear()
                    t_ano.send_keys(date.strftime('%Y'))
                    print(P(f"[{cont}/{len(empreendimentos)}] | Ano Selecionado...                   ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)
                    t_periodo = self._find_element(By.ID, 'txtDataLancamento')
                    t_periodo.clear()
                    t_periodo.send_keys(date.strftime('%d%m%Y'))
                    self._find_element(By.XPATH, '//*[@id="Content"]/section/div/div/div/div[1]/h4').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Período Selecionado...                 ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)
                    self._find_element(By.ID, 'btnNovo').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Procurando Faturamentos...               ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)
                    self._find_element(By.ID, 'Salvar').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Executando Faturamentos...                  ", color='yellow'), end='\r')
                    
                    print(end='\r')
                    
                    self.__esperar_carregamento(initial_wait=5)
                    if (t_error:=self._find_element(By.ID, 'divMsgError').text):
                        print(P(t_error, color='red'))
                        raise exceptions.CobrancaError(t_error)

                    self.__esperar_carregamento()
                    if (t_alerta:=self._find_element(By.ID, 'divAlert').text):
                        print(P(f"[{cont}/{len(empreendimentos)}] | {empreendimento} - {t_alerta}", color='cyan'))
                        #return True
                        
                    self.__esperar_carregamento()
                    break
                except Exception as err:
                    #print(P(f"Erro: {err}", color='red'))
                    if _ == 4:
                        print(P(f"Erro: {err}", color='red'))
                        raise exceptions.CobrancaError(f"Erro: {err}")
                    continue
                    
        
        print(P("Faturamentos realizados com sucesso!", color='green'))
        return True

    @verify_login
    def verificar_indices(self, *, date: datetime, lista_indices:List[str]) -> bool:
        """
        Verifica se os índices informados estão aprovados na data especificada.

        Args:
            date (datetime): Data de referência.
            lista_indices (List[str]): Lista de nomes dos índices a serem verificados.

        Returns:
            bool: True se todos os índices estiverem aprovados, caso contrário False.
        """
        lista_indices = deepcopy(lista_indices)
        self.__load_page('Indice/Valores')
        
        self.__esperar_carregamento()
        self._find_element(By.XPATH, '//*[@id="AgreementTabs"]/li[2]/a').click()
        
        # t_indices = self._find_element(By.ID, 'ddlIndiceBase_chzn')
        # t_indices.click()
        # lista_indices = [indice.text for indice in t_indices.find_elements(By.TAG_NAME, 'li') if indice.text != 'Todos']
        # t_indices.click()
        self.__esperar_carregamento()
        self._find_element(By.ID, 'txtData').send_keys(date.strftime('%d%m%Y'))
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[1]/h4').click()

        self.__esperar_carregamento()
        t_body = self._find_element(By.ID, 'tblIndiceAprovacao')
        
        for status in t_body.find_elements(By.TAG_NAME, 'tr'):
            for indice in lista_indices:
                if indice in status.text:
                    if 'Aprovado' in status.text:
                        lista_indices.remove(indice)
                        
        if not lista_indices:
            print(P("Todos os indices estão aprovados!", color='green'))
            return True
        
        print(P("Os seguintes indices não estão aprovados:", color='red'))
        print(P(lista_indices, color='red'))
        return False
        
        
        
        
if __name__ == '__main__':
    pass

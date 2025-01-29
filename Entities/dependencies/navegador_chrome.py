from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from functions import P
from time import sleep
from typing import List, Union
import os

class ElementNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class PageError(Exception):
    """
    Exceção lançada quando ocorre falha no carregamento de página.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NavegadorChrome(Chrome):
    @property
    def default_timeout(self):
        """
        Retorna o tempo padrão de carregamento de página definido pelo navegador.

        Returns:
            int | float: Valor do timeout padrão.
        """
        return self.__default_timeout
    
    """
    Classe que estende o navegador Chrome, adicionando configurações personalizadas.
    """
    def __init__(self, 
                 options: Union[Options, None] = None, 
                 service = None, 
                 keep_alive = True, 
                 speak:bool=False,
                 download_path:str="",
                 save_user:bool = False,
        ):
        """
        Construtor do NavegadorChrome.

        Args:
            options (Union[Options, None]): Opções para o Chrome.
            service: Serviço responsável por iniciar o ChromeDriver.
            keep_alive (bool): Mantém o driver vivo após execução.
            speak (bool): Exibe mensagens de status no console.
            download_path (str): Diretório onde arquivos serão baixados.
            save_user (bool): Utiliza diretório de usuário salvo no Chrome.

        Returns:
            None
        """
        # Cria diretório de download, se necessário
        if download_path:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            prefs:dict = {"download.default_directory": download_path}
            if options:
                options.add_experimental_option("prefs", prefs)
            else:
                options = Options()
                options.add_experimental_option("prefs", prefs)
        
        if save_user:
            if options:
                options.add_argument(f"user-data-dir=C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google")
            else:
                options = Options()
                options.add_argument(f"user-data-dir=C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google")
        

        super().__init__(options, service, keep_alive) #type: ignore
        
        self.__default_timeout = self.timeouts.page_load
        
        self.speak:bool = speak 
        
    def find_element(
        self, 
        by=By.ID, 
        value: str | None = None, 
        *, 
        timeout:int=10, 
        force:bool=False, 
        wait_before:int|float=0, 
        wait_after:int|float=0
    ) -> WebElement:
        """
        Localiza um único elemento na página, com tentativas repetidas.

        Args:
            by: Tipo de busca (ex: By.ID, By.XPATH).
            value (str | None): Valor para busca do elemento.
            timeout (int): Tempo total de tentativas (em segundos).
            force (bool): Força o retorno do elemento HTML caso não seja encontrado.
            wait_before (float): Intervalo antes de iniciar a busca.
            wait_after (float): Intervalo após encontrar o elemento.

        Returns:
            WebElement: Elemento localizado ou, se 'force' for True e não encontrado,
                        retorna o elemento HTML principal.
        """
        # Espera antes de iniciar (caso necessário)
        if wait_before > 0:
            sleep(wait_before)
        for _ in range(timeout*4):
            try:
                result = super().find_element(by, value)
                print(P(f"({by=}, {value=}): Encontrado com!", color='green')) if self.speak else None
                if wait_after > 0:
                    sleep(wait_after)
                return result
            except NoSuchElementException:
                pass                

            sleep(.25)
        
        if force:
            print(P(f"({by=}, {value=}): não encontrado, então foi forçado!", color='yellow')) if self.speak else None
            return super().find_element(By.TAG_NAME, 'html')
        
        print(P(f"({by=}, {value=}): não encontrado! -> erro será executado", color='red')) if self.speak else None
        raise ElementNotFound(f"({by=}, {value=}): não encontrado!")

    def find_elements(
        self, 
        by=By.ID, 
        value: str | None = None, 
        *, 
        timeout:int=10, 
        force:bool=False,
        wait_before:int|float=0, 
        wait_after:int|float=0
    ) -> List[WebElement]:
        """
        Localiza vários elementos na página, com tentativas repetidas.

        Args:
            by: Tipo de busca (ex: By.ID, By.XPATH).
            value (str | None): Valor para busca.
            timeout (int): Tempo total de tentativas (em segundos).
            force (bool): Retorna lista vazia caso não encontre elementos.
            wait_before (float): Intervalo antes de iniciar a busca.
            wait_after (float): Intervalo após encontrar os elementos.

        Returns:
            List[WebElement]: Lista de elementos localizados ou vazia, caso 'force' seja True.
        """
        # Espera antes de iniciar (caso necessário)
        if wait_before > 0:
            sleep(wait_before)
        for _ in range(timeout*4):
            try:
                result = super().find_elements(by, value)
                print(P(f"({by=}, {value=}): Encontrado com Sucesso!", color='green')) if self.speak else None
                if wait_after > 0:
                    sleep(wait_after)
                return result
            except NoSuchElementException:
                pass                

            sleep(.25)
        
        if force:
            print(P(f"({by=}, {value=}): não encontrado, então foi forçado!", color='yellow')) if self.speak else None
            return []
        
        print(P(f"({by=}, {value=}): não encontrado! -> erro será executado", color='red')) if self.speak else None
        raise ElementNotFound(f"({by=}, {value=}): não encontrado!")
    
    def get(self, url: str) -> None:
        """
        Carrega a URL especificada com tentativas de reenvio.

        Args:
            url (str): Endereço da página que será carregada.

        Returns:
            None
        """
        self.set_page_load_timeout(3)
        for _ in range(10):
            try:
                result = super().get(url)
                result = super().get(url)
                sleep(1)
                self.set_page_load_timeout(self.default_timeout)
                return result
            except:
                if _ == 9:
                    raise PageError("Página não encontrada!")
        
        
        

if __name__ == "__main__":
    pass

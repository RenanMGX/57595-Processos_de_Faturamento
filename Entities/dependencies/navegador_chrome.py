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
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NavegadorChrome(Chrome):
    @property
    def default_timeout(self):
        """
        Retorna o timeout padrão configurado para o carregamento de páginas.
        
        Esse valor é definido na inicialização a partir de self.timeouts.page_load,
        permitindo que métodos como get() reajustem o tempo de espera.

        Returns:
            int or float: Valor do timeout padrão.
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
                 headless:bool=True
        ):
        """
        Inicializa o navegador com configurações customizadas e gerencia o diretório de downloads e perfil de usuário.

        Fluxo Detalhado:
          1. Se 'download_path' for informado, verifica se o diretório existe – caso contrário, cria-o.
          2. Configura as preferências do Chrome para utilizar o diretório de downloads.
          3. Se 'save_user' for True, adiciona argumento para manter dados do usuário.
          4. Chama o construtor da classe base Chrome, passando as opções configuradas.
          5. Define o atributo __default_timeout com o valor de timeouts.page_load.
          6. Armazena o flag 'speak' para a exibição condicional de mensagens.
          
        Args:
            options (Union[Options, None]): Opções avançadas para o Chrome.
            service: Serviço que controla o ChromeDriver.
            keep_alive (bool): Determina se o driver permanece ativo após a execução.
            speak (bool): Ativa mensagens no console em tempo de execução.
            download_path (str): Diretório de destino para arquivos baixados.
            save_user (bool): Ativa o uso do perfil do usuário para persistência.
            
        Returns:
            None
        """
        # Cria diretório de download, se necessário
        if options is None:
            options = Options()
        
        if download_path:
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            prefs:dict = {"download.default_directory": download_path}
            self.download_path = download_path
            options.add_experimental_option("prefs", prefs)
        
        if save_user:
            options.add_argument(f"user-data-dir=C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google")
                
        if headless:
            options.add_argument("--headless")  # Ativa o modo headless
            options.add_argument("--disable-gpu")  # Desativa o uso de GPU (opcional)
            options.add_argument("--window-size=1920,1080")  # Define o tamanho da janela (opcional)
            options.add_argument("--no-sandbox")  # Necessário em alguns ambientes Linux
            options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória compartilhada         
        

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
        Localiza um único elemento na página, realizando diversas tentativas.

        Fluxo Detalhado:
          1. Se 'wait_before' for especificado, aguarda o tempo definido.
          2. Tenta, em um loop (com passos de 0.25 s e número total definido por timeout*4), localizar o elemento.
             - Se encontrado: opcionalmente exibe mensagem (quando speak=True) e espera 'wait_after'.
             - Retorna o elemento imediatamente.
          3. Se nenhuma tentativa for bem-sucedida:
             - Se force=True, retorna o elemento que representa a tag 'html' como fallback.
             - Caso contrário, imprime mensagem de erro (se speak=True) e lança ElementNotFound.
        
        Args:
            by: Estratégia para encontrar o elemento (ex.: By.ID, By.XPATH).
            value (str | None): Valor que identifica o elemento.
            timeout (int): Tempo total em segundos para tentar localizar o elemento.
            force (bool): Se True, utiliza fallback no caso de não encontrar.
            wait_before (int|float): Tempo de espera antes do início das tentativas.
            wait_after (int|float): Tempo de espera após encontrar o elemento.
        
        Returns:
            WebElement: Elemento encontrado ou fallback (tag 'html') se force for True.
        
        Raises:
            ElementNotFound: Caso o elemento não seja localizado e force seja False.
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
        Localiza vários elementos na página com tentativas repetidas.

        Fluxo:
          1. Aguarda um tempo inicial se 'wait_before' for informado.
          2. Em loop (até timeout*4 iterações):
              - Tenta buscar elementos via método da classe base.
              - Se encontrados, exibe mensagem (quando speak=True), aguarda 'wait_after' e retorna a lista.
          3. Se não encontrar e force for True, retorna uma lista vazia.
          4. Caso contrário, lança a exceção ElementNotFound.
        
        Args:
            by: Método de busca (por exemplo, By.ID ou By.XPATH).
            value (str | None): Texto ou valor a ser procurado.
            timeout (int): Tempo total de tentativa (em segundos).
            force (bool): Se True, retorna lista vazia caso nenhum elemento seja localizado.
            wait_before (float): Espera inicial antes de iniciar a busca.
            wait_after (float): Espera adicional após encontrar os elementos.
        
        Returns:
            List[WebElement]: Lista com os elementos encontrados.
        
        Raises:
            ElementNotFound: Se nenhum elemento for achado e force for False.
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
        Carrega a URL especificada em múltiplas tentativas, ajustando o timeout para garantir o sucesso.

        Fluxo:
          1. Reduz o tempo de timeout para 3 segundos para tentar um carregamento rápido.
          2. Em um loop de 10 tentativas:
             - Tenta carregar a página pelo método da classe base.
             - Aguarda 1 segundo para estabilizar o carregamento.
             - Caso consiga carregar, redefine o timeout para o valor padrão e retorna.
          3. Se todas as tentativas falharem, lança um PageError informando que a página não foi encontrada.
        
        Args:
            url (str): Endereço da página a ser carregada.
        
        Returns:
            None
        
        Raises:
            PageError: Se a página não puder ser carregada após 10 tentativas.
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
    bot = NavegadorChrome(speak=False, download_path="C:\\Users\\Patrimar\\Downloads", headless=False)
    bot.get("https://www.google.com")
    input("Pressione Enter para sair...")

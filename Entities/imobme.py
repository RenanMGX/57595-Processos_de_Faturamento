from selenium.webdriver.chrome.options import Options
from dependencies.navegador_chrome import NavegadorChrome as Nav
from dependencies.navegador_chrome import By, Keys, P, Select, WebElement
from dependencies.config import Config
from dependencies.credenciais import Credential
from dependencies.logs import Logs
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
    @property
    def base_url(self) -> str:
        if (url:=re.search(r'[A-z]+://[A-z0-9.]+/', self.__crd['url'])):
            return url.group()
        raise exceptions.UrlError("URL inválida!")
    
    @staticmethod
    def verify_login(func):
        def wrap(*args, **kwargs):
            self:Imobme = args[0]
            
            tag_html = self.find_element(By.TAG_NAME, 'html').text
            if "Imobme - Autenticação" in tag_html:
                print(P("Efetuando login...", color='yellow'))
                sleep(3)
                self.find_element(By.ID, 'login').send_keys(self.__crd['login'])
                t_password = self.find_element(By.ID, 'password')
                t_password.send_keys(self.__crd['password'])
                
                print(P("Aguardando resposta...", color='yellow'))
                t_password.send_keys(Keys.ENTER)                
                
                sleep(2)
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
    
    def __init__(self, download_path:str=""):
        self.__crd:dict = Credential(Config()['credenciais']['imobme']).load()
        
        if not download_path:
            download_path = Config()['path']['download']
        
        if not os.path.exists(download_path):
            download_path = f"C:\\Users\\{os.getlogin()}\\Downloads"
        
        print(P(f"    Navegador DownloadPath {download_path=}   ", color='yellow'))
        super().__init__(download_path=download_path, save_user=True)
        
        self.__load_page('Autenticacao/Login')
        sleep(3)
        self.__load_page('Autenticacao/Login')
        self.maximize_window()
        
    
    def __load_page(self, endpoint:str):
        if not endpoint.endswith('/'):
            endpoint += '/'
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]
        
        url = os.path.join(self.base_url, endpoint)
        print(P(f"Carregando página: {url}...          ", color='yellow'))  
        self.get(url)
        
    def __esperar_carregamento(self, *, initial_wait:Union[int, float]=1):
        sleep(initial_wait)
        while self._find_element(By.ID, 'feedback-loader').text == 'Carregando':
            print(P("Aguardando carregar página...                ", color='yellow'), end='\r')
            sleep(1)
        print(end='\r')
    
    @verify_login     
    def _find_element(self, by=By.ID, value: str | None = None, *, timeout: int = 10, force: bool = False, wait_before: int | float = 0, wait_after: int | float = 0) -> WebElement:
        return super().find_element(by, value, timeout=timeout, force=force, wait_before=wait_before, wait_after=wait_after)
    
    @verify_login  
    def cobranca(self, date: datetime, *, tamanho_mini_lista=10) -> bool:
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
                            element.find_element(By.TAG_NAME, 'input').click()
                            #element.click()
                    
                    
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
    def abrir_periodo(self, date: datetime, *, tamanho_mini_lista=10) -> bool:
        self.__load_page('Periodo/Novo')
        print(P("Aguardando carregar página...                           ", color='yellow'))
        
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/button').click()
        t_ul = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/ul')
        lista_empreendimentos:List[str] = [element.text for element in t_ul.find_elements(By.TAG_NAME, 'li') if (element.text != '') and (element.text != 'Todos')]
        
        empreendimentos:List[List[str]] = utils.criar_listas_de_mini_listas(lista=lista_empreendimentos, tamanho_mini_lista=tamanho_mini_lista)
        
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/button').click()
        
        cont = 0   
        for empreendimento in empreendimentos:
            cont += 1
            for _ in range(5):
                try:
                    self.__load_page('Periodo/Novo')
                    self.__esperar_carregamento()
                    self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/button').click()
                    
                    t_ul = self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/ul')
                    for element in [element for element in t_ul.find_elements(By.TAG_NAME, 'li') if (element.text != '') and (element.text != 'Todos')]:
                        if element.text in empreendimento:
                            element.find_element(By.TAG_NAME, 'input').click()
                            #element.click()

                    sleep(1)
                    self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div/div/div[3]/div[1]/div/button').click()
                    
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
                    self._find_element(By.ID, 'AddNovo').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Procurando Faturamentos...               ", color='yellow'), end='\r')
                    
                    self.__esperar_carregamento(initial_wait=0.2)
                    self._find_element(By.ID, 'Salvar').click()
                    print(P(f"[{cont}/{len(empreendimentos)}] | Executando Faturamentos...                  ", color='yellow'), end='\r')
                    
                    print(end='\r')
                    
                    self.__esperar_carregamento(initial_wait=5)
                    if (t_error:=self._find_element(By.ID, 'divMsgError').text):
                        print(P(t_error, color='red'))
                        raise exceptions.CobrancaError(t_error)

                    # self.__esperar_carregamento()
                    # if (t_alerta:=self._find_element(By.ID, 'divAlert').text):
                    #     print(P(f"[{cont}/{len(empreendimentos)}] | {empreendimento} - {t_alerta}", color='cyan'))
                    #     #return True
                    
                    print(P(f"[{cont}/{len(empreendimentos)}] | {empreendimento} - Periodo Aberto!", color='green'))   
                    self.__esperar_carregamento()
                    #import pdb;pdb.set_trace()
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
        
    @verify_login
    def rel_previsao_receita(self, *, date: datetime):
        self.__load_page('Relatorio')
        
        for _ in range(5):
            try:
                self._find_element(By.XPATH, '//*[@id="Relatorios_chzn"]/a').click()
                self._find_element(By.XPATH, '//*[@id="Relatorios_chzn_o_9"]').click()
                break
            except:
                sleep(2)
            if _ == 4:
                raise exceptions.RelatorioError("Erro ao selecionar relatório!")
                
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div[1]/div[1]/h4').click()   
        
        self._find_element(By.ID, 'DataInicio').send_keys(utils.primeiro_dia_proximo_mes(date).strftime('%d%m%Y'))
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div[1]/div[1]/h4').click()   
        
        self._find_element(By.ID, 'DataFim').send_keys(utils.ultimo_dia_proximo_mes(date).strftime('%d%m%Y'))
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div[1]/div[1]/h4').click()   
        
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/button').click() # clica em Empreendimentos
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/ul/li[2]/a/label/input').click() # clica em todos
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/button').click() # clica em Empreendimentos
        
        self._find_element(By.ID, 'DataBase').send_keys(utils.primeiro_dia_proximo_mes(date).strftime('%d%m%Y'))
        self._find_element(By.XPATH, '//*[@id="Content"]/section/div[2]/div[1]/div[1]/h4').click()  
        
    
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/button').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[4]/a/label').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[7]/a/label').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[12]/a/label').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/button').click()
        
        
        self._find_element(By.XPATH, '//*[@id="GerarRelatorio"]').click() # clica em gerar relatorio
        sleep(7)
        
        relatories_id = [self._find_element(By.XPATH, '//*[@id="result-table"]/tbody/tr[1]/td[1]').text]
        
        
        print(P("Iniciando verificação de download", color='cyan'))
        cont_final: int = 0
        while True:
            if cont_final >= 1080:
                print(P("saida emergencia acionada a espera da geração dos relatorios superou as 1,5 horas"))
                raise TimeoutError("saida emergencia acionada a espera da geração dos relatorios superou as 1,5 horas")
            else:
                cont_final += 1
            if not relatories_id:
                break
            
            try:
                table = self._find_element(By.ID, 'result-table')
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
                    for id in relatories_id:
                        if id == tr.find_elements(By.TAG_NAME, 'td')[0].text:
                            for tag_a in tr.find_elements(By.TAG_NAME, 'a'):
                                if tag_a.get_attribute('title') == 'Download':
                                    print(P(f"o {relatories_id=} foi baixado!", color='green'))
                                    tag_a.send_keys(Keys.ENTER)
                                    relatories_id.pop(relatories_id.index(id))
            except:
                sleep(5)
                continue
            
            self._find_element(By.ID, 'btnProximaDefinicao').click()
            sleep(5)
            print(P("Atualizando Pagina"))
        

        return self.__ultimo_download()
    
    @verify_login
    def extrair_previsaoReceita(self, *, initial_date: datetime, final_date:datetime):
        self.__load_page("Relatorio")
        
        
        self._find_element(By.XPATH, '//*[@id="Content"]').location_once_scrolled_into_view
        for _ in range(5):
            try:
                self._find_element(By.ID, 'Relatorios_chzn').click() # clique em selecionar Relatorios
                self._find_element(By.XPATH, '//*[@id="Relatorios_chzn_o_10"]').click() # clique em IMOBME - Previsão de Receita
                break
            except:
                sleep(1)
            if _ == 4:
                raise exceptions.RelatorioError("Erro ao selecionar relatório!")
        
        import pdb; pdb.set_trace()
        self._find_element(By.XPATH, '//*[@id="DataInicio"]').send_keys(initial_date.strftime("%d%m%Y")) # escreve a data de inicio padrao 01/01/2015
        self._find_element(By.XPATH, '//*[@id="Header"]/div[1]/img[1]').click() #<-------------------
        self._find_element(By.XPATH, '//*[@id="DataFim"]').send_keys(final_date.strftime("%d%m%Y")) # escreve a data de fim padrao com a data atual mais 25 anos
        self._find_element(By.XPATH, '//*[@id="Header"]/div[1]/img[1]').click() #<-------------------
                
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/button').click() # clica em Empreendimentos
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/ul/li[2]/a/label/input').click() # clica em todos
        self._find_element(By.XPATH, '//*[@id="dvEmpreendimento"]/div[1]/div/div/button').click() # clica em Empreendimentos
        self._find_element(By.XPATH, '//*[@id="DataBase"]').send_keys(datetime.now().strftime("%d%m%Y")) # escreve a data de hoje
        self._find_element(By.XPATH, '//*[@id="Header"]/div[1]/img[1]').click() #<-------------------
        
        #import pdb; pdb.set_trace()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[1]/div/h4').location_once_scrolled_into_view
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/button').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[4]/a/label/input').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[7]/a/label/input').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/ul/li[12]/a/label/input').click()
        self._find_element(By.XPATH, '//*[@id="parametrosReport"]/div[4]/div/div[2]/div/button').click()
        
        self._find_element(By.XPATH, '//*[@id="GerarRelatorio"]').click() # clica em gerar relatorio
        
        self._find_element(By.XPATH, '//*[@id="parametroAgendamento"]/div[1]/div/h4').location_once_scrolled_into_view
        
        relatories_id:list = [self._find_element(By.XPATH, '//*[@id="result-table"]/tbody/tr[1]/td[1]').text]
        
        self.download_path
        #verificar itens para download
        print(P("Iniciando verificação de download", color='cyan'))
        cont_final: int = 0
        while True:
            if cont_final >= 2880:
                print(P("saida emergencia acionada a espera da geração dos relatorios superou as 1,5 horas"))
                Logs().register(status='Report', description=f"saida emergencia acionada a espera da geração dos relatorios superou as 1,5 horas")
                raise TimeoutError("saida emergencia acionada a espera da geração dos relatorios superou as 1,5 horas")
            else:
                cont_final += 1
            if not relatories_id:
                break
            
            try:
                table = self._find_element(By.ID, 'result-table')
                tbody = table.find_element(By.TAG_NAME, 'tbody')
                for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
                    for id in relatories_id:
                        if id == tr.find_elements(By.TAG_NAME, 'td')[0].text:
                            for tag_a in tr.find_elements(By.TAG_NAME, 'a'):
                                if tag_a.get_attribute('title') == 'Download':
                                    print(P(f"o {relatories_id=} foi baixado!", color='green'))
                                    tag_a.send_keys(Keys.ENTER)
                                    relatories_id.pop(relatories_id.index(id))
            except:
                sleep(5)
                continue
            
            self._find_element(By.ID, 'btnProximaDefinicao').click()
            sleep(5)
            print(P("Atualizando Pagina"))
        
        print(P("verificando pasta de download"))
        for _ in range(10*60):
            isnot_excel = False 
            for file in os.listdir(self.download_path):
                if not file.endswith(".xlsx"):
                    isnot_excel = True
            if not isnot_excel:
                sleep(2)
                break
            else:
                sleep(1)
        self._find_element(By.TAG_NAME, 'html').location
        print(P("extração de relatorios no imobme concluida!"))
        
        
        
    def __ultimo_download(self) -> str:
        for _ in range(60):
            sleep(1)
            lista_arquivos:list = [os.path.join(self.download_path, file) for file in os.listdir(self.download_path)]
            if lista_arquivos:
                arquivo:str = max(lista_arquivos, key=os.path.getctime)
                sleep(1)
                if '.crdownload' in arquivo:
                    #print(arquivo)
                    del lista_arquivos
                    del arquivo
                    continue
                else:
                    return arquivo
            else:
                sleep(1)
        raise Exception("não foi possivel identificar ultimo download")
        
if __name__ == '__main__':
    pass

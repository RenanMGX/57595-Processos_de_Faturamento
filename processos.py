from Entities.imobme import Imobme, datetime, P
from Entities.etapas import Etapa
from Entities.dependencies.functions import Functions
from Entities.sap import SAP
from Entities.tratar_dados import TratarDados, pd

from Entities.dependencies.logs import Logs, traceback
from Entities.dependencies.config import Config
from Entities.emails import Email
from typing import List, Dict
from time import sleep
from datetime import datetime
from lista_indices import lista_indices
from Entities.informativo import Informativo


import Entities.utils as utils
import os
import sys
import multiprocessing

class Processos:
    @property
    def relatorios_path(self) -> str:
        return os.path.join(os.getcwd(), 'relatorios')
    
    def __init__(self, date: datetime=datetime.now(), *, pasta: str = r"W:\BOLETOS_SEGUNDA_VIA") -> None:
        """
        Inicializa a classe Processos definindo a data de referência e a pasta para armazenar boletos.

        Fluxo:
          1. Armazena a data base para os processos.
          2. Instancia a classe Etapa, que gerencia a execução das etapas mensais.
          3. Define o caminho da pasta onde os boletos serão salvos.

        Args:
            date (datetime): Data utilizada como referência para os processos.
            pasta (str): Diretório onde os boletos serão gerados/armazenados.

        Returns:
            None
        """
        self.date = date
        self.etapa = Etapa()
        self.pasta: str = pasta
        self.emails_to_send_path:str = os.path.join(os.getcwd(), 'emails_to_send.json')
        self.emails_to_delete_path:str = os.path.join(os.getcwd(), 'emails_to_delete.json')
        self.mensagem_html_path:str = os.path.join(os.getcwd(), 'Entities', 'layout_email')
        #self.assinatura_path:str = r"\\server011\NETLOGON\ASSINATURA"
        self.email_to_send_logs:str = Config()['lista_emails']['emailToSendLogs']
        
        self.informativo = Informativo(email=self.email_to_send_logs, assunto="Informativo da Automação do Processo de Faturamento")
        
        if not os.path.exists(self.relatorios_path):
            os.makedirs(self.relatorios_path)
            
    def _limpar_pasta_relatorios(self, *, etapa:str="limpar_pasta_relatorios") -> None:
        if (not self.etapa.executed_month(etapa) or etapa == ""):
            if os.path.exists(self.relatorios_path):
                for file in os.listdir(self.relatorios_path):
                    os.unlink(os.path.join(self.relatorios_path, file))
            print(P("Pasta de relatórios limpa!", color='cyan'))

    def imobme_cobranca_global(self, date: datetime | None = None, *, finalizar: bool, etapa:str) -> bool:
        """
        Executa a cobrança global no sistema Imobme para o mês corrente.

        Fluxo:
          1. Se a data não for informada, utiliza a data base definida na instância.
          2. Exibe uma mensagem informativa com a data de execução.
          3. Verifica se o processo "imobme_cobranca_global" ainda não foi executado neste mês.
          4. Instancia a classe Imobme e:
               a. Verifica se os índices estão aprovados para o mês anterior.
               b. Se aprovado, realiza o processo de cobrança para o primeiro dia do mês seguinte,
                  dividindo os empreendimentos conforme o tamanho mini da lista.
          5. Se o processo for concluído com sucesso, salva o status e, opcionalmente, encerra a aplicação.
          6. Caso contrário, emite mensagem de erro ou alerta.

        Args:
            date (datetime | None): Data para a cobrança. Se None, usa self.date.
            finalizar (bool): Se True, encerra a aplicação em caso de sucesso.

        Returns:
            bool: Retorna True se a cobrança foi executada com sucesso; False caso contrário.
        """
        if date is None:
            date = self.date
        print(P(f"Executando Imobme cobrança global em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (not self.etapa.executed_month(etapa) or etapa == ""):
            bot = Imobme()
            if bot.verificar_indices(date=utils.primeiro_dia_penultimo_mes(date), lista_indices=lista_indices):
                if not bot.abrir_periodo(date, tamanho_mini_lista=12):
                    self.informativo.error("Erro ao abrir o período no Imobme!")
                    return False
                if bot.cobranca(date, tamanho_mini_lista=12):
                    self.etapa.save(etapa)
                    self.informativo.sucess("Imobme Cobrança global executada com sucesso!")
                    bot.close()
                    del bot
                    if finalizar:
                        print(P("Finalizando aplicação...", color='magenta'))
                        sys.exit()                        
                    return True
                else:
                    self.informativo.error("Erro ao executar Imobme cobrança global!")
            else:                
                self.informativo.error("Erro ao executar Imobme cobrança global, índices não aprovados!")
        else:
            print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        return False
           
    def rel_partidas_individuais(self, date: datetime | None = None, *, etapa:str, ultima_etapa:str="", remover_empresas:list=[]):
        """
        Gera o relatório de partidas individuais via SAP para um determinado mês.

        Fluxo:
          1. Define a data a ser utilizada (self.date se não fornecida).
          2. Verifica se a etapa "imobme_cobranca_global" foi executada, necessária para a continuidade.
          3. Se o relatório ainda não foi gerado (verificado por etapa "rel_partidas_individuais"):
               a. Chama o método do SAP para gerar o relatório.
               b. Trata exceções e registra erros caso ocorram.
               c. Após obter o caminho do arquivo, realiza extração dos dados e separa-os por empresas.
               d. Fecha o arquivo Excel, remove o arquivo temporário e grava a estrutura extraída em um JSON.
          4. Registra a etapa e informa o sucesso da operação.

        Args:
            date (datetime | None): Data para a qual o relatório deve ser gerado.
                                   Se None, utiliza self.date.

        Returns:
            bool or None: Retorna True se o relatório foi gerado com sucesso; 
                          False ou None em caso de erro.
        """
        if date is None:
            date = self.date
        print(P(f"Executando relatório partidas individuais em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                sap = SAP()
                try:
                    file_path = sap.relatorio_partidas_individuais_cliente(date)
                except Exception as err:
                    self.informativo.error(f"Erro ao executar o processo! -> {err}")
                    return False
                finally:
                    sap.fechar_sap()
                
                if file_path:
                    docs:list = TratarDados.sep_dados_por_empresas(file_path, remover_empresas=remover_empresas)
                    sleep(3)
                    Functions.fechar_excel(file_path)
                    os.unlink(file_path)
                    
                    docs_path = os.path.join(os.getcwd(), 'docs.json')
                    if os.path.exists(docs_path):
                        os.unlink(docs_path)
                                                
                    utils.jsonFile.write(docs_path, docs)
                    
                    self.etapa.save(etapa)
                    self.informativo.sucess("Relatório partidas individuais executado com sucesso!")
                    return True
                else:
                    self.informativo.error("Erro ao executar relatório partidas individuais!")
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def gerar_arquivos_de_remessa(self , *, finalizar: bool=False, etapa:str, ultima_etapa:str=""):
        """
        Gera arquivos de remessa a partir dos dados consolidados do relatório de partidas individuais.

        Fluxo:
          1. Verifica se a etapa "rel_partidas_individuais" foi concluída.
          2. Se a etapa "gerar_arquivos_de_remessa" ainda não foi executada:
               a. Abre o arquivo JSON com os dados separados.
               b. Itera sobre os dados de cada empresa.
               c. Se a empresa possuída documentos, chama o método para gerar o arquivo de remessa.
               d. Em caso de exceção, registra o erro e continua para os próximos dados.
          3. Após finalizar, chama o método para fechar a interface do SAP,
             registra a etapa e retorna sucesso.
          4. Se já executado, informa que a etapa já foi realizada.

        Args:
            None

        Returns:
            bool: True se os arquivos foram gerados com sucesso, False caso contrário.
        """
        print(P("Executando geração de arquivos de remessa", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                sap = SAP()

                dados:List[Dict[str,object]] = utils.jsonFile.read('docs.json')
                
                for dado in dados:
                    if not dado['docs']:
                        print(P(f"    {dado['empresa']} não possui documentos!", color='cyan'))
                        continue
                    
                    try:
                        sap.gerar_arquivos_de_remessa(data=dado)
                    except Exception as err:
                        print(P(f"    Erro ao executar o processo! -> {err}", color='red'))
                        Logs().register(status='Report', description=str(err), exception=traceback.format_exc())
                        continue
                    
                sap.fechar_sap()
                self.etapa.save(etapa)
                self.informativo.sucess("Geração de arquivos de remessa executada com sucesso!")
                if finalizar:
                    print(P("Finalizando aplicação...", color='magenta'))
                    sys.exit()
                return True
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def verificar_lancamentos(self,
                              date: datetime | None = None, 
                              *,
                              finalizar: bool=False,
                              etapa:str, ultima_etapa:str="",
                              ignorar_empresas:list=[],
                              timeout:int = 5
                              ):
        """
        Realiza a verificação dos lançamentos no SAP para confirmar a efetividade das operações.

        Fluxo:
          1. Determina a data de verificação (usa self.date se não informada).
          2. Verifica se a etapa "gerar_arquivos_de_remessa" foi realizada.
          3. Se a etapa "verificar_lancamentos" ainda não foi executada:
               a. Em até cinco tentativas, gera um relatório de partidas individuais.
               b. Lê o arquivo Excel, remove linhas sem dados essenciais e verifica se há lançamentos pendentes.
               c. Se todos os lançamentos estiverem confirmados, registra a etapa e, se solicitado,
                  encerra a aplicação.
               d. Em caso de falha, aguarda e tenta novamente.
          4. Se nenhuma tentativa for bem-sucedida, registra e informa o erro.

        Args:
            date (datetime | None): Data para a verificação. Se None, utiliza self.date.
            finalizar (bool): Se True, encerra a aplicação caso a verificação seja bem-sucedida.

        Returns:
            bool: True se a verificação for concluída com sucesso; False caso contrário.
        """
        if date is None:
            date = self.date
        print(P(f"Executando verificação de lançamentos em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):

                lista_campos_vazios = pd.DataFrame({"Empresa": []})
                for _ in range(timeout):
                    path = SAP().relatorio_partidas_individuais_cliente(date)
                    df = pd.read_excel(path)

                    os.unlink(path)
                    df = df.dropna(subset=['Conta'])
                    
                    for empresa in ignorar_empresas:
                        df = df[df['Empresa'] != empresa]                    
                    
                    if (df_campos:=df[df['Solicitação de L/C'].isna()]).empty:
                        self.etapa.save(etapa)
                        self.informativo.sucess("Verificação de lançamentos executada com sucesso!")
                        if finalizar:
                            print(P("Finalizando aplicação...", color='magenta'))
                            sys.exit()
                        return True
                    else:
                        lista_campos_vazios = df_campos
                    
                    sleep(15)
                
                file_path = os.path.join(self.relatorios_path, datetime.now().strftime("%Y%m%d%H%M%S_relatorioErro_verificarLancamentos.xlsx"))
                lista_campos_vazios.to_excel(file_path, index=False)
                self.informativo.error(f"Erro ao executar verificação de lançamentos as seguintes empresas não estão com o campo 'Solicitação de L/C' preenchido:\n- {'\n- '.join(lista_campos_vazios["Empresa"].unique().tolist())}",
                                       anexo=[
                                           file_path
                                       ])
                os.unlink(file_path)
                
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
        return False

    def verificar_retorno_do_banco(self, date: datetime | None = None, *, finalizar: bool=False, etapa:str, ultima_etapa:str=""):
        """
        Confirma se o retorno do banco foi registrado corretamente.

        Fluxo:
          1. Define a data de verificação.
          2. Verifica se a etapa "verificar_lancamentos" foi concluída.
          3. Se a etapa "verificar_retorno_do_banco" ainda não foi realizada:
               a. Gera através do SAP um relatório e lê-o em um DataFrame.
               b. Elimina registros sem a coluna 'Conta' e filtra as linhas cujo campo
                  'Chave referência 3' esteja ausente.
               c. Se houver linhas filtradas, gera um arquivo Excel para esses registros
                  no diretório padrão de downloads do usuário.
               d. Registra a etapa e informa o sucesso da operação.
          4. Caso a etapa já tenha sido executada, apenas informa o status.

        Args:
            date (datetime | None): Data para a verificação. Se None, utiliza self.date.

        Returns:
            bool or None: True se a verificação foi bem-sucedida; False ou None, caso contrário.
        """
        if date is None:
            date = self.date
        print(P(f"Executando verificação de retorno do banco em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                path = SAP().relatorio_partidas_individuais_cliente(date)
                df = pd.read_excel(path)
                os.unlink(path)
                df = df.dropna(subset=['Conta'])
                #df.to_excel(os.path.join(f"C:\\Users\\{os.getlogin()}\\Downloads", datetime.now().strftime("%Y%m%d%H%M%S_temp.xlsx")), index=False)
                filtro = df[
                    df['Chave referência 3'].isna()
                ]
                if not filtro.empty:
                    file_path = os.path.join(self.relatorios_path, datetime.now().strftime("%Y%m%d%H%M%S_relatorioErro_verificarRetornoBanco.xlsx"))
                    filtro.to_excel(file_path, index=False)
                    self.informativo.error(f"Erro ao executar verificação de retorno do banco, registros sem 'Chave referência 3' foram encontrados!",
                                           anexo=[
                                               file_path
                                           ])
                    os.unlink(file_path)
                
                self.etapa.save(etapa)
                self.informativo.sucess("Verificação de retorno do banco executada com sucesso!")
                if finalizar:
                    print(P("Finalizando aplicação...", color='magenta'))
                    sys.exit()
                return True
                
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def gerar_boletos(self, *,
                      date: datetime | None = None,
                      finalizar: bool=False,
                      etapa:str,
                      ultima_etapa:str="",
                      mover_pdf:bool=False
                      ):
        """
        Executa o processo de geração de boletos via SAP para a data informada.

        Fluxo:
          1. Define a data de geração dos boletos.
          2. Confirma se a etapa "verificar_retorno_do_banco" foi concluída.
          3. Se os boletos ainda não foram gerados:
               a. Chama o método responsável por gerar boletos, passando parâmetros como data e pasta.
               b. Se o processo resultar em sucesso, registra a etapa.
               c. Caso contrário, informa o erro no console.
          4. Se a etapa já tiver sido executada, informa o status.

        Args:
            date (datetime | None): Data para geração dos boletos. Se None, utiliza self.date.

        Returns:
            bool or None: True se os boletos forem gerados com sucesso, False ou None caso contrário.
        """
        if date is None:
            date = self.date
        print(P(f"Executando geração de boletos em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                if SAP().gerar_boletos_no_sap(date=date, pasta=self.pasta, mover_pdf=mover_pdf):
                    self.etapa.save(etapa)
                    self.informativo.sucess("Geração de boletos executada com sucesso!")
                    if finalizar:
                        print(P("Finalizando aplicação...", color='magenta'))
                        sys.exit()
                    return True
                else:
                    self.informativo.error("Erro ao executar geração de boletos!")
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def criptografar_boletos(self, date: datetime | None=None, quant_nucleos:int=int(multiprocessing.cpu_count()/1.2)):
        """
        Realiza a criptografia dos PDFs de boletos armazenados na pasta definida.

        Fluxo:
          1. Percorre todos os arquivos presentes na pasta.
          2. Para cada arquivo, instancia a classe PDFManipulator.
          3. Se o objeto PDF possuir um CPF ou CNPJ válido, exibe o dado e chama o método para proteger o PDF.
          4. Silencia exceções para evitar interrupções em caso de arquivo incompatível.
          5. Ao final, informa que a criptografia foi executada com sucesso.

        Args:
            None

        Returns:
            None
        """
        if date is None:
            date = self.date

        if quant_nucleos <= 0:
            quant_nucleos = 1
        
        print(P("Executando criptografia de boletos", color='yellow'))

        lista_files = []
        for file in os.listdir(self.pasta):
            file_path:str = os.path.join(self.pasta, file)
            if not os.path.isfile(file_path):
                continue
            
            file_date = os.path.basename(file_path)
            if not file_date.lower().endswith('.pdf'):
                continue
            
            try:
                file_date = file_date.split('-')[3]
            except:
                print(os.path.basename(file_path))
                continue
            if file_date != str(date.month).zfill(2):
                continue
            lista_files.append(file_path)
            
        print(P(f"Quantidade de arquivos: {len(lista_files)}", color='cyan'))
        
                    
        lista_arquivos_para_multiprocess = utils.split_list(lista_files, quant_nucleos)
        lista_multiprocess:List[multiprocessing.Process] = []
        for lista in lista_arquivos_para_multiprocess:
            lista_multiprocess.append(multiprocessing.Process(target=utils.cripto, args=(lista,)))
            
        #import pdb; pdb.set_trace()
        for processo in lista_multiprocess:
            processo.start()
            
        for processo in lista_multiprocess:
            processo.join()
                
        print(P("    Criptografia de boletos executada com sucesso!", color='green'))
        
    def preparar_lista_envio_email(self, *,
                      date: datetime | None = None,
                      finalizar: bool=False,
                      etapa:str,
                      ultima_etapa:str="",
                      extrair_relatorio:bool=True
                      ):
        
        if date is None:
            date = self.date
        print(P(f"Executando preparação de lista de envio de e-mails em {date.strftime('%d/%m/%Y')}", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                planila_clientes_path:str = Config()['path']['planilhaClientes']
                if os.path.exists(planila_clientes_path):
                    if planila_clientes_path.lower().endswith('.json'):
                        df_clientes = pd.read_json(planila_clientes_path)
                    else:
                        print(P("    Erro ao carregar planilha de clientes!", color='red'))
                        raise FileNotFoundError("Arquivo de clientes não encontrado!")
                else:
                    print(P("    Erro ao carregar planilha de clientes!", color='red'))
                    raise FileNotFoundError("Arquivo de clientes não encontrado!")
                
                download_path:str = os.path.join(os.getcwd(), 'downloads')
                
                if not os.path.exists(download_path):
                    os.makedirs(download_path)
                else:
                    if extrair_relatorio:
                        for file in os.listdir(download_path):
                            os.unlink(os.path.join(download_path, file))
                
                if extrair_relatorio:
                    bot = Imobme(download_path=download_path)                
                    bot.extrair_previsaoReceita(initial_date=utils.primeiro_dia_mes(date), final_date=utils.ultimo_dia_mes(date))
                    bot.close()
                    del bot
                
                file_prevReceita_path = [os.path.join(download_path, file) for file in os.listdir(download_path)]
                if file_prevReceita_path:
                    file_prevReceita_path = file_prevReceita_path[0]
                else:
                    print(P("    Erro ao extrair previsão de receita!", color='red'))
                    raise FileNotFoundError("Arquivo de previsão de receita não encontrado!")
                
                df_previsaoReceita = TratarDados.load_previReceita(file_prevReceita_path)
                
                df:pd.DataFrame = TratarDados.generate_df_with_emails(df_clientes=df_clientes, df_previsaoReceita=df_previsaoReceita)
                
                emails_to_send, df_files_not_found = TratarDados.generate_files_to_send(df=df, path=self.pasta)
                
                df_files_not_found:pd.DataFrame
                if not df_files_not_found.empty:
                    file_path = os.path.join(self.relatorios_path, datetime.now().strftime("%Y%m%d%H%M%S_relatorioErro_arquivosNãoEncontrados.xlsx"))
                    df_files_not_found.to_excel(file_path, index=False)
                    self.informativo.error(f"Erro ao executar preparação de lista de envio de e-mails, arquivos não encontrados!",
                                           anexo=[
                                               file_path
                                           ])
                    os.unlink(file_path)
                    
                utils.jsonFile.write(self.emails_to_send_path, emails_to_send)
                utils.jsonFile.write(self.emails_to_delete_path, [])
                
                self.etapa.save(etapa)
                self.informativo.sucess("Preparação de lista de envio de e-mails executada com sucesso!")
                if finalizar:
                    print(P("Finalizando aplicação...", color='magenta'))
                    sys.exit()
                return True
            
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()

        return False
    
    
    def enviar_emails(self, *,
                      finalizar: bool=False,
                      etapa:str,
                      ultima_etapa:str="",
                      testes:bool=False
                      ):
        
        print(P(f"Executando envio de e-mails", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                emails_to_send:dict = utils.jsonFile.read(self.emails_to_send_path)
                print(P(f"    {len(emails_to_send)} e-mails para enviar!", color='cyan'))
                
                emails_to_delete:list
                if not os.path.exists(self.emails_to_delete_path):
                    utils.jsonFile.write(self.emails_to_delete_path, data=[])
                else:
                    for value in utils.jsonFile.read(self.emails_to_delete_path):
                        emails_to_send.pop(value)
                    utils.jsonFile.write(self.emails_to_delete_path, data=[])
                    utils.jsonFile.write(self.emails_to_send_path, emails_to_send)
                
                send_email = Email('email')
                
                if not emails_to_send:
                    self.etapa.save(etapa)
                    if finalizar:
                        print(P("Finalizando aplicação...", color='magenta'))
                        sys.exit()
                    print(P("    Nenhum e-mail para enviar!", color='cyan'))
                    return True
                
                if testes:
                    count = 1  # temporario
                    empresa_to_valid = ["patrimar", "novolar"] # temporario
                for email, dados in emails_to_send.items():
                    try:
                        empresa:str = dados['empresa']
                        if testes:
                            if not empresa_to_valid: #type:ignore temporario 
                                break # temporario
                        
                        empresa = "Patrimar" if empresa.upper().startswith("P") else "Novolar" if empresa.upper().startswith("N") else ""
                        
                        if testes:
                            if empresa.lower() in empresa_to_valid: #type:ignore temporario
                               empresa_to_valid.pop(empresa_to_valid.index(empresa.lower())) #type:ignore temporario
                            else: # temporario
                                continue # temporario
                        
                        
                        assunto = f"Boleto {empresa} - {dados['date']} - {dados['empreendimento']} - {dados['bloco']} - Unidade {dados['unidade']}"
                        
                        # assinatura = ""
                        # if os.path.exists(self.assinatura_path):
                        #     assinatura = [os.path.join(self.assinatura_path, file) for file in os.listdir(self.assinatura_path)][0]
                        
                        # if assinatura:
                        #     assinatura = f'<img src="{assinatura}" alt="assinatura" style="height:1.947in;width:4.583in">'
                        
                        msg = utils.jsonFile.read_qualquer_arquivo(os.path.join(self.mensagem_html_path, f'{empresa.lower()}.html'))
                        #msg = utils.jsonFile.read_qualquer_arquivo(os.path.join(self.mensagem_html_path, f'teste.html'))
                        
                        if testes:
                            msg = msg.replace("{{teste}}", f'<span style="text-decoration: underline">este é um teste de envio de e-mail e deveria ser entregue ao {email}</span>') # <------------------- campo para teste deixar limpo para produção
                        else:
                            msg = msg.replace("{{teste}}", "")
                            
                        msg = msg.replace("{{nome_empreendimento}}", dados['empreendimento'])
                        msg = msg.replace("{{bloco}}", dados['bloco'])
                        msg = msg.replace("{{unidade}}", f"Unidade {dados['unidade']}")
                        msg = msg.replace("{{nome_cliente}}", dados['nome'].title())
                        msg = msg.replace("{{data}}", dados['date'])
                        
                        if testes:
                            destino=['kleryson.lara@patrimar.com.br', 'renan.oliveira@patrimar.com.br']
                            cc = "thays.freitas@patrimar.com.br"
                        else:
                            destino = email 
                            cc = ""    
                            
                                     
                        send_email.mensagem(
                            Destino=destino,
                            Assunto=assunto,
                            CC = cc,
                            Corpo_email=msg,
                            _type='html'
                        )
                        
                        for file in dados['files']:
                            send_email.Anexo(
                                Attachment_path=file
                            )
                          
                        
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', f'emp_{empresa.lower()}.png'), tag="emp_header")  
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', f'logo_{empresa.lower()}.png'), tag="logo_header")
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', f'patrimar_vertical.png'), tag='patrimar_vertical')
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', f'novolar_vertical.png'), tag='novolar_vertical')
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', f'bt_portal_{empresa.lower()}.png'), tag='botao')
                        
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', 'icons', f'email.png'), tag='icon-email')
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', 'icons', f'tel.png'), tag='icon-tel')
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', 'icons', f'whatsapp.png'), tag='icon-whatsapp')
                        send_email.addImagemCid(Attachment_path=os.path.join(self.mensagem_html_path, 'img', 'icons', f'internet.png'), tag='icon-internet')
                        
                        send_email.send(msg_envio=" "*4+assunto)    
                        
                        emails_to_delete = utils.jsonFile.read(self.emails_to_delete_path)
                        emails_to_delete.append(email)
                        utils.jsonFile.write(self.emails_to_delete_path, emails_to_delete)
                    except Exception as err:
                        Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
                        print(type(err), err)
                    
                    if testes: 
                        if count >= 5: #type:ignore temporario
                            break # temporario
                        count += 1 #type:ignore temporario
                
                for value in utils.jsonFile.read(self.emails_to_delete_path):
                    emails_to_send.pop(value)
                utils.jsonFile.write(self.emails_to_delete_path, data=[])
                utils.jsonFile.write(self.emails_to_send_path, emails_to_send)
                
                emails_to_send:dict = utils.jsonFile.read(self.emails_to_send_path)

                if not testes:
                    self.informativo.sucess(f"E-mails enviados com sucesso!\ncom '{len(emails_to_send)}' e-mails restantes!")
                self.etapa.save(etapa)
                if finalizar:
                    print(P("Finalizando aplicação...", color='magenta'))
                    sys.exit()
                return True
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
        return False
    
    def finalizar(self, *,
                      etapa:str,
                      ultima_etapa:str="",
                      ):
        
        print(P(f"Executando envio de e-mails", color='yellow'))
        
        if (self.etapa.executed_month(ultima_etapa) or ultima_etapa == ""):
            if (not self.etapa.executed_month(etapa) or etapa == ""):
                self.etapa.save(etapa)
                print(P("Processo de Faturamento Finalizado!", color='green'))
                self.informativo.sucess("Processo de Faturamento Finalizado!\n ate o próximo mês!")
                sys.exit()
            else:
                print(P(f"    {etapa} já foi executada este mês!", color='cyan'))
        else:
            print(P(f"    {ultima_etapa} não foi executada este mês!", color='magenta'))
            sys.exit()
        return False

if __name__ == "__main__":
    pass

from Entities.imobme import Imobme, datetime, P
from Entities.etapas import Etapa
from Entities.dependencies.functions import Functions
from Entities.sap import SAP
from Entities.tratar_dados import TratarDados, pd
from Entities.pdf_manipulator import PDFManipulator
from Entities.dependencies.logs import Logs, traceback
from typing import List, Dict
from time import sleep
import Entities.utils as utils

import os
import json
import sys

lista_indices = [
    r'0,8% a.m.',
    r'0,5% a.m.',
    r'JUROS 1%',
    r'JUROS 0,5%',
    r'INCC',
    r'CDI',
    r'CDI 3% a.a.',
    r'IPCA',
    r'IPCA 12a.a.',
    r'IPCA 1%',
    r'POUPA 12',
    r'POUPA 15',
    r'POUPA 28',
    r'IGPM',
    r'IGPM 0,5%',
    r'IGPM 1%',
]


class Processos:
    def __init__(self, date: datetime, *, pasta: str = r"W:\BOLETOS_SEGUNDA_VIA_HML") -> None:
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

    def primeiro_imobme_cobranca_global(self, date: datetime | None = None, *, finalizar: bool) -> bool:
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
        
        if not self.etapa.executed_month('imobme_cobranca_global'):
            bot = Imobme()
            if bot.verificar_indices(date=utils.primeiro_dia_ultimo_mes(date), lista_indices=lista_indices):
                if bot.cobranca(utils.primeiro_dia_proximo_mes(date), tamanho_mini_lista=12):
                    self.etapa.save('imobme_cobranca_global')
                    print(P("    Imobme Cobrança global executada com sucesso!", color='green'))
                    bot.close()
                    del bot
                    if finalizar:
                        print(P("Finalizando aplicação...", color='magenta'))
                        sys.exit()                        
                    return True
                else:
                    print(P("    Erro ao executar Imobme cobrança global!", color='red'))
            else:
                print(P("    Erro ao verificar indices!", color='red'))
        else:
            print(P("    Imobme Cobrança global já foi executada este mês!", color='cyan'))
        return False
    
    def pre_segundo_verificar_documentos_imobme_para_sap(self, date: datetime | None = None) -> bool:
        if date is None:
            date = self.date
            
        if self.etapa.executed_month('imobme_cobranca_global'):
            if not self.etapa.executed_month('verificar_documentos_imobme_para_sap'):
                download_path = os.path.join(os.getcwd(), 'downloads')
                if not os.path.exists(download_path):
                    os.makedirs(download_path)
                else:
                    for file in os.listdir(download_path):
                        os.unlink(os.path.join(download_path, file))
                        
                bot = Imobme(download_path=download_path)
                
                file_previsaoReceita = ""
                try:
                    file_previsaoReceita = bot.rel_previsao_receita(date=date)
                except:
                    print(P("    Erro ao executar relatório de previsão de receita!", color='red'))
                    return False
                
                df = TratarDados.load_previReceita(file_previsaoReceita)
                
                import pdb; pdb.set_trace()
                
                bot.close()
                del bot
        else:
            sys.exit()
            
        return False
           
    def segundo_rel_partidas_individuais(self, date: datetime | None = None):
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
        
        if self.etapa.executed_month('verificar_documentos_imobme_para_sap'):
            if not self.etapa.executed_month('rel_partidas_individuais'):
                sap = SAP()
                try:
                    file_path = sap.relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
                except Exception as err:
                    print(P(f"    Erro ao executar o processo! -> {err}", color='red'))
                    Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
                    return False
                
                if file_path:
                    docs:list = TratarDados.sep_dados_por_empresas(file_path)
                    sleep(3)
                    Functions.fechar_excel(file_path)
                    os.unlink(file_path)
                    
                    docs_path = os.path.join(os.getcwd(), 'docs.json')
                    if os.path.exists(docs_path):
                        os.unlink(docs_path)
                        
                    with open(docs_path, 'w') as file:
                        json.dump(docs, file)
                    
                    self.etapa.save('rel_partidas_individuais')
                    print(P("    Relatório partidas individuais executado com sucesso!", color='green'))
                    return True
                else:
                    print(P("    Erro ao executar relatório partidas individuais!", color='red'))
            else:
                print(P("    Relatório partidas individuais já foi executado este mês!", color='cyan'))
        else:
            print(P("    Verificar documentos Imobme para SAP não foi executado este mês!", color='magenta'))
            sys.exit()
            
            
    def terceiro_gerar_arquivos_de_remessa(self):
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
        
        if self.etapa.executed_month('rel_partidas_individuais'):
            if not self.etapa.executed_month('gerar_arquivos_de_remessa'):
                sap = SAP()
                with open('docs.json', 'r') as file:
                    data:List[Dict[str,object]] = json.load(file)
                    
                for dado in data:
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
                self.etapa.save('gerar_arquivos_de_remessa')
                print(P("    Geração de arquivos de remessa executada com sucesso!", color='green'))
                return True
            else:
                print(P("    Geração de arquivos de remessa já foi executada este mês!", color='cyan'))
        else:
            print(P("    Relatório partidas individuais não foi executado este mês!", color='magenta'))
            sys.exit()
            
    def quarto_verificar_lancamentos(self, date: datetime | None = None, *, finalizar: bool):
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
        
        if self.etapa.executed_month('gerar_arquivos_de_remessa'):
            if not self.etapa.executed_month('verificar_lancamentos'):

                for _ in range(5):
                    path = SAP().relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
                    df = pd.read_excel(path)
                    os.unlink(path)
                    df = df.dropna(subset=['Conta'])
                    if df[df['Solicitação de L/C'].isna()].empty:
                        self.etapa.save('verificar_lancamentos')
                        print(P("    Verificação de lançamentos executada com sucesso!", color='green'))
                        if finalizar:
                            print(P("Finalizando aplicação...", color='magenta'))
                            sys.exit()
                        return True
                    
                    sleep(15)
                
                Logs().register(status='Error', description="Erro ao executar verificação de lançamentos", exception=traceback.format_exc())
                print(P("    Erro ao executar verificação de lançamentos!", color='red'))
            else:
                print(P("    Verificação de lançamentos já foi executada este mês!", color='cyan'))
        else:
            print(P("    Geração de arquivos de remessa não foi executada este mês!", color='magenta'))
            sys.exit()
        
        return False

    def quinto_verificar_retorno_do_banco(self, date: datetime | None = None):
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
        
        if self.etapa.executed_month('verificar_lancamentos'):
            if not self.etapa.executed_month('verificar_retorno_do_banco'):
                path = SAP().relatorio_partidas_individuais_cliente(utils.primeiro_dia_proximo_mes(date))
                df = pd.read_excel(path)
                os.unlink(path)
                df = df.dropna(subset=['Conta'])
                filtro = df[
                    df['Chave referência 3'].isna()
                ]
                if not filtro.empty:
                    empty_files_path = os.path.join(f"C:\\Users\\{os.getlogin()}\\Downloads", datetime.now().strftime("%Y%m%d%H%M%S_empty_files.xlsx"))
                    filtro.to_excel(empty_files_path, index=False)
                
                self.etapa.save('verificar_retorno_do_banco')
                print(P("    Verificação de retorno do banco executada com sucesso!", color='green'))
                return True
                
            else:
                print(P("    Verificação de retorno do banco já foi executada este mês!", color='cyan'))
        else:  
            print(P("    Verificação de lançamentos não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def sexto_gerar_boletos(self, *, date: datetime | None = None):
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
        
        if self.etapa.executed_month('verificar_retorno_do_banco'):
            if not self.etapa.executed_month('gerar_boletos'):
                if SAP().gerar_boletos_no_sap(date=date, pasta=self.pasta, debug=True): # O DEBUG ESTA ATIVADO REMOVER PARA PRODUÇÂO
                    self.etapa.save('gerar_boletos')
                    print(P("    Geração de boletos executada com sucesso!", color='green'))
                else:
                    print(P("    Erro ao executar geração de boletos!", color='red'))
            else:
                print(P("    Geração de boletos já foi executada este mês!", color='cyan'))
        else:
            print(P("    Verificação de retorno do banco não foi executada este mês!", color='magenta'))
            sys.exit()
            
    def setimo_criptografar_boletos(self):
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
        print(P("Executando criptografia de boletos", color='yellow'))
        
        for file in os.listdir(self.pasta):
            file_path:str = os.path.join(self.pasta, file)
            try:
                pdf = PDFManipulator(file_path)
                if pdf.CPF_CNPJ:
                    print(P(f"    {pdf.CPF_CNPJ}", color='yellow'))
                    pdf.proteger_pdf()
            except:
                pass
                
        print(P("    Criptografia de boletos executada com sucesso!", color='green'))

if __name__ == "__main__":
    pass

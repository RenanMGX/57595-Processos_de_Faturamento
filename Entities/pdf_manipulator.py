from PyPDF2 import PdfReader, PdfWriter
from pdfminer import high_level
import re
import os
from typing import Union

class PDFManipulator:
    @property
    def path(self) -> str:
        return self.__path
    
    @property
    def CPF_CNPJ(self) -> str|None:
        if (x:=self.__extract_cpf_cnpj_from_caixa()):
            return x
        elif (x:=self.__extract_cpf_cnpj_from_safra()):
            return x
    
    def __init__(self, path:str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo {path} não encontrado!")
        if not path.lower().endswith(".pdf"):
            raise ValueError("Arquivo não é um PDF!")
        
        self.__data = high_level.extract_text(path)
        
        self.__path = path
        
    def __repr__(self) -> str:
        return f"PDFManipulator({self.path})"
    
    
    def __extract_cpf_cnpj_from_caixa(self) -> Union[str, None]:
        pdf_cnpj = None
        if (pagador:=re.search(r'Pagador:\n\n[A-z ]+[-] CNPJ/CPF: [\d./-]+', self.__data)):
            pagador = pagador.group()
            if (dados:=re.search(r'(?<=CNPJ/CPF: )[\d./-]+', pagador)):
                pdf_cnpj = dados.group()

        if pdf_cnpj:   
            pdf_cnpj = re.sub(r'[./-]', '', pdf_cnpj)
        
        return pdf_cnpj    
    
    def __extract_cpf_cnpj_from_safra(self) -> Union[str, None]:
        pdf_cnpj = None
        if (pagador:=re.search(r'Pagador\n[A-z ]+CNPJ/CPF: [\d./-]+', self.__data)):
            pagador = pagador.group()
            if (dados:=re.search(r'(?<=CNPJ/CPF: )[\d./-]+', pagador)):
                pdf_cnpj = dados.group()

        if pdf_cnpj:   
            pdf_cnpj = re.sub(r'[./-]', '', pdf_cnpj)
        
        return pdf_cnpj    
    
    
    def proteger_pdf(self):
        """
        Adiciona senha a um arquivo PDF, gerando um novo PDF protegido.

        Args:
            input_pdf (str): Caminho para o PDF de entrada (sem proteção).
            output_pdf (str): Caminho para o PDF de saída (protegido).
            user_password (str): Senha de abertura (user password).
            owner_password (str, opcional): Senha de permissões (owner password).
                                            Se None, assume a mesma do user.
        """
        if self.CPF_CNPJ:
            user_password = self.CPF_CNPJ[0:3]

            # Carrega o arquivo PDF de entrada
            reader = PdfReader(self.path)
            writer = PdfWriter()

            # Copia todas as páginas do PDF original
            for page in reader.pages:
                writer.add_page(page)

            # Criptografa o PDF com as senhas
            writer.encrypt(
                user_password=user_password, 
                owner_password=None, 
                use_128bit=True
            )

            # Salva o PDF protegido
            with open(self.path, "wb") as f_out:
                writer.write(f_out)      
        
if __name__ == "__main__":
    pdf = PDFManipulator(r"R:\57595 - Processos de Faturamento - Financeiro - Kleryson\#material\Safra-A044-1-2302-02-2025-3-10-7001068652.pdf")
    x = pdf.CPF_CNPJ# type: ignore
    if x:
        print(type(x), x)
        pdf.proteger_pdf()
        
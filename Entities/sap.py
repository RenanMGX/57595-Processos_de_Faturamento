from dependencies.sap import SAPManipulation
from dependencies.config import Config
from dependencies.credenciais import Credential
from dependencies.functions import Functions, P
from dependencies.logs import Logs, traceback
from datetime import datetime
from time import sleep
import os
import pandas as pd
import utils


class SAP(SAPManipulation):
    def __init__(self) -> None:
        crd:dict = Credential(Config()['credenciais']['sap']).load()
        
        super().__init__(user=crd['user'], password=crd['password'], ambiente=crd['ambiente'])
        
    
    @SAPManipulation.start_SAP
    def relatorio_partidas_individuais_cliente(self, date:datetime):
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n fbl5n"
        self.session.findById("wnd[0]").sendVKey(0)
        self.session.findById("wnd[0]/usr/ctxtDD_KUNNR-LOW").text = "*"
        self.session.findById("wnd[0]/tbar[1]/btn[16]").press()
        self.session.findById("wnd[0]/usr/chkX_SHBV").selected = "true"
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/ctxt%%DYN012-LOW").text = date.strftime("%d.%m.%Y")
        self.session.findById("wnd[0]/usr/ctxtPA_STIDA").text = ""
        self.session.findById("wnd[0]/usr/ctxtPA_VARI").text = "/A_RECEBER2"
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        
        #import pdb; pdb.set_trace()
        try:
            if self.session.findById("wnd[0]/sbar/pane[0]").text == 'Nenhuma partida selecionada (ver texto descritivo)':
                self.fechar_sap()
                raise Exception("Nenhuma partida selecionada!")
        except:
            pass
        
        path:str = os.path.join(f"C:\\Users\\{os.getlogin()}\\Downloads", datetime.now().strftime("%Y%m%d%H%M%S_relatorio_partidas_indivudais_cliente.xlsx"))
        
        self.session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select()
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(path)
        self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = os.path.basename(path)
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        
        sleep(5)
        
        Functions.fechar_excel(path)
        
        self.fechar_sap()
        
        return path
    
    
    @SAPManipulation.start_SAP
    def gerar_arquivos_de_remessa(self, data:dict) -> str:
        try:
            data['empresa']
            data['banco']
            data['docs']
        except KeyError as err:
            raise KeyError(f"Chave não encontrada! -> {err}")
        
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n zfi010"
        self.session.findById("wnd[0]").sendVKey(0)
        
        self.session.findById("wnd[0]/usr/ctxtS_BUKRS-LOW").text = data.get('empresa')
        self.session.findById("wnd[0]/usr/ctxtS_HBKID-LOW").text = data.get('banco')
        
        self.session.findById("wnd[0]/usr/btn%_S_BELNR_%_APP_%-VALU_PUSH").press()
        pd.DataFrame(data.get('docs')).to_clipboard(index=False, header=False)
        self.session.findById("wnd[1]/tbar[0]/btn[24]").press()
        self.session.findById("wnd[1]/tbar[0]/btn[8]").press()
        
        #import pdb; pdb.set_trace()
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        result = self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").getCellValue(0, "MSG")
        if result == "Nenhum documento encontrado":
            return ""
        return result
            
    

    @SAPManipulation.start_SAP
    def gerar_boletos_no_sap(self, *, date: datetime, pasta:str, debug:bool=False, mover_pdf:bool=False) -> bool:
        try:
            self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n zfi018"
            self.session.findById("wnd[0]").sendVKey(0)
            
            self.session.findById("wnd[0]/usr/ctxtS_BUKRS-LOW").text = "*"
            
            self.session.findById("wnd[0]/usr/txtS_GJAHR-LOW").text = str(date.year)
            self.session.findById("wnd[0]/usr/ctxtP_VENINI").text = utils.primeiro_dia_mes(date).strftime("%d.%m.%Y")#"01.02.2025"
            self.session.findById("wnd[0]/usr/ctxtP_VENFIM").text = utils.ultimo_dia_mes(date).strftime("%d.%m.%Y")#"28.02.2025"
            
            self.session.findById("wnd[0]/usr/ctxtP_PASTA").text = pasta # PASTA TEMPORARIA PARA DESENVOLVIMENTO
            self.session.findById("wnd[0]/usr/txtP_ARQ").text = r"{GSBER}-{BLOCO}-{UNIDADE}-{MES_VENC}-{ANO_VENC}-{SERIE}-{PARCELA}-{BELNR}.pdf"



            # apenas para desenvolvimento Remover depois
            if debug:
                self.session.findById("wnd[0]/usr/chkP_REIMP").selected = "false"
            ############################################

            self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
            
            if (sbar:=self.session.findById("wnd[0]/sbar").text) == 'Nenhum registro encontrado para os parâmetros informados':
                Logs().register(status='Report', description=f"Relatório de boletos não encontrado para o mês {date.strftime('%m/%Y')}<br>\n{sbar}")
                self.fechar_sap()
                return True
            
            self.session.findById("wnd[0]/usr/shell").setCurrentCell( -1,"")
            self.session.findById("wnd[0]/usr/shell").selectAll()
            if mover_pdf:
                utils.mover_pdfs(path=pasta, _date=datetime.now())
            self.session.findById("wnd[0]/usr/shell").pressToolbarButton("ZPDF")
            
            self.fechar_sap()
            
            return True
        except Exception as err:
            print(P(str(err), color='red'))
            Logs().register(status='Error', description=str(err), exception=traceback.format_exc())
            self.fechar_sap()
            
            return False
        
        
    
    @SAPManipulation.start_SAP
    def teste(self):
        import pdb; pdb.set_trace()
        
if __name__ == "__main__":
    pass

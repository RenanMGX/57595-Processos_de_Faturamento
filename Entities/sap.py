from dependencies.sap import SAPManipulation
from dependencies.config import Config
from dependencies.credenciais import Credential
from dependencies.functions import Functions, P
from datetime import datetime
from time import sleep
import os

class SAP(SAPManipulation):
    def __init__(self) -> None:
        crd:dict = Credential(Config()['credenciais']['sap']).load()
        
        super().__init__(user=crd['user'], password=crd['password'], ambiente=crd['ambiente'])
        
    
    @SAPManipulation.start_SAP
    def relatorio_partidas_individuais_cliente(self, date:datetime):
        import pdb; pdb.set_trace()
        
        self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n fbl5n"
        self.session.findById("wnd[0]").sendVKey(0)
        self.session.findById("wnd[0]/usr/ctxtDD_KUNNR-LOW").text = "*"
        self.session.findById("wnd[0]/tbar[1]/btn[16]").press()
        self.session.findById("wnd[0]/usr/chkX_SHBV").selected = "true"
        self.session.findById("wnd[0]/usr/ssub%_SUBSCREEN_%_SUB%_CONTAINER:SAPLSSEL:2001/ssubSUBSCREEN_CONTAINER2:SAPLSSEL:2000/ssubSUBSCREEN_CONTAINER:SAPLSSEL:1106/ctxt%%DYN012-LOW").text = "1.2.2025"
        self.session.findById("wnd[0]/usr/ctxtPA_STIDA").text = ""
        self.session.findById("wnd[0]/usr/ctxtPA_VARI").text = "/A_RECEBER2"
        self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        
        path:str = os.path.join(f"C:\\Users\\{os.getlogin()}\\Downloads", datetime.now().strftime("%Y%m%d%H%M%S_relatorio_partidas_indivudais_cliente.xlsx"))
        
        self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell/shellcont[1]/shell").contextMenu()
        self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell/shellcont[1]/shell").selectContextMenuItem("&XXL")
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(path)
        self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = os.path.basename(path)
        self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
        
        sleep(5)
        
        Functions.fechar_excel(path)
        
        self.fechar_sap()
        
        return path
        
        
if __name__ == "__main__":
    pass

from typing import Dict
from getpass import getuser

default:Dict[str, Dict[str,object]] = {
    'log': {
        'hostname': 'Patrimar-RPA',
        'port': '80',
        'token': 'Central-RPA'
    },
    'credenciais': {
        'imobme': 'IMOBME_PRD',
        'sap': 'SAP_PRD',
    },
    'path': {
        "download" : f"C:\\Users\\{getuser()}\\Downloads",
        "planilhaClientes": f"C:\\Users\\{getuser()}\\PATRIMAR ENGENHARIA S A\\RPA - Documentos\\RPA - Dados\\Relatorio_Imobme_Financeiro\\ClientesContratos.json"
    }
}
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
        'email': 'Email-Boletos',
        'email_debug': 'Microsoft-RPA'
    },
    'lista_emails':{
        'emailToSendLogs': 'contasareceber@patrimar.com.br'
    },    
    'path': {
        "download" : f"C:\\Users\\{getuser()}\\Downloads",
        "planilhaClientes": f"C:\\Users\\{getuser()}\\PATRIMAR ENGENHARIA S A\\RPA - Documentos\\RPA - Dados\\Relatorio_Imobme_Financeiro\\ClientesContratos.json"
    },
    'param': {
        'dias_ate_virar_mes': 7,
    }
}
from typing import Dict
from getpass import getuser

default:Dict[str, Dict[str,object]] = {
    'log': {
        'hostname': 'Patrimar-RPA',
        'port': '80',
        'token': 'Central-RPA'
    },
    'credenciais': {
        'imobme': 'IMOBME_PRD'
    },
    'path': {
        "download" : f"C:\\Users\\{getuser()}\\Downloads",
    }
}
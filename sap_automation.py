import win32com.client

def connect_to_sap():
    try:
        # Conecta ao SAP GUI
        sap_gui = win32com.client.GetObject("SAPGUI")
        if not sap_gui:
            raise Exception("SAP GUI não está disponível.")
        
        application = sap_gui.GetScriptingEngine
        connection = application.Children(0)  # Seleciona a primeira conexão aberta
        session = connection.Children(0)  # Seleciona a primeira sessão aberta
        
        return session
    except Exception as e:
        print(f"Erro ao conectar ao SAP: {e}")
        return None

def execute_transaction(session, transaction_code):
    try:
        # Executa uma transação no SAP
        session.StartTransaction(Transaction=transaction_code)
        print(f"Transação {transaction_code} executada com sucesso.")
    except Exception as e:
        print(f"Erro ao executar a transação {transaction_code}: {e}")

def main():
    session = connect_to_sap()
    if session:
        # Exemplo: Executar a transação "SE16N"
        execute_transaction(session, "SE16N")
        # Adicione outras interações com o SAP aqui
        # Exemplo: Preencher campos, clicar em botões, etc.
        # session.findById("wnd[0]/usr/ctxtSOME_FIELD").text = "valor"
        # session.findById("wnd[0]/tbar[1]/btn[8]").press()

if __name__ == "__main__":
    main()

import pandas as pd

def get_email_principal(row:pd.Series, df_clientes:pd.DataFrame):
    unidade = row['PEP Unidade']
    documento = row['Documento Principal']
    
    df_email:pd.Series = df_clientes[
        (df_clientes['PEP Unidade'] == unidade) &
        (df_clientes['CPF/ CNPJ'] == documento) &
        (df_clientes['Principal (Sim ou Não)'] == 'Sim')
    ]['E-mail']
    
    if not df_email.empty:
        return df_email.unique().tolist()[0]
    
    return pd.NA


def get_email_segundo(row:pd.Series, df_clientes:pd.DataFrame):
    unidade = row['PEP Unidade']
    
    df_email:pd.Series = df_clientes[
        (df_clientes['PEP Unidade'] == unidade) &
        (df_clientes['Principal (Sim ou Não)'] == 'Não')
    ]['E-mail']
    
    if not df_email.empty:
        return df_email.unique().tolist()[0]
    
    return pd.NA


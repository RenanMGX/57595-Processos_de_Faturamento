import google.generativeai as gemini
from typing import Literal
import json
import os
class Historico:
    path = os.path.join(f'C:\\Users\\{os.getlogin()}', '.historico_gemini.json')
    
    @staticmethod
    def get_historico() -> list:
        try:
            with open(Historico.path, "r", encoding='utf-8') as _file:
                historico = json.loads(_file.read())
            return historico
        except:
            return []
    
    @staticmethod
    def set_historico(historico:list):
        with open(Historico.path, "w", encoding='utf-8') as _file:
            json.dump(historico, _file, indent=4)
    
    @staticmethod  
    def clear_historico():
        with open(Historico.path, "w", encoding='utf-8') as _file:
            json.dump([], _file, indent=4)

class GeminiIA:
    @property
    def safety_settings(self):
        return [
                {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_NONE"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH",
                                "threshold": "BLOCK_NONE"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_NONE"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_NONE"
                            },            
                    ]
    
    @property
    def model(self):
        return self.__model
        
    def __init__(self, *,
                token:str,
                instructions:str = "voce é um assistente virual prestavito e educado!",
                model:Literal["gemini-2.0-flash", "gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-preview-05-06", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"] = "gemini-2.0-flash-lite",
                    temperature: float = 0.5,
                    max_output_tokens: int = 500,
                    top_p: float = 0.9,
                    top_k: int = 40,
                 ):
        
        self.__model = gemini.GenerativeModel(#type: ignore
            model_name = model,
            generation_config={
                "temperature": temperature, #type: ignore
                "max_output_tokens": max_output_tokens,
                "top_p": top_p,
                "top_k": top_k,
            },
            system_instruction = f"{instructions}\n Adicional: seu nome e 'RPA' e quem esta te programando é o Renan Oliveira usando api da google generative ai",
            safety_settings=self.safety_settings        
        )
        
        gemini.configure(api_key=token)#type: ignore
        
    def clear_historico(self, *, path:str):
        Historico.clear_historico()
    
    def perguntar(self, pergunta:str, *, save_history:bool=False):
        if save_history:
            history = Historico.get_historico()
            
            formated_history = []
            for interacao in history:
                for mensagem in interacao:
                    formated_history.append({
                        "role": mensagem["role"],  # Certifique-se de que a chave é 'author'
                        "parts": mensagem["parts"]    # 'parts' deve ser uma lista de strings
            }) 
                    
            history = formated_history
        else:
            history = []
        
        
        response = self.model.start_chat(history=history).send_message(pergunta)
        
        if save_history:
            historico_temp = []
            historico_temp.append({"role": "user", "parts": [pergunta]})
            historico_temp.append({"role": "model", "parts": [response.text]})

            history.append(historico_temp)
            Historico.set_historico(historico=history)
            
        return response
        
if __name__ == "__main__":
    from credenciais import Credential
    api_token = Credential('GeminiIA-Token-Default').load()['token']
    
    ia = GeminiIA(token=api_token, model='gemini-2.0-flash-lite',
                  instructions="vc irá receber um Tracback de um programa python vc vai analisar e explicar o erro de forma curta e objetiva e sujerir uma solução de forma curta e objetiva"
                  
                  )
    try:
        import json
        json.loads("{")
    except Exception as e:
        import traceback
        response = ia.perguntar(traceback.format_exc())
    
        print(response.text)
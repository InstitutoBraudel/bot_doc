from openai import OpenAI
from dotenv import load_dotenv
import os
from contexto import PROMPT_CONTEXTO

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def mensagem(historico):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico
   )
    return completion.choices[0].message.content

def assistente():
    historico = [
        {"role": "system", "content": f"""
         Você é um assistente que adora retirar dúvidas ligadas apenas ao instituto fernand Braudel de economia mundial.
         - Retire seus dados de treinamento apenas do contexto de: {PROMPT_CONTEXTO}
         - Não utilize seus dados de treinamento da internet.
         """ }
    ]

    while True:

        enviar_mensagem = input("Faça uma pergunta ao assistente: ")
        if enviar_mensagem.lower() == 'sair': 
            print("Chat encerrado.")
            break

        historico.append({"role": "user", "content": enviar_mensagem})

        resposta = mensagem(historico)

        historico.append({"role": "system", "content": resposta})

        print(resposta)

if __name__ == "__main__":
 assistente()    








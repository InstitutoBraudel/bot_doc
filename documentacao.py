from openai import OpenAI
from dotenv import load_dotenv
import os
from contexto import PROMPT_CONTEXTO
<<<<<<< HEAD
from flask import Flask, request, jsonify
import requests
=======
>>>>>>> 97c0c5cfc0c50bbc6b0529ad21927eda394d3c25

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
<<<<<<< HEAD
whatsapp_token = os.getenv("WHATSAPP_TOKEN")
whatsapp_phone_id = os.getenv("NUMBER_ID")
VERIFY_TOKEN = "my_verify_token"

app = Flask(__name__)

historicos = {}
=======
>>>>>>> 97c0c5cfc0c50bbc6b0529ad21927eda394d3c25

def mensagem(historico):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico
   )
    return completion.choices[0].message.content

<<<<<<< HEAD
def send_whatsapp_message(phone_number, message):
    url = f"https://graph.facebook.com/v13.0/{whatsapp_phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
      }

    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        } 
    } 
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/webhook', methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
           if mode == "subscribe" and token == VERIFY_TOKEN:
             return challenge, 200      
           else: 
             return "Forbidden", 403
           
    if request.method == "POST":
     data = request.get_json()
    if data["object"] == "whatsapp_business_account":
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                  for message in change["value"]["messages"]:
                      if message["type"] == "text":
                        phone_number = message["from"]
                        texto_mensagem = message["text"]["body"]

                        if phone_number not in historicos:
                            historicos[phone_number] = [
                                            {"role": "system", "content": f"""Você é um bot prestativo que adora ajudar o usuário a retirar suas dúvidas sobre o instituto Fernand Braudel de Economia Mundial.
                                            - Você não deve responder sobre nenhum assunto que fuja do contexto em: {PROMPT_CONTEXTO}
                                            """} 
                                            ]
                            
                            historicos[phone_number].append({"role": "user", "content": texto_mensagem})

                            resposta = mensagem(historicos[phone_number])

                            historicos[phone_number].append({"role": "system", "content": resposta})

                            send_whatsapp_message(phone_number, resposta)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
 app.run(debug=True)    
=======
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
>>>>>>> 97c0c5cfc0c50bbc6b0529ad21927eda394d3c25








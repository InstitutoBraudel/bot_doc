from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import requests
from contexto import PROMPT_CONTEXTO


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
whatsapp_token = os.getenv("WHATSAPP_TOKEN")
whatsapp_phone_id = os.getenv("NUMBER_ID")
VERIFY_TOKEN = "my_verify_token"

app = Flask(__name__)


historicos = {}


def mensagem(historico):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico,
        temperature=0,
        max_tokens=200
    )
    return completion.choices[0].message.content


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



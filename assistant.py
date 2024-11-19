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
modelo = "gpt-4o-mini" 

app = Flask(__name__)

def bot(prompt):
    assistant = client.beta.assistants.create(
        name="Assistente Braudel",
        instructions="""
                    Você é o assistente virtual do Instituto Fernand Braudel e deve tirar todas as dúvidas referente ao tema.
                    Avalie todos os documentos fornecidos e não fuja do assunto.
                    Limite suas respostas apenas ao contexto e informações fornecidas.
                """,
        model=modelo,
        temperature=0,
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Arquivos Braudel")

    file_paths = [
              "./dados/braudel_lembrancas.pdf",
              "./dados/braudel_papers.txt",
              "./dados/braudel.txt",
              "./dados/guia_circulosS.txt",
              "./dados/livreto_contos.pdf",
              "./dados/metodologia.txt",
              "./dados/modulo_amor.pdf",
              ]
    
    file_streams = [open(path, "rb") for path in file_paths]

    # Faz o upload dos arquivos para o repositório de vetores
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    print(file_batch.status)

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        instructions=F"Você é um atendente do instituto Braudel, siga as instruções do contexto passado em: {PROMPT_CONTEXTO}",
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        temperature=0
    )


    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    # Executa a conversa e aguarda a resposta
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    resposta = messages[0]

    for message in messages:
        if 'tool_use' in message:
            tool_use = message['tool_use']
            if tool_use['type'] == 'file_search':
                file_hits = tool_use['file_search']['file_hits']
                for hit in file_hits:
                    print(f"Response derived from file: {hit['file_name']}")

    return resposta #Retorna a resposta do assistente Braudel

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
        app.logger.info(f"Received webhook data: {data}")
        if data["object"] == "whatsapp_business_account":
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "messages" in change["value"]:
                        for message in change["value"]["messages"]:
                            if message["type"] == "text":
                                phone_number = message["from"]
                                text = message["text"]["body"]
                                resposta = bot(text)  # Chama a função bot com o texto recebido
                                texto_resposta = resposta.content[0].text.value
                                send_whatsapp_message(phone_number, texto_resposta)  # Envia a resposta para o WhatsApp

        return jsonify({"status": "success"}), 200  # Retorna sucesso após processar o webhook


if __name__ == "__main__":
    app.run(debug=True)

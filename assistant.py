from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
whatsapp_token = os.getenv("WHATSAPP_TOKEN")
whatsapp_phone_id = os.getenv("NUMBER_ID")
VERIFY_TOKEN = "my_verify_token"

app = Flask(__name__)

historicos = {}

def adicionar_arquivos_a_vector_store(client, vector_store_id, file_paths):
    file_streams = [open(path, "rb") for path in file_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    print(file_batch.status)

def criar_assistente_com_vector_store(client, model, nome, instrucoes, file_paths):
    assistant = client.beta.assistants.create(
        name=nome,
        instructions=instrucoes,
        model=model,
        temperature=0,
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Arquivos Braudel")
    adicionar_arquivos_a_vector_store(client, vector_store.id, file_paths)

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        instructions=f"""
            Você é um atendente do instituto Braudel, suas funções são:
            - Tirar dúvidas sobre o Instituto Braudel,
            - Tirar dúvidas sobre o projeto Braudel Papers,
            - Tirar dúvidas sobre o projeto Programa Círculos de Leitura,
            - Tirar dúvidas sobre os livros do Programa Círculos de Leitura,
            Não responderei nada que fuja do tema Instituto Braudel
            Os arquivos associados à thread são os arquivos que vou utilizar para responder as perguntas.
        """,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        temperature=0
    )

    return assistant

file_paths = ["./arquivos/contexto.txt", "./arquivos/BraudelPaper_42.pdf"]

assistant = criar_assistente_com_vector_store(
    client=client,
    model="gpt-4o-mini",
    nome="Atendente Braudel",
    instrucoes="Você é um atendente do instituto Braudel e só deve responder perguntas relacionadas ao instituto Braudel",
    file_paths=file_paths
)

def bot(prompt):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

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

    return resposta

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
                                        {"role": "system", "content": """Você é um atendente do instituto Fernand Braudel de Economia Mundial.
                                         - Sempre receba o usuário com a frase: Olá, sou atendente do instituto Braudel, Posso tirar suas dúvidas e apresentar o instituto.
                                         - Caso o usuário realize perguntas que saíam do contexto do instituto Braudel informe sempre: Perdão, não  possuo informações que não sejam relacionadas ao instituto Braudel.
                                         """}
                                    ]

                                historicos[phone_number].append({"role": "user", "content": texto_mensagem})

                                resposta = bot(texto_mensagem)

                                historicos[phone_number].append({"role": "assistant", "content": resposta.content[0].text.value})

                                send_whatsapp_message(phone_number, resposta.content[0].text.value)
                                
        return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True)

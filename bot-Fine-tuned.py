from openai import OpenAI
import os
from dotenv import load_dotenv
import time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Modelos de fine-tunning (teste): 
 #ft:gpt-4o-mini-2024-07-18:braudel::ASTOXWnL (teste de funcionamento redações 01
 #ft:gpt-4o-mini-2024-07-18:braudel::AXzVig1A (teste de funcionamento redações*50 linhas)
 #ft:gpt-4o-mini-2024-07-18:braudel::AYCOLWJU (teste de funcionamento redações*100 linhas)
 #ft:gpt-4o-mini-2024-07-18:braudel::AaW3l981 (teste de fincionamento redações*200 linhas)
 #ft:gpt-4o-mini-2024-07-18:braudel::AaWUmHzE (teste de funcionamento apenas competência #1)
 #ft:gpt-4o-mini-2024-07-18:braudel::Ab68gaVE (teste de funcionamento apenas competência #1*100 linhas de treinamento)
 #ft:gpt-4o-mini-2024-07-18:braudel::Ad0c4qWC (teste de funcionamento apenas competência #1*100 linhas apenas com pontuação)

# Função para fazer upload do arquivo de fine-tuning e treinar o modelo
def upload_and_train_fine_tuning(client, file_path):
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Arquivo {file_path} não encontrado.")
        return None

    # Upload do arquivo de fine-tuning
    with open(file_path, 'rb') as f:
        file_response = client.files.create(
            file=f,
            purpose='fine-tune'
        )
    file_id = file_response.id
    print(f"Arquivo de fine-tuning enviado com sucesso. ID do arquivo: {file_id}")

    # Treinamento do modelo com o arquivo de fine-tuning
    fine_tune_response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-4o-mini-2024-07-18",  # Usando um modelo disponível para fine-tuning
    )
    fine_tune_id = fine_tune_response.id
    print(f"Fine-tuning iniciado. ID do fine-tune: {fine_tune_id}") 

    return fine_tune_id

# Caminho do arquivo de fine-tuning
<<<<<<< HEAD
fine_tuning_file_path = "./fine-tunning/fine-tune-comp1.jsonl"

=======
fine_tuning_file_path = "./fine-tunning/fine-tune-comp1_2.jsonl"
>>>>>>> 937183d42de4255b9c8a3235ff6b200d8f8ebef0

# Verificar se o caminho do arquivo está correto
if not os.path.exists(fine_tuning_file_path):
    print(f"Erro: Arquivo não encontrado em {fine_tuning_file_path}")
else:
    print(f"Arquivo encontrado: {fine_tuning_file_path}")

    # Fazer upload e iniciar o treinamento
    fine_tune_id = upload_and_train_fine_tuning(client, fine_tuning_file_path)

    # Aguardar a conclusão do fine-tuning (isso pode levar algum tempo)
    if fine_tune_id:
        while True:
            status_response = client.fine_tuning.jobs.retrieve(fine_tune_id)
            status = status_response.status
            if status == 'succeeded':
                fine_tuned_model = status_response.fine_tuned_model
                print(f"Fine-tuning concluído. Modelo de fine-tuning: {fine_tuned_model}")
                break
            elif status == 'failed':
                print("Fine-tuning falhou.")
                break
            else:
                print(f"Status atual: {status}. Verificando novamente em 60 segundos...")
<<<<<<< HEAD
            time.sleep(60)  # Espera de 60 segundos antes de checar novamente

  #Teste de fine-tunning: 
 #ft:gpt-4o-mini-2024-07-18:braudel::ASTOXWnL (teste de funcionamento redações 01)
 #ft:gpt-4o-mini-2024-07-18:braudel::AXzVig1A (teste de funcionamento redações*50 linhas)
 #ft:gpt-4o-mini-2024-07-18:braudel::AYCOLWJU (teste de funcionamento redação*100 linhas)
 #ft:gpt-4o-mini-2024-07-18:braudel::AaW3l981 (teste de funcionamento redação*200)
 #ft:gpt-4o-mini-2024-07-18:braudel::AaWUmHzE (teste fine tunning competência 1)

=======
            time.sleep(60)  # Espera de 60 segundos antes de checar novamente
>>>>>>> 937183d42de4255b9c8a3235ff6b200d8f8ebef0

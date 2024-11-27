from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client.files.create(
  file=open("mydata.jsonl", "rb"),
  purpose="fine-tune"
)






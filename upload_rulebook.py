from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

vector_store = client.vector_stores.create(
    name="Horse Jumping Rulebook"
)

file = client.files.create(
    file=open("FEI Jumping Rules 2026.pdf", "rb"),
    purpose="assistants"
)

client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file.id
)

print("Vector store ID:", vector_store.id)

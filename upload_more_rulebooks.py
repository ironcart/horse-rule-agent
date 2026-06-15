from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

VECTOR_STORE_ID = "vs_6a2f824f1698819199faf10e087e5b20"

files_to_upload = [
    "FEI General Regulations 2026.pdf",
    "FEI Veterinary Regulations 2026.pdf"
]

for filename in files_to_upload:
    print(f"Uploading {filename}...")

    file = client.files.create(
        file=open(filename, "rb"),
        purpose="assistants"
    )

    client.vector_stores.files.create(
        vector_store_id=VECTOR_STORE_ID,
        file_id=file.id
    )

    print(f"Uploaded {filename}")

print("Done.")

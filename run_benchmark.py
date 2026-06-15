import csv
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

VECTOR_STORE_ID = "vs_6a2f824f1698819199faf10e087e5b20"

with open("benchmark.csv", "r") as infile, open("benchmark_results.csv", "w", newline="") as outfile:

    reader = csv.DictReader(infile)

    writer = csv.writer(outfile)

    writer.writerow([
        "Question",
        "Expected Article",
        "Expected Outcome",
        "AI Answer"
    ])

    for row in reader:

        question = row["Question"]

        print(f"Running: {question}")

        response = client.responses.create(
            model="gpt-4.1",
            input=question,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": ["vs_6a2f824f1698819199faf10e087e5b20"]
                }
            ]
        )

        writer.writerow([
            row["Question"],
            row["Expected Article"],
            row["Expected Outcome"],
            response.output_text
        ])

print("Done.")

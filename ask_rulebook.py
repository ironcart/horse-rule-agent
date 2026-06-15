from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

VECTOR_STORE_ID = "vs_6a2f824f1698819199faf10e087e5b20"

print("Horse Jumping Rulebook Assistant")
print("--------------------------------")

federation = input("Federation? Example: FEI, USEF, local: ")
competition_type = input("Competition type? Example: CSI, national, schooling: ")
class_type = input("Class type? Example: normal round, speed, jump-off, two-phase: ")
incident_type = input("Incident type? Example: refusal, fall, tack, blood, lameness: ")
round_type = input("Round? Example: first round, second round, jump-off: ")

question = input("What is your rulebook question? ")

full_question = f"""
Federation: {federation}
Competition type: {competition_type}
Class type: {class_type}
Incident type: {incident_type}
Round: {round_type}

Question:
{question}
"""

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system",
            "content": """

You are a horse jumping steward rulebook assistant.

You are advisory only. You do not make official rulings.

Answer only from retrieved rulebook content.

Never invent:
- article numbers
- penalties
- procedures
- interpretations not supported by the rulebook

If information is missing, ask for it.

If no rule is found, state:
"Not found in the loaded rulebook."

Every answer must use this exact structure:

QUESTION SUMMARY
One-sentence summary of the user’s question.

OUTCOME
Permitted / Not Permitted / Warning / Elimination / Disqualification / Ground Jury Decision Required / Not Found / Depends

APPLICABLE RULE
Rule/article number. If not found, say "Not found."

SOURCE
Document name and page number if available.

QUOTE
Short exact quote from the rulebook. If not found, say "No supporting quote found."

PRACTICAL INTERPRETATION
Plain English explanation for a steward.

MISSING FACTS
List missing facts. If none, say "None."

CONFIDENCE
High / Medium / Low

STEWARD ACTION
What the steward should do next.
"""

 },
        {
            "role": "user",
            "content": full_question
        }
    ],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID]
        }
    ]
)

print("\n--- ANSWER ---\n")
print(response.output_text)

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import csv
from datetime import datetime

load_dotenv()

client = OpenAI()


CORE_VECTOR_STORE_ID = "vs_6a2f824f1698819199faf10e087e5b20"

if "event_vector_store_id" not in st.session_state:
    st.session_state.event_vector_store_id = None


st.set_page_config(
    page_title="Horse Jumping Rulebook Assistant",
    layout="wide"
)


st.title("Horse Jumping Rulebook Assistant")

event_name = st.sidebar.text_input("Event name", placeholder="Example: CSI Woodside July 2026")

if st.button("Create new event workspace"):
    if event_name:
        event_vector_store = client.vector_stores.create(
            name=f"Event Workspace - {event_name}"
        )
        st.session_state.event_vector_store_id = event_vector_store.id
        st.session_state.event_docs = []
        st.success(f"Created event workspace: {event_name}")
    else:
        st.error("Enter an event name first.")


st.warning(
    "Advisory only. Official decisions remain with the Ground Jury, Steward, Technical Delegate, Veterinarian, and applicable Federation."
)


st.divider()
st.subheader("Current Workspace")

if st.session_state.event_vector_store_id:
    st.write("Event workspace active:")
    st.code(st.session_state.event_vector_store_id)
else:
    st.write("No event workspace active. Using core rulebooks only.")


if st.button("Reset event workspace"):
    st.session_state.event_vector_store_id = None
    st.session_state.event_docs = []
    st.success("Event workspace reset. The app is now using core rulebooks only.")

if st.session_state.get("event_docs"):
    st.write("Uploaded event documents:")
    for doc in st.session_state.event_docs:
        st.write(f"- {doc}")
else:
    st.write("No event-specific documents uploaded.")

federation = st.sidebar.selectbox(
    "Federation",
    ["FEI", "USEF", "Local / Other"]
)

competition_type = st.sidebar.selectbox(
    "Competition Type",
    ["CSI", "National", "Schooling", "Other"]
)

class_type = st.sidebar.selectbox(
    "Class Type",
    ["Normal Round", "Speed", "Jump-Off", "Two-Phase", "Other"]
)

incident_type = st.sidebar.selectbox(
    "Incident Type",
    [
        "Refusal",
        "Fall",
        "Tack",
        "Blood",
        "Lameness",
        "Timing",
        "Eligibility",
        "General Rule Question",
        "Other"
    ]
)

round_type = st.sidebar.selectbox(
    "Round",
    [
        "First Round",
        "Second Round",
        "Jump-Off",
        "Other"
    ]
)


st.divider()
st.subheader("Upload Event-Specific Document")

event_file = st.sidebar.file_uploader(
    "Upload event schedule, prize list, ground jury notes, or local rules PDF",
    type=["pdf"]
)

if event_file is not None:
    if st.button("Add event document to rule search"):
        temp_filename = event_file.name

        with open(temp_filename, "wb") as f:
            f.write(event_file.getbuffer())

        with st.spinner("Uploading event document..."):
            uploaded_file = client.files.create(
                file=open(temp_filename, "rb"),
                purpose="assistants"
            )

            client.vector_stores.files.create(
                vector_store_id=st.session_state.event_vector_store_id or CORE_VECTOR_STORE_ID,
                file_id=uploaded_file.id
            )

        
        if "event_docs" not in st.session_state:
            st.session_state.event_docs = []

        st.session_state.event_docs.append(event_file.name)

        st.success(f"Uploaded and indexed: {event_file.name}")
        st.warning("This event document is now part of the search index. Remove or reset the vector store before using this app for a different event.")



if "event_docs" in st.session_state and st.session_state.event_docs:
    st.info("Active event documents: " + ", ".join(st.session_state.event_docs))

question = st.text_area(
    "Rulebook Question",
    height=120
)

if st.button("Ask Rulebook") and question:

    full_question = f"""
Federation: {federation}
Competition Type: {competition_type}
Class Type: {class_type}
Incident Type: {incident_type}
Round: {round_type}

Question:
{question}
"""

    with st.expander("Debug: context sent to AI"):
        st.text(full_question)

    with st.spinner("Searching rulebooks..."):

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": """
You are a horse jumping steward rulebook assistant.

You are advisory only.
You do not make official rulings.

Answer only from retrieved rulebook content.

Never invent:
- article numbers
- penalties
- procedures
- interpretations not supported by the rulebook

If information is missing, ask for it.

If no rule is found, state:
Not found in the loaded rulebook.

Every answer must use this exact structure:

QUESTION SUMMARY

OUTCOME

APPLICABLE RULE

SOURCE

QUOTE

PRACTICAL INTERPRETATION

MISSING FACTS

CONFIDENCE

STEWARD ACTION
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
                    "vector_store_ids": [CORE_VECTOR_STORE_ID] + ([st.session_state.event_vector_store_id] if st.session_state.event_vector_store_id else [])
                }
            ]
        )

    answer_text = response.output_text

    st.success("Answer generated")

    sections = [
        "QUESTION SUMMARY",
        "OUTCOME",
        "APPLICABLE RULE",
        "SOURCE",
        "QUOTE",
        "PRACTICAL INTERPRETATION",
        "MISSING FACTS",
        "CONFIDENCE",
        "STEWARD ACTION"
    ]

    found_section = False

    for section in sections:
        if section in answer_text:
            found_section = True
            start = answer_text.find(section) + len(section)

            next_positions = [
                answer_text.find(next_section, start)
                for next_section in sections
                if answer_text.find(next_section, start) != -1
            ]

            end = min(next_positions) if next_positions else len(answer_text)
            content = answer_text[start:end].strip()

            st.subheader(section)
            st.write(content)

    if not found_section:
        st.subheader("Answer")
        st.text_area("", answer_text, height=500)

    with open("audit_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            federation,
            competition_type,
            class_type,
            incident_type,
            round_type,
            question,
            answer_text,
            ", ".join(st.session_state.get("event_docs", []))
        ])

st.divider()

try:
    with open("audit_log.csv", "rb") as f:
        st.download_button(
            label="Download audit log",
            data=f,
            file_name="audit_log.csv",
            mime="text/csv"
        )
except FileNotFoundError:
    st.info("No audit log yet. Ask a question first.")

if st.button("Clear audit log"):
    try:
        open("audit_log.csv", "w").close()
        st.success("Audit log cleared.")
    except Exception as e:
        st.error(f"Could not clear audit log: {e}")

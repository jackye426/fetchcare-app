import streamlit as st
import base64
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

from auth import login_ui
from firestore_utils import save_message, get_chat_history, save_tracker, get_tracker

# ---------- Secure Key Loading ----------
# Load Streamlit secrets or fallback to local .env
api_key = st.secrets.get("openai_api_key")
if api_key is None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


# ---------- Auth ----------
if "user_id" not in st.session_state:
    login_ui()
    st.stop()

user_id = st.session_state.user_id

# ---------- Initialize Session State ----------
if "pet_list" not in st.session_state:
    st.session_state.pet_list = ["➕ Add New Pet"]

if "messages" not in st.session_state:
    st.session_state.messages = {}

if "selected_pet_name" not in st.session_state:
    st.session_state.selected_pet_name = "Your Pet"

# ---------- Select or Add Pet ----------
selected_pet = st.sidebar.selectbox("Select Pet", st.session_state.pet_list)

if selected_pet == "➕ Add New Pet":
    with st.sidebar.form("add_pet_form"):
        new_name = st.text_input("Pet Name")
        new_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Other"])
        new_age = st.number_input("Age (years)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Add")

        if submitted and new_name:
            name_cap = new_name.strip().capitalize()
            if name_cap not in st.session_state.messages:
                st.session_state.messages[name_cap] = []
            st.session_state.pet_list.insert(0, name_cap)
            st.session_state.selected_pet_name = name_cap
            st.session_state.pet_species = new_species.lower()
            st.session_state.pet_age = new_age
            st.rerun()
else:
    st.session_state.selected_pet_name = selected_pet

pet_name = st.session_state.selected_pet_name

# ---------- Initialize chat history for pet ----------
if pet_name not in st.session_state.messages:
    st.session_state.messages[pet_name] = [{
        "role": "assistant",
        "content": f"Hi! I'm here to help with {pet_name}'s care. Can you tell me what's going on with them today?"
    }] + get_chat_history(user_id, pet_name)

# ---------- Sidebar: Profile & Trackers ----------
st.sidebar.header("🐾 Pet Profile & Trackers")
name = st.sidebar.text_input("Name", value=pet_name)
species = st.sidebar.selectbox("Species", ["Dog", "Cat", "Rabbit", "Other"])
age = st.sidebar.number_input("Age (years)", min_value=0.0, step=0.1, value=st.session_state.get("pet_age", 0.0))

if st.sidebar.button("Update Profile"):
    st.session_state.selected_pet_name = name.strip().capitalize()
    st.session_state.pet_species = species.lower()
    st.session_state.pet_age = age

# ---------- Trackers ----------
with st.sidebar.expander("🍽 Meal Tracker"):
    meal_input = st.text_input("What did your pet eat?", key="meal_input")
    if st.sidebar.button("Log Meal", key="meal_btn") and meal_input:
        save_tracker(user_id, pet_name, "meal", meal_input)

with st.sidebar.expander("💩 Poop Tracker"):
    poop_input = st.text_input("Describe poop (color, consistency, etc.)", key="poop_input")
    if st.sidebar.button("Log Poop", key="poop_btn") and poop_input:
        save_tracker(user_id, pet_name, "poop", poop_input)

with st.sidebar.expander("🌀 Swelling Tracker"):
    swell_input = st.text_input("Location, size, tenderness", key="swell_input")
    if st.sidebar.button("Log Swelling", key="swell_btn") and swell_input:
        save_tracker(user_id, pet_name, "swelling", swell_input)

with st.sidebar.expander("⚖️ Weight Tracker"):
    weight_input = st.number_input("Current weight (kg)", key="weight_input")
    if st.sidebar.button("Log Weight", key="weight_btn") and weight_input:
        save_tracker(user_id, pet_name, "weight", str(weight_input))

# ---------- Typing Animation ----------
def write_stream(text, speed=0.03):
    container = st.empty()
    current_text = ""
    for word in text.split():
        current_text += word + " "
        container.markdown(current_text + "▌")
        time.sleep(speed)
    container.markdown(current_text)

# ---------- Main App ----------
st.title("🐶 FetchCare.ai — Chat with Pip")

# Display chat history
messages = st.session_state.messages.get(pet_name, [])
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Upload image
uploaded_file = st.file_uploader("📸 Upload a photo of your pet’s symptom (optional)", type=["jpg", "jpeg", "png"])

# Chat input
user_message = st.chat_input(f"Ask Pip about {pet_name}...")


if user_message:
    st.session_state.messages[pet_name].append({"role": "user", "content": user_message})
    save_message(user_id, pet_name, "user", user_message)

    content_parts = [{"type": "text", "text": user_message}]
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:image/png;base64,{image_b64}"
        content_parts.append({"type": "image_url", "image_url": {"url": image_url}})

    with st.chat_message("assistant"):
        thinking = st.empty()
        thinking.markdown("🤖 Pip is thinking...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Pip, a kind and careful AI triage assistant for pets. "
                        "You NEVER diagnose. You observe gently, help owners assess urgency, log symptoms, "
                        "and suggest if a vet visit is needed. Always be warm and emotionally supportive. "
                        "Follow the Veterinary Surgeons Act of 1966."
                    )
                },
                {
                    "role": "user",
                    "content": content_parts
                }
            ],
            temperature=0.6,
            max_tokens=1000
        )

        reply = response.choices[0].message.content.strip()
        thinking.empty()
        write_stream(reply)

    st.session_state.messages[pet_name].append({"role": "assistant", "content": reply})
    save_message(user_id, pet_name, "assistant", reply)
    st.rerun()

# ---------- Report Generator ----------
if st.button("📝 Generate Report for Vet"):
    profile = {
        "name": pet_name,
        "species": st.session_state.get("pet_species", "unknown"),
        "age": st.session_state.get("pet_age", 0)
    }

    report_lines = [
        "🐾 **Pet Profile**",
        f"Name: {profile['name']}",
        f"Species: {profile['species']}",
        f"Age: {profile['age']}",
        "",
        "📝 **Recent Logs**"
    ]

    for key in ["meal", "poop", "swelling", "weight"]:
        logs = get_tracker(user_id, pet_name, key)[-3:]
        report_lines.append(f"- {key.capitalize()}: {logs if logs else 'None logged'}")

    report_lines.append("\n⚠️ This summary is for informational purposes only and does not include any diagnosis or treatment advice.")

    st.download_button("Download Vet Report", "\n".join(report_lines), file_name="fetchcare_vet_report.txt")
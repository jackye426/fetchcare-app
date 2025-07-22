import pyrebase
import streamlit as st
from google.cloud import firestore
import os
import json
from dotenv import load_dotenv

# ---------- Load Secrets ----------
# Use Streamlit secrets in production, fallback to .env locally
firebaseConfig = {
    "apiKey": st.secrets.get("firebase_api_key", None),
    "authDomain": st.secrets.get("firebase_auth_domain", None),
    "projectId": st.secrets.get("firebase_project_id", None),
    "storageBucket": st.secrets.get("firebase_storage_bucket", None),
    "messagingSenderId": st.secrets.get("firebase_messaging_sender_id", None),
    "appId": st.secrets.get("firebase_app_id", None),
    "measurementId": st.secrets.get("firebase_measurement_id", None),
    "databaseURL": st.secrets.get("firebase_database_url", None)
}

if not firebaseConfig["apiKey"]:  # fallback to .env if not on Streamlit
    load_dotenv()
    firebaseConfig = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
    }

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------- Firestore (service account) ----------
if "service_account_json" in st.secrets:
    service_account_info = json.loads(st.secrets["service_account_json"])
    db = firestore.Client.from_service_account_info(service_account_info)
else:
    db = firestore.Client.from_service_account_json("serviceAccountKey.json")

# ---------- Auth UI ----------
def login_ui():
    st.subheader("🔐 Login to FetchCare")

    choice = st.radio("Login or Sign up?", ["Login", "Sign up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Sign up":
        if st.button("Create Account"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Account created! Please log in.")
            except Exception as e:
                st.error(f"Error creating account: {e}")
    else:
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user
                st.session_state.user_id = user["localId"]
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error("Login failed. Please check your credentials.")

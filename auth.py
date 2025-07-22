import pyrebase
import streamlit as st
from google.cloud import firestore

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyCuuRBNm5xw4R51Rbbmypm99kOR3cpAqTI",
    "authDomain": "fetchcare-71b29.firebaseapp.com",
    "projectId": "fetchcare-71b29",
    "storageBucket": "fetchcare-71b29.appspot.com",
    "messagingSenderId": "125951012154",
    "appId": "1:125951012154:web:29cf6f879580285a663403",
    "measurementId": "G-PE948Y24FP",
    "databaseURL": "https://fetchcare-71b29.firebaseio.com"  # <-- Add this line
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firestore.Client.from_service_account_json("serviceAccountKey.json")

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
                st.session_state.user_id = user["localId"]  # unique ID
                st.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.error("Login failed. Please check your credentials.")

# Use db for Firestore operations elsewhere in your code

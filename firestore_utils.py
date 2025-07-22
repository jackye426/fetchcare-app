from google.cloud import firestore
import streamlit as st

# ---------- Firestore Connection ----------
# Support both Streamlit secrets and local JSON key
if "service_account_json" in st.secrets:
    db = firestore.Client.from_service_account_info(dict(st.secrets["service_account_json"]))
else:
    db = firestore.Client.from_service_account_json("serviceAccountKey.json")

# Print Firestore project (for debugging)
print("Firestore project ID:", db.project)

# Define example user_id and pet_name (remove in production)
user_id = "test_user"
pet_name = "test_pet"
print(db.collection("fetchcare2").document(user_id).collection("pets").document(pet_name).path)

# ---------- Firestore Functions ----------

def save_message(user_id, pet_name, role, content):
    """Save a chat message to Firestore."""
    db.collection("fetchcare2").document(user_id)\
      .collection("pets").document(pet_name)\
      .collection("chat_history").add({
          "role": role,
          "content": content,
          "timestamp": firestore.SERVER_TIMESTAMP
      })

def get_chat_history(user_id, pet_name):
    """Retrieve chat history sorted by timestamp."""
    ref = db.collection("fetchcare2").document(user_id)\
            .collection("pets").document(pet_name)\
            .collection("chat_history").order_by("timestamp")
    return [doc.to_dict() for doc in ref.stream()]

def save_tracker(user_id, pet_name, tracker_type, value):
    """Append a value to the specified tracker log."""
    db.collection("fetchcare2").document(user_id)\
      .collection("pets").document(pet_name)\
      .collection("trackers").document(tracker_type)\
      .set({
          "entries": firestore.ArrayUnion([value])
      }, merge=True)

def get_tracker(user_id, pet_name, tracker_type):
    """Retrieve tracker log entries."""
    doc = db.collection("fetchcare2").document(user_id)\
            .collection("pets").document(pet_name)\
            .collection("trackers").document(tracker_type).get()
    if doc.exists:
        return doc.to_dict().get("entries", [])
    return []

from google.cloud import firestore

# Connect to Firestore with service account
db = firestore.Client.from_service_account_json("serviceAccountKey.json")
print("Firestore project ID:", db.project)  # Add this line

# Define example user_id and pet_name
user_id = "test_user"
pet_name = "test_pet"

# Example: print the document path
print(db.collection("fetchcare2").document(user_id).collection("pets").document(pet_name).path)

# Save a message to the user's chat history
def save_message(user_id, pet_name, role, content):
    db.collection("fetchcare2").document(user_id)\
      .collection("pets").document(pet_name)\
      .collection("chat_history").add({
          "role": role,
          "content": content,
          "timestamp": firestore.SERVER_TIMESTAMP
      })

# Load full chat history
def get_chat_history(user_id, pet_name):
    ref = db.collection("fetchcare2").document(user_id)\
            .collection("pets").document(pet_name)\
            .collection("chat_history").order_by("timestamp")
    return [doc.to_dict() for doc in ref.stream()]

# Save a tracker log (e.g., meal, poop, swelling, weight)
def save_tracker(user_id, pet_name, tracker_type, value):
    db.collection("fetchcare2").document(user_id)\
      .collection("pets").document(pet_name)\
      .collection("trackers").document(tracker_type)\
      .set({
          "entries": firestore.ArrayUnion([value])
      }, merge=True)

# Load tracker logs
def get_tracker(user_id, pet_name, tracker_type):
    doc = db.collection("fetchcare2").document(user_id)\
            .collection("pets").document(pet_name)\
            .collection("trackers").document(tracker_type).get()
    if doc.exists:
        return doc.to_dict().get("entries", [])
    return []

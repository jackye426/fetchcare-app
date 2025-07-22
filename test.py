from google.cloud import firestore

db = firestore.Client.from_service_account_json("serviceAccountKey.json")
doc_ref = db.collection("test").document("ping")
doc_ref.set({"message": "hello"})

print(doc_ref.get().to_dict())

print(db.project)
from streamlit_authenticator.utilities.hasher import Hasher

# List your plain-text passwords here
plaintext_passwords = ["yourpassword1", "yourpassword2"]

# Use Hasher's class method to hash multiple passwords
hashed_passwords = Hasher.hash_list(plaintext_passwords)

print(hashed_passwords)

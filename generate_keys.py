# File: generate_keys.py
from Crypto.PublicKey import RSA

# Tạo cặp khóa cho client
client_key = RSA.generate(2048)
with open("private_key.pem", "wb") as f:
    f.write(client_key.export_key())
with open("public_key.pem", "wb") as f:
    f.write(client_key.publickey().export_key())

# Tạo cặp khóa cho server
server_key = RSA.generate(2048)
with open("receiver_private_key.pem", "wb") as f:
    f.write(server_key.export_key())
with open("receiver_public_key.pem", "wb") as f:
    f.write(server_key.publickey().export_key())
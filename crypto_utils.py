from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA512, SHA256
from Crypto.Signature import pss
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64
import json
import time

def encrypt_and_sign(file_path, receiver_public_key, password, metadata):
    # Đọc file
    with open(file_path, "rb") as f:
        data = f.read()

    # Tạo khóa phiên (SessionKey) và IV
    session_key = get_random_bytes(16)  # AES-128
    iv = get_random_bytes(16)

    # Mã hóa file bằng AES-CBC
    cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
    padded_data = data + b"\0" * (16 - len(data) % 16)  # Padding
    ciphertext = cipher_aes.encrypt(padded_data)

    # Tính hash toàn vẹn
    h = SHA512.new()
    h.update(iv + ciphertext)
    data_hash = h.hexdigest()

    # Ký metadata bằng RSA/SHA-512
    key = RSA.import_key(open("private_key.pem").read())
    h = SHA512.new()
    h.update(metadata.encode())
    signer = pss.new(key)
    signature = signer.sign(h)

    # Mã hóa SessionKey bằng RSA
    recipient_key = RSA.import_key(receiver_public_key)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Hash mật khẩu
    pwd_hash = SHA256.new(password.encode()).hexdigest()

    # Tạo gói tin, bao gồm metadata
    packet = {
        "iv": base64.b64encode(iv).decode(),
        "cipher": base64.b64encode(ciphertext).decode(),
        "hash": data_hash,
        "sig": base64.b64encode(signature).decode(),
        "pwd": pwd_hash,
        "enc_key": base64.b64encode(enc_session_key).decode(),
        "metadata": metadata  # Thêm metadata vào gói tin
    }
    return json.dumps(packet)

def verify_and_decrypt(packet, sender_public_key, expected_password):
    packet = json.loads(packet)
    iv = base64.b64decode(packet["iv"])
    ciphertext = base64.b64decode(packet["cipher"])
    data_hash = packet["hash"]
    signature = base64.b64decode(packet["sig"])
    pwd_hash = packet["pwd"]
    enc_session_key = base64.b64decode(packet["enc_key"])
    metadata = packet["metadata"]  # Lấy metadata từ gói tin

    # Kiểm tra mật khẩu
    if SHA256.new(expected_password.encode()).hexdigest() != pwd_hash:
        return False, "Invalid password"

    # Kiểm tra toàn vẹn
    h = SHA512.new()
    h.update(iv + ciphertext)
    if h.hexdigest() != data_hash:
        return False, "Integrity check failed"

    # Kiểm tra chữ ký
    key = RSA.import_key(sender_public_key)
    h = SHA512.new()
    h.update(metadata.encode())  # Sử dụng metadata từ gói tin
    verifier = pss.new(key)
    try:
        verifier.verify(h, signature)
    except:
        return False, "Signature verification failed"

    # Giải mã SessionKey
    private_key = RSA.import_key(open("receiver_private_key.pem").read())
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Giải mã file
    cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
    decrypted_data = cipher_aes.decrypt(ciphertext).rstrip(b"\0")

    # Lưu file
    with open("received_medical_record.txt", "wb") as f:
        f.write(decrypted_data)
    
    return True, "File received and verified"
import socket
import time
from crypto_utils import encrypt_and_sign

def send_file(host, port, file_path, password):
    metadata = f"medical_record.txt|{int(time.time())}|PATIENT123"
    receiver_public_key = open("receiver_public_key.pem", "rb").read()
    
    packet = encrypt_and_sign(file_path, receiver_public_key, password, metadata)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Handshake
        s.send(b"Hello!")
        response = s.recv(1024).decode()
        if response != "Ready!":
            return False, "Handshake failed"
        
        # Gửi gói tin
        s.send(packet.encode())
        
        # Nhận ACK/NACK
        response = s.recv(4096).decode()
        print("Server response:", response)
        
        # Kiểm tra phản hồi từ server
        if response == "File received and verified":
            return True, "File sent successfully"
        else:
            return False, response

if __name__ == "__main__":
    success, message = send_file("localhost", 9999, "medical_record.txt", "123123123")
    print(message)
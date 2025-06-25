import socket
from crypto_utils import verify_and_decrypt

def start_server(host, port, password):
    sender_public_key = open("public_key.pem", "rb").read()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server listening...")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                # Handshake
                data = conn.recv(1024).decode()
                if data == "Hello!":
                    conn.send(b"Ready!")
                else:
                    conn.send(b"Handshake failed")
                    continue
                
                # Receive packet with proper handling for large data
                packet = ""
                while True:
                    chunk = conn.recv(4096).decode('utf-8', errors='ignore')
                    if not chunk:
                        break
                    packet += chunk
                    # Check if the packet is complete (assuming JSON ends with '}')
                    if packet.endswith('}'):
                        break
                
                try:
                    success, message = verify_and_decrypt(packet, sender_public_key, password)
                    conn.send(message.encode())
                    print(f"Response sent: {message}")
                except Exception as e:
                    error_msg = f"Error processing packet: {str(e)}"
                    conn.send(error_msg.encode())
                    print(error_msg)

if __name__ == "__main__":
    start_server("localhost", 9999, "123123123")
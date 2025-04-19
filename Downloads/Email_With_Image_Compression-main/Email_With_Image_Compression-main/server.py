import socket

HOST = 'localhost'
SENDER_PORT = 12345
RECEIVER_PORT = 12346
BUFFER_SIZE = 4096

def main():
    print("[🖥️] Secure Image Transfer Server Starting...")

    # Step 1: Connect to Receiver
    print("[📥] Waiting for receiver to connect...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as recv_sock:
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind((HOST, RECEIVER_PORT))
        recv_sock.listen(1)
        conn_receiver, addr_r = recv_sock.accept()
        print(f"[✅] Receiver connected from {addr_r}")

        # Step 2: Connect to Sender
        print("[📤] Waiting for sender to connect...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_sock:
            send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_sock.bind((HOST, SENDER_PORT))
            send_sock.listen(1)
            conn_sender, addr_s = send_sock.accept()
            print(f"[✅] Sender connected from {addr_s}")

            # Step 3: Relay data from sender to receiver in real-time
            print("[🔄] Relaying data from sender to receiver...")
            try:
                while True:
                    chunk = conn_sender.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    conn_receiver.sendall(chunk)
            except Exception as e:
                print(f"[❌] Relay error: {e}")
            finally:
                conn_sender.close()
                conn_receiver.close()
                print("[🏁] Transfer complete. Connections closed.")

if __name__ == "__main__":
    main()

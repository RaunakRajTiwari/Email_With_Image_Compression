import socket
from PIL import Image
import io
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

def load_private_key(filename):
    with open(filename, "rb") as f:
        return RSA.import_key(f.read())

def load_public_key(filename):
    with open(filename, "rb") as f:
        return RSA.import_key(f.read())

def save_lossless_image(byte_data, output_path="received_image.png"):
    print("[🧼] Saving lossless image...")
    buffer = io.BytesIO(byte_data)
    img = Image.open(buffer)
    img.save(output_path, format="PNG")
    print(f"[💾] Image saved as '{output_path}'")

HOST = 'localhost'
PORT = 12346

print("[🔌] Connecting to server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("[🔗] Connected to server.")

    print("[🔑] Loading keys...")
    private_key = load_private_key("keys/Bob_private.pem")
    sender_public_key = load_public_key("keys/Alice_public.pem")

    print("[📥] Receiving encrypted AES key...")
    encrypted_key = s.recv(256)
    aes_key = PKCS1_OAEP.new(private_key).decrypt(encrypted_key)
    print("[🔓] AES key decrypted.")

    iv = s.recv(16)
    print(f"[📥] Received IV: {len(iv)} bytes")

    sig_len = int.from_bytes(s.recv(4), 'big')
    signature = s.recv(sig_len)
    print(f"[✍️] Received signature of length: {sig_len} bytes")

    img_len = int.from_bytes(s.recv(8), 'big')
    print(f"[📦] Receiving encrypted image of size: {img_len} bytes")
    encrypted_img = b""
    while len(encrypted_img) < img_len:
        part = s.recv(2048)
        if not part:
            break
        encrypted_img += part

    print("[🔐] Decrypting image with AES...")
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher_aes.decrypt(encrypted_img), AES.block_size)
    print(f"[✅] Image decrypted. Final size: {len(decrypted_data)} bytes")

    print("[🔍] Verifying signature...")
    h = SHA256.new(decrypted_data)
    try:
        pkcs1_15.new(sender_public_key).verify(h, signature)
        print("[✓] Signature verified successfully.")
    except (ValueError, TypeError):
        print("[✗] Signature verification failed.")

    save_lossless_image(decrypted_data)

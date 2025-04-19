import socket
from os import urandom, path
from PIL import Image
import io
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad

def load_public_key(filename): 
    with open(filename, "rb") as f:
        return RSA.import_key(f.read())

def load_private_key(filename):
    with open(filename, "rb") as f:
        return RSA.import_key(f.read())

def compress_image_lossless(input_path):
    """
    Compress image using lossless PNG format.
    """
    print("[📥] Opening image for lossless compression...")
    img = Image.open(input_path).convert("RGB")  # Ensure consistent format
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")  # Lossless compression
    print("[✅] Image compressed (lossless PNG).")
    return buffer.getvalue()

# ---- Configuration ----
IMAGE_PATH = "self.jpg"  # Placeholder image
HOST = 'localhost'
PORT = 12345  # Server port (should match server.py)
# -----------------------

# Load RSA keys
print("[🔑] Loading RSA keys...")
public_key = load_public_key("keys/Bob_public.pem")      # Receiver's public key
private_key = load_private_key("keys/Alice_private.pem") # Sender's private key

# Read and compress image
original_size = path.getsize(IMAGE_PATH)
print(f"[📦] Original Image Size: {original_size} bytes")
img_data = compress_image_lossless(IMAGE_PATH)
compressed_size = len(img_data)
print(f"[🗜️] Compressed (PNG) Size: {compressed_size} bytes")

# Encrypt image with AES
print("[🔒] Encrypting image with AES (CBC mode)...")
aes_key = urandom(32)  # 256-bit AES key
iv = urandom(16)       # 128-bit IV
cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
encrypted_img = cipher_aes.encrypt(pad(img_data, AES.block_size))
print(f"[🔐] Encrypted Image Size: {len(encrypted_img)} bytes")

# Sign the original (compressed) data
print("[✍️] Signing the image data...")
hash_obj = SHA256.new(img_data)
signature = pkcs1_15.new(private_key).sign(hash_obj)
print(f"[✔️] Signature created. Size: {len(signature)} bytes")

# Encrypt AES key using RSA
print("[🔐] Encrypting AES key using RSA...")
cipher_rsa = PKCS1_OAEP.new(public_key)
enc_aes_key = cipher_rsa.encrypt(aes_key)

# Send everything to server
print("[📡] Sending data to server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(enc_aes_key)                               # 256 bytes
    s.sendall(iv)                                        # 16 bytes
    s.sendall(len(signature).to_bytes(4, 'big'))         # Signature length (4 bytes)
    s.sendall(signature)                                 # Signature
    s.sendall(len(encrypted_img).to_bytes(8, 'big'))     # Image length (8 bytes)
    s.sendall(encrypted_img)                             # Encrypted image

print("[✅] Image sent to server successfully.")

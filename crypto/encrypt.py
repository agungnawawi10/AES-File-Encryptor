# type: ignore
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

KEY = b"akujugagatau"


def encrypt(text):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode())

    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

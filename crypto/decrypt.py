# type: ignore
from Crypto.Cipher import AES
import base64

KEY = b"1234567890123456"

def decrypt(encoded_text):
    data = base64.b64decode(encoded_text)

    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]

    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)

    return decrypted.decode()

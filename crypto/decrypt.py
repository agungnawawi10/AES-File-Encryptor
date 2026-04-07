# type: ignore
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


def decrypt_data(password: str, encrypted: bytes):

    # ambil bagian yang di perlukan
    salt = encrypted[:16]
    nonce = encrypted[16:32]
    tag = encrypted[32:48]
    ciphertext = encrypted[48:]

    key = PBKDF2(password, salt, dkLen=16, count=200000)

    # setup AES
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    # dekripsi
    data = cipher.decrypt(ciphertext)

    try:
        cipher.verify(tag)
        return data
    except ValueError:
        return None  # password salah

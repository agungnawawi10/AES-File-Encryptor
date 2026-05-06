from aeslib.decrypt import decrypt
from aeslib.encrypt import encrypt


text = "halo dunia"

enc = encrypt(text)
dec = decrypt(enc)

print("Encrypted:", enc)
print("Decrypted:", dec)

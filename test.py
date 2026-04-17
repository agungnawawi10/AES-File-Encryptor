from crypto.decrypt import decrypt
from crypto.encrypt import encrypt


text = "halo dunia"

enc = encrypt(text)
dec = decrypt(enc)

print("Encrypted:", enc)
print("Decrypted:", dec)

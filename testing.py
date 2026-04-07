# type: ignore
from Crypto.Cipher import AES

data = b"data ini akan kita enkripsi"
key = b"1n1kunC1S4yaN1hh"  # 16 blok

# enkripsi

chiper = AES.new(key, AES.MODE_EAX)
nonce = chiper.nonce
chiperText, tag = chiper.encrypt_and_digest(data)

# cetak
print("Hasil enkripsi")
print(chiperText, "\n", tag, "\n", nonce, "\n")

# dekripsi

key = b"1n1kunC1S4yaN1hh"
chiper = AES.new(key, AES.MODE_EAX, nonce)
plaintext = chiper.decrypt(chiperText)

try:
    chiper.verify(tag)
    print("Hasil dekripsi")
    print(plaintext.decode())
except ValueError:
    print("Kunci yang anda masukan salah")

# type:ignore
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


def encrypt_data(password: str, data: bytes):

    # generate salt untuk PBKDF2
    salt = get_random_bytes(16)

    # Membuat "Kunci Gembok" dari Kata Sandi:
    # - Salt: Memastikan kunci unik (tidak ada duplikat).
    # - Count: Menempa kunci 200.000 kali agar sangat kuat dan anti-bobol.
    # - dkLen: Ukuran kunci standar (16 byte) untuk gembok digital AES.
    # - Derive Key: Memperkuat password menggunakan standar PBKDF2.
    # - Menghasilkan kunci 16-byte dengan 200.000 iterasi untuk mencegah brute force.

    key = PBKDF2(password, salt, dkLen=16, count=200000)

    # Setup AES
    # .new() artinya: "Buatkan saya satu unit gembok baru yang segar"
    # Gembok ini dirakit khusus pakai kunci (key) dan model keamanan (EAX) pilihan kita.
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    # enkripsi
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    # output final = salt + nonce +tag + ciphertext
    return salt + nonce + tag + ciphertext
    
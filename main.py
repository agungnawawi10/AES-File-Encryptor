from crypto.encrypt import encrypt_data
from crypto.decrypt import decrypt_data
from utils.file_io import read_file, write_file


print("=== Program Enkripsi / Deksripsi AES ===")
print("1. Enkripsi file")
print("2. Dekripsi File")

pilih = input("pilih menu (1/2): ")

if pilih == "1":
    file_in = input("Masukan path File: ")
    password = input("Masuksan password: ")

    data = read_file(file_in)
    encrypted = encrypt_data(password, data)

    file_out = file_in + ".enc"
    write_file(file_out, encrypted)

    print(f"File berhasil dienkripsi -> {file_out}")

elif pilih == "2":
    file_in = input("Masukan file .enc: ")
    password = input("Masukan password")

    encrypted = read_file(file_in)
    decrypted = decrypt_data(password, encrypted)

    if decrypted is None:
        print("Password salah atau file rusak")
    else:
        file_out = file_in.replace(".enc", ".dec")
        write_file(file_out, decrypted)

        print(f"file berhasil didekripsi -> {file_out}")
else:
    print("Menu tidak valid")

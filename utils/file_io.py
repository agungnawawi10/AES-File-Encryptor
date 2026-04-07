# FUNGSI UNTUK MENGAMBIL DATA MENTAH DARI FILE:
# 1. Buka file sesuai lokasi (path) dengan mode "rb" (Baca Biner/Data Mentah).
# 2. Ambil seluruh isi filenya untuk diproses (misal: untuk dikunci/di-enkripsi).
def read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


# FUNGSI UNTUK MENYIMPAN DATA KE DALAM FILE:
# 1. Buka/buat file di lokasi (path) dengan mode "wb" (Tulis Biner/Data Mentah).
# 2. Tuangkan data hasil proses (seperti hasil enkripsi) ke dalam file tersebut.
def write_file(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)

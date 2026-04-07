import tkinter as tk
from tkinter import filedialog, messagebox

from crypto.encrypt import encrypt_data
from crypto.decrypt import decrypt_data
from utils.file_io import read_file, write_file

# === Function GUI ===

def pilih_file():
    path = filedialog.askopenfilename()
    entry_file.delete(0, tk.END)
    entry_file.insert(0, path)

def enkripsi():
    path = entry_file.get()
    password = entry_password.get()

    if not path:
        messagebox.showerror("Error", "Pilih file terlebih dahulu.")
        return

    if not password:
        messagebox.showerror("Error", "Password tidak boleh kosong.")
        return

    try:
        data = read_file(path)
        encrypted = encrypt_data(password, data)

        output_path = path + ".enc"
        write_file(output_path, encrypted)

        messagebox.showinfo("Sukses", f"File berhasil dienkripsi:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")

def dekripsi():
    path = entry_file.get()
    password = entry_password.get()

    if not path:
        messagebox.showerror("Error", "Pilih file terlebih dahulu.")
        return

    if not password:
        messagebox.showerror("Error", "Password tidak boleh kosong.")
        return

    try:
        encrypted = read_file(path)
        data = decrypt_data(password, encrypted)

        if data is None:
            messagebox.showerror("Error", "Password salah atau file rusak.")
            return

        output_path = path.replace(".enc", "") + ".dec"
        write_file(output_path, data)

        messagebox.showinfo("Sukses", f"File berhasil didekripsi:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")


# === GUI SETUP ===


# === Styling ===
BG_COLOR = "#232946"
FG_COLOR = "#eebbc3"
ENTRY_BG = "#121629"
BTN_BG = "#eebbc3"
BTN_FG = "#232946"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_ENTRY = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 11, "bold")

root = tk.Tk()
root.title("AES File Encryption")
root.geometry("480x260")
root.configure(bg=BG_COLOR)

# Title
title = tk.Label(root, text="AES File Encryptor", font=FONT_TITLE, fg=FG_COLOR, bg=BG_COLOR)
title.pack(pady=(12, 8))

# File Frame
file_frame = tk.Frame(root, bg=BG_COLOR)
file_frame.pack(pady=2)

label_file = tk.Label(file_frame, text="File:", font=FONT_LABEL, fg=FG_COLOR, bg=BG_COLOR)
label_file.grid(row=0, column=0, sticky="w")

entry_file = tk.Entry(file_frame, width=38, font=FONT_ENTRY, bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR, borderwidth=2, relief="groove")
entry_file.grid(row=0, column=1, padx=6)

btn_pilih = tk.Button(file_frame, text="Pilih File", font=FONT_BTN, bg=BTN_BG, fg=BTN_FG, activebackground=FG_COLOR, activeforeground=BG_COLOR, command=pilih_file, borderwidth=0, padx=8, pady=2)
btn_pilih.grid(row=0, column=2, padx=2)

# Password Frame
pass_frame = tk.Frame(root, bg=BG_COLOR)
pass_frame.pack(pady=8)

label_password = tk.Label(pass_frame, text="Password:", font=FONT_LABEL, fg=FG_COLOR, bg=BG_COLOR)
label_password.grid(row=0, column=0, sticky="w")

entry_password = tk.Entry(pass_frame, width=28, font=FONT_ENTRY, bg=ENTRY_BG, fg=FG_COLOR, show="*", insertbackground=FG_COLOR, borderwidth=2, relief="groove")
entry_password.grid(row=0, column=1, padx=6)

# Button Frame
frame_btn = tk.Frame(root, bg=BG_COLOR)
frame_btn.pack(pady=16)

btn_encrypt = tk.Button(frame_btn, text="Encrypt", width=12, font=FONT_BTN, bg=BTN_BG, fg=BTN_FG, activebackground=FG_COLOR, activeforeground=BG_COLOR, command=enkripsi, borderwidth=0, padx=6, pady=4)
btn_encrypt.grid(row=0, column=0, padx=8)

btn_decrypt = tk.Button(frame_btn, text="Decrypt", width=12, font=FONT_BTN, bg=BTN_BG, fg=BTN_FG, activebackground=FG_COLOR, activeforeground=BG_COLOR, command=dekripsi, borderwidth=0, padx=6, pady=4)
btn_decrypt.grid(row=0, column=1, padx=8)

# Footer
footer = tk.Label(root, text="by AES File Encryptor", font=("Segoe UI", 9), fg="#b8c1ec", bg=BG_COLOR)
footer.pack(side="bottom", pady=4)

root.mainloop()

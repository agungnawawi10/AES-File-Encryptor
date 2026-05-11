# Voice Note Protocol (WebSocket)

Dokumen ini mendefinisikan protocol voice note untuk project AES-File-Encryptor.
Target: kompatibel dengan alur chat yang sudah ada, aman (AES), dan siap dipakai mobile client.

## 1. Prinsip Desain

- Tetap pakai kanal WebSocket yang sama (`ws://host:8765`).
- Gunakan `type` untuk membedakan event (`join`, `message`, `voice_start`, `voice_chunk`, `voice_end`, `voice_error`).
- Audio dikirim dalam chunk kecil (streaming), bukan satu file besar.
- Payload audio dienkripsi sebagai bytes, bukan teks.
- Kompatibel dengan implementasi saat ini (pesan teks tetap berjalan).

## 2. Event Message Format

Semua frame kontrol tetap JSON UTF-8.
Untuk performa sederhana awal, chunk audio dapat memakai base64 di JSON.
Versi lanjutan dapat migrasi ke binary frame.

### 2.1 `voice_start`

Dikirim sebelum chunk pertama.

```json
{
  "type": "voice_start",
  "voice_id": "uuid-v4",
  "sender": "alice",
  "codec": "audio/webm;codecs=opus",
  "sample_rate": 48000,
  "channels": 1,
  "duration_ms_estimate": 3200,
  "sent_at": "2026-05-10T10:00:00Z"
}
```

Field wajib:
- `voice_id` string unik per voice note
- `codec`
- `sample_rate`
- `channels`

### 2.2 `voice_chunk`

Dikirim berkali-kali sampai selesai.

```json
{
  "type": "voice_chunk",
  "voice_id": "uuid-v4",
  "seq": 0,
  "is_last": false,
  "payload_b64": "BASE64_AES_ENCRYPTED_BYTES"
}
```

Field wajib:
- `voice_id`
- `seq` integer mulai 0
- `payload_b64` (hasil enkripsi bytes -> base64)
- `is_last` boolean

### 2.3 `voice_end`

Dikirim setelah semua chunk terkirim.

```json
{
  "type": "voice_end",
  "voice_id": "uuid-v4",
  "total_chunks": 22,
  "duration_ms": 3180,
  "sha256": "hex_of_plain_audio_or_cipher_audio"
}
```

### 2.4 `voice_error`

Dikirim server/client saat ada kegagalan.

```json
{
  "type": "voice_error",
  "voice_id": "uuid-v4",
  "code": "INVALID_CHUNK_ORDER",
  "message": "expected seq 3 got 4"
}
```

## 3. Enkripsi Audio

Tambahkan fungsi bytes-level agar tidak memaksa `.encode()` / `.decode()`.

### API baru yang direkomendasikan

Di `aeslib/encrypt.py`:
- `encrypt_bytes(data: bytes) -> bytes`
- `encrypt_text(text: str) -> str` (wrapper dari bytes + base64)

Di `aeslib/decrypt.py`:
- `decrypt_bytes(data: bytes) -> bytes`
- `decrypt_text(text_b64: str) -> str`

Aturan:
- Audio chunk plaintext: bytes
- Setelah AES: ciphertext bytes
- Wire format JSON: base64 string (`payload_b64`)

## 4. Alur End-to-End

1. Client rekam audio (mobile).
2. Client generate `voice_id`.
3. Kirim `voice_start`.
4. Potong audio menjadi chunk tetap (misal 16KB-32KB per chunk).
5. Untuk tiap chunk:
- enkripsi bytes
- encode base64
- kirim `voice_chunk` dengan `seq` naik
6. Kirim `voice_end`.
7. Server broadcast event yang sama ke penerima lain.
8. Penerima:
- buffer by `voice_id`
- urutkan berdasarkan `seq`
- decrypt per chunk
- gabung bytes
- simpan/play ke audio player

## 5. State Server yang Perlu Ditambah

Di `server/state.py` tambahkan:
- `voice_sessions = {}`: map `voice_id -> session metadata`
- `voice_history = []`: list ringkas aktivitas voice

Struktur session yang direkomendasikan:
- `sender`
- `codec`
- `sample_rate`
- `channels`
- `next_seq_expected`
- `received_chunks`
- `started_at`

## 6. Perubahan Per File (Rencana Implementasi)

### 6.1 `server/ws_handler.py`

Tambah branch baru:
- `type == "voice_start"`
- `type == "voice_chunk"`
- `type == "voice_end"`

Validasi minimal:
- `voice_id` wajib
- `seq` berurutan
- ukuran chunk max (misal 64KB sebelum base64)
- timeout sesi voice (misal 30 detik tanpa chunk)

Broadcast:
- teruskan event ke semua client (kecuali sender opsional)

### 6.2 `client/client.py` (CLI tahap awal)

Tambah command test non-mobile:
- `/voice fake <seconds>` untuk kirim dummy bytes
- handler receive untuk `voice_*` event

### 6.3 `server/ui.py`

Tambah panel kecil atau counter:
- active voice streams
- last voice sender
- total voice notes

### 6.4 `aeslib/encrypt.py` dan `aeslib/decrypt.py`

Refactor ke bytes-first API seperti di Bagian 3.

## 7. Nilai Default yang Direkomendasikan

- `chunk_size_bytes`: 16384 (16KB)
- `max_voice_duration_ms`: 180000 (3 menit)
- `max_chunks_per_voice`: 1200
- `session_timeout_ms`: 30000
- `max_parallel_voice_per_user`: 1

## 8. Kompatibilitas & Migrasi

- Jangan ubah event teks existing (`type: message`).
- Tambahkan voice event sebagai jalur baru.
- Client lama yang tidak kenal voice event boleh ignore event tersebut.

## 9. Checklist Implementasi

- [ ] Tambah bytes encryption/decryption API
- [ ] Tambah server handler `voice_start/chunk/end`
- [ ] Tambah validasi urutan `seq`
- [ ] Tambah broadcast voice events
- [ ] Tambah state voice session
- [ ] Tambah logging/history voice di server UI
- [ ] Tambah client support receive `voice_*`
- [ ] Tambah test untuk out-of-order chunk, dropped chunk, oversize payload

## 10. Contoh Sequence Singkat

```text
A -> server: voice_start(v1)
A -> server: voice_chunk(v1, seq=0)
A -> server: voice_chunk(v1, seq=1)
A -> server: voice_chunk(v1, seq=2, is_last=true)
A -> server: voice_end(v1)

server -> B,C: voice_start(v1)
server -> B,C: voice_chunk(v1, seq=0..2)
server -> B,C: voice_end(v1)
```

Dengan protocol ini, fitur voice note bisa dibangun bertahap tanpa memecah flow chat teks yang sudah ada.

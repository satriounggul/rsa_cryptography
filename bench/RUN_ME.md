# Menjalankan benchmark di komputer Anda (Windows, macOS, Linux)

Tujuan: mengukur waktu dekripsi RSA standar, CRT-Garner, dan CRT-Gauss di komputer Anda, supaya makalah memuat hasil dari
lebih dari satu mesin. Skrip hanya memakai pustaka standar Python (tidak perlu `pip install` apa pun).

> **Status verifikasi.** Skrip ini diuji penuh hanya pada Linux (Python 3.14.4). Jalur Windows dan macOS (tanpa pemakuan CPU,
> `spawn` sebagai pengganti `fork`) hanya disimulasikan di Linux. Jika ada pesan galat di mesin Anda, salin seluruh pesan dan
> kirim ke penyusun; jangan mengubah kode inti.

## 0. Yang perlu disiapkan

- Python 3 terpasang. Cek versinya:
  - Windows (PowerShell): `py -3 --version` (jika gagal: `python --version`)
  - macOS dan Linux (Terminal): `python3 --version`
- Zip pengumpulan sudah diekstrak. Buka terminal **di folder `kriptografi_rsa`** (yang berisi `core`, `bench`, `tests`).
  - Windows: di Explorer buka folder itu, klik bilah alamat, ketik `powershell`, tekan Enter.
- Di bawah, `python` berarti `py -3` di Windows dan `python3` di macOS/Linux.

## 1. Pastikan kode berfungsi (±10 detik, opsional tetapi disarankan)

```
python -m unittest discover tests
```

Harus berakhir dengan `OK` (55 tes). Jika ada yang gagal, berhenti dan laporkan.

## 2. Siapkan mesin agar hasil tidak bising

1. Tutup browser, pemutar musik, aplikasi sinkronisasi (Drive, OneDrive), dan antivirus yang sedang memindai.
2. Laptop: colokkan charger; matikan mode hemat daya.
   - Windows: Settings → System → Power → Power mode = **Best performance**.
   - macOS: System Settings → Battery → matikan **Low Power Mode**.
3. Jangan memakai komputer selama pengukuran (jangan menggerakkan mouse atau membuka aplikasi lain).
4. Catat: nama komputer, tipe prosesor, apakah laptop atau desktop, dan apakah memakai charger.

## 3. Uji fungsi cepat dengan `--quick`

```
python bench/benchmark.py --quick
```

- Mengukur bits 512, 1024, 2048 dan k = 2, 3, 5 dengan 10 putaran terukur per metode.
- Di server kami selesai dalam ±13 detik; waktu di mesin Anda **TIDAK TERVERIFIKASI**.
- Keberhasilan ditandai baris terakhir `[selesai] 900 baris -> ...` dan **tidak ada** baris `[GAGAL]`.
- Di Windows dan macOS akan muncul `PERINGATAN: OS ini tidak mendukung pemakuan CPU`. Itu normal.
- **Hasil `--quick` hanya uji bahwa skrip berjalan. Jangan dimasukkan ke makalah.**

## 4. Benchmark penuh (untuk data makalah)

```
python bench/benchmark.py
```

- Grid: bits 64 sampai 4096, k = 2 sampai 5, 30 ciphertext, 3 putaran pemanasan, 30 putaran terukur.
- Di server kami pengukuran memakan 235 detik (±4 menit) dan pembangkitan kunci beberapa detik (total 248 detik); di laptop dapat beberapa kali lebih lama (**TIDAK TERVERIFIKASI**). Biarkan sampai muncul `[selesai] 9600 baris`.
- Jika harus diulang dengan nama berkas berbeda: `python bench/benchmark.py --tag ulang2`. Skrip **menolak menimpa** hasil yang sudah ada.

## 5. Berkas yang dihasilkan dan yang dikirim

Folder `results/` dibuat otomatis (atau folder lain lewat `--out-dir`). Isinya:

| Berkas | Kirim? |
|---|---|
| `benchmark_raw_<namakomputer>.csv` | **Ya** (data mentah) |
| `benchmark_meta_<namakomputer>.json` | **Ya** (versi Python, CPU, OS, load average, durasi) |
| `benchmark_keys_<namakomputer>.json` | **Tidak** (kunci uji acak; tidak diperlukan) |

Kirim kedua berkas pertama lewat Drive, e-mail, atau grup. Nama komputer ikut tertulis di nama berkas dan kolom `hostname`; jika
ingin menyamarkan, ubah nama berkas dan gunakan label saat membandingkan (langkah 6).

## 6. Membandingkan beberapa mesin (dijalankan oleh penyusun)

Kumpulkan semua `benchmark_raw_*.csv` dalam satu folder, lalu:

```
python bench/compare_machines.py server=results/final/benchmark_raw_l0125001.csv laptopA=kiriman/benchmark_raw_LAPTOP-A.csv --min-bits 512 --out perbandingan.md --csv perbandingan.csv
```

`label=berkas` memberi nama pada kolom. Keluarannya tabel speedup (median standar / median metode) per mesin berdampingan.
Gunakan hanya hasil **mode penuh** untuk makalah, dan sebutkan CPU, versi Python, dan OS setiap mesin dari tabel di bagian atas keluaran.

## 7. Masalah umum

| Gejala | Tindakan |
|---|---|
| `python` tidak dikenal (Windows) | Pakai `py -3 ...`, atau pasang Python dari python.org dan centang "Add to PATH" |
| `Berkas sudah ada, tidak ditimpa` | Tambahkan `--tag nama_lain`, atau pindahkan hasil lama |
| `PERINGATAN: ... pemakuan CPU` | Normal di Windows dan macOS; abaikan |
| Galat `multiprocessing` / `spawn` saat membangkitkan kunci | Coba `python bench/benchmark.py --workers 1`; laporkan pesan lengkapnya |
| Ada baris `[GAGAL]` | Hentikan; hasil tidak valid. Kirim log lengkap |
| Hasil sangat berbeda antar pengulangan | Ulangi dengan mesin lebih tenang (langkah 2), tanpa `--quick` |

Jangan menjalankan `bench/analyze.py` di mesin tim kecuali sudah memasang matplotlib; untuk perbandingan cukup `compare_machines.py`.

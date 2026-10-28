# Koreksi untuk makalah (versi PDF `Matematika Diskrit_Kelompok1.pdf`, 35 halaman)

> **Draf untuk dibaca, diperiksa, dan disunting sendiri oleh mahasiswa.** PDF asli tidak diubah. Berkas sumber makalah (Google Docs) **tidak ditemukan** di mesin ini
> (pencarian `.docx/.odt/.tex/.md` hanya menemukan proyek lain di `/root/kaggle`), jadi tidak ada berkas yang dapat saya sunting; semua koreksi di bawah harus Anda masukkan sendiri.

**Cara membaca.** "Hal." memakai nomor halaman **cetak** (angka di kaki halaman); nomor halaman PDF = nomor cetak + 2 (halaman Daftar Isi dan Bab I sama-sama bernomor 1).
Kutipan diambil dari teks PDF (`pdftotext`); simbol matematika disederhanakan ke teks biasa. Prinsip: bila makalah dan kode berbeda, **makalah yang dikoreksi**, kode final (`v1-final`, commit `58aafdd`) tidak diubah.
Angka pengganti berasal dari `results/final/` (sumber disebut per butir; hasil dibangkitkan oleh `bench/make_paper_assets.py` ke `paper/tabel/`). Dalam teks pengganti, tanda `[…]` berarti Anda perlu memastikan angkanya.

Ringkasan: 12 butir dari audit awal (REVIEW §5.3), tiga butir tambahan setelah pembacaan ulang (13 sampai 15), dan butir kelengkapan (16 sampai 17). Butir 6, 7, dan 13 diperbarui karena kode final berbeda dari kode yang diaudit pertama kali.

---

## 1. "Percepatan k² kali" (hal. 1)

- **Kutipan:** "Secara teoritis, penggunaan k prima memberikan percepatan dekripsi sebesar k² kali dibandingkan metode standar, karena setiap sub-perhitungan dilakukan pada modulus yang lebih kecil (sekitar n^(1/k))."
- **Teks pengganti:** "Dengan model biaya sederhana (perkalian dua bilangan L bit berbiaya O(L²) sehingga satu eksponensiasi modular berbiaya O(L³)), penggunaan k prima berukuran seimbang memberikan batas atas percepatan teoretis sekitar k² kali, karena k × (B/k)³ = B³/k². Pada pengukuran dalam proyek ini percepatan waktu terukur lebih kecil daripada k²: pada modulus 4096 bit sebesar 3,53 kali (k = 2) sampai 15,69 kali (k = 5), atau 88% sampai 63% dari k²."
- **Alasan:** klaim "k² kali" tidak tercapai pada waktu terukur (kecuali mendekati pada model biaya berbobot-bit: 3,97 / 9,04 / 15,95 / 25,17 pada 4096 bit) dan makalah sendiri menyebut angka itu "bukan hasil benchmark" (hal. 10).
- **Bukti:** `results/final/benchmark_summary.csv` (layer=core, method=crt_garner, kolom `speedup`); `paper/tabel/01_speedup_garner.md`, `06_efisiensi_kuadrat.md`, `07_biaya_berbobot_bit.md`.

## 2. "Garner lebih efisien dibandingkan Gauss" (hal. 6)

- **Kutipan:** "Metode Garner lebih efisien dibandingkan metode Gauss karena meminimalkan ukuran bit pada variabel perantara selama proses iterasi."
- **Teks pengganti:** "Pada pengukuran dalam proyek ini, CRT-Garner dan CRT-Gauss dengan koefisien yang diprekomputasi saat pembangkitan kunci (varian b) memiliki waktu hampir sama: rasio waktu median Garner terhadap Gauss (b) berkisar 0,997 sampai 1,110 pada seluruh grid, dan paling besar 1,014 untuk modulus 512 bit ke atas. Garner lebih cepat daripada Gauss varian (a), yang menghitung invers modular di dalam setiap dekripsi (rasio Gauss (a) terhadap Gauss (b): 1,025 sampai 1,323), tetapi selisih itu berasal dari pekerjaan invers modular, bukan dari ukuran variabel perantara."
- **Alasan:** pernyataan sebab ("meminimalkan ukuran bit") tidak diuji; selisih pada kode awal hanya karena `modinv` dihitung di dalam dekripsi Gauss.
- **Bukti:** `paper/tabel/04_rasio_garner_gauss_b.md` (sumber `benchmark_summary.csv`, kolom `median_s`).

## 3. Eksponen privat memakai λ(n), padahal kode memakai φ(n) (hal. 4, hal. 24; hal. 9 sudah benar)

Tiga kutipan perlu diganti (lihat juga butir 3b di bawah untuk paragraf penjelasan).

- **Hal. 4, II.A.3.a. Kutipan:** "Menghitung eksponen privat d sebagai invers modular dari eksponen publik e terhadap fungsi totient Carmichael λ(n), yang dirumuskan melalui persamaan d · e ≡ 1 (mod λ(n))."
  **Pengganti:** "Menghitung eksponen privat d sebagai invers modular dari eksponen publik e terhadap φ(n) = ∏(pᵢ − 1), yaitu d · e ≡ 1 (mod φ(n)). (Standar PKCS #1 memakai λ(n) = lcm(pᵢ − 1); lihat Bab II.E.)"
- **Hal. 24, IV.B.3. Kutipan:** "Fungsi Carmichael λ(n): Menghitung λ(n) = lcm(p₁ − 1, p₂ − 1, ..., pk − 1) sebagai nilai totient untuk menentukan pasangan eksponen publik dan privat."
  **Pengganti:** "Fungsi totien Euler φ(n): menghitung φ(n) = ∏(pᵢ − 1) sebagai modulus untuk menentukan eksponen privat. Fungsi λ(n) = lcm(pᵢ − 1) tersedia di kode hanya sebagai pemeriksaan cadangan pada validasi kunci."
- **Hal. 24. Kutipan:** "Memilih eksponen publik e (secara baku e = 65537) yang memenuhi gcd(e, λ(n)) = 1, lalu menghitung eksponen privat d = e⁻¹ mod λ(n)."
  **Pengganti:** "Memilih eksponen publik e (utamanya e = 65537 bila e < pᵢ dan gcd(e, pᵢ − 1) = 1 untuk semua i; selain itu bilangan ganjil terkecil yang memenuhi syarat itu), lalu menghitung eksponen privat d = e⁻¹ mod φ(n). Syarat gcd(e, pᵢ − 1) = 1 untuk semua i setara dengan gcd(e, φ(n)) = 1."
- **Hal. 24 (Validasi Kunci). Kutipan:** "…hubungan e · d ≡ 1 (mod λ(n)) terpenuhi, dan seluruh nilai dᵢ > 0."
  **Pengganti:** "…hubungan e · d ≡ 1 (mod φ(n)) terpenuhi (atau, sebagai cadangan, modulo λ(n)), dan seluruh nilai dᵢ > 0."
- **Alasan:** `core/keygen.py` memanggil `compute_phi` lalu `modinv(e, phi)`; Bab II.E (hal. 9) sudah menyatakan hal ini dengan benar, sehingga makalah bertentangan dengan dirinya sendiri.
- **Bukti:** `core/keygen.py` (`select_e`, `compute_phi`, `modinv(e, phi)`, `validate_keys`); `results/final/audit_d_phi_lambda.txt`.

### 3b. Paragraf penjelasan yang konsisten (usulan untuk Bab II.E, hal. 9, dan sebagai catatan di Bab IV)

> Rumusan standar PKCS #1 (RFC 8017) mendefinisikan d sebagai invers e modulo λ(n) = lcm(p₁ − 1, …, pₖ − 1). Implementasi proyek ini menghitung d sebagai invers e modulo φ(n) = ∏(pᵢ − 1). Karena λ(n) membagi φ(n), d berbasis φ memenuhi e·d ≡ 1 (mod λ(n)) juga, sehingga m^(ed) ≡ m (mod pᵢ) untuk setiap i dan dekripsi tetap benar. Eksponen per prima dᵢ = d mod (pᵢ − 1) **sama persis** untuk kedua pilihan, sebab (pᵢ − 1) membagi λ(n) dan λ(n) membagi φ(n), sehingga d berbasis φ dan d berbasis λ kongruen modulo (pᵢ − 1). Perbedaannya hanya pada panjang d: d berbasis φ dapat lebih panjang, dan hal ini memengaruhi dekripsi standar (c^d mod n) tetapi tidak memengaruhi dekripsi CRT, yang hanya memakai dᵢ.

- **Bukti (kode final, kunci acak):** dari 800 kunci (64–1024 bit, k = 2–5), dᵢ identik pada 800 kunci; c^d_φ mod n = c^d_λ mod n pada 4.000 dari 4.000 ciphertext; d_φ lebih panjang daripada d_λ pada 717 dari 800 kunci, selisih 0 sampai 30 bit. Sumber: `results/final/audit_d_phi_lambda.txt` (`bench/audit_d_phi_lambda.py`). Angka selisih bit bergantung pada sampel acak.
- Buktinya ada di `paper/BUKTI_MATEMATIS_draf.md`, bagian 4.

## 4. "textContent (bukan innerHTML)" (hal. 26)

- **Kutipan:** "Keamanan: Semua output ditampilkan menggunakan textContent (bukan innerHTML) untuk mencegah serangan XSS."
- **Teks pengganti:** "Keamanan: teks dan angka hasil enkripsi serta dekripsi yang berasal dari masukan pengguna ditampilkan dengan `textContent`. `innerHTML` masih dipakai pada 13 tempat di `static/app.js`, yaitu untuk mengosongkan kontainer dan menyusun tabel langkah antara dari nilai bilangan bulat yang dikirim server dalam bentuk string digit. Aplikasi hanya dimaksudkan berjalan di `127.0.0.1` untuk pembelajaran dan tidak diaudit terhadap server yang dimodifikasi."
- **Alasan:** `grep -c innerHTML static/app.js` = 13 pada kode final. Sebaran: baris 128, 138, 148, 280, 285, 295, 303, 310, 324, 338, 363, 378, 393 (nomor baris pada kode final; dapat bergeser bila berkas diubah).
- **Bukti:** `static/app.js`; REVIEW §3e (internal).

## 5. Penghitung operasi "mencatat secara presisi setiap operasi" (hal. 25)

- **Kutipan:** "Modul op_counter.py menyediakan kelas khusus OperationCounter yang bertugas untuk mencatat dan menghitung secara presisi setiap operasi aritmetika dasar yang terjadi selama eksekusi dekripsi."
- **Teks pengganti:** "Modul op_counter.py menyediakan kelas OperationCounter yang mencacah operasi perkalian, modulo, pembagian, pergeseran bit, dan penjumlahan pada langkah eksponensiasi modular dan rekombinasi. Operasi di dalam `modinv`/`extended_gcd` (dipakai oleh dekripsi Gauss varian a) dan di dalam Miller–Rabin tidak dicacah. Secara bawaan penghitung tidak memperhitungkan panjang operan, sehingga rasio total operasi standar/CRT mendekati 1 (0,878 sampai 1,118 pada seluruh grid; 0,986 sampai 1,018 untuk 512 bit ke atas); karena itu proyek ini juga memakai mode opsional `track_bits` yang membobot biaya dengan panjang bit operan."
- **Alasan:** pernyataan "presisi setiap operasi" tidak benar; perhitungan waktu dan biaya berbobot-bit lebih informatif daripada cacah mentah.
- **Bukti:** `paper/tabel/11_rasio_op_counter.md` (`benchmark_summary.csv`, kolom `ops_ratio_standard_over_method`); `results/final/costmodel_crosscheck.txt` (Gauss (a): penghitung inti lebih rendah rata-rata 5,14% daripada model karena `modinv` tidak dicacah).
- **Catatan rentang:** rentang lama "0,95–1,04" jangan dipakai (berasal dari 6 sel contoh). Pada hasil baseline rentang penuh 0,847–1,042; pada hasil final 0,878–1,118.

## 6. Panjang bit modulus tidak terjamin (hal. 16, 10, 27) dan pseudocode pembangkitan kunci (hal. 16–17)

- **Hal. 16. Kutipan:** "Bit paling signifikan menjamin panjang bit yang diminta, sedangkan bit paling rendah yang dibuat 1 menjamin kandidat ganjil." — **benar untuk setiap prima**, tetapi pada versi awal tidak menjamin panjang n (untuk k = 5 hanya sekitar 3% kunci tepat). Pada kode final panjang n dijamin tepat (30 dari 30 kunci pada sampel di `results/final/ukuran_prima_sampel.txt`; uji formal di `tests/test_keygen_exact.py`).
- **Hal. 10. Kutipan:** "Aplikasi membangkitkan prima dengan panjang bit yang dibagi sedekat mungkin secara merata, mengurutkan faktor prima…"
  **Pengganti:** "Aplikasi membangkitkan k − 1 prima pertama dengan panjang bit yang dibagi sedekat mungkin secara merata. Prima terakhir dipilih dari rentang [⌈2^(B−1)/P⌉, ⌊(2^B − 1)/P⌋], dengan P hasil kali k − 1 prima pertama, sehingga modulus n tepat berukuran B bit; akibatnya prima terakhir dapat sedikit lebih panjang daripada rencana (pada sampel 30 kunci per konfigurasi di `results/final/ukuran_prima_sampel.txt`, prima terbesar 0 sampai 3 bit di atas ukuran terbesar yang direncanakan)."
- **Hal. 16–17, pseudocode GENERATE_KEYS. Pengganti (sesuai kode final):**

```
procedure GENERATE_KEYS(bits, k)
    validasi k ≥ 2, bits ≥ 16, dan floor(bits / k) ≥ 4
    base ← floor(bits / k);  rem ← bits mod k
    untuk i = 1 sampai k: prime_bits[i] ← base + 1 jika i ≤ rem; selain itu base
    tolak (raise error) kombinasi yang tidak menyediakan cukup prima berbeda pada ukuran kecil
    for attempt ← 1 to 100 do
        primes ← daftar kosong
        for i ← 1 to k − 1 do
            p ← GENERATE_PRIME(prime_bits[i], 40)
            ulangi (paling banyak 200 kali) sampai p belum ada di primes; jika gagal, lanjutkan attempt berikutnya
            tambahkan p ke primes
        P ← hasil kali semua prima di primes
        lo ← ceil(2^(bits−1) / P);  hi ← floor((2^bits − 1) / P)
        p_k ← prima acak dalam [lo, hi]; jika tidak ada atau sudah ada di primes, lanjutkan attempt berikutnya
        tambahkan p_k ke primes; urutkan primes dari kecil ke besar
        n ← hasil kali semua pᵢ;  (n tepat bits bit menurut konstruksi)
        φ ← hasil kali semua (pᵢ − 1);  e ← SELECT_E(primes)
        coba d ← MODINV(e, φ); jika gagal, lanjutkan attempt berikutnya
        untuk setiap i: dᵢ ← d mod (pᵢ − 1); jika dᵢ = 0 maka dᵢ ← pᵢ − 1
        hitung koefisien Garner t₂, …, tₖ dan koefisien Gauss C₁, …, Cₖ (Cᵢ = Nᵢ·Mᵢ mod n)
        if VALIDATE_KEYS(kunci publik, kunci privat) then return kedua kunci
    raise error jika 100 percobaan gagal
```

- **Flowchart pembangkitan kunci (hal. 20):** kotak "Bangkitkan k prima yang berbeda" dapat tetap, tetapi sebaiknya ditambah satu kotak "Prima terakhir dipilih dari rentang agar n tepat bits bit" dan keluaran "Gagal" untuk kombinasi (bits, k) yang tidak layak. Gambar harus digambar ulang oleh Anda.
- **Tangkapan layar "Hasil pembangkitan kunci (512 bit, k=5)" (hal. 27):** dibuat dengan kode awal; ganti dengan tangkapan layar dari kode final.
- **Bukti:** `core/keygen.py` (`generate_keys`); `results/final/ukuran_prima_sampel.txt`; `tests/test_keygen_exact.py`.

## 7. Validasi server (hal. 25)

- **Kutipan:** "Selain itu, server dilengkapi dengan fungsi validasi masukan untuk memastikan tipe data, panjang bit, dan batasan nilai k yang diterima memenuhi syarat sebelum diproses."
- **Status pada kode final:** pernyataan ini kini **lebih benar** daripada versi awal. Kode final memakai `ThreadingHTTPServer`, membatasi body 1.000.000 byte, menolak path di luar folder `static/` (`realpath` dan `commonpath`), dan mengubah `ValueError` menjadi HTTP 400; perilaku ini diuji di `tests/test_http_e2e.py` (mis. `test_invalid_input_is_400_not_500`, `test_oversized_body_is_rejected_without_reading_it`, `test_static_files_served_and_path_traversal_blocked`).
- **Teks tambahan yang disarankan:** "Server membatasi ukuran body permintaan, menolak akses di luar direktori `static/`, dan mengembalikan HTTP 400 untuk masukan tidak valid; perilaku ini diuji pada `tests/test_http_e2e.py`. Server menerima data kunci privat dari klien apa adanya tanpa memeriksa konsistensinya, sehingga hanya cocok untuk penggunaan lokal." (Pernyataan terakhir berdasarkan pembacaan `server/app.py::_handle_decrypt`; saya tidak menguji ulang pada kode final.)
- **Bukti:** `server/app.py`, `tests/test_http_e2e.py`.

## 8. Tabel kompleksitas (hal. 23)

- **Kutipan (baris tabel):** `miller_rabin(n, rounds)` — "O(rounds × log²n)".
- **Pengganti:** "O(rounds × log³ n)". Pada tabel yang sama `modexp(b, e, m)` ditulis O(log e × (log m)²); satu putaran Miller–Rabin memanggil satu `modexp` dengan eksponen d < n, sehingga biayanya O((log n) × (log n)²) = O(log³ n) per putaran.
- **Catatan keseragaman:** baris `gcd`, `extended_gcd`, dan `modinv` (O(log …)) menghitung **jumlah iterasi**, bukan biaya bit; dengan model biaya bit yang sama (pembagian bilangan L bit dengan kuosien kecil berbiaya O(L²)) biayanya O(log² …). Tambahkan keterangan di bawah tabel: "Kompleksitas pada baris gcd, extended_gcd, dan modinv dinyatakan dalam jumlah iterasi."
- **Alasan:** analitis; lihat `paper/BUKTI_MATEMATIS_draf.md`, bagian 7.

## 9. "k ≥ 3" di Latar Belakang (hal. 1) vs "k ≥ 2" (hal. 9, 24, kode)

- **Kutipan hal. 1:** "…menggunakan lebih dari dua bilangan prima (k≥3) untuk membentuk modulus n = p₁×p₂×... ×pk."
- **Kutipan hal. 9 (II.E):** "…menjadi hasil kali k prima berbeda, dengan k ≥ 2." dan hal. 24: "Dukungan Faktor Prima Banyak (k ≥ 2)". Kode: `if k < 2: raise ValueError`.
- **Pengganti hal. 1:** "…menggunakan k bilangan prima berbeda (k ≥ 2; RSA standar adalah kasus k = 2, sedangkan Multi-Prime RSA umumnya dipakai untuk k ≥ 3) untuk membentuk modulus n = p₁×p₂×... ×pk."
- **Hasil pemeriksaan konsistensi:** tidak ada tempat lain yang menyebut k ≥ 3 (pencarian pada teks PDF).

## 10. Rentang UI dan API (hal. 26)

- **Kutipan:** "Tab 'Pembangkitan Kunci': Pilih ukuran bit (64–2048) dan jumlah prima k (2–5)…" — **benar untuk UI** (`static/index.html`).
- **Tambahan yang disarankan:** "API `/keygen` menerima 16 sampai 4096 bit dan k = 2 sampai 8 (`server/app.py`); kombinasi yang tidak layak (mis. 16 bit dengan k = 4) ditolak dengan HTTP 400."

## 11. Rumusan masalah no. 2 dan tujuan no. 3 belum terjawab (hal. 1–2; Bab V–VI kosong)

- **Pengganti:** isi Bab V dan Bab VI dengan `paper/BAB_V_draf.md` dan `paper/BAB_VI_draf.md`, lalu pastikan tiap rumusan masalah punya jawaban eksplisit di Bab VI.

## 12. Judul sub-bab ganda di Bab V (hal. 31)

- **Kutipan:** "A. Test Vector Bilangan Kecil / B. Pengujian Kebenaran / C. Pengujian Kebenaran".
- **Pengganti (selaras dengan draf):** A. Test Vector Bilangan Kecil; B. Pengujian Kebenaran; C. Metodologi Pengujian Kinerja; D. Hasil Pengujian Kinerja; E. Analisis; F. Keterbatasan.

---

## 13. (tambahan) Deskripsi Gauss belum mencerminkan kode final (hal. 6, 19, 24; UI)

- **Kutipan hal. 19:** "Berbeda dari Garner pada proyek ini, Nᵢ dan Mᵢ dihitung ketika rekombinasi dijalankan." — ini **varian (a)**.
- **Fakta kode final:** kunci kini membawa `gauss_coeffs` (Cᵢ = Nᵢ·Mᵢ mod n, dihitung saat pembangkitan kunci), dan `decrypt_crt_gauss` secara bawaan memakai koefisien itu (varian b, tidak ada invers modular saat dekripsi). Varian (a) tetap tersedia (`use_precomputed=False`; di UI "Gauss (invers dihitung saat dekripsi)").
- **Pengganti hal. 19:** "Proyek ini menyediakan dua varian rekombinasi Gauss. Varian (a) menghitung Nᵢ = n div pᵢ dan Mᵢ = Nᵢ⁻¹ mod pᵢ di dalam setiap dekripsi. Varian (b) memakai koefisien Cᵢ = Nᵢ·Mᵢ mod n yang dihitung sekali saat pembangkitan kunci, sehingga x = (Σ mᵢ·Cᵢ) mod n tanpa invers modular saat dekripsi." Pseudocode `RECOMBINE_GAUSS` pada hal. 19 menggambarkan varian (a); tambahkan pseudocode varian (b):

```
procedure RECOMBINE_GAUSS_PRECOMP(m_residues, gauss_coeffs, n)
    x ← 0
    for i ← 1 to k do
        x ← x + mᵢ × Cᵢ
    return x mod n
```

- **Tambahan di hal. 24 (tabel `rsa.py`):** baris "CRT Gauss (C)" dipecah menjadi (C-a) dan (C-b); daftar isi kunci privat (Bab IV.B.3 dan tabel kunci pada UI) ditambah `gauss_coeffs`.
- **Bukti:** `core/rsa.py::decrypt_crt_gauss`, `core/keygen.py::compute_gauss_coefficients`, `tests/test_gauss_precompute.py`; `results/final/contoh_hitung.txt` (contoh numerik kedua varian).

## 14. (tambahan) "secara paralel" (hal. 1)

- **Kutipan:** "CRT memungkinkan perhitungan modular dilakukan pada modulus-modulus yang lebih kecil secara paralel…"
- **Pengganti:** "CRT memungkinkan perhitungan modular dilakukan pada modulus-modulus yang lebih kecil (dapat dijalankan paralel pada perangkat keras yang mendukung; pada implementasi proyek ini dijalankan berurutan pada satu utas)…"
- **Alasan:** percepatan yang diukur berasal dari ukuran operan yang lebih kecil, bukan dari paralelisme. Hal. 10 sudah menyebut "pada satu prosesor".

## 15. (tambahan) Bukti Fermat mengasumsikan pᵢ ∤ c (hal. 5)

- **Kutipan:** "Langkah selanjutnya menggunakan Teorema Fermat Kecil: c^(pᵢ−1) ≡ 1 (mod pᵢ), dengan asumsi pᵢ ∤ c (yang berlaku dengan probabilitas sangat tinggi dalam RSA)."
- **Pengganti:** "…dengan pᵢ ∤ c. Bila pᵢ | c, maka c ≡ 0 (mod pᵢ), dan karena dᵢ ≥ 1 (kode menjamin dᵢ > 0), cᵢ^dᵢ ≡ 0 ≡ c^d (mod pᵢ); jadi reduksi eksponen tetap berlaku pada kasus ini." Hal. 9–10 sudah menyinggung kasus nol; sebaiknya digabungkan di satu tempat.
- **Bukti:** `results/final/audit_exhaustive.txt` (semua c dalam [0, n) termasuk kelipatan pᵢ dan 0, untuk 12 kunci kecil: tidak ada kegagalan); `paper/BUKTI_MATEMATIS_draf.md`, bagian 3.

## 16. (kelengkapan) Daftar Isi dan Daftar Pustaka kosong

- **Daftar Isi (PDF hal. 2): benar-benar kosong.** Terverifikasi tiga cara: (1) `pdftotext` hanya menghasilkan judul "DAFTAR ISI" dan nomor halaman; (2) halaman dirasterisasi (`pdftoppm`) dan terlihat kosong selain judul dan nomor; (3) `pdfinfo` melaporkan `Form: none` dan `pdffonts` hanya mendaftar font teks biasa; keduanya tidak menunjukkan objek daftar isi yang gagal tampil (bukti lemah; hanya melengkapi dua cara pertama). Kemungkinan penyebab: daftar isi otomatis Google Docs belum dibangkitkan atau hilang saat ekspor; **penyebab TIDAK TERVERIFIKASI**. Tindakan: sisipkan Daftar Isi di Google Docs, ekspor ulang, dan periksa hasil PDF.
- **Daftar Pustaka (hal. 33): kosong**, padahal RFC 8017 dan PKCS #1 disebut di hal. 1, 7, 9, dan 24 tanpa sitasi. Lihat `paper/DAFTAR_PUSTAKA_draf.md`.
- Bab V (hal. 31) dan Bab VI (hal. 32) hanya berisi judul sub-bab.

## 17. (kelengkapan) Keterangan gambar tanpa nomor (hal. 26–29)

- Keterangan seperti "Gambar Tab Pembangkitan Kunci sebelum kunci dibangkitkan" tidak bernomor. Beri nomor ("Gambar 4.1 …") dan rujuk dari teks. Gambar hasil pengukuran memakai `paper/gambar/` dengan nomor Bab V.

---

## Yang konsisten (diperiksa ulang pada kode final)

Pseudocode SELECT_E, COMPUTE_GARNER_COEFFICIENTS, dan DECRYPT_CRT_GARNER sesuai `core/keygen.py` dan `core/rsa.py` (dibaca ulang pada kode final); pseudocode keygen dan flowchart Garner juga dinyatakan sesuai pada audit awal (REVIEW §5.3), kecuali butir 6. Pseudocode GCD, Extended GCD, MODINV, MODEXP, dan MILLER_RABIN tidak saya baca ulang satu per satu pada kode final. Contoh Garner p = (3, 5, 7), m = (2, 3, 2) → x = 23 (hal. 11–12) **benar**: dihitung ulang dengan kode inti di `results/final/contoh_hitung.txt`. Pernyataan bahwa `pow` 3-argumen dan `math.gcd` tidak dipakai di `core/` dan `server/` benar (diuji `tests/test_forbidden.py`).

## Yang belum bisa saya periksa

- Isi gambar flowchart dekripsi (hal. 21) dan tangkapan layar UI terhadap versi UI final (hanya flowchart pembangkitan kunci yang saya lihat).
- Aturan format sitasi dan tata tulis dosen pengampu.
- Berkas sumber Google Docs.

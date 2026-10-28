# BAB V — PENGUJIAN DAN ANALISIS (draf)

<!-- DRAF UNTUK DISUNTING MAHASISWA. Bukan teks final. Setiap angka diberi komentar sumber; angka berasal dari results/final/ (diukur pada kode v1-final) atau dari perintah yang dijalankan dan dicatat di results/final/. Penanda DIISI FASE D = nilai yang baru ditetapkan saat paket akhir dibangun. Metode di sini adalah metode yang sudah ada (CRT, Garner, Gauss/SRC); tidak ada klaim kebaruan. -->

## A. Test Vector Bilangan Kecil

### 1. Vektor uji CRT

Vektor uji berikut dipakai untuk memeriksa rekombinasi CRT dengan tangan dan dengan kode. Tiga prima p₁ = 3, p₂ = 5, p₃ = 7 (n = 105) dan residu m = (2, 3, 2). Pencarian langsung pada x ∈ [0, 105) menemukan tepat satu solusi, yaitu x = 23.
<!-- sumber: results/final/contoh_hitung.txt (bagian A, "pencarian langsung x in [0, 105): [23]"); bench/contoh_hitung.py -->

**Rekombinasi Garner.** Koefisien t₂ = 3⁻¹ mod 5 = 2 dan t₃ = (3·5)⁻¹ mod 7 = 1. Mulai dari x = m₁ = 2 dan P = 3. Untuk i = 2: u₂ = (3 − 2)·2 mod 5 = 2, sehingga x = 2 + 2·3 = 8. Untuk i = 3: u₃ = (2 − 8)·1 mod 7 = 1, sehingga x = 8 + 1·15 = 23.
<!-- sumber: results/final/contoh_hitung.txt (bagian A, langkah Garner) -->

**Rekombinasi Gauss.** Nᵢ = n/pᵢ dan Mᵢ = Nᵢ⁻¹ mod pᵢ: (N₁, M₁) = (35, 2), (N₂, M₂) = (21, 1), (N₃, M₃) = (15, 1). Jumlah mᵢNᵢMᵢ = 140 + 63 + 30 = 233, dan 233 mod 105 = 23.
<!-- sumber: results/final/contoh_hitung.txt (bagian A, langkah Gauss) -->

Hasil ketiganya sama: x = 23, dan memang 23 mod 3 = 2, 23 mod 5 = 3, 23 mod 7 = 2.

Vektor yang sama dilewatkan melalui dekripsi RSA penuh: n = 105, φ(n) = 48, e = 5, d = 29, pesan m = 23. Ciphertext c = 23⁵ mod 105 = 53; sisa cᵢ = (2, 3, 4); eksponen per prima dᵢ = (1, 1, 5); hasil per prima mᵢ = (2, 3, 2), tepat residu pada vektor uji. Dekripsi standar, CRT-Garner, CRT-Gauss (a), dan CRT-Gauss (b) pada kode inti semuanya menghasilkan 23, sama dengan pembanding pow(c, d, n).
<!-- sumber: results/final/contoh_hitung.txt (bagian A, "Vektor yang sama lewat dekripsi RSA penuh") -->

### 2. Contoh RSA multi-prima penuh

Contoh dengan tiga prima p = (11, 13, 17): n = 2431, φ(n) = 10·12·16 = 1920, e = 7 (gcd(7, 1920) = 1), d = 7⁻¹ mod 1920 = 823 (7·823 mod 1920 = 1). Eksponen per prima dᵢ = (3, 7, 7); koefisien Garner t = (6, 5); koefisien Gauss (b) Cᵢ = (221, 1496, 715).
<!-- sumber: results/final/contoh_hitung.txt (bagian B) -->

Pesan m = 1234 dienkripsi menjadi c = 1234⁷ mod 2431 = 1195. Sisa cᵢ = (7, 12, 5) dan hasil per prima mᵢ = (2, 12, 10), sama dengan m mod pᵢ. Garner: x = 2; i = 2: u = (12 − 2)·6 mod 13 = 8, x = 2 + 8·11 = 90; i = 3: u = (10 − 90)·5 mod 17 = 8, x = 90 + 8·143 = 1234. Gauss: 442 + 17952 + 7150 = 25544 dan 25544 mod 2431 = 1234. Keempat jalur dekripsi pada kode inti memulihkan m = 1234, sama dengan pow(c, d, n).
<!-- sumber: results/final/contoh_hitung.txt (bagian B); total operasi tercatat penghitung: standar 45, Garner 60, Gauss (a) 65, Gauss (b) 53 (tidak bermakna untuk kinerja pada ukuran sekecil ini) -->

## B. Pengujian Kebenaran

Kebenaran diperiksa pada lima tingkat.

1. **Tes otomatis.** Seluruh 55 tes (teori bilangan, kunci, dekripsi tiga metode, penghitung operasi, codec teks, server HTTP) lulus pada Python 3.10.20, 3.13.14, dan 3.14.4.
<!-- sumber: results/final/uji_versi_python.txt (Python 3.10 dan 3.13 dipasang lewat uv di direktori sementara; 3.14 adalah versi sistem). Catatan: hanya ketiga versi ini yang diuji. -->
2. **Setiap hasil benchmark divalidasi.** Pada 9.600 pengukuran, hasil dekripsi yang dikembalikan sama dengan plaintext asal pada 9.600 dari 9.600 baris (kolom `correct`), dan panjang modulus aktual sama dengan yang diminta pada semua baris.
<!-- sumber: results/final/benchmark_raw_l0125001.csv (kolom correct, bits_actual, bits_target; 9600 baris) -->
3. **Uji menyeluruh pada kunci kecil.** Untuk 12 kunci acak 16–17 bit dengan k = 2 dan 3, ketiga metode dibandingkan dengan pow(c, d, n) untuk **semua** c ∈ [0, n), termasuk c = 0 dan kelipatan setiap pᵢ: 969.502 pasangan (kunci, c), tidak ada kegagalan.
<!-- sumber: results/final/audit_exhaustive.txt (bench/audit_exhaustive.py; kunci acak, jumlah pasangan berbeda tiap jalan). Catatan kaki: pada kode awal (baseline) jalan serupa memeriksa 532.536 pasangan tanpa kegagalan (results/audit_exhaustive.txt di repo; tidak ikut paket pengumpulan). -->
4. **Hitungan operasi tidak berubah oleh perbaikan.** Kode inti akhir dibandingkan dengan kode awal pada kunci dan ciphertext yang sama (24 kunci, 8 ciphertext termasuk 0, 1, n − 1; 3 metode): plaintext dan keenam bidang `operation_counts` identik pada 576 dari 576 perbandingan.
<!-- sumber: results/final/audit_opcount_regression.txt (bench/audit_opcount_regression.py) -->
5. **Dua implementasi biaya berbobot-bit saling cocok.** Penghitung di `core/` dan model terpisah di `bench/` memberi biaya literal dan refined yang identik pada 960 dari 960 perbandingan (standar, Garner, Gauss (b)). Untuk Gauss (a) penghitung inti rata-rata 5,14% lebih rendah karena invers modular tidak dicacah.
<!-- sumber: results/final/costmodel_crosscheck.txt -->

Selain itu, d berbasis φ(n) (yang dipakai kode) memberi eksponen per prima dᵢ yang sama persis dengan d berbasis λ(n) pada 800 dari 800 kunci acak, dan c^d_φ mod n = c^d_λ mod n pada 4.000 dari 4.000 ciphertext; d berbasis φ lebih panjang pada 717 dari 800 kunci (selisih 0 sampai 30 bit), yang hanya memengaruhi dekripsi standar.
<!-- sumber: results/final/audit_d_phi_lambda.txt (kunci acak; angka berbeda tiap jalan) -->

## C. Metodologi Pengujian Kinerja

### 1. Yang diukur

Tiga jalur dekripsi pada kunci multi-prima dengan k faktor: (i) **RSA standar**, m = c^d mod n; (ii) **CRT-Garner**; (iii) **CRT-Gauss**, dengan dua varian: **(a)** Nᵢ = n div pᵢ dan Mᵢ = Nᵢ⁻¹ mod pᵢ dihitung di dalam setiap dekripsi, dan **(b)** koefisien Cᵢ = Nᵢ·Mᵢ mod n dihitung sekali saat pembangkitan kunci. Varian (b) adalah perlakuan yang sama dengan koefisien tᵢ pada Garner, sehingga perbandingan Garner–Gauss tidak dikacaukan oleh pekerjaan invers modular di dalam waktu dekripsi.

Setiap sel (ukuran modulus, k) diukur pada tiga **lapisan** implementasi: **core** (kode inti apa adanya, termasuk penghitung operasi dan pencatatan langkah; lapisan utama laporan ini), **lean** (salinan tanpa penghitung dan pencatatan, untuk melihat overhead instrumentasi), dan **builtin** (pow() bawaan Python; hanya informatif karena proyek ini melarang pow() 3-argumen di kode inti).

### 2. Desain

- Grid: panjang modulus {64, 128, 256, 512, 1024, 2048, 3072, 4096} bit × k ∈ {2, 3, 4, 5} = 32 sel; sepuluh kombinasi (metode, lapisan) per sel.
- Tiap sel memakai satu kunci dan 30 ciphertext yang **sama** untuk semua metode; 3 putaran pemanasan dibuang, lalu 30 putaran terukur per metode. Urutan metode diacak pada tiap putaran. Waktu diukur dengan `time.perf_counter`, pemungut sampah dimatikan selama pengukuran, dan proses dipatok pada satu inti CPU.
- Tiap hasil dekripsi divalidasi terhadap plaintext asal sebelum waktunya dicatat.
- **Speedup** = median waktu RSA standar ÷ median waktu metode pada sel yang sama. **Interval kepercayaan 95%** dihitung dengan bootstrap persentil (1.000 resampling, sampel standar dan metode diresampel secara independen) dan hanya mencerminkan variasi antar putaran dalam satu sesi pengukuran.
- **Titik silang** didefinisikan sebelum data ada: bits terkecil di grid sehingga batas bawah CI95 speedup > 1 untuk semua bits yang lebih besar.
- **Model biaya berbobot-bit** (tidak bergantung pada interpreter): biaya literal tiap perkalian, modulo, dan pembagian = bl(a)·bl(b); biaya refined: perkalian bl(a)·bl(b), modulo dan pembagian = (panjang kuosien)·(panjang pembagi).
<!-- sumber: results/final/benchmark_meta_l0125001.json (config: bits, k, reps=30, warmup=3, n_ct=30, seed, cpu=43); bench/benchmark.py (docstring); bench/costmodel.py -->

### 3. Lingkungan dan identitas kode

**Tabel 5.1.** Lingkungan dan konfigurasi pengukuran

| Butir | Nilai |
|---|---|
| Commit sumber kode | 58aafddf4f3fe1c8a3a95f8a91c332f873ff92b9 |
| Pohon kerja bersih (tanpa perubahan terlacak) | ya |
| Python | 3.14.4 (main, Jun 18 2026, 14:25:02) [GCC 15.2.0] |
| OS | Linux-6.17.9-1-pve-x86_64-with-glibc2.43 |
| CPU | Intel(R) Xeon(R) Silver 4216 CPU @ 2.10GHz |
| CPU logis tersedia | 16 |
| CPU dipatok ke nomor | 43 |
| Host | l0125001 |
| Waktu mulai | 2026-10-28T08:36:08 |
| Load average awal (1/5/15 menit) | 9,20 / 9,76 / 10,25 |
| Load average akhir (1/5/15 menit) | 9,70 / 9,86 / 10,18 |
| Durasi pengukuran (detik) | 235,3 |
| Durasi total (detik) | 248,2 |
| Baris data | 9600 |
| Putaran terukur per sel | 30 |
| Pemanasan | 3 |
| Ciphertext bersama per kunci | 30 |
| Seed | 20261028 |

<!-- sumber: paper/tabel/00_lingkungan.md ("Tabel") <- results/final/ -->

Pengukuran dijalankan pada pohon kerja bersih tepat di commit `58aafddf4f3fe1c8a3a95f8a91c332f873ff92b9` (tag `v1-final`) dan memerlukan 235,3 detik pengukuran (248,2 detik total) untuk 9.600 baris.
<!-- sumber: results/final/benchmark_meta_l0125001.json (source_commit, source_dirty=false, measure_time_s, wall_time_s, rows) -->

Paket pengumpulan dibangun dari ujung cabang `final-submission` pada commit **[DIISI FASE D: hash commit]** dengan SHA-256 **[DIISI FASE D: hash zip kriptografi_rsa_final_v2.zip]**. Kode yang diukur dan kode di paket identik pada direktori `core/`, `server/`, `static/`, dan `tests/`; buktinya keluaran `git diff v1-final..HEAD -- core server static tests` yang kosong **[DIISI FASE D: tempel keluaran dan kode keluar perintah]**.

## D. Hasil Pengujian Kinerja

Seluruh angka di bawah adalah lapisan core. Tabel utama memuat modulus 512 bit ke atas; hasil 64–256 bit ada di Lampiran (lihat bagian E.5 mengenai kurva yang tidak mulus pada ukuran kecil).

### 1. Waktu dekripsi RSA standar

**Tabel 5.2.** Waktu median dekripsi RSA standar (ms), lapisan core

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 0,061 | 0,057 | 0,063 | 0,060 |
| 128 | 0,136 | 0,128 | 0,127 | 0,129 |
| 256 | 0,352 | 0,361 | 0,345 | 0,356 |
| 512 | 1,370 | 1,327 | 1,421 | 1,318 |
| 1024 | 6,980 | 6,774 | 6,825 | 6,800 |
| 2048 | 41,488 | 41,886 | 40,538 | 41,608 |
| 3072 | 124,715 | 128,632 | 128,446 | 127,793 |
| 4096 | 291,873 | 294,830 | 290,632 | 290,418 |

<!-- sumber: paper/tabel/08_waktu_standar_ms.md ("Tabel") <- results/final/ -->

Waktu RSA standar praktis tidak bergantung pada k pada modulus yang sama (pada 4096 bit: 291,873; 294,830; 290,632; 290,418 ms untuk k = 2 sampai 5), sesuai harapan karena jalur ini tidak memakai faktor prima.
<!-- sumber: results/final/benchmark_summary.csv (layer=core, method=standard, median_s) -->

### 2. Speedup CRT-Garner

**Tabel 5.3.** Speedup CRT-Garner terhadap RSA standar: median [CI95]

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,83 [1,82–1,83] | 2,23 [2,22–2,24] | 2,70 [2,69–2,72] | 2,72 [2,71–2,74] |
| 1024 | 2,55 [2,54–2,55] | 3,98 [3,97–3,99] | 4,71 [4,70–4,73] | 5,58 [5,56–5,66] |
| 2048 | 3,03 [3,03–3,03] | 5,91 [5,90–5,91] | 7,48 [7,48–7,49] | 10,24 [10,23–10,25] |
| 3072 | 3,27 [3,26–3,27] | 6,26 [6,22–6,28] | 10,04 [10,02–10,05] | 13,54 [13,51–13,56] |
| 4096 | 3,53 [3,52–3,54] | 7,15 [7,13–7,16] | 10,40 [10,39–10,42] | 15,69 [15,68–15,71] |

<!-- sumber: paper/tabel/01_speedup_garner.md ("Tabel utama (512–4096 bit)") <- results/final/ -->

Pada 4096 bit, CRT-Garner 3,53 kali lebih cepat dari RSA standar untuk k = 2 dan 15,69 kali untuk k = 5; pada 2048 bit 3,03 kali (k = 2) sampai 10,24 kali (k = 5). Waktu absolutnya pada 4096 bit turun dari 291,873 ms (standar, k = 2) menjadi 82,673 ms (Garner, k = 2) dan 18,506 ms (Garner, k = 5).
<!-- sumber: results/final/benchmark_summary.csv (layer=core; speedup, median_s) -->

### 3. Speedup CRT-Gauss (a) dan (b)

**Tabel 5.4.** Speedup CRT-Gauss (a) terhadap RSA standar: median [CI95]

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,54 [1,53–1,55] | 1,82 [1,82–1,83] | 2,20 [2,20–2,21] | 2,16 [2,15–2,17] |
| 1024 | 2,26 [2,26–2,27] | 3,39 [3,38–3,39] | 3,92 [3,91–3,92] | 4,54 [4,52–4,57] |
| 2048 | 2,86 [2,85–2,86] | 5,35 [5,34–5,36] | 6,68 [6,68–6,70] | 8,87 [8,86–8,88] |
| 3072 | 3,15 [3,14–3,16] | 5,90 [5,88–5,92] | 9,18 [9,15–9,20] | 12,17 [12,15–12,19] |
| 4096 | 3,44 [3,44–3,45] | 6,86 [6,85–6,87] | 9,82 [9,81–9,84] | 14,46 [14,43–14,47] |

<!-- sumber: paper/tabel/02_speedup_gauss_a.md ("Tabel utama (512–4096 bit)") <- results/final/ -->

**Tabel 5.5.** Speedup CRT-Gauss (b) terhadap RSA standar: median [CI95]

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,83 [1,82–1,84] | 2,24 [2,23–2,25] | 2,73 [2,73–2,75] | 2,76 [2,75–2,78] |
| 1024 | 2,55 [2,54–2,55] | 3,99 [3,97–4,00] | 4,73 [4,72–4,73] | 5,62 [5,59–5,70] |
| 2048 | 3,03 [3,02–3,03] | 5,91 [5,90–5,92] | 7,50 [7,49–7,50] | 10,27 [10,26–10,28] |
| 3072 | 3,27 [3,26–3,27] | 6,27 [6,25–6,28] | 10,04 [10,03–10,06] | 13,57 [13,54–13,59] |
| 4096 | 3,53 [3,52–3,54] | 7,15 [7,14–7,16] | 10,40 [10,39–10,41] | 15,70 [15,68–15,71] |

<!-- sumber: paper/tabel/03_speedup_gauss_b.md ("Tabel utama (512–4096 bit)") <- results/final/ -->

### 4. Garner dibandingkan Gauss

**Tabel 5.6.** Rasio waktu median CRT-Garner terhadap CRT-Gauss (b)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,002 | 1,005 | 1,012 | 1,014 |
| 1024 | 0,999 | 1,001 | 1,004 | 1,007 |
| 2048 | 0,999 | 1,000 | 1,002 | 1,003 |
| 3072 | 1,000 | 1,001 | 1,001 | 1,002 |
| 4096 | 1,000 | 0,999 | 1,000 | 1,000 |

<!-- sumber: paper/tabel/04_rasio_garner_gauss_b.md ("Garner / Gauss (b), 512–4096 bit") <- results/final/ -->

Rasio waktu median Garner terhadap Gauss (b) berkisar 0,997 sampai 1,110 pada seluruh grid dan 0,999 sampai 1,014 untuk 512 bit ke atas, yaitu praktis sama. Gauss (a) lebih lambat daripada Gauss (b): rasionya 1,025 sampai 1,323 pada seluruh grid dan 1,025 sampai 1,280 untuk 512 bit ke atas.
<!-- sumber: results/final/benchmark_summary.csv (layer=core; median_s); paper/tabel/04_rasio_garner_gauss_b.md -->

### 5. Multi-prime dibandingkan CRT dua prima

**Tabel 5.7.** Speedup CRT-Garner k = 3–5 terhadap CRT-Garner k = 2 (CI95 dalam kurung siku)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,00 (acuan) | 1,26 [1,25–1,26] | 1,43 [1,42–1,44] | 1,55 [1,55–1,56] |
| 1024 | 1,00 (acuan) | 1,61 [1,61–1,62] | 1,89 [1,89–1,90] | 2,25 [2,24–2,28] |
| 2048 | 1,00 (acuan) | 1,93 [1,93–1,93] | 2,53 [2,52–2,53] | 3,37 [3,36–3,37] |
| 3072 | 1,00 (acuan) | 1,86 [1,85–1,86] | 2,98 [2,98–2,99] | 4,05 [4,04–4,05] |
| 4096 | 1,00 (acuan) | 2,01 [2,00–2,01] | 2,96 [2,95–2,96] | 4,47 [4,46–4,47] |

<!-- sumber: paper/tabel/05_multiprime_vs_crt2.md ("Terhadap CRT-Garner k = 2, 512–4096 bit") <- results/final/ -->

Dibanding CRT-Garner dengan dua prima (k = 2) pada ukuran modulus yang sama, k = 3 sampai 5 lebih cepat pada seluruh 24 sel (batas bawah CI95 di atas 1 pada 24 dari 24 sel); untuk 512 bit ke atas faktornya 1,26 sampai 4,47. Pada 4096 bit, k = 5 mencapai 4,47 kali dibanding CRT dua prima dan 15,77 kali dibanding RSA standar dua prima.
<!-- sumber: results/final/benchmark_summary.csv (layer=core, method=crt_garner; speedup_vs_garner_k2, speedup_vs_garner_k2_lo, speedup_vs_standard_k2); paper/tabel/05_multiprime_vs_crt2.md -->

### 6. Efisiensi terhadap k²

**Tabel 5.8.** Efisiensi CRT-Garner: speedup dibagi k²

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 46% | 25% | 17% | 11% |
| 1024 | 64% | 44% | 29% | 22% |
| 2048 | 76% | 66% | 47% | 41% |
| 3072 | 82% | 70% | 63% | 54% |
| 4096 | 88% | 79% | 65% | 63% |

<!-- sumber: paper/tabel/06_efisiensi_kuadrat.md ("Tabel utama (512–4096 bit)") <- results/final/ -->

Pada 4096 bit efisiensi (speedup ÷ k²) adalah 88%, 79%, 65%, dan 63% untuk k = 2 sampai 5; pada 512 bit hanya 46%, 25%, 17%, dan 11%. Speedup waktu terukur tidak pernah mencapai k².
<!-- sumber: results/final/benchmark_summary.csv (layer=core, method=crt_garner; speedup dibagi k²); paper/tabel/06_efisiensi_kuadrat.md -->

### 7. Model biaya berbobot-bit

**Tabel 5.9.** Speedup menurut model biaya berbobot-bit, CRT-Garner (literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 3,95 / 3,96 | 8,99 / 9,02 | 16,36 / 16,41 | 25,05 / 25,09 |
| 1024 | 3,97 / 3,98 | 9,01 / 9,03 | 15,89 / 15,90 | 24,84 / 24,85 |
| 2048 | 3,94 / 3,94 | 9,03 / 9,04 | 15,82 / 15,82 | 24,52 / 24,53 |
| 3072 | 3,96 / 3,96 | 9,04 / 9,04 | 15,88 / 15,89 | 25,34 / 25,34 |
| 4096 | 3,97 / 3,98 | 9,04 / 9,05 | 15,95 / 15,95 | 25,17 / 25,18 |

<!-- sumber: paper/tabel/07_biaya_berbobot_bit.md ("CRT-Garner, 512–4096 bit (literal / refined)") <- results/final/ -->

Pada model biaya, speedup CRT-Garner pada 4096 bit adalah 3,97 / 9,04 / 15,95 / 25,17 (literal) dan 3,98 / 9,05 / 15,95 / 25,18 (refined) untuk k = 2 sampai 5, sangat dekat dengan k² = 4, 9, 16, 25. Untuk CRT-Gauss (a) pada 4096 bit: 3,81 / 8,66 / 15,23 / 24,00 (literal) dan 3,97 / 9,03 / 15,91 / 25,08 (refined); CRT-Gauss (b) hampir identik dengan Garner.
<!-- sumber: results/final/benchmark_cost.csv (speedup_literal, speedup_refined; 10 ciphertext per sel); paper/tabel/07_biaya_berbobot_bit.md -->

### 8. Penghitung operasi bawaan

Rasio total operasi RSA standar terhadap CRT-Garner yang dicatat `OperationCounter` berkisar 0,878 sampai 1,118 pada seluruh grid (64–4096 bit) dan 0,986 sampai 1,018 untuk 512 bit ke atas. Rentang yang lebih sempit untuk 512 bit ke atas ditampilkan karena pada ukuran kecil rasio menyimpang lebih jauh dari 1, dan penyebabnya tidak diselidiki. Rasio yang mendekati 1 berarti penghitung tidak membedakan CRT dari RSA standar; penghitung mencacah operasi tanpa memperhitungkan panjang operan.
<!-- sumber: results/final/benchmark_summary.csv (layer=core, method=crt_garner; ops_ratio_standard_over_method); paper/tabel/11_rasio_op_counter.md -->

### 9. Gambar

Gambar 5.1 (waktu terhadap panjang modulus, log–log), Gambar 5.2 (speedup beserta CI95), Gambar 5.3 (model biaya terhadap k²), dan Gambar 5.4 (efisiensi terhadap k²) berada di `paper/gambar/` dengan draf keterangan di `paper/gambar/KETERANGAN_GAMBAR.md`.

## E. Analisis

### 1. Menjawab rumusan masalah

**Percepatan terhadap RSA standar dan CRT dua prima.** CRT-Garner dan CRT-Gauss (b) lebih cepat daripada RSA standar pada seluruh 32 sel (batas bawah CI95 minimum 1,132 untuk Garner dan 1,133 untuk Gauss (b); speedup minimum 1,151 dan 1,154; maksimum 15,69 dan 15,70). Pada modulus 512 bit ke atas Garner 1,83 sampai 15,69 kali. Multi-prime (k = 3–5) lebih cepat daripada CRT dua prima pada 24 dari 24 sel.
<!-- sumber: results/final/benchmark_crossover.csv (min_speedup, max_speedup); benchmark_summary.csv (speedup_ci95_lo) -->

**Pengaruh k.** Pada modulus yang sama, speedup naik seiring k, tetapi lebih lambat daripada k²: efisiensi turun dari 88% (k = 2) menjadi 63% (k = 5) pada 4096 bit, dan penurunannya lebih tajam pada modulus kecil.

### 2. Garner versus Gauss

Dengan perlakuan yang sama (koefisien diprekomputasi), Garner dan Gauss tidak berbeda berarti: rasio waktu 0,999 sampai 1,014 untuk 512 bit ke atas. Karena itu pernyataan bahwa Garner "lebih efisien" daripada Gauss tidak didukung oleh pengukuran ini. Varian Gauss (a) lebih lambat 2,5% sampai 28% daripada Gauss (b) pada 512 bit ke atas, yang konsisten dengan tambahan pekerjaan invers modular di dalam waktu dekripsi; **ini penjelasan yang selaras dengan data, tidak diuji dengan percobaan terpisah**. Gauss (a) memberi speedup di bawah 1 hanya pada dua sel kecil: 0,93 [0,92–0,94] pada 128 bit, k = 2, dan 0,98 [0,97–1,00] pada 128 bit, k = 3. Titik silangnya 256 bit untuk k = 2, 3, dan 4 serta tidak ada titik silang di dalam grid untuk k = 5; Garner dan Gauss (b) tidak punya titik silang di dalam grid (semua sel lebih cepat).
<!-- sumber: results/final/benchmark_summary.csv; benchmark_crossover.csv (core, crt_gauss: crossover_bits 256, 256, 256, 64 untuk k = 2..5; "64" berarti tidak ada titik silang di dalam grid) -->

### 3. Mengapa speedup di bawah k²

Argumen model: eksponensiasi dengan operan L bit berbiaya sekitar L³, sehingga k eksponensiasi pada B/k bit berbiaya B³/k², yaitu percepatan k² (untuk k = 2: sekitar 4, seperti dinyatakan pula pada [12] dan diturunkan dari [5]; lihat `BUKTI_MATEMATIS_draf.md` bagian 7). [Sitasi [5], [12] merujuk `DAFTAR_PUSTAKA_draf.md`; [12] adalah makalah mahasiswa, bukan jurnal.] Model biaya berbobot-bit memang mendekati k² pada 512 bit ke atas (butir D.7). Waktu terukur lebih rendah. Bukti dari data: jumlah operasi yang dicatat hampir sama antara standar dan CRT (rasio mendekati 1; butir D.8), jadi CRT melakukan sebanyak operasi yang kira-kira sama tetapi dengan operan yang lebih pendek. Pada operan pendek, waktu satu operasi di interpreter Python lebih didominasi biaya tetap per operasi (pemanggilan, alokasi objek) daripada panjang operan; karena itu keuntungan ukuran operan baru terlihat penuh pada modulus besar. Ini **dugaan yang konsisten dengan data** (efisiensi naik terhadap bits, dan lapisan lean serta builtin yang overhead-nya lebih kecil memberi speedup lebih tinggi pada ukuran kecil), tetapi **tidak diuji dengan percobaan yang memisahkan biaya tetap dari biaya operan**. Dugaan tambahan: biaya rekombinasi (yang bertambah dengan k tetapi tidak ikut mengecil seperti eksponensiasi) ikut menurunkan efisiensi pada k besar; ini juga tidak diuji terpisah.

### 4. Pengaruh instrumentasi dan lapisan implementasi

Lapisan core (dengan penghitung operasi dan pencatatan langkah) lebih lambat daripada lean: pada 4096 bit rasionya 1,01 (standar) dan 1,02 sampai 1,09 (Garner, k = 2 sampai 5); pada 64 bit 1,65 (standar, k = 2) dan 3,12 (Garner, k = 5). Karena overhead lebih besar pada CRT, speedup lapisan core lebih rendah daripada lean (mis. Garner, 4096 bit, k = 5: 15,69 pada core dan 17,06 pada lean; builtin dengan pow(): 17,33). Kesimpulan kualitatif tidak berubah di ketiga lapisan.
<!-- sumber: paper/tabel/12_overhead_dan_kestabilan.md; paper/tabel/09_lapisan_garner.md; results/final/benchmark_summary.csv -->

### 5. Ukuran kecil (64–256 bit) dan lonjakan pada modulus 30 bit

Pada 64–256 bit, speedup Garner hanya 1,15 sampai 1,63 dan kurvanya tidak mulus terhadap bits (Lampiran). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik dari 0,2099 µs pada modulus 30 bit menjadi 0,3100 µs pada 31 bit dan 0,3427 µs pada 32 bit, yaitu naik 48% dan 63%; kenaikan serupa teramati pada dua sesi pengukuran. Ukuran prima per faktor pada sel kecil berkisar 12,8 sampai 128 bit, sehingga sebagian sel berada di sisi bawah dan sebagian di sisi atas ambang itu. Mekanisme lonjakan **TIDAK TERVERIFIKASI**; modul ini tidak dipakai untuk menarik kesimpulan tentang tren pada ukuran kecil.
<!-- sumber: results/final/probe_smallint.txt; paper/tabel/01_speedup_garner.md (lampiran); "dua sesi" = probe pada baseline (results/probe_smallint.txt di repo, tidak ikut paket) dan probe final -->

### 6. Konsistensi dengan pengukuran sebelumnya

Pengukuran ini juga dibandingkan dengan pengukuran yang dilakukan pada kode sebelum perbaikan: hanya 5 dari 96 sel (speedup tiap metode dan sel) berubah lebih dari 10%, seluruhnya pada k = 2 dan modulus 64 atau 256 bit; median perubahan mutlak 2,0% sampai 2,6%. Penyebab perubahan itu **belum dipisahkan secara eksperimen**; dugaan yang tercatat: perbedaan pembangkitan kunci (panjang eksponen per prima acak), lokasi pemanggilan varian Gauss (b), overhead penghitung biaya, dan perbedaan sesi atau beban mesin.
<!-- sumber: results/final/perbandingan_baseline.md (lampiran opsional; merujuk berkas baseline yang tidak ikut paket pengumpulan) -->

## F. Keterbatasan

1. **Satu mesin, satu sesi.** Seluruh data berasal dari satu server (Intel Xeon Silver 4216, Python 3.14.4, Linux). CI95 hanya mencerminkan variasi antar putaran dalam satu sesi; variasi antar sesi dan antar mesin **tidak diukur**.
2. **Beban host tidak terkendali.** Server dipakai bersama; load average selama pengukuran sekitar 9–10 (9,20 sebelum, 9,70 sesudah), dan CPU hanya dipatok ke satu inti, bukan diisolasi.
<!-- sumber: results/final/benchmark_meta_l0125001.json (loadavg_start, loadavg_end); catatan_waktu_dan_load.txt -->
3. **Windows dan macOS belum diuji sungguhan.** Skrip benchmark dan petunjuknya (`bench/RUN_ME.md`) hanya diuji penuh di Linux; jalur untuk sistem operasi lain hanya disimulasikan di Linux.
4. **`bench/compare_machines.py` belum diuji dengan data dari mesin lain.** Skrip itu baru diuji pada tiga sesi dari host yang sama (dengan label berbeda).
5. **Versi Python.** Tes (bukan benchmark) lulus pada Python 3.10, 3.13, dan 3.14; benchmark waktu hanya dijalankan pada 3.14.4, dan hasilnya dapat berbeda pada versi lain.
6. **Mekanisme lonjakan 30 bit dan penyebab selisih terhadap pengukuran sebelumnya** tidak terverifikasi (butir E.5 dan E.6).
7. **Lingkup keamanan.** Implementasi adalah RSA dasar tanpa padding (bukan OAEP); aplikasi untuk pembelajaran. Penggunaan lebih banyak prima mengecilkan tiap faktor sehingga lebih mudah difaktorkan; batas aman jumlah dan ukuran prima **TIDAK TERVERIFIKASI** di sini (rujuk RFC 8017 [1] dan literatur keamanan seperti [7]). Dekripsi berbasis CRT juga dikenal rentan terhadap kesalahan perhitungan (*fault*) [8]; implementasi ini tidak memiliki perlindungan terhadap galat. [Isi [8] belum dibaca penyusun draf; baca sebelum mengutip.] Pengukuran memakai kunci acak tiap sel (satu kunci per sel), sehingga variasi antar kunci tidak diukur.
8. **Pengukuran waktu sisi-klien/aplikasi web tidak dilakukan**; waktu yang ditampilkan antarmuka adalah satu pengukuran tunggal dengan instrumentasi dan tidak dipakai sebagai data.
9. **Hasil mode `--quick`** (uji fungsi skrip) tidak dipakai dalam bab ini.

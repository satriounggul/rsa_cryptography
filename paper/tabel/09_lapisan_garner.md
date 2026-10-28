# Speedup CRT-Garner pada tiga lapisan implementasi

<!-- sumber: results/final/benchmark_summary.csv (layer=core, lean, builtin; method=crt_garner; kolom speedup); dibangkitkan oleh bench/make_paper_assets.py -->

core = kode inti apa adanya (dengan penghitung operasi); lean = salinan tanpa penghitung/dict; builtin = pow() bawaan Python (hanya informatif). Lapisan lean dan builtin tidak diberi CI di tabel ini.

## 512–4096 bit

| bits | lapisan | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|---|
| 512 | core | 1,83 | 2,23 | 2,70 | 2,72 |
| 512 | lean | 2,15 | 2,84 | 3,65 | 3,83 |
| 512 | builtin | 2,36 | 3,21 | 3,99 | 4,41 |
| 1024 | core | 2,55 | 3,98 | 4,71 | 5,58 |
| 1024 | lean | 2,81 | 4,88 | 6,15 | 7,74 |
| 1024 | builtin | 2,92 | 5,21 | 6,74 | 8,89 |
| 2048 | core | 3,03 | 5,91 | 7,48 | 10,24 |
| 2048 | lean | 3,16 | 6,54 | 8,62 | 12,37 |
| 2048 | builtin | 3,23 | 6,58 | 9,01 | 13,52 |
| 3072 | core | 3,27 | 6,26 | 10,04 | 13,54 |
| 3072 | lean | 3,33 | 6,59 | 10,97 | 15,39 |
| 3072 | builtin | 3,41 | 6,77 | 11,40 | 16,01 |
| 4096 | core | 3,53 | 7,15 | 10,40 | 15,69 |
| 4096 | lean | 3,58 | 7,40 | 10,99 | 17,06 |
| 4096 | builtin | 3,66 | 7,40 | 11,31 | 17,33 |

## 64–256 bit (lampiran)

| bits | lapisan | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|---|
| 64 | core | 1,22 | 1,35 | 1,27 | 1,22 |
| 64 | lean | 1,46 | 2,16 | 2,19 | 2,24 |
| 64 | builtin | 1,38 | 2,54 | 2,53 | 2,78 |
| 128 | core | 1,15 | 1,23 | 1,18 | 1,58 |
| 128 | lean | 1,28 | 1,54 | 1,44 | 2,84 |
| 128 | builtin | 1,15 | 1,56 | 1,32 | 3,39 |
| 256 | core | 1,31 | 1,60 | 1,47 | 1,63 |
| 256 | lean | 1,49 | 2,04 | 1,77 | 2,29 |
| 256 | builtin | 1,59 | 2,23 | 1,74 | 2,52 |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


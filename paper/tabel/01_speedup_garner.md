# Speedup CRT-Garner terhadap RSA standar (lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=crt_garner, kolom speedup, speedup_ci95_lo, speedup_ci95_hi; dibangkitkan oleh bench/make_paper_assets.py -->

Speedup = median waktu RSA standar / median waktu metode pada kunci k-prima dan 30 ciphertext yang sama; kurung siku = CI95 bootstrap (1000 resampling independen, persentil) dalam satu sesi pengukuran.

## Tabel utama (512–4096 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,83 [1,82–1,83] | 2,23 [2,22–2,24] | 2,70 [2,69–2,72] | 2,72 [2,71–2,74] |
| 1024 | 2,55 [2,54–2,55] | 3,98 [3,97–3,99] | 4,71 [4,70–4,73] | 5,58 [5,56–5,66] |
| 2048 | 3,03 [3,03–3,03] | 5,91 [5,90–5,91] | 7,48 [7,48–7,49] | 10,24 [10,23–10,25] |
| 3072 | 3,27 [3,26–3,27] | 6,26 [6,22–6,28] | 10,04 [10,02–10,05] | 13,54 [13,51–13,56] |
| 4096 | 3,53 [3,52–3,54] | 7,15 [7,13–7,16] | 10,40 [10,39–10,42] | 15,69 [15,68–15,71] |

## Lampiran (64–256 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,22 [1,19–1,23] | 1,35 [1,32–1,37] | 1,27 [1,25–1,30] | 1,22 [1,21–1,24] |
| 128 | 1,15 [1,13–1,16] | 1,23 [1,20–1,25] | 1,18 [1,17–1,19] | 1,58 [1,56–1,61] |
| 256 | 1,31 [1,30–1,31] | 1,60 [1,59–1,61] | 1,47 [1,45–1,48] | 1,63 [1,62–1,64] |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


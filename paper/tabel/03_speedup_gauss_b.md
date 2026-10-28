# Speedup CRT-Gauss (b), koefisien diprekomputasi saat pembangkitan kunci terhadap RSA standar (lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=crt_gauss_precomp, kolom speedup, speedup_ci95_lo, speedup_ci95_hi; dibangkitkan oleh bench/make_paper_assets.py -->

Speedup = median waktu RSA standar / median waktu metode pada kunci k-prima dan 30 ciphertext yang sama; kurung siku = CI95 bootstrap (1000 resampling independen, persentil) dalam satu sesi pengukuran.

## Tabel utama (512–4096 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,83 [1,82–1,84] | 2,24 [2,23–2,25] | 2,73 [2,73–2,75] | 2,76 [2,75–2,78] |
| 1024 | 2,55 [2,54–2,55] | 3,99 [3,97–4,00] | 4,73 [4,72–4,73] | 5,62 [5,59–5,70] |
| 2048 | 3,03 [3,02–3,03] | 5,91 [5,90–5,92] | 7,50 [7,49–7,50] | 10,27 [10,26–10,28] |
| 3072 | 3,27 [3,26–3,27] | 6,27 [6,25–6,28] | 10,04 [10,03–10,06] | 13,57 [13,54–13,59] |
| 4096 | 3,53 [3,52–3,54] | 7,15 [7,14–7,16] | 10,40 [10,39–10,41] | 15,70 [15,68–15,71] |

## Lampiran (64–256 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,24 [1,22–1,26] | 1,42 [1,39–1,44] | 1,37 [1,35–1,39] | 1,35 [1,34–1,38] |
| 128 | 1,15 [1,13–1,17] | 1,24 [1,22–1,26] | 1,22 [1,21–1,23] | 1,66 [1,65–1,70] |
| 256 | 1,30 [1,30–1,31] | 1,62 [1,61–1,63] | 1,49 [1,48–1,51] | 1,68 [1,67–1,69] |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


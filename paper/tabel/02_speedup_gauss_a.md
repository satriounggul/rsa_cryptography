# Speedup CRT-Gauss (a), invers modular dihitung saat dekripsi terhadap RSA standar (lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=crt_gauss, kolom speedup, speedup_ci95_lo, speedup_ci95_hi; dibangkitkan oleh bench/make_paper_assets.py -->

Speedup = median waktu RSA standar / median waktu metode pada kunci k-prima dan 30 ciphertext yang sama; kurung siku = CI95 bootstrap (1000 resampling independen, persentil) dalam satu sesi pengukuran.

## Tabel utama (512–4096 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,54 [1,53–1,55] | 1,82 [1,82–1,83] | 2,20 [2,20–2,21] | 2,16 [2,15–2,17] |
| 1024 | 2,26 [2,26–2,27] | 3,39 [3,38–3,39] | 3,92 [3,91–3,92] | 4,54 [4,52–4,57] |
| 2048 | 2,86 [2,85–2,86] | 5,35 [5,34–5,36] | 6,68 [6,68–6,70] | 8,87 [8,86–8,88] |
| 3072 | 3,15 [3,14–3,16] | 5,90 [5,88–5,92] | 9,18 [9,15–9,20] | 12,17 [12,15–12,19] |
| 4096 | 3,44 [3,44–3,45] | 6,86 [6,85–6,87] | 9,82 [9,81–9,84] | 14,46 [14,43–14,47] |

## Lampiran (64–256 bit)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,00 [0,98–1,01] | 1,08 [1,06–1,10] | 1,07 [1,05–1,08] | 1,02 [1,00–1,04] |
| 128 | 0,93 [0,92–0,94] | 0,98 [0,97–1,00] | 1,00 [1,00–1,01] | 1,31 [1,31–1,34] |
| 256 | 1,06 [1,06–1,07] | 1,27 [1,26–1,27] | 1,19 [1,18–1,20] | 1,33 [1,32–1,34] |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


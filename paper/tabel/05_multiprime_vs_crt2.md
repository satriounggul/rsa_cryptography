# Multi-prime CRT (k = 3–5) terhadap CRT dua prima (Garner, lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=crt_garner, kolom speedup_vs_garner_k2(_lo/_hi), speedup_vs_standard_k2(_lo/_hi); dibangkitkan oleh bench/make_paper_assets.py -->

Acuan: waktu median CRT-Garner dengan k = 2 pada bits yang sama (kunci berbeda, ciphertext berbeda; CI95 bootstrap independen). Tabel kedua memakai acuan RSA standar k = 2, yaitu RSA dua-prima tanpa CRT.

## Terhadap CRT-Garner k = 2, 512–4096 bit

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,00 (acuan) | 1,26 [1,25–1,26] | 1,43 [1,42–1,44] | 1,55 [1,55–1,56] |
| 1024 | 1,00 (acuan) | 1,61 [1,61–1,62] | 1,89 [1,89–1,90] | 2,25 [2,24–2,28] |
| 2048 | 1,00 (acuan) | 1,93 [1,93–1,93] | 2,53 [2,52–2,53] | 3,37 [3,36–3,37] |
| 3072 | 1,00 (acuan) | 1,86 [1,85–1,86] | 2,98 [2,98–2,99] | 4,05 [4,04–4,05] |
| 4096 | 1,00 (acuan) | 2,01 [2,00–2,01] | 2,96 [2,95–2,96] | 4,47 [4,46–4,47] |

## Terhadap RSA standar k = 2, 512–4096 bit

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,83 | 2,30 | 2,61 | 2,83 |
| 1024 | 2,55 | 4,10 | 4,82 | 5,73 |
| 2048 | 3,03 | 5,85 | 7,66 | 10,21 |
| 3072 | 3,27 | 6,07 | 9,74 | 13,22 |
| 4096 | 3,53 | 7,08 | 10,45 | 15,77 |

## Terhadap CRT-Garner k = 2, 64–256 bit (lampiran)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,00 (acuan) | 1,18 [1,16–1,20] | 1,02 [1,00–1,04] | 1,03 [1,01–1,05] |
| 128 | 1,00 (acuan) | 1,12 [1,11–1,14] | 1,09 [1,08–1,10] | 1,44 [1,43–1,46] |
| 256 | 1,00 (acuan) | 1,20 [1,19–1,21] | 1,15 [1,13–1,16] | 1,23 [1,23–1,25] |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


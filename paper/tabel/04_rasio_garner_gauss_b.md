# Rasio waktu median terhadap CRT-Gauss (b)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), kolom median_s; dibangkitkan oleh bench/make_paper_assets.py -->

Rasio > 1 berarti metode pembilang lebih lambat daripada CRT-Gauss (b). Rasio dua median (tanpa CI).

## Garner / Gauss (b), 512–4096 bit

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,002 | 1,005 | 1,012 | 1,014 |
| 1024 | 0,999 | 1,001 | 1,004 | 1,007 |
| 2048 | 0,999 | 1,000 | 1,002 | 1,003 |
| 3072 | 1,000 | 1,001 | 1,001 | 1,002 |
| 4096 | 1,000 | 0,999 | 1,000 | 1,000 |

## Gauss (a) / Gauss (b), 512–4096 bit

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 512 | 1,185 | 1,226 | 1,242 | 1,280 |
| 1024 | 1,126 | 1,176 | 1,207 | 1,238 |
| 2048 | 1,060 | 1,105 | 1,122 | 1,157 |
| 3072 | 1,037 | 1,062 | 1,094 | 1,115 |
| 4096 | 1,025 | 1,042 | 1,059 | 1,086 |

## Garner / Gauss (b), 64–256 bit (lampiran)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,019 | 1,050 | 1,075 | 1,110 |
| 128 | 1,002 | 1,011 | 1,035 | 1,055 |
| 256 | 0,997 | 1,011 | 1,015 | 1,030 |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.

## Gauss (a) / Gauss (b), 64–256 bit (lampiran)

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,239 | 1,308 | 1,282 | 1,323 |
| 128 | 1,243 | 1,268 | 1,213 | 1,267 |
| 256 | 1,226 | 1,277 | 1,251 | 1,263 |


# Efisiensi terhadap k² (CRT-Garner, lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=crt_garner, kolom speedup; dibangkitkan oleh bench/make_paper_assets.py -->

Efisiensi = speedup terukur / k². Nilai 100% berarti waktu turun tepat sebesar faktor k² (acuan teoretis untuk k prima berukuran sama).

## Tabel utama (512–4096 bit)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 46% | 25% | 17% | 11% |
| 1024 | 64% | 44% | 29% | 22% |
| 2048 | 76% | 66% | 47% | 41% |
| 3072 | 82% | 70% | 63% | 54% |
| 4096 | 88% | 79% | 65% | 63% |

## Lampiran (64–256 bit)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 64 | 30% | 15% | 8% | 5% |
| 128 | 29% | 14% | 7% | 6% |
| 256 | 33% | 18% | 9% | 7% |

Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per iterasi eksponensiasi modular naik bila modulus melewati 30 bit (results/final/probe_smallint.txt: 0,2099 µs/iterasi pada 30 bit, 0,3100 pada 31 bit, 0,3427 pada 32 bit; kenaikan 48% dan 63% terhadap 30 bit); karena itu kurva speedup pada rentang ini tidak mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.


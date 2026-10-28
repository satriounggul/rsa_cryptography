# Titik silang speedup > 1 (lapisan core)

<!-- sumber: results/final/benchmark_crossover.csv (layer=core); dibangkitkan oleh bench/make_paper_assets.py -->

Titik silang = bits terkecil di grid yang untuk semua bits yang lebih besar punya batas bawah CI95 speedup > 1. "-" berarti tidak ada bits di grid dengan median ≤ 1 (atau CI95 bawah ≤ 1). Grid terkecil 64 bit, jadi "64" berarti tidak ada titik silang di dalam grid (bukan bahwa titik silang tepat di 64 bit).

## Tabel

| metode | k | titik silang (bit) | bits dengan median ≤ 1 | bits dengan CI95 bawah ≤ 1 | speedup min | speedup maks |
|---|---|---|---|---|---|---|
| CRT-Garner | 2 | 64 | - | - | 1,151 | 3,53 |
| CRT-Garner | 3 | 64 | - | - | 1,225 | 7,15 |
| CRT-Garner | 4 | 64 | - | - | 1,175 | 10,40 |
| CRT-Garner | 5 | 64 | - | - | 1,221 | 15,69 |
| CRT-Gauss (a) | 2 | 256 | 128 | 64 128 | 0,928 | 3,44 |
| CRT-Gauss (a) | 3 | 256 | 128 | 128 | 0,977 | 6,86 |
| CRT-Gauss (a) | 4 | 256 | - | 128 | 1,002 | 9,82 |
| CRT-Gauss (a) | 5 | 64 | - | - | 1,024 | 14,46 |
| CRT-Gauss (b) | 2 | 64 | - | - | 1,154 | 3,53 |
| CRT-Gauss (b) | 3 | 64 | - | - | 1,239 | 7,15 |
| CRT-Gauss (b) | 4 | 64 | - | - | 1,216 | 10,40 |
| CRT-Gauss (b) | 5 | 64 | - | - | 1,355 | 15,70 |


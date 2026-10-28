# Waktu median dekripsi RSA standar (ms, lapisan core)

<!-- sumber: results/final/benchmark_summary.csv (layer=core), method=standard, kolom median_s; dibangkitkan oleh bench/make_paper_assets.py -->

Waktu median satu dekripsi (30 putaran terukur per sel).

## Tabel

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


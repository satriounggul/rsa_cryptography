# Overhead instrumentasi (core / lean) dan kestabilan pengukuran

<!-- sumber: results/final/benchmark_summary.csv (layer=core dan lean), kolom median_s dan iqr_s; dibangkitkan oleh bench/make_paper_assets.py -->

Rasio waktu median lapisan core (dengan penghitung operasi dan pencatatan langkah) terhadap lapisan lean (tanpa keduanya). Sebaran antar putaran dalam satu sesi (IQR / median, seluruh 320 sel semua lapisan): median 0,8%, persentil ke-90 3,7%, maksimum 10,0%. Pada lapisan core saja (128 sel): median 0,7%, maksimum 4,5%. Variasi antar sesi dan antar mesin tidak diukur.

## Rasio core / lean, 512–4096 bit

| bits | standar k=2 | standar k=3 | standar k=4 | standar k=5 | Garner k=2 | Garner k=3 | Garner k=4 | Garner k=5 |
|---|---|---|---|---|---|---|---|---|
| 512 | 1,16 | 1,18 | 1,16 | 1,17 | 1,37 | 1,50 | 1,57 | 1,64 |
| 1024 | 1,06 | 1,06 | 1,06 | 1,06 | 1,17 | 1,30 | 1,39 | 1,48 |
| 2048 | 1,02 | 1,02 | 1,02 | 1,02 | 1,06 | 1,13 | 1,18 | 1,23 |
| 3072 | 1,01 | 1,01 | 1,01 | 1,01 | 1,03 | 1,06 | 1,10 | 1,15 |
| 4096 | 1,01 | 1,01 | 1,01 | 1,01 | 1,02 | 1,04 | 1,06 | 1,09 |

## Rasio core / lean, 64–256 bit (lampiran)

| bits | standar k=2 | standar k=3 | standar k=4 | standar k=5 | Garner k=2 | Garner k=3 | Garner k=4 | Garner k=5 |
|---|---|---|---|---|---|---|---|---|
| 64 | 1,65 | 1,69 | 1,69 | 1,70 | 1,98 | 2,71 | 2,90 | 3,12 |
| 128 | 1,55 | 1,53 | 1,59 | 1,52 | 1,72 | 1,92 | 1,95 | 2,73 |
| 256 | 1,36 | 1,36 | 1,39 | 1,36 | 1,55 | 1,74 | 1,67 | 1,92 |


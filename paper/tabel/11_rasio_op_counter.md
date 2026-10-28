# Rasio total operasi (op_counter) RSA standar terhadap metode CRT, lapisan core

<!-- sumber: results/final/benchmark_summary.csv (layer=core), kolom ops_ratio_standard_over_method (rata-rata total_operations standar / metode); dibangkitkan oleh bench/make_paper_assets.py -->

Penghitung operasi mencatat banyaknya operasi aritmetika tanpa memperhitungkan panjang operan, sehingga rasionya mendekati 1: CRT melakukan k eksponensiasi dengan eksponen sekitar k kali lebih pendek, sehingga jumlah langkah kuadrat-dan-kali kira-kira sama dengan satu eksponensiasi penuh (penjelasan analitis; tidak diuji terpisah). Penghitung tidak melihat bahwa operan CRT lebih pendek; hal itu hanya terlihat pada waktu dan model biaya berbobot-bit. Pada bits kecil rasio menyimpang lebih jauh dari 1 (arahnya bergantung pada k); penyebabnya tidak diselidiki (TIDAK TERVERIFIKASI).

## CRT-Garner: rasio total operasi standar / metode

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,118 | 1,000 | 0,878 | 0,878 |
| 128 | 1,037 | 0,990 | 0,987 | 0,941 |
| 256 | 0,957 | 1,008 | 0,991 | 0,944 |
| 512 | 0,990 | 0,993 | 1,018 | 1,002 |
| 1024 | 0,993 | 0,999 | 0,992 | 0,994 |
| 2048 | 0,988 | 1,001 | 0,991 | 0,986 |
| 3072 | 0,991 | 1,002 | 0,994 | 1,010 |
| 4096 | 0,995 | 1,003 | 0,997 | 1,005 |

Rentang seluruh grid (64–4096 bit): 0,878 sampai 1,118; untuk bits ≥ 512: 0,986 sampai 1,018.

## CRT-Gauss (a): rasio total operasi standar / metode

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,088 | 0,980 | 0,866 | 0,870 |
| 128 | 1,025 | 0,980 | 0,979 | 0,935 |
| 256 | 0,952 | 1,003 | 0,988 | 0,942 |
| 512 | 0,987 | 0,991 | 1,016 | 1,001 |
| 1024 | 0,992 | 0,998 | 0,991 | 0,993 |
| 2048 | 0,988 | 1,001 | 0,991 | 0,985 |
| 3072 | 0,991 | 1,002 | 0,994 | 1,009 |
| 4096 | 0,994 | 1,003 | 0,997 | 1,005 |

Rentang seluruh grid (64–4096 bit): 0,866 sampai 1,088; untuk bits ≥ 512: 0,985 sampai 1,016.

## CRT-Gauss (b): rasio total operasi standar / metode

| bits | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|
| 64 | 1,128 | 1,029 | 0,917 | 0,932 |
| 128 | 1,041 | 1,004 | 1,010 | 0,972 |
| 256 | 0,959 | 1,015 | 1,003 | 0,960 |
| 512 | 0,991 | 0,997 | 1,024 | 1,011 |
| 1024 | 0,994 | 1,000 | 0,995 | 0,998 |
| 2048 | 0,989 | 1,002 | 0,992 | 0,988 |
| 3072 | 0,991 | 1,003 | 0,995 | 1,011 |
| 4096 | 0,995 | 1,003 | 0,998 | 1,006 |

Rentang seluruh grid (64–4096 bit): 0,917 sampai 1,128; untuk bits ≥ 512: 0,988 sampai 1,024.


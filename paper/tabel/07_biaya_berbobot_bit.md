# Speedup menurut model biaya berbobot-bit (RSA standar / metode)

<!-- sumber: results/final/benchmark_cost.csv, kolom speedup_literal dan speedup_refined (n_ciphertexts = 10 per sel; kunci dan ciphertext sama dengan benchmark waktu); dibangkitkan oleh bench/make_paper_assets.py -->

Model biaya tidak bergantung pada overhead interpreter. Literal: tiap perkalian, modulo, dan pembagian bernilai bl(a)·bl(b). Refined: perkalian bl(a)·bl(b); modulo/pembagian bernilai (panjang kuosien)·(panjang pembagi). Sel berisi "literal / refined". Pada CRT-Gauss (a) model bench menghitung invers modular saat dekripsi; penghitung di core/ tidak menghitungnya (lihat results/final/costmodel_crosscheck.txt).

## CRT-Garner, 512–4096 bit (literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 3,95 / 3,96 | 8,99 / 9,02 | 16,36 / 16,41 | 25,05 / 25,09 |
| 1024 | 3,97 / 3,98 | 9,01 / 9,03 | 15,89 / 15,90 | 24,84 / 24,85 |
| 2048 | 3,94 / 3,94 | 9,03 / 9,04 | 15,82 / 15,82 | 24,52 / 24,53 |
| 3072 | 3,96 / 3,96 | 9,04 / 9,04 | 15,88 / 15,89 | 25,34 / 25,34 |
| 4096 | 3,97 / 3,98 | 9,04 / 9,05 | 15,95 / 15,95 | 25,17 / 25,18 |

## CRT-Gauss (a), 512–4096 bit (literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 3,76 / 3,94 | 8,46 / 8,91 | 15,29 / 16,09 | 23,11 / 24,36 |
| 1024 | 3,79 / 3,96 | 8,57 / 8,97 | 15,05 / 15,74 | 23,41 / 24,49 |
| 2048 | 3,77 / 3,94 | 8,62 / 9,01 | 15,08 / 15,74 | 23,28 / 24,35 |
| 3072 | 3,78 / 3,96 | 8,63 / 9,02 | 15,13 / 15,84 | 24,11 / 25,22 |
| 4096 | 3,81 / 3,97 | 8,66 / 9,03 | 15,23 / 15,91 | 24,00 / 25,08 |

## CRT-Gauss (b), 512–4096 bit (literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 512 | 3,95 / 3,96 | 8,96 / 9,01 | 16,29 / 16,43 | 24,91 / 25,16 |
| 1024 | 3,97 / 3,98 | 9,00 / 9,02 | 15,86 / 15,90 | 24,77 / 24,88 |
| 2048 | 3,94 / 3,94 | 9,03 / 9,04 | 15,80 / 15,82 | 24,49 / 24,55 |
| 3072 | 3,96 / 3,96 | 9,03 / 9,04 | 15,87 / 15,89 | 25,32 / 25,35 |
| 4096 | 3,97 / 3,97 | 9,04 / 9,04 | 15,94 / 15,95 | 25,16 / 25,18 |

## CRT-Garner, 64–256 bit (lampiran; literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 64 | 4,71 / 4,80 | 9,15 / 9,34 | 13,81 / 14,11 | 21,33 / 21,60 |
| 128 | 4,23 / 4,28 | 9,07 / 9,18 | 16,08 / 16,30 | 23,30 / 23,38 |
| 256 | 3,81 / 3,82 | 9,19 / 9,25 | 16,04 / 16,16 | 23,19 / 23,31 |

## CRT-Gauss (a), 64–256 bit (lampiran; literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 64 | 4,21 / 4,52 | 7,63 / 8,41 | 11,27 / 12,29 | 16,36 / 17,70 |
| 128 | 3,93 / 4,18 | 8,18 / 8,74 | 14,13 / 15,13 | 19,50 / 20,89 |
| 256 | 3,60 / 3,77 | 8,52 / 9,03 | 14,68 / 15,55 | 20,85 / 22,07 |

## CRT-Gauss (b), 64–256 bit (lampiran; literal / refined)

| bits | k=2 (k²=4) | k=3 (k²=9) | k=4 (k²=16) | k=5 (k²=25) |
|---|---|---|---|---|
| 64 | 4,64 / 4,74 | 8,95 / 9,28 | 13,49 / 14,26 | 20,54 / 21,98 |
| 128 | 4,20 / 4,26 | 8,98 / 9,16 | 15,86 / 16,38 | 22,82 / 23,67 |
| 256 | 3,79 / 3,81 | 9,14 / 9,24 | 15,92 / 16,18 | 22,95 / 23,44 |


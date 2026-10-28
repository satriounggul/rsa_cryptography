# Draf keterangan gambar (satu kalimat per gambar)

<!-- Draf untuk disunting mahasiswa. Semua gambar dibangkitkan oleh bench/make_paper_assets.py dari results/final/ (PNG 300 dpi). -->

| Berkas | Draf keterangan | Sumber angka |
|---|---|---|
| `gambar1_waktu_vs_bits.png` | Waktu median dekripsi (ms; sumbu log–log) RSA standar, CRT-Garner, CRT-Gauss (a), dan CRT-Gauss (b) untuk k = 2 sampai 5; kurva CRT-Garner hampir seluruhnya tertutup kurva CRT-Gauss (b) karena waktunya nyaris sama, dan pita menunjukkan kuartil 1–3 dari 30 putaran. | `results/final/benchmark_summary.csv` (layer=core; median_s, q1_s, q3_s) |
| `gambar2_speedup_vs_bits.png` | Speedup terhadap RSA standar (median waktu standar dibagi median waktu metode) beserta CI95 bootstrap dalam satu sesi pengukuran; garis putus-putus menandai speedup = 1, dan pada 4096 bit CRT-Garner mencapai 3,53 kali (k = 2) sampai 15,69 kali (k = 5). | `results/final/benchmark_summary.csv` (layer=core; speedup, speedup_ci95_lo/hi) |
| `gambar3_biaya_vs_k2.png` | Speedup menurut model biaya berbobot-bit (kiri: definisi literal; kanan: refined) terhadap k²; pada 4096 bit CRT-Garner berada sangat dekat dengan garis y = k² (3,97; 9,04; 15,95; 25,17 untuk k = 2 sampai 5 pada biaya literal), sedangkan CRT-Gauss (a) berada sedikit di bawahnya karena invers modular dihitung saat dekripsi. | `results/final/benchmark_cost.csv` (speedup_literal, speedup_refined) |
| `gambar4_efisiensi_vs_k2.png` | Efisiensi waktu CRT-Garner (speedup terukur dibagi k²) menurun seiring k tetapi naik seiring panjang modulus, dari 88% (k = 2) menjadi 63% (k = 5) pada 4096 bit dan dari 46% menjadi 11% pada 512 bit. | `results/final/benchmark_summary.csv` (layer=core, method=crt_garner; speedup) |

Catatan:
- CI95 hanya mencerminkan variasi dalam satu sesi pada satu mesin; variasi antar sesi dan antar mesin tidak diukur.
- Gauss (b) tidak digambar terpisah di Gambar 3 dan 4 karena nilainya hampir identik dengan Garner (lihat `paper/tabel/04_rasio_garner_gauss_b.md` dan `07_biaya_berbobot_bit.md`).
- Untuk bits < 512, kurva tidak mulus; lihat catatan lonjakan biaya pada modulus 30 bit di tabel lampiran (mekanisme TIDAK TERVERIFIKASI).

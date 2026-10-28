# BAB VI — PENUTUP (draf)

<!-- DRAF UNTUK DISUNTING MAHASISWA. Angka berasal dari results/final/ (pengukuran pada kode v1-final); rujukan butir ke BAB_V_draf.md. Tidak ada klaim kebaruan: CRT, rekombinasi Garner, rekombinasi Gauss, dan RSA multi-prima adalah metode yang sudah ada. -->

## A. Kesimpulan

**1. Implementasi (rumusan masalah 1, tujuan 1 dan 2).** Algoritma RSA multi-prima dengan dekripsi CRT, Teorema Fermat Kecil, serta rekombinasi Garner dan Gauss telah diimplementasikan dalam Python standar tanpa pustaka kriptografi, termasuk GCD, Extended Euclid, invers modular, eksponensiasi modular, dan Miller–Rabin. Kebenarannya diperiksa pada beberapa tingkat: 55 tes otomatis lulus pada Python 3.10, 3.13, dan 3.14; 9.600 dari 9.600 hasil dekripsi pada benchmark benar; uji menyeluruh atas 969.502 pasangan (kunci, ciphertext) pada kunci kecil tanpa kegagalan; dan test vector p = (3, 5, 7), m = (2, 3, 2) memberi x = 23 pada ketiga cara (Garner, Gauss, pencarian langsung).
<!-- sumber: BAB_V_draf.md butir A dan B; results/final/uji_versi_python.txt; benchmark_raw_l0125001.csv (kolom correct); audit_exhaustive.txt; contoh_hitung.txt -->

**2. Percepatan terhadap RSA standar dan CRT dua prima (rumusan masalah 2, tujuan 3).** Pada pengukuran satu mesin (Python 3.14.4, lapisan core), CRT-Garner dan CRT-Gauss dengan koefisien diprekomputasi lebih cepat daripada RSA standar pada seluruh 32 kombinasi (ukuran modulus 64–4096 bit, k = 2–5), dengan batas bawah CI95 speedup minimum 1,132 dan 1,133. Pada modulus 4096 bit, CRT-Garner 3,53 kali (k = 2) sampai 15,69 kali (k = 5) lebih cepat; pada 2048 bit 3,03 sampai 10,24 kali. Dibanding CRT dua prima, multi-prima k = 3–5 lebih cepat pada 24 dari 24 sel (1,26 sampai 4,47 kali untuk 512 bit ke atas; 4,47 kali pada 4096 bit, k = 5).
<!-- sumber: results/final/benchmark_crossover.csv (min_speedup, max_speedup); benchmark_summary.csv (speedup, speedup_ci95_lo, speedup_vs_garner_k2); paper/tabel/01_speedup_garner.md, paper/tabel/05_multiprime_vs_crt2.md -->

**3. Pengaruh jumlah prima k (rumusan masalah 3).** Pada modulus yang sama, speedup naik seiring k tetapi selalu di bawah k²: efisiensi (speedup ÷ k²) pada 4096 bit adalah 88%, 79%, 65%, dan 63% untuk k = 2 sampai 5, dan lebih rendah pada modulus lebih kecil (pada 512 bit: 46%, 25%, 17%, 11%). Model biaya berbobot-bit mendekati k² pada 4096 bit (3,97 / 9,04 / 15,95 / 25,17), sehingga selisih antara model dan waktu terukur berasal dari faktor yang tidak diwakili model (dugaan: biaya tetap per operasi pada interpreter dan biaya rekombinasi; tidak diuji terpisah).
<!-- sumber: paper/tabel/06_efisiensi_kuadrat.md; 07_biaya_berbobot_bit.md -->

**4. Garner dan Gauss.** Garner dan Gauss dengan koefisien diprekomputasi praktis tidak berbeda (rasio waktu median 0,999 sampai 1,014 untuk 512 bit ke atas). Gauss yang menghitung invers modular di dalam dekripsi lebih lambat 2,5% sampai 28% pada 512 bit ke atas dan satu-satunya yang memberi speedup di bawah 1, yaitu pada dua sel kecil (128 bit, k = 2 dan 3). Pernyataan bahwa Garner "lebih efisien" daripada Gauss tidak didukung oleh data ini kecuali pada varian yang menghitung invers saat dekripsi.
<!-- sumber: paper/tabel/04_rasio_garner_gauss_b.md; results/final/benchmark_crossover.csv -->

**5. Cakupan hasil.** Angka di atas berlaku untuk implementasi Python ini, satu mesin dan satu sesi pengukuran; angka absolut dan, pada modulus kecil, bentuk kurva dapat berbeda pada mesin, versi Python, atau implementasi lain. Hasil tidak menyatakan bahwa metode ini lebih baik daripada implementasi pustaka kriptografi produksi (tidak dibandingkan).

## B. Saran

1. **Ulangi pengukuran pada lebih dari satu mesin dan sistem operasi** (termasuk Windows dan macOS, yang belum diuji sungguhan) dengan `bench/benchmark.py` dan banding hasilnya dengan `bench/compare_machines.py`, yang juga belum diuji dengan data mesin lain; laporkan beban mesin selama pengukuran.
2. **Pisahkan penyebab selisih antara speedup terukur dan k²**, mis. dengan percobaan yang memvariasikan biaya tetap per operasi atau memakai implementasi bilangan besar lain, serta selidiki lonjakan biaya pada modulus 30 bit yang mekanismenya belum terverifikasi.
3. **Ukur variasi antar kunci dan antar sesi** (banyak kunci per sel, beberapa sesi) agar interval kepercayaan mencerminkan lebih dari variasi dalam satu sesi.
4. **Aspek keamanan.** Implementasi ini RSA dasar tanpa padding dan hanya untuk pembelajaran. Kaji batas aman jumlah dan ukuran prima pada multi-prime RSA dari RFC 8017 [1] dan literatur keamanan [7], serta kerentanan dekripsi CRT terhadap kesalahan perhitungan [8], sebelum mempertimbangkan penggunaan nyata; penggunaan banyak prima mengecilkan tiap faktor sehingga lebih mudah difaktorkan (batas angkanya TIDAK TERVERIFIKASI di sini).
5. **Perluasan.** Bandingkan dengan teknik percepatan lain yang sudah dikenal, mis. varian RSA lain dalam survei [13], reduksi Montgomery [10], [11] (dibahas juga pada [12]), dan paralelisme perhitungan per prima, yang tidak dipakai pada implementasi ini. [Nomor sitasi merujuk `DAFTAR_PUSTAKA_draf.md`.]

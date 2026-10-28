# Daftar Pustaka (draf, diperbarui 28 Oktober 2026)

> **Format sementara: IEEE.** Format yang dikehendaki dosen pengampu **tidak diketahui**; sesuaikan sebelum dikumpulkan.
> Status verifikasi ditulis per entri. Saya tidak mengarang DOI, volume, atau halaman: bagian yang tidak terkonfirmasi ditulis **PERLU DIVERIFIKASI** dan harus Anda cek langsung pada sumbernya (jurnal, penerbit, atau perpustakaan) sebelum dikutip.
> "Terkonfirmasi" berarti data bibliografi (bukan isi) cocok dengan catatan yang muncul pada pencarian web 28 Oktober 2026; saya **tidak membaca isi** artikel jurnal di bawah, kecuali makalah lampiran Anda. Jangan menulis klaim isi dari entri ini sebelum membacanya sendiri.
> Jenis sumber ditulis per entri: **jurnal**, **standar**, **buku**, **buletin teknis**, **makalah mahasiswa**.

## A. Standar dan buku

**[1]** K. Moriarty, Ed., B. Kaliski, J. Jonsson, and A. Rusch, "PKCS #1: RSA Cryptography Specifications Version 2.2," RFC 8017, Internet Engineering Task Force, Nov. 2016. [Online]. Available: https://www.rfc-editor.org/info/rfc8017
- Jenis: standar (RFC informasional). **Status: terkonfirmasi** (pengarang, judul, nomor, bulan dan tahun).
- **Sitasi di:** Bab I (spesifikasi multi-prime RSA), Bab II.D dan II.E (PKCS #1, λ(n)), Bab IV.B.3, Bab V.F. Rujukan ini sudah disebut di makalah (hal. 1, 7, 9, 24) tanpa sitasi. Pernyataan "RFC 8017 mendefinisikan multi-prime RSA" tidak saya verifikasi dari isi RFC; baca bagian definisi kunci privat sebelum mengutip nomor bagian.

**[2]** A. J. Menezes, P. C. van Oorschot, and S. A. Vanstone, *Handbook of Applied Cryptography*. Boca Raton, FL, USA: CRC Press, 1996.
- Jenis: buku. **Status: saya yakin buku ini ada, tetapi tidak dicari ulang.** Nomor bab dan algoritma (Garner, Miller–Rabin, Extended Euclid) **PERLU DIVERIFIKASI**; jangan menulis nomor bab dari ingatan.
- **Sitasi di:** Bab II (Euclid, invers modular, Fermat), Bab II.F (Garner), Bab III.A.5 (Miller–Rabin).

**[3]** [Buku ajar Matematika Diskrit yang dipakai kuliah]: **PERLU DIVERIFIKASI.** Saya tidak tahu buku yang dipakai (mis. K. H. Rosen, *Discrete Mathematics and Its Applications*, bila itu yang dipakai); edisi, penerbit, dan nomor bab diisi dari buku yang Anda pegang.
- **Sitasi di:** Bab II.A (kongruensi), II.B (Fermat), II.C (CRT).

## B. Artikel jurnal

**[4]** R. L. Rivest, A. Shamir, and L. Adleman, "A method for obtaining digital signatures and public-key cryptosystems," *Commun. ACM*, vol. 21, no. 2, pp. 120–126, Feb. 1978.
- Jenis: jurnal. **Status: saya yakin entri ini ada (pengetahuan saya, dicatat pada audit awal); tidak dicari ulang.** Cek volume, nomor, halaman, bulan di ACM Digital Library.
- **Sitasi di:** Bab I (RSA dan dasar keamanannya), Bab II.D.

**[5]** J.-J. Quisquater and C. Couvreur, "Fast decipherment algorithm for RSA public-key cryptosystem," *Electron. Lett.*, vol. 18, no. 21, pp. 905–907, 1982.
- Jenis: jurnal. **Status: sebagian terkonfirmasi.** Volume 18, nomor 21, halaman 905–907 pada *Electronics Letters* menurut catatan IET; tanggal terbit berbeda antar sumber (14 Oktober 1982 vs 27 Agustus 1982), jadi **tulis hanya tahun 1982**; bulan **PERLU DIVERIFIKASI**. DOI tidak saya tulis.
- **Sitasi di:** Bab I dan II.C.2 (asal dekripsi RSA dengan CRT), Bab V.E (pembanding CRT dua prima).

**[6]** H. L. Garner, "The residue number system," *IRE Trans. Electron. Comput.*, vol. EC-8, no. 6, pp. 140–147, Jun. 1959.
- Jenis: jurnal. **Status: sebagian terkonfirmasi, tidak dari sumber primer.** Sejumlah kutipan pada paten dan makalah lain menyebut vol. EC-8, hlm. 140–147, Juni 1959; beberapa menulis nomor 6 (dan ada yang salah menulis "EL-8"). **Nomor terbitan "6" berasal dari kutipan sekunder; PERLU DIVERIFIKASI di IEEE Xplore** sebelum ditulis.
- **Sitasi di:** Bab II.F (rekombinasi Garner).

**[7]** M. J. Hinek, "On the security of multi-prime RSA," *J. Math. Cryptol.*, Jul. 2008, doi: 10.1515/JMC.2008.006.
- Jenis: jurnal. **Status: sebagian terkonfirmasi.** Judul, jurnal, bulan Juli 2008, dan DOI muncul di DOI.org dan DOAJ; nama pengarang M. Jason Hinek muncul pada hasil pencarian. **Volume, nomor, halaman, dan ada tidaknya pengarang lain tidak terkonfirmasi** (PERLU DIVERIFIKASI; tidak saya isi). Abstrak yang terlihat menyebut kompilasi serangan aljabar terhadap multi-prime RSA (faktorisasi, eksponen privat kecil, eksponen CRT kecil, pembukaan sebagian kunci).
- **Sitasi di:** Bab V.F dan Bab VI.B (keterbatasan keamanan: jumlah dan ukuran prima). Jangan menyimpulkan batas aman dari entri ini sebelum membaca isinya.

**[8]** D. Boneh, R. A. DeMillo, and R. J. Lipton, "On the importance of eliminating errors in cryptographic computations," *J. Cryptol.*, vol. 14, no. 2, pp. 101–119, 2001, doi: 10.1007/s001450010016.
- Jenis: jurnal. **Status: sebagian terkonfirmasi.** DBLP mencatat J. Cryptology 14(2): 101–119 (2001) dan pencarian menunjukkan DOI di atas; tanggal 2000 pada satu sumber kemungkinan rilis daring (tidak dinyatakan eksplisit). Versi awalnya adalah makalah konferensi 1997 (LNCS 1233, hlm. 37–51).
- **Relevansi (dari pengetahuan saya; isi tidak dibaca di sesi ini, baca sebelum mengutip):** kerentanan dekripsi RSA berbasis CRT terhadap kesalahan perhitungan (*fault*). Dipakai sebagai rujukan keterbatasan keamanan: implementasi proyek ini tidak memiliki perlindungan terhadap galat dan tidak dimaksudkan untuk penggunaan nyata.
- **Sitasi di:** Bab V.F butir 7, Bab VI.B butir 4.

**[9]** M. O. Rabin, "Probabilistic algorithm for testing primality," *J. Number Theory*, vol. 12, no. 1, pp. 128–138, Feb. 1980.
- Jenis: jurnal. **Status: terkonfirmasi** (catatan Hebrew University dan BibTeX: vol. 12, no. 1, hlm. 128–138, Februari 1980). Isi: algoritma probabilistik uji primalitas yang menjadi dasar Miller–Rabin; hasil "komposit" selalu benar. Kutipan sekunder menyebut batas galat 1/4 per putaran; batas itu dan hubungannya dengan "4⁻⁴⁰" pada makalah **PERLU DIVERIFIKASI** dari isi artikel.
- **Sitasi di:** Bab III.A.5 (Miller–Rabin) dan tabel kompleksitas Bab IV.B.2.

**[10]** P. L. Montgomery, "Modular multiplication without trial division," *Math. Comp.*, vol. 44, no. 170, pp. 519–521, 1985, doi: 10.1090/S0025-5718-1985-0777282-X.
- Jenis: jurnal. **Status: sebagian terkonfirmasi.** Math. Comp. 44 (1985), hlm. 519–521 dan DOI muncul pada catatan AMS; nomor terbitan (170) berasal dari ingatan saya dan **PERLU DIVERIFIKASI**.
- **Relevansi:** teknik percepatan perkalian modular yang bersifat pelengkap (tidak dipakai proyek ini); dibahas pada makalah lampiran [12]. **Sitasi di:** Bab VI.B (saran).

**[11]** Ç. K. Koç, T. Acar, and B. S. Kaliski Jr., "Analyzing and comparing Montgomery multiplication algorithms," *IEEE Micro*, vol. 16, no. 3, pp. 26–33, Jun. 1996.
- Jenis: jurnal/majalah IEEE. **Status: terkonfirmasi** dari catatan Microsoft Research dan daftar publikasi (urutan pengarang pada halaman Microsoft Research berbeda; pakai urutan pada artikel aslinya, **PERLU DIVERIFIKASI**). Isi tidak dibaca. **Sitasi di:** Bab VI.B (saran), bersama [10].

## C. Buletin teknis dan makalah mahasiswa

**[12]** S. Jethefer, "Studi dan perbandingan mengenai metode perkalian Montgomery dan Chinese Remainder Theorem (CRT) dalam mempercepat dekripsi RSA," makalah mahasiswa, Program Studi Teknik Informatika, Sekolah Teknik Elektro dan Informatika, Institut Teknologi Bandung (NIM 13504080), c. 2007.
- Jenis: **makalah mahasiswa (bukan jurnal)**; berkas lampiran Anda "Makalah-001 (1).pdf". Tahun tidak tertera jelas di teks; metadata PDF menunjukkan Januari 2007 (**PERLU DIVERIFIKASI**); daftar pustakanya memuat bahan kuliah (Munir 2006), buku Schneier 1996, dan makalah lain.
- **Yang saya baca dan boleh dipakai:** (i) untuk dekripsi RSA dengan CRT dua prima, makalah menyatakan bahwa kedua eksponensiasi (modulus dan eksponen setengah panjang) memberi faktor percepatan teoretis sekitar 4 (dituliskan "4 − ε"), dan bahwa kombinasi hasil dapat dilakukan dengan satu langkah *Single Radix Conversion* (SRC), yaitu bentuk Gauss pada makalah kita; (ii) makalah menyinggung varian RSA lain (Multi-Prime, Multi-Power, Rebalanced, Batch RSA) tanpa pengukuran sendiri yang dapat saya cocokkan dengan hasil kita.
- **Keterbatasan sumber:** bukan artikel jurnal dan tidak ditinjau sejawat; hasilnya bersifat teoretis dan arsitektur perangkat keras, bukan pengukuran perangkat lunak seperti pada proyek ini. Pakai hanya sebagai rujukan pendukung untuk klaim teoretis k = 2 (≈ 4), dan sebisa mungkin sandarkan klaim pada sumber primer [5], [2], [13]. Jangan mengutip angka percepatan darinya sebagai pembanding hasil kita.
- **Sitasi di:** Bab V.E butir 3 (batas teoretis k² untuk k = 2) dan Bab VI.B.

**[13]** D. Boneh and H. Shacham, "Fast variants of RSA," *CryptoBytes*, vol. 5, no. 1, pp. 1–9, 2002.
- Jenis: **buletin teknis RSA Laboratories (bukan jurnal ditinjau sejawat)**. **Status: terkonfirmasi** (halaman Stanford dan sumber sekunder; survei empat varian RSA yang mempercepat dekripsi, termasuk "MPrime RSA").
- **Sitasi di:** Bab I dan II.E (multi-prime RSA sebagai varian percepatan), Bab VI.B.

## Catatan pemakaian

1. Sitasi di teks memakai nomor dalam kurung siku; susun ulang nomor sesuai urutan kemunculan pertama setelah penempatan final.
2. Pernyataan bahwa CRT-RSA, rekombinasi Garner, rekombinasi Gauss/SRC, dan multi-prime RSA adalah teknik yang **sudah ada** mengikuti [1], [5], [6], [12], [13]; tidak ada klaim kebaruan di draf Bab V dan VI.
3. Entri jurnal yang hanya sebagian terkonfirmasi ([5], [6], [7], [8], [10]) wajib dicek langsung pada sumbernya.
4. Perangkat lunak yang dipakai (bila diminta dosen): Python 3.14.4 untuk pengukuran; Python 3.10.20 dan 3.13.14 untuk uji (lihat `results/final/`).

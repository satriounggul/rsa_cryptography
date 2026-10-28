# Bukti matematis (draf)

> **Draf untuk dipahami dan ditulis ulang oleh mahasiswa; bukan untuk disalin mentah.** Bukti di bawah adalah bukti standar teori bilangan yang ditulis ulang secara ringkas; periksa tiap langkah, pastikan Anda dapat menjelaskannya, dan sesuaikan notasi dengan Bab II makalah. Contoh numerik diperiksa dengan kode (`bench/contoh_hitung.py`, keluarannya di `results/final/contoh_hitung.txt`); buktinya sendiri tidak diverifikasi dengan alat bukti formal. Pernyataan analitis tentang biaya (bagian 7) bukan hasil pengukuran.

Notasi: a ≡ b (mod m) berarti m | (a − b); semua pᵢ adalah prima berbeda, n = p₁p₂…pₖ, φ(n) = ∏(pᵢ − 1), λ(n) = lcm(pᵢ − 1).

---

## 1. Invers modular dan koefisien Bézout

**Teorema 1.** Untuk bilangan bulat a dan m > 0, ada x dengan ax ≡ 1 (mod m) **jika dan hanya jika** gcd(a, m) = 1. Invers tunggal modulo m.

*Bukti.* (⇒) Jika ax ≡ 1 (mod m), maka ax − 1 = qm untuk suatu q, sehingga ax − qm = 1. Setiap pembagi persekutuan a dan m membagi ax − qm = 1, jadi gcd(a, m) = 1.
(⇐) *Identitas Bézout:* untuk a, m bilangan bulat ada s, t dengan as + mt = gcd(a, m). Bukti: himpunan S = {as + mt > 0} tidak kosong (mis. a² + m² > 0 bila a ≠ 0), ambil elemen terkecil g = as₀ + mt₀. Bagi a dengan g: a = qg + r, 0 ≤ r < g. Maka r = a − qg = a(1 − qs₀) + m(−qt₀) adalah kombinasi yang sama jenisnya; karena g terkecil dan r < g, haruslah r = 0, jadi g | a. Dengan cara sama g | m. Sebaliknya setiap pembagi persekutuan a dan m membagi g. Maka g = gcd(a, m). Jika gcd(a, m) = 1 maka as₀ + mt₀ = 1, yaitu as₀ ≡ 1 (mod m); x = s₀ mod m.
*Ketunggalan:* jika ax ≡ ax′ ≡ 1, maka x ≡ x(ax′) = (xa)x′ ≡ x′ (mod m). ∎

**Algoritma.** Extended Euclid memeriksa invarian old_r = a·old_s + m·old_t dan r = a·s + m·t pada tiap iterasi (benar pada awal: (old_r, old_s, old_t) = (a, 1, 0) dan (r, s, t) = (m, 0, 1), dan tiap langkah mengurangkan q kali baris kedua dari baris pertama). Saat r = 0, old_r = gcd(a, m) = a·old_s + m·old_t; lalu x = old_s mod m. Pseudocode `MODINV` makalah (hal. 14) sesuai: error jika gcd ≠ 1.

## 2. Teorema Fermat Kecil

**Teorema 2.** Jika p prima dan p ∤ a, maka a^(p−1) ≡ 1 (mod p). Untuk semua a, aᵖ ≡ a (mod p).

*Bukti.* Pandang himpunan R = {1, 2, …, p − 1} dan R′ = {a·1, a·2, …, a·(p − 1)} modulo p. Karena gcd(a, p) = 1, a punya invers modulo p (Teorema 1), jadi a·r ≡ a·s (mod p) mengakibatkan r ≡ s; maka unsur-unsur R′ berbeda modulo p dan tak ada yang ≡ 0 (karena p prima dan p ∤ a, p ∤ r). Jadi R′ adalah permutasi dari R modulo p. Mengalikan semua unsur: a^(p−1)·(p − 1)! ≡ (p − 1)! (mod p). Karena (p − 1)! tidak habis dibagi p (hasil kali bilangan yang tidak habis dibagi prima p), ia punya invers modulo p; kalikan kedua sisi dengan inversnya untuk memperoleh a^(p−1) ≡ 1. Bentuk aᵖ ≡ a: jika p ∤ a kalikan a^(p−1) ≡ 1 dengan a; jika p | a kedua sisi ≡ 0. ∎

**Akibat 2a (reduksi eksponen).** Jika p prima, dᵢ ≥ 1, dan d ≡ dᵢ (mod p − 1), maka c^d ≡ c^dᵢ (mod p) untuk **semua** c.

*Bukti.* Tulis d = q(p − 1) + dᵢ dengan q ≥ 0 (karena d ≥ dᵢ bila dᵢ = d mod (p − 1) atau dᵢ = p − 1 saat sisa 0). Jika p ∤ c: c^d = (c^(p−1))^q · c^dᵢ ≡ c^dᵢ (Teorema 2). Jika p | c: c ≡ 0, dan karena d ≥ 1 dan dᵢ ≥ 1 kedua sisi ≡ 0. ∎
Syarat dᵢ ≥ 1 mengapa kode mengganti dᵢ = 0 menjadi p − 1 (`keygen.py`): dengan dᵢ = 0, c⁰ = 1 ≢ 0 = c^d bila p | c.

## 3. CRT: keberadaan dan ketunggalan

**Teorema 3 (CRT).** Jika n₁, …, nₖ saling prima berpasangan dan N = n₁⋯nₖ, maka untuk sebarang a₁, …, aₖ sistem x ≡ aᵢ (mod nᵢ) mempunyai solusi, dan solusinya tunggal modulo N.

*Bukti.* *Keberadaan.* Untuk tiap i, Nᵢ = N/nᵢ relatif prima terhadap nᵢ (semua faktor nⱼ, j ≠ i, saling prima dengan nᵢ), jadi ada Mᵢ dengan NᵢMᵢ ≡ 1 (mod nᵢ) (Teorema 1). Definisikan x = Σⱼ aⱼNⱼMⱼ. Modulo nᵢ: untuk j ≠ i, nᵢ | Nⱼ sehingga suku ke-j ≡ 0; suku ke-i ≡ aᵢ·1. Jadi x ≡ aᵢ (mod nᵢ).
*Ketunggalan.* Jika x, y keduanya solusi, nᵢ | (x − y) untuk semua i; karena nᵢ saling prima berpasangan, hasil kalinya N | (x − y) (induksi: bila gcd(u, v) = 1 dan u | z, v | z maka uv | z, sebab z = ub, v | ub, dan v relatif prima terhadap u sehingga v | b). Jadi x ≡ y (mod N). ∎

Konstruksi pada bukti keberadaan adalah **rumus Gauss / SRC**: x ≡ Σ aᵢNᵢMᵢ (mod N), yang dipakai pada metode Gauss di makalah (hal. 6).

## 4. Kebenaran dekripsi RSA multi-prima (kasus pᵢ | m termasuk)

**Teorema 4.** Misalkan e·d ≡ 1 (mod (pᵢ − 1)) untuk setiap i (mis. d = e⁻¹ mod φ(n), atau mod λ(n)). Maka untuk setiap 0 ≤ m < n: m^(ed) ≡ m (mod n).

*Bukti.* Karena (pᵢ − 1) | (ed − 1) dan ed − 1 ≥ 0 (e, d ≥ 1), tulis ed = 1 + t(pᵢ − 1) dengan t ≥ 0. Jika pᵢ ∤ m: m^(ed) = m·(m^(pᵢ−1))^t ≡ m·1 = m (mod pᵢ) (Teorema 2). Jika pᵢ | m: kedua sisi ≡ 0 (mod pᵢ) karena ed ≥ 1. Jadi pᵢ | (m^(ed) − m) untuk semua i; karena pᵢ berbeda (saling prima), n | (m^(ed) − m) (lihat ketunggalan pada Teorema 3). Karena 0 ≤ m < n dan 0 ≤ m^(ed) mod n < n, keduanya sama. ∎

**Mengapa φ dan λ sama baiknya.** (pᵢ − 1) | λ(n) | φ(n). Jika e·d ≡ 1 (mod φ(n)), maka juga (mod λ(n)) dan (mod (pᵢ − 1)); jadi syarat Teorema 4 terpenuhi. Eksponen per prima: dφ dan dλ keduanya memenuhi e·d ≡ 1 (mod (pᵢ − 1)); karena e punya invers tunggal modulo (pᵢ − 1) (Teorema 1; e relatif prima terhadap pᵢ − 1 oleh pilihan e), dφ ≡ dλ ≡ e⁻¹ (mod (pᵢ − 1)). Jadi **dᵢ = d mod (pᵢ − 1) sama untuk keduanya** (termasuk penyesuaian 0 → pᵢ − 1). Perbedaan hanya panjang d: dλ < λ(n) sedangkan dφ < φ(n) dan λ(n) | φ(n), sehingga dφ dapat jauh lebih panjang. Pengamatan numerik: `results/final/audit_d_phi_lambda.txt`.

**Dekripsi CRT benar.** Dari Akibat 2a dengan dᵢ ≡ d (mod pᵢ − 1) dan dᵢ ≥ 1: mᵢ = cᵢ^dᵢ mod pᵢ ≡ c^d ≡ m^(ed) ≡ m (mod pᵢ) (c ≡ m^e, jadi c^d ≡ m^(ed)). Jadi mᵢ = m mod pᵢ untuk setiap i. Rekombinasi CRT (Teorema 3) dari (m mod pᵢ) menghasilkan x ≡ m (mod n) yang tunggal; karena 0 ≤ m < n, x = m. ∎ Pemeriksaan numerik semua c ∈ [0, n) pada kunci kecil, termasuk kelipatan pᵢ: `results/final/audit_exhaustive.txt`.

## 5. Rekombinasi Garner

Definisi: Pᵢ = p₁⋯pᵢ₋₁ (P₁ = 1 tidak dipakai), tᵢ = Pᵢ⁻¹ mod pᵢ (ada: Pᵢ relatif prima terhadap pᵢ). Algoritma: x₁ = m₁; untuk i = 2..k: uᵢ = ((mᵢ − xᵢ₋₁)·tᵢ) mod pᵢ, xᵢ = xᵢ₋₁ + uᵢ·Pᵢ.

**Teorema 5.** Untuk tiap i, 0 ≤ xᵢ < p₁⋯pᵢ dan xᵢ ≡ mⱼ (mod pⱼ) untuk semua j ≤ i. Jadi xₖ adalah solusi tunggal CRT di [0, n) dan tidak perlu reduksi modulo n.

*Bukti (induksi).* Untuk i = 1: x₁ = m₁ ∈ [0, p₁). Langkah i: Pᵢ habis dibagi pⱼ untuk j < i, jadi xᵢ ≡ xᵢ₋₁ ≡ mⱼ (mod pⱼ) untuk j < i. Modulo pᵢ: xᵢ = xᵢ₋₁ + uᵢPᵢ ≡ xᵢ₋₁ + (mᵢ − xᵢ₋₁)·tᵢ·Pᵢ ≡ xᵢ₋₁ + (mᵢ − xᵢ₋₁) = mᵢ, karena tᵢPᵢ ≡ 1 (mod pᵢ). Batas: xᵢ₋₁ ≤ Pᵢ − 1 dan uᵢ ≤ pᵢ − 1, jadi xᵢ ≤ Pᵢ − 1 + (pᵢ − 1)Pᵢ = Pᵢpᵢ − 1 < Pᵢpᵢ = p₁⋯pᵢ. Ketunggalan di [0, n): Teorema 3. ∎

**Contoh (p = 3, 5, 7; m = 2, 3, 2).** t₂ = 2, t₃ = 1; x₂ = 2 + 2·3 = 8; u₃ = ((2 − 8)·1) mod 7 = 1, x₃ = 8 + 1·15 = 23 (`results/final/contoh_hitung.txt`). Kode menyertakan pemeriksaan defensif `if x >= n: x %= n`, yang menurut teorema ini tidak pernah aktif.

## 6. Rekombinasi Gauss (dua varian)

Dari rumus Teorema 3: x ≡ Σ mᵢNᵢMᵢ (mod n), Nᵢ = n/pᵢ, Mᵢ = Nᵢ⁻¹ mod pᵢ.

- **Varian (a)** (kode: `use_precomputed=False`): hitung Nᵢ = n div pᵢ, Mᵢ = modinv(Nᵢ mod pᵢ, pᵢ) di dalam dekripsi; suku tᵢ = ((mᵢMᵢ) mod pᵢ)·Nᵢ. Ekuivalen karena (mᵢMᵢ mod pᵢ)·Nᵢ ≡ mᵢMᵢNᵢ (mod n): kedua sisi ≡ 0 modulo pⱼ (j ≠ i, karena pⱼ | Nᵢ), dan modulo pᵢ keduanya ≡ mᵢMᵢNᵢ. Jumlahnya < k·n, maka reduksi mod n diperlukan.
- **Varian (b)** (kode: bawaan, koefisien di kunci): Cᵢ = (NᵢMᵢ) mod n dihitung sekali; x = (Σ mᵢCᵢ) mod n. Benar karena Cᵢ ≡ NᵢMᵢ (mod n), jadi Σ mᵢCᵢ ≡ Σ mᵢNᵢMᵢ (mod n).

Kedua varian menghitung nilai yang sama; perbedaannya hanya kapan invers modular dihitung. Contoh numerik: `results/final/contoh_hitung.txt`.

## 7. Analisis biaya (analitis; bukan pengukuran)

Model: perkalian dua bilangan L bit berbiaya O(L²) (algoritma sekolah) dan reduksi modulo hasil O(L²). Dengan B = log₂ n.

| Operasi | Biaya (operasi bit) | Catatan |
|---|---|---|
| `gcd(a, b)` / `extended_gcd` | O(log² min(a, b)) | Banyak iterasi O(log min); total biaya bit O(log²) karena jumlah (panjang kuosien × panjang pembagi) berurutan berjumlah O(L²). Tabel makalah (hal. 23) menulis banyak iterasi, O(log min(a, b)). |
| `modinv(a, m)` | O(log² m) | Extended Euclid; makalah menulis O(log m) (jumlah iterasi). |
| `modexp(b, e, m)` | O(log e · log² m) | e bit-eksponen; tiap bit ≤ 2 perkalian dan reduksi O(log² m). |
| `miller_rabin(n, rounds)` | **O(rounds · log³ n)** | Tiap putaran satu `modexp` dengan eksponen d < n (log e = O(log n)) dan modulus n: O(log n · log² n). Tabel makalah menulis O(rounds · log² n), yang kurang satu faktor log n; koreksi (KOREKSI_MAKALAH butir 8). |
| RSA standar, c^d mod n | O(B³) | e = d dengan B bit, modulus B bit. |
| k eksponensiasi CRT | k · O((B/k)·(B/k)²) = **O(B³/k²)** | Prima ≈ B/k bit, dᵢ < pᵢ − 1 sehingga ≈ B/k bit. Rasio terhadap standar: k². |
| Rekombinasi Garner | O(B²) | k − 1 langkah; tiap langkah: mod pᵢ atas bilangan ≤ B bit: O(B·B/k); kali tᵢ: O((B/k)²); uᵢ·Pᵢ: O((B/k)·B). Jumlah k langkah O(B²). |
| Rekombinasi Gauss (b) | O(B²) | k perkalian mᵢ·Cᵢ ((B/k) × B bit) = k·O(B²/k) = O(B²); satu reduksi mod n atas ≈ B + log k bit. |
| Rekombinasi Gauss (a) | O(B²) | Sama, ditambah k kali Nᵢ = n div pᵢ (O(B²/k) tiap), `modinv` (O((B/k)²) tiap) dan mod; total O(B²). |
| Total dekripsi CRT | O(B³/k² + B²) | Eksponensiasi mendominasi bila B³/k² ≫ B², yaitu B ≫ k² (konstanta diabaikan). |

**Kesimpulan analitis.** Model ini memberi batas atas percepatan sekitar k² (untuk B besar dibanding k²), yaitu klaim "k² kali" pada hal. 1 makalah **sebagai batas teoretis**, bukan hasil pengukuran; pengukuran pada Bab V menunjukkan 63–88% dari k² pada 4096 bit (`paper/tabel/06_efisiensi_kuadrat.md`). Kedua rekombinasi (Garner, Gauss) sama-sama O(B²) pada model ini, sehingga model tidak memprediksi keunggulan asimtotik salah satunya; keunggulan harus ditunjukkan dengan pengukuran (`paper/tabel/04_rasio_garner_gauss_b.md`: praktis sama bila koefisien diprekomputasi). Prekomputasi koefisien (tᵢ atau Cᵢ) satu kali saat pembangkitan kunci tidak dihitung dalam biaya dekripsi.
*Keterbatasan model:* perkalian bilangan besar CPython tidak persis O(L²) untuk operan besar (algoritma yang lebih cepat dipakai di atas ambang tertentu; **ambang dan penerapannya PERLU DIVERIFIKASI** pada dokumentasi atau sumber CPython) dan biaya tetap per operasi pada interpreter tidak diwakili; keduanya membuat percepatan terukur berbeda dari model.

---

### Pemeriksaan mandiri yang disarankan sebelum menulis ulang

1. Tunjukkan Teorema 1 dengan contoh: 7⁻¹ mod 1920 = 823 (7·823 = 5761 = 3·1920 + 1) — sesuai `results/final/contoh_hitung.txt`.
2. Jalankan Teorema 5 tangan untuk p = (11, 13, 17), m = (2, 12, 10): hasil x = 1234 (`contoh_hitung.txt`, bagian B).
3. Kasus pᵢ | m: n = 105, e = 5, d = 29, m = 21 (3 | 21 dan 7 | 21). Kode memberi c = 21, cᵢ = (0, 1, 0), mᵢ = (0, 1, 0), dan keempat jalur dekripsi memulihkan 21 (`results/final/contoh_hitung.txt`, bagian C). Jelaskan sendiri mengapa dᵢ ≥ 1 penting pada kasus ini (Akibat 2a).

#!/usr/bin/env python3
"""
Membandingkan benchmark FINAL (results/final/) dengan BASELINE (results/): selisih relatif speedup lapisan core untuk
CRT-Garner, CRT-Gauss (a), dan CRT-Gauss (b) per (bits, k). Menandai sel yang berubah > 10% dan melaporkan INDIKATOR
terukur untuk tiap dugaan penyebab. Indikator bukan bukti penyebab.

Pemakaian: python3 bench/compare_baseline.py [--out results/final/perbandingan_baseline.md]
Syarat: results/benchmark_summary.csv (baseline), results/final/benchmark_summary.csv (final);
opsional (untuk indikator kunci): results/benchmark_keys.json dan results/final/benchmark_keys_<host>.json (tidak di-commit).
"""
import argparse
import csv
import glob
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BITS = [64, 128, 256, 512, 1024, 2048, 3072, 4096]
KS = [2, 3, 4, 5]
METHODS = [("crt_garner", "CRT-Garner"), ("crt_gauss", "CRT-Gauss (a), invers saat dekripsi"),
           ("crt_gauss_precomp", "CRT-Gauss (b), koefisien prekomputasi")]
THRESH = 10.0


def load_summary(path):
    with open(path, encoding="utf-8") as fh:
        return {(r["layer"], r["method"], int(r["bits_target"]), int(r["k"])): r for r in csv.DictReader(fh)}


def bl(x):
    return abs(int(x)).bit_length()


def key_work(stored):
    """Indikator beban aritmetika dari kunci: W_std = bl(d)*bl(n)^2 ; W_crt = sum bl(d_i)*bl(p_i)^2 (per (bits,k))."""
    out = {}
    for name, rec in stored.items():
        b, k = map(int, name.split("-"))
        p = rec["key"]["private_key"]
        w_std = bl(p["d"]) * bl(p["n"]) ** 2
        w_crt = sum(bl(di) * bl(pi) ** 2 for di, pi in zip(p["d_primes"], p["primes"]))
        out[(b, k)] = dict(w_std=w_std, w_crt=w_crt, d_bits=bl(p["d"]), prime_bits=[bl(x) for x in p["primes"]])
    return out


def md_table(header, rows):
    out = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        out += "| " + " | ".join(str(x) for x in r) + " |\n"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.path.join(ROOT, "results"))
    ap.add_argument("--final", default=os.path.join(ROOT, "results", "final"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "final", "perbandingan_baseline.md"))
    a = ap.parse_args()

    base = load_summary(os.path.join(a.base, "benchmark_summary.csv"))
    fin = load_summary(os.path.join(a.final, "benchmark_summary.csv"))
    kb = os.path.join(a.base, "benchmark_keys.json")
    kf = (glob.glob(os.path.join(a.final, "benchmark_keys_*.json")) or [None])[0]
    work_b = work_f = None
    if os.path.exists(kb) and kf:
        with open(kb, encoding="utf-8") as fh:
            work_b = key_work(json.load(fh))
        with open(kf, encoding="utf-8") as fh:
            work_f = key_work(json.load(fh))

    def g(tab, layer, method, b, k, col):
        return float(tab[(layer, method, b, k)][col])

    L = ["# Perbandingan hasil final dengan baseline", "",
         "Sumber: `results/benchmark_summary.csv` (baseline) dan `results/final/benchmark_summary.csv` (final). Lapisan **core**.",
         "Selisih Δ% = (speedup final / speedup baseline - 1) × 100. Sel dengan |Δ| > 10% ditandai ⚠. "
         "\"CI tumpang tindih\" = CI95 bootstrap kedua sesi beririsan (kedua CI hanya mencerminkan variasi dalam satu sesi).", "",
         "Perbedaan yang diketahui antara kedua sesi (bukan penyebab terbukti):", "",
         "1. **Kode inti**: baseline = commit `e44081f` (sebelum Fase 4); final = `v1-final` (`58aafdd`). Fase 4 menambah argumen operan pada pemanggilan `OperationCounter` "
         "(overhead terukur +3% sampai +8% pada 64-256 bit, ≤ 0,5% pada ≥ 2048 bit; lihat REVIEW.md §6.2).",
         "2. **Varian (b)**: baseline = salinan `bench/variants.py`; final = default `core/rsa.py` (koefisien dari kunci).",
         "3. **Kunci**: baseline = hasil regenerasi `generate_keys` lama sampai n tepat; final = keygen baru (n tepat secara konstruktif, prima terakhir dipilih dari interval). "
         "Kunci berbeda di kedua sesi (satu kunci per sel).",
         "4. **Sesi dan mesin**: host sama, CPU 43 dipatok pada keduanya, tetapi host dibagi dengan tenant lain (load average ≈ 9,2-10,3 pada keduanya), sesi berbeda.", ""]

    flagged = []
    for method, title in METHODS:
        rows = []
        for b in BITS:
            for k in KS:
                sb, sf = g(base, "core", method, b, k, "speedup"), g(fin, "core", method, b, k, "speedup")
                lb, hb = g(base, "core", method, b, k, "speedup_ci95_lo"), g(base, "core", method, b, k, "speedup_ci95_hi")
                lf, hf = g(fin, "core", method, b, k, "speedup_ci95_lo"), g(fin, "core", method, b, k, "speedup_ci95_hi")
                d = (sf / sb - 1) * 100
                overlap = not (hb < lf or hf < lb)
                flag = "⚠" if abs(d) > THRESH else ""
                if flag:
                    flagged.append((method, b, k, sb, sf, d, overlap))
                rows.append([b, k, f"{sb:.2f} [{lb:.2f}-{hb:.2f}]", f"{sf:.2f} [{lf:.2f}-{hf:.2f}]", f"{d:+.1f}%", flag,
                             "ya" if overlap else "tidak"])
        L += [f"## {title}", "", md_table(["bits", "k", "speedup baseline [CI95]", "speedup final [CI95]", "Δ%", "tanda", "CI tumpang tindih"], rows), ""]
        ds = [abs((g(fin, "core", method, b, k, "speedup") / g(base, "core", method, b, k, "speedup") - 1) * 100) for b in BITS for k in KS]
        L.append(f"Ringkasan: median |Δ| = {st.median(ds):.1f}%, maksimum = {max(ds):.1f}%, sel dengan |Δ| > {THRESH:.0f}%: "
                 f"{sum(1 for x in ds if x > THRESH)} dari {len(ds)}.\n")

    # ------------------------------------------------ indikator
    L += ["## Indikator untuk dugaan penyebab", "",
          "Semua indikator di bawah **terukur**, tetapi hanya menunjukkan apakah suatu dugaan *konsisten* dengan data; tidak ada yang membuktikan penyebab.", ""]

    # (A) geseran mesin: waktu standar final / baseline
    r_std = [g(fin, "core", "standard", b, k, "median_s") / g(base, "core", "standard", b, k, "median_s") for b in BITS for k in KS]
    r_std_big = [g(fin, "core", "standard", b, k, "median_s") / g(base, "core", "standard", b, k, "median_s") for b in BITS for k in KS if b >= 1024]
    L += ["### (A) Geseran kecepatan mesin atau sesi: rasio waktu median RSA standar final/baseline (core)", "",
          f"Semua 32 sel: median {st.median(r_std):.3f}, rentang {min(r_std):.3f} sampai {max(r_std):.3f}. "
          f"Hanya bits ≥ 1024: median {st.median(r_std_big):.3f}, rentang {min(r_std_big):.3f} sampai {max(r_std_big):.3f}. "
          "Bila mesin berubah kecepatan, rasio ini menyimpang dari 1 untuk semua metode sekaligus; speedup (rasio dua metode) hanya terpengaruh bila pergeseran tidak sama antar metode.", ""]
    rows = [[b] + [f"{g(fin, 'core', 'standard', b, k, 'median_s') / g(base, 'core', 'standard', b, k, 'median_s'):.3f}" for k in KS] for b in BITS]
    L += [md_table(["bits"] + [f"k={k}" for k in KS], rows), ""]

    # (B) kunci
    if work_b and work_f:
        L += ["### (B) Perbedaan kunci: prediksi perubahan speedup dari beban aritmetika kunci", "",
              "Indikator beban: W_std = bl(d)·bl(n)² dan W_CRT = Σ bl(d_i)·bl(p_i)². Speedup prediksi = W_std/W_CRT. "
              "Kolom \"prediksi Δ%\" = perubahan speedup prediksi antara kunci baseline dan kunci final. "
              "Jika prediksi Δ% kecil, perbedaan kunci tidak cukup menjelaskan Δ% teramati (Garner). Model ini mengabaikan overhead interpreter.", ""]
        rows = []
        for b in BITS:
            for k in KS:
                pb = work_b[(b, k)]["w_std"] / work_b[(b, k)]["w_crt"]
                pf = work_f[(b, k)]["w_std"] / work_f[(b, k)]["w_crt"]
                obs = (g(fin, "core", "crt_garner", b, k, "speedup") / g(base, "core", "crt_garner", b, k, "speedup") - 1) * 100
                rows.append([b, k, f"{work_b[(b, k)]['d_bits']}/{work_f[(b, k)]['d_bits']}", f"{pb:.2f}", f"{pf:.2f}", f"{(pf / pb - 1) * 100:+.1f}%", f"{obs:+.1f}%"])
        L += [md_table(["bits", "k", "bit d (base/final)", "W_std/W_CRT baseline", "W_std/W_CRT final", "prediksi Δ%", "Δ% teramati (Garner)"], rows), ""]
    else:
        L += ["### (B) Perbedaan kunci", "", "Berkas kunci tidak tersedia; indikator dilewati.", ""]

    # (C) lokasi varian (b)
    L += ["### (C) Lokasi varian (b): rasio waktu median Gauss (b)/Garner (core), baseline (salinan bench) vs final (default core)", ""]
    rows = []
    for b in BITS:
        row = [b]
        for k in KS:
            rb = g(base, "core", "crt_gauss_precomp", b, k, "median_s") / g(base, "core", "crt_garner", b, k, "median_s")
            rf = g(fin, "core", "crt_gauss_precomp", b, k, "median_s") / g(fin, "core", "crt_garner", b, k, "median_s")
            row.append(f"{rb:.3f} → {rf:.3f}")
        rows.append(row)
    L += [md_table(["bits"] + [f"k={k}" for k in KS], rows), ""]

    # (E) overhead kode inti: rasio waktu final/baseline per metode, median atas k, per bits
    L += ["### (E) Perubahan kode inti (overhead penghitung Fase 4): rasio waktu median final/baseline per metode (core), median atas k", "",
          "Pengukuran terpisah di Fase 4 (lama vs baru, berselang-seling) memberi +3% sampai +8% pada 64-256 bit, ≤ 3% pada 1024 bit, 0,3% sampai 0,5% pada 2048 bit "
          "(REVIEW.md §6.2). Bandingkan dengan rasio di bawah (sesi berbeda, kunci berbeda).", ""]
    rows = []
    for b in BITS:
        row = [b]
        for m in ("standard", "crt_garner", "crt_gauss", "crt_gauss_precomp"):
            row.append(f"{st.median(g(fin, 'core', m, b, k, 'median_s') / g(base, 'core', m, b, k, 'median_s') for k in KS):.3f}")
        rows.append(row)
    L += [md_table(["bits", "standar", "Garner", "Gauss (a)", "Gauss (b)"], rows), ""]

    # (D) noise
    L += ["### (D) Noise: IQR/median pada sel yang ditandai ⚠ (baseline dan final)", ""]
    if flagged:
        rows = []
        for method, b, k, sb, sf, d, overlap in flagged:
            nb = g(base, "core", method, b, k, "iqr_s") / g(base, "core", method, b, k, "median_s") * 100
            nf = g(fin, "core", method, b, k, "iqr_s") / g(fin, "core", method, b, k, "median_s") * 100
            rows.append([method, b, k, f"{sb:.2f}", f"{sf:.2f}", f"{d:+.1f}%", f"{nb:.1f}%", f"{nf:.1f}%", "ya" if overlap else "tidak"])
        L += [md_table(["metode", "bits", "k", "baseline", "final", "Δ%", "IQR/median baseline", "IQR/median final", "CI tumpang tindih"], rows), ""]
    else:
        L += ["Tidak ada sel ditandai.", ""]

    if flagged:
        L += ["### Pembacaan otomatis per sel ditandai (dugaan, bukan penyebab terbukti)", ""]
        for method, b, k, sb, sf, d, overlap in flagged:
            nb = g(base, "core", method, b, k, "iqr_s") / g(base, "core", method, b, k, "median_s") * 100
            nf = g(fin, "core", method, b, k, "iqr_s") / g(fin, "core", method, b, k, "median_s") * 100
            parts = [f"**{method}, {b} bit, k = {k}**: {sb:.2f} → {sf:.2f} ({d:+.1f}%)."]
            if work_b and work_f:
                pb = work_b[(b, k)]["w_std"] / work_b[(b, k)]["w_crt"]
                pf = work_f[(b, k)]["w_std"] / work_f[(b, k)]["w_crt"]
                pred = (pf / pb - 1) * 100
                if (pred > 0) == (d > 0) and abs(pred) >= 0.5 * abs(d):
                    parts.append(f"Indikator kunci (B) **konsisten**: prediksi {pred:+.1f}% vs teramati {d:+.1f}% (dugaan: kunci acak berbeda, panjang d_i berbeda).")
                else:
                    parts.append(f"Indikator kunci (B) **tidak menjelaskan**: prediksi {pred:+.1f}% vs teramati {d:+.1f}%.")
            if max(nb, nf) < 5:
                parts.append(f"Noise dalam-sesi kecil (IQR/median {nb:.1f}% dan {nf:.1f}%), jadi selisih bukan noise dalam-sesi; variasi antar-sesi tidak terukur di sini.")
            else:
                parts.append(f"Noise dalam-sesi tidak kecil (IQR/median {nb:.1f}% dan {nf:.1f}%).")
            if method == "crt_gauss_precomp":
                parts.append("Varian (b) berbeda lokasi (salinan bench vs default core) sehingga perbedaan kode juga mungkin berperan.")
            L += ["- " + " ".join(parts)]
        L += [""]

    L += ["## Catatan penafsiran", "",
          "- Tanda ⚠ hanya berarti |Δ| > 10%; arah dan besar selisih dilaporkan apa adanya.",
          "- Dugaan penyebab selisih (perbedaan keygen, lokasi varian b, overhead penghitung hasil Fase 4, sesi/mesin, noise) **tidak dipisahkan secara eksperimen**; "
          "pemisahan memerlukan percobaan terkontrol tambahan (mis. kunci baseline pada kode final) yang belum dilakukan.", ""]
    text = "\n".join(L) + "\n"
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"ditulis: {a.out}")
    print(f"sel ditandai (|Δ|>{THRESH:.0f}%): {len(flagged)}")
    for method, b, k, sb, sf, d, overlap in flagged:
        print(f"  {method:18s} bits={b:4d} k={k}: {sb:6.2f} -> {sf:6.2f} ({d:+.1f}%) CI tumpang tindih={overlap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

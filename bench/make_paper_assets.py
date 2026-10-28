#!/usr/bin/env python3
"""
Membangun tabel siap-tempel (paper/tabel/*.md, *.csv) dan gambar makalah (paper/gambar/*.png, 300 dpi)
HANYA dari berkas di results/final/. Tidak ada angka yang diketik tangan: semua berasal dari
benchmark_summary.csv, benchmark_cost.csv, benchmark_crossover.csv, benchmark_meta_*.json, probe_smallint.txt.

Tabel .md memakai koma desimal (EYD); tabel .csv memakai titik desimal. Tiap berkas .md memuat komentar
<!-- sumber: ... --> yang menyebut berkas dan kolom asal angka.

Pemakaian:
  python3 bench/make_paper_assets.py --tables-only                 # hanya tabel (pustaka standar)
  bench/.venv/bin/python bench/make_paper_assets.py                # tabel + gambar (perlu matplotlib)
Opsi: --src results/final  --out paper
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BITS = [64, 128, 256, 512, 1024, 2048, 3072, 4096]
MAIN_BITS = [b for b in BITS if b >= 512]
APPX_BITS = [b for b in BITS if b < 512]
KS = [2, 3, 4, 5]
METHODS = {"crt_garner": "CRT-Garner", "crt_gauss": "CRT-Gauss (a)", "crt_gauss_precomp": "CRT-Gauss (b)"}

NOTE_APPX = ("Catatan untuk 64–256 bit: ukuran prima per faktor adalah bits/k (12,8 sampai 128 bit). Pada probe terpisah, biaya per "
             "iterasi eksponensiasi modular naik bila modulus melewati 30 bit ({probe}); karena itu kurva speedup pada rentang ini tidak "
             "mulus dan sebaiknya tidak ditafsirkan sebagai tren. Mekanismenya TIDAK TERVERIFIKASI.")


def dec(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def table(header, rows):
    s = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s


class Data:
    def __init__(self, src):
        self.src = src
        with open(os.path.join(src, "benchmark_summary.csv"), encoding="utf-8") as fh:
            self.S = {(r["layer"], r["method"], int(r["bits_target"]), int(r["k"])): r for r in csv.DictReader(fh)}
        with open(os.path.join(src, "benchmark_cost.csv"), encoding="utf-8") as fh:
            self.C = {(r["method"], int(r["bits_target"]), int(r["k"])): r for r in csv.DictReader(fh)}
        with open(os.path.join(src, "benchmark_crossover.csv"), encoding="utf-8") as fh:
            self.X = list(csv.DictReader(fh))
        metas = glob.glob(os.path.join(src, "benchmark_meta_*.json"))
        if len(metas) != 1:
            sys.exit(f"harus ada tepat satu benchmark_meta_*.json di {src}, ditemukan {len(metas)}")
        self.meta_path = metas[0]
        with open(self.meta_path, encoding="utf-8") as fh:
            self.meta = json.load(fh)
        self.probe = {}
        pp = os.path.join(src, "probe_smallint.txt")
        if os.path.exists(pp):
            with open(pp, encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"\s*(\d+)\s+([\d.]+)\s+([\d.]+)", line)
                    if m:
                        self.probe[int(m.group(1))] = float(m.group(3))

    def f(self, layer, method, b, k, col):
        return float(self.S[(layer, method, b, k)][col])

    def med_ms(self, layer, method, b, k):
        return self.f(layer, method, b, k, "median_s") * 1e3


def emit(out_dir, name, title, sources, intro, sections, csv_header, csv_rows):
    """sections: list of (judul, md_table, catatan or None)."""
    os.makedirs(os.path.join(out_dir, "tabel"), exist_ok=True)
    md = f"# {title}\n\n<!-- sumber: {sources}; dibangkitkan oleh bench/make_paper_assets.py -->\n\n{intro}\n\n"
    for judul, tbl, cat in sections:
        md += f"## {judul}\n\n{tbl}\n"
        if cat:
            md += f"{cat}\n\n"
    with open(os.path.join(out_dir, "tabel", name + ".md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(out_dir, "tabel", name + ".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(csv_header)
        w.writerows(csv_rows)


def probe_text(D):
    p = D.probe
    if all(b in p for b in (30, 31, 32)):
        return (f"results/final/probe_smallint.txt: {dec(p[30] , 4)} µs/iterasi pada 30 bit, {dec(p[31], 4)} pada 31 bit, "
                f"{dec(p[32], 4)} pada 32 bit; kenaikan {dec(100 * (p[31] / p[30] - 1), 0)}% dan {dec(100 * (p[32] / p[30] - 1), 0)}% terhadap 30 bit")
    return "probe_smallint.txt tidak tersedia"


def build_tables(D, out_dir):
    appx_note = NOTE_APPX.format(probe=probe_text(D))
    sp_src = "results/final/benchmark_summary.csv (layer=core)"

    # 00 lingkungan
    m = D.meta
    rows = [["Commit sumber kode", m["source_commit"]], ["Pohon kerja bersih (tanpa perubahan terlacak)", "ya" if not m["source_dirty"] else "TIDAK"],
            ["Python", m["python_full"]], ["OS", m["platform"]], ["CPU", m["env"]["cpu"]],
            ["CPU logis tersedia", m["cpu_count"]], ["CPU dipatok ke nomor", m["env"]["pinned_cpu"]],
            ["Host", m["hostname"]], ["Waktu mulai", m["started"]],
            ["Load average awal (1/5/15 menit)", " / ".join(dec(x) for x in m["loadavg_start"])],
            ["Load average akhir (1/5/15 menit)", " / ".join(dec(x) for x in m["loadavg_end"])],
            ["Durasi pengukuran (detik)", dec(m["measure_time_s"], 1)], ["Durasi total (detik)", dec(m["wall_time_s"], 1)],
            ["Baris data", m["rows"]], ["Putaran terukur per sel", m["config"]["reps"]], ["Pemanasan", m["config"]["warmup"]],
            ["Ciphertext bersama per kunci", m["config"]["n_ct"]], ["Seed", m["config"]["seed"]]]
    emit(out_dir, "00_lingkungan", "Lingkungan dan konfigurasi pengukuran",
         "results/final/" + os.path.basename(D.meta_path), "Keadaan mesin dan konfigurasi benchmark final.",
         [("Tabel", table(["Butir", "Nilai"], rows), "Load average host tidak terkendali (host dipakai bersama).")],
         ["butir", "nilai"], rows)

    # 01-03 speedup
    for num, method, label in (("01", "crt_garner", "CRT-Garner"), ("02", "crt_gauss", "CRT-Gauss (a), invers modular dihitung saat dekripsi"),
                               ("03", "crt_gauss_precomp", "CRT-Gauss (b), koefisien diprekomputasi saat pembangkitan kunci")):
        def sec(bl):
            return table(["bits"] + [f"k={k}" for k in KS],
                         [[b] + [f"{dec(D.f('core', method, b, k, 'speedup'))} [{dec(D.f('core', method, b, k, 'speedup_ci95_lo'))}–"
                                 f"{dec(D.f('core', method, b, k, 'speedup_ci95_hi'))}]" for k in KS] for b in bl])
        rows = [[b, k, D.med_ms("core", "standard", b, k), D.med_ms("core", method, b, k), D.f("core", method, b, k, "speedup"),
                 D.f("core", method, b, k, "speedup_ci95_lo"), D.f("core", method, b, k, "speedup_ci95_hi"),
                 D.f("core", method, b, k, "n_runs")] for b in BITS for k in KS]
        emit(out_dir, f"{num}_speedup_{ {'crt_garner': 'garner', 'crt_gauss': 'gauss_a', 'crt_gauss_precomp': 'gauss_b'}[method] }",
             f"Speedup {label} terhadap RSA standar (lapisan core)",
             sp_src + f", method={method}, kolom speedup, speedup_ci95_lo, speedup_ci95_hi",
             "Speedup = median waktu RSA standar / median waktu metode pada kunci k-prima dan 30 ciphertext yang sama; "
             "kurung siku = CI95 bootstrap (1000 resampling independen, persentil) dalam satu sesi pengukuran.",
             [("Tabel utama (512–4096 bit)", sec(MAIN_BITS), None), ("Lampiran (64–256 bit)", sec(APPX_BITS), appx_note)],
             ["bits", "k", "median_standar_ms", "median_metode_ms", "speedup", "ci95_lo", "ci95_hi", "n_putaran"], rows)

    # 04 rasio Garner/Gauss(b) dan Gauss(a)/Gauss(b)
    def ratio(num_m, den_m, b, k):
        return D.f("core", num_m, b, k, "median_s") / D.f("core", den_m, b, k, "median_s")

    def sec_ratio(num_m, bl):
        return table(["bits"] + [f"k={k}" for k in KS], [[b] + [dec(ratio(num_m, "crt_gauss_precomp", b, k), 3) for k in KS] for b in bl])
    rows = [[b, k, ratio("crt_garner", "crt_gauss_precomp", b, k), ratio("crt_gauss", "crt_gauss_precomp", b, k)] for b in BITS for k in KS]
    emit(out_dir, "04_rasio_garner_gauss_b", "Rasio waktu median terhadap CRT-Gauss (b)",
         sp_src + ", kolom median_s", "Rasio > 1 berarti metode pembilang lebih lambat daripada CRT-Gauss (b). Rasio dua median (tanpa CI).",
         [("Garner / Gauss (b), 512–4096 bit", sec_ratio("crt_garner", MAIN_BITS), None),
          ("Gauss (a) / Gauss (b), 512–4096 bit", sec_ratio("crt_gauss", MAIN_BITS), None),
          ("Garner / Gauss (b), 64–256 bit (lampiran)", sec_ratio("crt_garner", APPX_BITS), appx_note),
          ("Gauss (a) / Gauss (b), 64–256 bit (lampiran)", sec_ratio("crt_gauss", APPX_BITS), None)],
         ["bits", "k", "garner_per_gauss_b", "gauss_a_per_gauss_b"], rows)

    # 05 multi-prime vs CRT-2
    def sec_mp(bl):
        return table(["bits"] + [f"k={k}" for k in KS],
                     [[b] + [f"{dec(D.f('core', 'crt_garner', b, k, 'speedup_vs_garner_k2'))} [{dec(D.f('core', 'crt_garner', b, k, 'speedup_vs_garner_k2_lo'))}–"
                             f"{dec(D.f('core', 'crt_garner', b, k, 'speedup_vs_garner_k2_hi'))}]" if k > 2 else "1,00 (acuan)" for k in KS] for b in bl])

    def sec_mp_std(bl):
        return table(["bits"] + [f"k={k}" for k in KS],
                     [[b] + [dec(D.f("core", "crt_garner", b, k, "speedup_vs_standard_k2")) for k in KS] for b in bl])
    rows = []
    for b in BITS:
        for k in KS:
            r = [b, k, D.f("core", "crt_garner", b, k, "speedup_vs_standard_k2"), D.f("core", "crt_garner", b, k, "speedup_vs_standard_k2_lo"),
                 D.f("core", "crt_garner", b, k, "speedup_vs_standard_k2_hi")]
            if k > 2:
                r += [D.f("core", "crt_garner", b, k, "speedup_vs_garner_k2"), D.f("core", "crt_garner", b, k, "speedup_vs_garner_k2_lo"),
                      D.f("core", "crt_garner", b, k, "speedup_vs_garner_k2_hi")]
            else:
                r += ["", "", ""]
            rows.append(r)
    emit(out_dir, "05_multiprime_vs_crt2", "Multi-prime CRT (k = 3–5) terhadap CRT dua prima (Garner, lapisan core)",
         sp_src + ", method=crt_garner, kolom speedup_vs_garner_k2(_lo/_hi), speedup_vs_standard_k2(_lo/_hi)",
         "Acuan: waktu median CRT-Garner dengan k = 2 pada bits yang sama (kunci berbeda, ciphertext berbeda; CI95 bootstrap independen). "
         "Tabel kedua memakai acuan RSA standar k = 2, yaitu RSA dua-prima tanpa CRT.",
         [("Terhadap CRT-Garner k = 2, 512–4096 bit", sec_mp(MAIN_BITS), None),
          ("Terhadap RSA standar k = 2, 512–4096 bit", sec_mp_std(MAIN_BITS), None),
          ("Terhadap CRT-Garner k = 2, 64–256 bit (lampiran)", sec_mp(APPX_BITS), appx_note)],
         ["bits", "k", "speedup_vs_standar_k2", "ci95_lo", "ci95_hi", "speedup_vs_garner_k2", "ci95_lo", "ci95_hi"], rows)

    # 06 efisiensi
    def eff(b, k):
        return D.f("core", "crt_garner", b, k, "speedup") / (k * k)

    def sec_eff(bl):
        return table(["bits"] + [f"k={k} (k²={k * k})" for k in KS], [[b] + [dec(100 * eff(b, k), 0) + "%" for k in KS] for b in bl])
    rows = [[b, k, k * k, D.f("core", "crt_garner", b, k, "speedup"), eff(b, k)] for b in BITS for k in KS]
    emit(out_dir, "06_efisiensi_kuadrat", "Efisiensi terhadap k² (CRT-Garner, lapisan core)",
         sp_src + ", method=crt_garner, kolom speedup",
         "Efisiensi = speedup terukur / k². Nilai 100% berarti waktu turun tepat sebesar faktor k² (acuan teoretis untuk k prima berukuran sama).",
         [("Tabel utama (512–4096 bit)", sec_eff(MAIN_BITS), None), ("Lampiran (64–256 bit)", sec_eff(APPX_BITS), appx_note)],
         ["bits", "k", "k_kuadrat", "speedup", "efisiensi"], rows)

    # 07 biaya berbobot-bit
    cost_src = "results/final/benchmark_cost.csv, kolom speedup_literal dan speedup_refined"

    def sec_cost(method, bl):
        return table(["bits"] + [f"k={k} (k²={k * k})" for k in KS],
                     [[b] + [f"{dec(float(D.C[(method, b, k)]['speedup_literal']))} / {dec(float(D.C[(method, b, k)]['speedup_refined']))}" for k in KS] for b in bl])
    rows = [[b, k, m, D.C[(m, b, k)]["cost_literal"], D.C[(m, b, k)]["cost_refined"], D.C[(m, b, k)]["speedup_literal"],
             D.C[(m, b, k)]["speedup_refined"]] for m in ("crt_garner", "crt_gauss", "crt_gauss_precomp") for b in BITS for k in KS]
    secs = []
    for method, lab in (("crt_garner", "CRT-Garner"), ("crt_gauss", "CRT-Gauss (a)"), ("crt_gauss_precomp", "CRT-Gauss (b)")):
        secs.append((f"{lab}, 512–4096 bit (literal / refined)", sec_cost(method, MAIN_BITS), None))
    for method, lab in (("crt_garner", "CRT-Garner"), ("crt_gauss", "CRT-Gauss (a)"), ("crt_gauss_precomp", "CRT-Gauss (b)")):
        secs.append((f"{lab}, 64–256 bit (lampiran; literal / refined)", sec_cost(method, APPX_BITS), None))
    emit(out_dir, "07_biaya_berbobot_bit", "Speedup menurut model biaya berbobot-bit (RSA standar / metode)",
         cost_src + f" (n_ciphertexts = {D.C[('standard', 4096, 2)]['n_ciphertexts']} per sel; kunci dan ciphertext sama dengan benchmark waktu)",
         "Model biaya tidak bergantung pada overhead interpreter. Literal: tiap perkalian, modulo, dan pembagian bernilai bl(a)·bl(b). "
         "Refined: perkalian bl(a)·bl(b); modulo/pembagian bernilai (panjang kuosien)·(panjang pembagi). Sel berisi \"literal / refined\". "
         "Pada CRT-Gauss (a) model bench menghitung invers modular saat dekripsi; penghitung di core/ tidak menghitungnya "
         "(lihat results/final/costmodel_crosscheck.txt).",
         secs, ["bits", "k", "metode", "biaya_literal", "biaya_refined", "speedup_literal", "speedup_refined"], rows)

    # 08 waktu standar
    rows = [[b, k, D.med_ms("core", "standard", b, k)] for b in BITS for k in KS]
    emit(out_dir, "08_waktu_standar_ms", "Waktu median dekripsi RSA standar (ms, lapisan core)", sp_src + ", method=standard, kolom median_s",
         "Waktu median satu dekripsi (30 putaran terukur per sel).",
         [("Tabel", table(["bits"] + [f"k={k}" for k in KS], [[b] + [dec(D.med_ms("core", "standard", b, k), 3) for k in KS] for b in BITS]), None)],
         ["bits", "k", "median_ms"], rows)

    # 09 lapisan
    def sec_layer(bl):
        hdr = ["bits", "lapisan"] + [f"k={k}" for k in KS]
        body = []
        for b in bl:
            for layer in ("core", "lean", "builtin"):
                body.append([b, layer] + [dec(D.f(layer, "crt_garner", b, k, "speedup")) for k in KS])
        return table(hdr, body)
    rows = [[b, layer, k, D.f(layer, "crt_garner", b, k, "speedup")] for b in BITS for layer in ("core", "lean", "builtin") for k in KS]
    emit(out_dir, "09_lapisan_garner", "Speedup CRT-Garner pada tiga lapisan implementasi",
         "results/final/benchmark_summary.csv (layer=core, lean, builtin; method=crt_garner; kolom speedup)",
         "core = kode inti apa adanya (dengan penghitung operasi); lean = salinan tanpa penghitung/dict; builtin = pow() bawaan Python "
         "(hanya informatif). Lapisan lean dan builtin tidak diberi CI di tabel ini.",
         [("512–4096 bit", sec_layer(MAIN_BITS), None), ("64–256 bit (lampiran)", sec_layer(APPX_BITS), appx_note)],
         ["bits", "lapisan", "k", "speedup"], rows)

    # 10 titik silang
    rows = [[r["layer"], r["method"], r["k"], r["crossover_bits"], r["bits_median_speedup_le_1"], r["bits_ci95_lo_le_1"], r["min_speedup"], r["max_speedup"]]
            for r in D.X if r["layer"] == "core"]
    body = [[METHODS[r[1]], r[2], r[3], r[4], r[5], dec(float(r[6]), 3), dec(float(r[7]), 2)] for r in rows]
    emit(out_dir, "10_titik_silang", "Titik silang speedup > 1 (lapisan core)",
         "results/final/benchmark_crossover.csv (layer=core)",
         "Titik silang = bits terkecil di grid yang untuk semua bits yang lebih besar punya batas bawah CI95 speedup > 1. \"-\" berarti tidak ada bits di grid dengan median ≤ 1 (atau CI95 bawah ≤ 1). "
         "Grid terkecil 64 bit, jadi \"64\" berarti tidak ada titik silang di dalam grid (bukan bahwa titik silang tepat di 64 bit).",
         [("Tabel", table(["metode", "k", "titik silang (bit)", "bits dengan median ≤ 1", "bits dengan CI95 bawah ≤ 1", "speedup min", "speedup maks"], body), None)],
         ["layer", "metode", "k", "titik_silang_bits", "bits_median_le_1", "bits_ci95_lo_le_1", "speedup_min", "speedup_maks"], rows)

    # 11 penghitung operasi (op_counter) dan 12 pendukung metodologi
    def ops(method, b, k):
        return D.f("core", method, b, k, "ops_ratio_standard_over_method")

    def rng(method, bl):
        v = [ops(method, b, k) for b in bl for k in KS]
        return min(v), max(v)
    secs = []
    for method in ("crt_garner", "crt_gauss", "crt_gauss_precomp"):
        lo_all, hi_all = rng(method, BITS)
        lo_m, hi_m = rng(method, MAIN_BITS)
        secs.append((f"{METHODS[method]}: rasio total operasi standar / metode", table(["bits"] + [f"k={k}" for k in KS],
                     [[b] + [dec(ops(method, b, k), 3) for k in KS] for b in BITS]),
                     f"Rentang seluruh grid (64–4096 bit): {dec(lo_all, 3)} sampai {dec(hi_all, 3)}; untuk bits ≥ 512: {dec(lo_m, 3)} sampai {dec(hi_m, 3)}."))
    rows = [[m_, b, k, ops(m_, b, k)] for m_ in ("crt_garner", "crt_gauss", "crt_gauss_precomp") for b in BITS for k in KS]
    emit(out_dir, "11_rasio_op_counter", "Rasio total operasi (op_counter) RSA standar terhadap metode CRT, lapisan core",
         sp_src + ", kolom ops_ratio_standard_over_method (rata-rata total_operations standar / metode)",
         "Penghitung operasi mencatat banyaknya operasi aritmetika tanpa memperhitungkan panjang operan, sehingga rasionya mendekati 1: "
         "CRT melakukan k eksponensiasi dengan eksponen sekitar k kali lebih pendek, sehingga jumlah langkah kuadrat-dan-kali kira-kira sama dengan satu "
         "eksponensiasi penuh (penjelasan analitis; tidak diuji terpisah). Penghitung tidak melihat bahwa operan CRT lebih pendek; hal itu hanya terlihat pada waktu dan model biaya berbobot-bit. "
         "Pada bits kecil rasio menyimpang lebih jauh dari 1 (arahnya bergantung pada k); penyebabnya tidak diselidiki (TIDAK TERVERIFIKASI).",
         secs, ["metode", "bits", "k", "rasio_total_operasi"], rows)

    import statistics as st
    iqr = [D.f(ly, m_, b, k, "iqr_s") / D.f(ly, m_, b, k, "median_s") for (ly, m_, b, k) in D.S]
    iqr_core = [D.f(ly, m_, b, k, "iqr_s") / D.f(ly, m_, b, k, "median_s") for (ly, m_, b, k) in D.S if ly == "core"]
    q = sorted(iqr)
    p90 = q[int(0.9 * (len(q) - 1))]
    ov_rows = [[m_, b, k, D.f("core", m_, b, k, "median_s") / D.f("lean", m_, b, k, "median_s")] for m_ in ("standard", "crt_garner") for b in BITS for k in KS]

    def sec_ov(bl):
        return table(["bits"] + [f"{lab} k={k}" for lab in ("standar", "Garner") for k in KS],
                     [[b] + [dec(D.f("core", m_, b, k, "median_s") / D.f("lean", m_, b, k, "median_s")) for m_ in ("standard", "crt_garner") for k in KS] for b in bl])
    stab = (f"Sebaran antar putaran dalam satu sesi (IQR / median, seluruh {len(iqr)} sel semua lapisan): median {dec(100 * st.median(iqr), 1)}%, "
            f"persentil ke-90 {dec(100 * p90, 1)}%, maksimum {dec(100 * max(iqr), 1)}%. Pada lapisan core saja ({len(iqr_core)} sel): median {dec(100 * st.median(iqr_core), 1)}%, "
            f"maksimum {dec(100 * max(iqr_core), 1)}%. Variasi antar sesi dan antar mesin tidak diukur.")
    emit(out_dir, "12_overhead_dan_kestabilan", "Overhead instrumentasi (core / lean) dan kestabilan pengukuran",
         sp_src.replace("(layer=core)", "(layer=core dan lean)") + ", kolom median_s dan iqr_s",
         "Rasio waktu median lapisan core (dengan penghitung operasi dan pencatatan langkah) terhadap lapisan lean (tanpa keduanya). " + stab,
         [("Rasio core / lean, 512–4096 bit", sec_ov(MAIN_BITS), None), ("Rasio core / lean, 64–256 bit (lampiran)", sec_ov(APPX_BITS), None)],
         ["metode", "bits", "k", "rasio_core_per_lean"], ov_rows)
    return sorted(os.listdir(os.path.join(out_dir, "tabel")))


def build_figures(D, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    gdir = os.path.join(out_dir, "gambar")
    os.makedirs(gdir, exist_ok=True)
    plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white", "text.color": "#111111",
                         "axes.labelcolor": "#333333", "xtick.color": "#333333", "ytick.color": "#333333", "axes.edgecolor": "#888888",
                         "axes.spines.top": False, "axes.spines.right": False, "grid.color": "#dddddd", "grid.linewidth": 0.6, "font.size": 9})
    KCOL = {2: "#2a78d6", 3: "#eb6834", 4: "#1baf7a", 5: "#a0267a"}
    KMK = {2: "o", 3: "s", 4: "^", 5: "D"}
    MCOL = {"standard": "#2a78d6", "crt_garner": "#eb6834", "crt_gauss": "#1baf7a", "crt_gauss_precomp": "#a0267a"}
    MLAB = {"standard": "RSA standar", "crt_garner": "CRT-Garner", "crt_gauss": "CRT-Gauss (a)", "crt_gauss_precomp": "CRT-Gauss (b)"}
    MMK = {"standard": "o", "crt_garner": "s", "crt_gauss": "^", "crt_gauss_precomp": "D"}
    foot = (f"{D.meta['env']['cpu']} | Python {D.meta['env']['python_version']} | commit {D.meta['source_commit'][:7]} | "
            f"median {D.meta['config']['reps']} putaran | lapisan core")
    made = []

    short = f"Python {D.meta['env']['python_version']} | commit {D.meta['source_commit'][:7]} | core, median {D.meta['config']['reps']} putaran"
    cost_foot = f"model biaya, {D.C[('standard', 4096, 2)]['n_ciphertexts']} ciphertext per sel | commit {D.meta['source_commit'][:7]}"

    def save(fig, name, text=None):
        fig.text(0.01, 0.005, text or foot, fontsize=6, color="#555555", ha="left", va="bottom")
        path = os.path.join(gdir, name)
        fig.savefig(path, dpi=300)
        plt.close(fig)
        made.append(name)

    # Gambar 1: waktu vs bits (log-log)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.0), sharex=True, sharey=True)
    for ax, k in zip(axes.ravel(), KS):
        for method in ("standard", "crt_garner", "crt_gauss", "crt_gauss_precomp"):
            ys = [D.med_ms("core", method, b, k) for b in BITS]
            lo = [D.f("core", method, b, k, "q1_s") * 1e3 for b in BITS]
            hi = [D.f("core", method, b, k, "q3_s") * 1e3 for b in BITS]
            ax.plot(BITS, ys, linestyle="--" if method == "crt_gauss_precomp" else "-", color=MCOL[method], marker=MMK[method], ms=4,
                    mfc="white" if method == "crt_gauss_precomp" else MCOL[method], lw=1.3, label=MLAB[method])
            ax.fill_between(BITS, lo, hi, color=MCOL[method], alpha=0.15, lw=0)
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(BITS)
        ax.set_xticklabels([str(b) for b in BITS], rotation=45, fontsize=7)
        ax.set_title(f"k = {k}", fontsize=10)
        ax.grid(True, which="major", axis="y")
        ax.set_axisbelow(True)
    for ax in axes[:, 0]:
        ax.set_ylabel("waktu median per dekripsi (ms)")
    for ax in axes[1, :]:
        ax.set_xlabel("panjang modulus n (bit)")
    axes[0, 0].legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle("Waktu dekripsi vs panjang modulus (pita = kuartil 1–3)", fontsize=10)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    save(fig, "gambar1_waktu_vs_bits.png")

    # Gambar 2: speedup vs bits per k dengan CI95
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 3.1), sharey=True)
    for ax, method in zip(axes, ("crt_garner", "crt_gauss", "crt_gauss_precomp")):
        for k in KS:
            ys = [D.f("core", method, b, k, "speedup") for b in BITS]
            lo = [D.f("core", method, b, k, "speedup_ci95_lo") for b in BITS]
            hi = [D.f("core", method, b, k, "speedup_ci95_hi") for b in BITS]
            ax.plot(BITS, ys, "-", color=KCOL[k], marker=KMK[k], ms=3.5, lw=1.3, label=f"k = {k}")
            ax.fill_between(BITS, lo, hi, color=KCOL[k], alpha=0.2, lw=0)
        ax.axhline(1.0, color="#555555", lw=1, ls="--")
        ax.set_xscale("log", base=2)
        ax.set_xticks(BITS)
        ax.set_xticklabels([str(b) for b in BITS], rotation=60, fontsize=6.5)
        ax.set_title(MLAB[method], fontsize=9)
        ax.set_xlabel("panjang modulus n (bit)")
        ax.grid(True, which="major", axis="y")
        ax.set_axisbelow(True)
    axes[0].set_ylabel("speedup terhadap RSA standar")
    axes[0].legend(fontsize=7, frameon=False, loc="upper left")
    axes[0].text(BITS[-1], 0.97, "speedup = 1 ", fontsize=6, va="top", ha="right", color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "gambar2_speedup_vs_bits.png")

    # Gambar 3: speedup model biaya vs k^2
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    ks2 = [k * k for k in KS]
    for ax, col, ttl in ((axes[0], "speedup_literal", "Biaya literal bl(a)·bl(b)"), (axes[1], "speedup_refined", "Biaya refined (kuosien × pembagi)")):
        ax.plot([3.5, 25.5], [3.5, 25.5], color="#555555", lw=1, ls=":", label="y = k² (acuan)")
        for method, b, ls in (("crt_garner", 4096, "-"), ("crt_gauss", 4096, "-"), ("crt_garner", 512, "--"), ("crt_gauss", 512, "--")):
            ys = [float(D.C[(method, b, k)][col]) for k in KS]
            ax.plot(ks2, ys, linestyle=ls, color=MCOL[method], marker=MMK[method], ms=4, lw=1.3, mfc=MCOL[method] if b == 4096 else "white",
                    label=f"{MLAB[method]}, {b} bit")
        ax.set_xticks(ks2)
        ax.set_xlabel("k²")
        ax.set_title(ttl, fontsize=9)
        ax.grid(True, which="major", axis="y")
        ax.set_axisbelow(True)
    axes[0].set_ylabel("speedup biaya (standar / metode)")
    axes[0].legend(fontsize=6.5, frameon=False, loc="upper left")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "gambar3_biaya_vs_k2.png", cost_foot)

    # Gambar 4: efisiensi terhadap k^2
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    shades = {512: "#9ecae1", 1024: "#6baed6", 2048: "#3182bd", 3072: "#1f5f9e", 4096: "#08306b"}
    mk = {512: "o", 1024: "s", 2048: "^", 3072: "v", 4096: "D"}
    for b in (512, 1024, 2048, 3072, 4096):
        ys = [100 * D.f("core", "crt_garner", b, k, "speedup") / (k * k) for k in KS]
        ax.plot(ks2, ys, "-", color=shades[b], marker=mk[b], ms=4, lw=1.4, label=f"{b} bit")
    ax.axhline(100, color="#555555", lw=1, ls=":")
    ax.text(ks2[-1], 101, "100% (speedup = k²)", fontsize=6.5, ha="right", va="bottom", color="#555555")
    ax.set_xticks(ks2)
    ax.set_xlabel("k²")
    ax.set_ylabel("efisiensi = speedup / k² (%)")
    ax.set_ylim(0, 110)
    ax.grid(True, which="major", axis="y")
    ax.set_axisbelow(True)
    ax.legend(fontsize=7, frameon=False, title="CRT-Garner", title_fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "gambar4_efisiensi_vs_k2.png", short)
    return made


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "final"))
    ap.add_argument("--out", default=os.path.join(ROOT, "paper"))
    ap.add_argument("--tables-only", action="store_true")
    ap.add_argument("--figures-only", action="store_true")
    a = ap.parse_args()
    D = Data(os.path.abspath(a.src))
    if not a.figures_only:
        print("tabel:", ", ".join(build_tables(D, os.path.abspath(a.out))))
    if not a.tables_only:
        print("gambar:", ", ".join(build_figures(D, os.path.abspath(a.out))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

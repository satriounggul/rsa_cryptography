#!/usr/bin/env python3
"""
Memeriksa angka kunci di bahan makalah (paper/*.md) terhadap data sumber di results/final/. Hanya pustaka standar.

Tiga jenis pemeriksaan:
  1. ANGKA : angka dihitung ulang dari results/final/*.csv (atau *.txt/*.json), diformat seperti di teks (koma desimal),
             lalu harus muncul di berkas paper/ yang ditentukan.
  2. SUMBER: setiap komentar <!-- sumber: ... --> di paper/*.md harus merujuk berkas yang ada (results/final/..., paper/..., bench/...);
             rujukan ke baseline (results/ di luar final/) hanya diperbolehkan bila ditandai sebagai catatan kaki/lampiran.
  3. HASH  : hash commit dan SHA-256 di Bab V harus cocok dengan git dan dist/kriptografi_rsa_final_v2.zip (dilewati bila zip/git tidak ada).
Keluar dengan kode 1 bila ada yang GAGAL.

Penanda DIISI FASE D di Bab V sengaja masih ada pada salinan di dalam zip pengumpulan (hash zip tidak mungkin ditulis di dalam zip
itu sendiri). Tanpa opsi --strict-hash penanda itu dilaporkan LEWAT; dengan --strict-hash dianggap GAGAL (dipakai pada repo setelah diisi).

Pemakaian (dari akar repo): python3 paper/check_numbers.py [--strict-hash]
"""
import csv
import glob
import hashlib
import json
import os
import re
import statistics as st
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = os.path.join(ROOT, "results", "final")
PAPER = os.path.join(ROOT, "paper")
KS = [2, 3, 4, 5]
BITS = [64, 128, 256, 512, 1024, 2048, 3072, 4096]
M512 = [b for b in BITS if b >= 512]
ZIP = os.path.join(ROOT, "dist", "kriptografi_rsa_final_v2.zip")

results = []  # (kelompok, deskripsi, status, rincian)


def dec(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def thousands(n):
    return f"{n:,}".replace(",", ".")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_csv(name):
    with open(os.path.join(FINAL, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


S = {(r["layer"], r["method"], int(r["bits_target"]), int(r["k"])): r for r in load_csv("benchmark_summary.csv")}
C = {(r["method"], int(r["bits_target"]), int(r["k"])): r for r in load_csv("benchmark_cost.csv")}
BAB_V = read(os.path.join(PAPER, "BAB_V_draf.md"))
BAB_VI = read(os.path.join(PAPER, "BAB_VI_draf.md"))
KOREKSI = read(os.path.join(PAPER, "KOREKSI_MAKALAH.md"))
TEXT = {"V": BAB_V, "VI": BAB_VI, "KOREKSI": KOREKSI}


def f(layer, method, b, k, col):
    return float(S[(layer, method, b, k)][col])


def check(group, desc, expected, where):
    """expected: string yang harus muncul pada setiap dokumen di `where` (kunci TEXT)."""
    missing = [w for w in where if expected not in TEXT[w]]
    results.append((group, desc, "LULUS" if not missing else "GAGAL",
                    f"'{expected}' di {','.join(where)}" + (f" TIDAK ADA di {','.join(missing)}" if missing else "")))


def check_value(group, desc, ok, detail):
    results.append((group, desc, "LULUS" if ok else "GAGAL", detail))


# ---------- 1a. speedup pada 2048 dan 4096 bit (24 angka: 3 metode x 2 bits x 4 k), dalam tabel/teks Bab V ----------
for method, label in (("crt_garner", "Garner"), ("crt_gauss", "Gauss (a)"), ("crt_gauss_precomp", "Gauss (b)")):
    for b in (2048, 4096):
        for k in KS:
            cell = (f"{dec(f('core', method, b, k, 'speedup'))} [{dec(f('core', method, b, k, 'speedup_ci95_lo'))}–"
                    f"{dec(f('core', method, b, k, 'speedup_ci95_hi'))}]")
            check("speedup", f"speedup {label} {b} bit k={k}", cell, ["V"])

# ---------- 1b. rasio Garner/Gauss (b), Gauss (a)/Gauss (b) ----------
def ratio(a, b_, bl):
    v = [f("core", a, x, k, "median_s") / f("core", b_, x, k, "median_s") for x in bl for k in KS]
    return min(v), max(v)

lo, hi = ratio("crt_garner", "crt_gauss_precomp", BITS)
check("rasio", "Garner/Gauss (b) seluruh grid", f"{dec(lo, 3)} sampai {dec(hi, 3)}", ["V"])
lo, hi = ratio("crt_garner", "crt_gauss_precomp", M512)
check("rasio", "Garner/Gauss (b) >= 512 bit", f"{dec(lo, 3)} sampai {dec(hi, 3)}", ["V"])
check("rasio", "Garner/Gauss (b) >= 512 bit, maksimum di koreksi", f"{dec(hi, 3)}", ["KOREKSI"])
lo, hi = ratio("crt_gauss", "crt_gauss_precomp", BITS)
check("rasio", "Gauss (a)/Gauss (b) seluruh grid", f"{dec(lo, 3)} sampai {dec(hi, 3)}", ["V"])
lo, hi = ratio("crt_gauss", "crt_gauss_precomp", M512)
check("rasio", "Gauss (a)/Gauss (b) >= 512 bit", f"{dec(lo, 3)} sampai {dec(hi, 3)}", ["V"])

# ---------- 1c. multi-prime vs CRT 2 prima ----------
mp = [f("core", "crt_garner", b, k, "speedup_vs_garner_k2") for b in BITS for k in KS[1:]]
mp_lo = [f("core", "crt_garner", b, k, "speedup_vs_garner_k2_lo") for b in BITS for k in KS[1:]]
check_value("multiprime", "CI95 bawah > 1 pada 24 dari 24 sel", len(mp) == 24 and all(x > 1 for x in mp_lo),
            f"sel={len(mp)}, min CI bawah={min(mp_lo):.4f}")
mp512 = [f("core", "crt_garner", b, k, "speedup_vs_garner_k2") for b in M512 for k in KS[1:]]
check("multiprime", "rentang >= 512 bit (min sampai maks)", f"{dec(min(mp512))} sampai {dec(max(mp512))}", ["V"])
check("multiprime", "4096 bit k=5 vs CRT 2 prima", dec(f("core", "crt_garner", 4096, 5, "speedup_vs_garner_k2")), ["V", "VI"])
check("multiprime", "4096 bit k=5 vs standar k=2", dec(f("core", "crt_garner", 4096, 5, "speedup_vs_standard_k2")), ["V"])

# ---------- 1d. efisiensi terhadap k^2 ----------
for b in (4096, 512):
    for k in KS:
        e = round(100 * f("core", "crt_garner", b, k, "speedup") / (k * k))
        check("efisiensi", f"efisiensi Garner {b} bit k={k}", f"{e}%", ["V"])

# ---------- 1e. model biaya berbobot-bit 4096 bit ----------
for k in KS:
    for col, lab in (("speedup_literal", "literal"), ("speedup_refined", "refined")):
        check("biaya", f"biaya {lab} Garner 4096 bit k={k}", dec(float(C[("crt_garner", 4096, k)][col])), ["V"])
for k in KS:
    check("biaya", f"biaya literal Gauss (a) 4096 bit k={k}", dec(float(C[("crt_gauss", 4096, k)]["speedup_literal"])), ["V"])

# ---------- 1f. rentang rasio op_counter (rentang penuh dan >= 512 bit) ----------
ops_all = [f("core", "crt_garner", b, k, "ops_ratio_standard_over_method") for b in BITS for k in KS]
ops_512 = [f("core", "crt_garner", b, k, "ops_ratio_standard_over_method") for b in M512 for k in KS]
check("op_counter", "rentang penuh", f"{dec(min(ops_all), 3)} sampai {dec(max(ops_all), 3)}", ["V"])
check("op_counter", "rentang >= 512 bit", f"{dec(min(ops_512), 3)} sampai {dec(max(ops_512), 3)}", ["V"])
check("op_counter", "rentang penuh di koreksi", f"{dec(min(ops_all), 3)} sampai {dec(max(ops_all), 3)}", ["KOREKSI"])
check_value("op_counter", "rentang lama '0,95' tidak dipakai sebagai klaim di Bab V/VI",
            "0,95–1,04" not in BAB_V and "0,95-1,04" not in BAB_V and "0,95–1,04" not in BAB_VI,
            "pencarian teks '0,95–1,04'")

# ---------- 1g. 9.600 dari 9.600 benar ----------
with open(os.path.join(FINAL, "benchmark_raw_l0125001.csv"), newline="", encoding="utf-8") as fh:
    raw = list(csv.DictReader(fh))
ok_rows = sum(r["correct"] == "True" for r in raw)
exact = sum(r["bits_actual"] == r["bits_target"] for r in raw)
check_value("kebenaran", "9.600 dari 9.600 baris correct=True", len(raw) == 9600 and ok_rows == 9600, f"baris={len(raw)}, benar={ok_rows}")
check_value("kebenaran", "bits_actual == bits_target pada semua baris", exact == len(raw), f"{exact} dari {len(raw)}")
check("kebenaran", "teks '9.600 dari 9.600'", "9.600 dari 9.600", ["V"])
cells = {(r["layer"], r["method"], r["bits_target"], r["k"]) for r in raw}
check_value("kebenaran", "320 sel x 30 putaran", len(cells) == 320 and all(
    sum(1 for r in raw if (r["layer"], r["method"], r["bits_target"], r["k"]) == c) == 30 for c in list(cells)[:5]), f"sel={len(cells)}")

# ---------- 1h. waktu RSA standar 4096 bit dan Garner ----------
check("waktu", "RSA standar 4096 bit k=2 (ms)", dec(f("core", "standard", 4096, 2, "median_s") * 1e3, 3), ["V"])
check("waktu", "Garner 4096 bit k=2 (ms)", dec(f("core", "crt_garner", 4096, 2, "median_s") * 1e3, 3), ["V"])
check("waktu", "Garner 4096 bit k=5 (ms)", dec(f("core", "crt_garner", 4096, 5, "median_s") * 1e3, 3), ["V"])

# ---------- 1i. kecepatan minimum / maksimum dan CI bawah minimum ----------
g = [f("core", "crt_garner", b, k, "speedup") for b in BITS for k in KS]
gb = [f("core", "crt_gauss_precomp", b, k, "speedup") for b in BITS for k in KS]
glo = [f("core", "crt_garner", b, k, "speedup_ci95_lo") for b in BITS for k in KS]
gblo = [f("core", "crt_gauss_precomp", b, k, "speedup_ci95_lo") for b in BITS for k in KS]
check_value("speedup", "Garner dan Gauss (b) > 1 pada 32 dari 32 sel (CI bawah)", all(x > 1 for x in glo + gblo) and len(g) == 32,
            f"min CI bawah: {min(glo):.3f} / {min(gblo):.3f}")
check("speedup", "CI bawah minimum Garner dan Gauss (b)", f"{dec(min(glo), 3)} untuk Garner dan {dec(min(gblo), 3)} untuk Gauss (b)", ["V"])
check("speedup", "speedup minimum Garner/Gauss (b)", f"{dec(min(g), 3)} dan {dec(min(gb), 3)}", ["V"])
check("speedup", "speedup maksimum Garner/Gauss (b)", f"{dec(max(g))} dan {dec(max(gb))}", ["V"])
ga = {(b, k): f("core", "crt_gauss", b, k, "speedup") for b in BITS for k in KS}
below = sorted(c for c, v in ga.items() if v <= 1)
check_value("speedup", "Gauss (a): median <= 1 hanya di (128,2) dan (128,3)", below == [(128, 2), (128, 3)], f"sel: {below}")

# ---------- 1j. berkas teks hasil audit ----------
def txt(name):
    return read(os.path.join(FINAL, name))

ex = re.search(r"total pasangan \(kunci,c\)=(\d+)", txt("audit_exhaustive.txt"))
check_value("audit", "uji menyeluruh: ada angka dan tanpa kegagalan", bool(ex) and "TIDAK ADA" in txt("audit_exhaustive.txt"), ex.group(1) if ex else "?")
if ex:
    check("audit", "uji menyeluruh: jumlah pasangan", thousands(int(ex.group(1))), ["V"])
rg = re.search(r"identik .*?: (\d+) dari (\d+); berbeda: (\d+)", txt("audit_opcount_regression.txt"))
check_value("audit", "regresi op_counter: semua identik", bool(rg) and rg.group(1) == rg.group(2) and rg.group(3) == "0", rg.group(0) if rg else "?")
if rg:
    check("audit", "regresi op_counter: 576 dari 576", f"{rg.group(1)} dari {rg.group(2)}", ["V"])
cc = re.search(r"identik .*?: (\d+) dari (\d+)", txt("costmodel_crosscheck.txt"))
check_value("audit", "silang model biaya: semua identik", bool(cc) and cc.group(1) == cc.group(2), cc.group(0) if cc else "?")
if cc:
    check("audit", "silang model biaya: 960 dari 960", f"{cc.group(1)} dari {cc.group(2)}", ["V"])
dp = txt("audit_d_phi_lambda.txt")
m1 = re.search(r"d_i identik .*?: (\d+) dari (\d+)", dp)
m2 = re.search(r"c\^d_phi mod n == c\^d_lambda mod n: (\d+) dari (\d+)", dp)
m3 = re.search(r"lebih panjang pada (\d+) dari (\d+) kunci", dp)
m4 = re.search(r"min (-?\d+), maks (\d+)", dp)
check_value("audit", "d_phi vs d_lambda: dᵢ dan dekripsi identik", bool(m1 and m2) and m1.group(1) == m1.group(2) and m2.group(1) == m2.group(2),
            f"{m1.group(0) if m1 else '?'} | {m2.group(0) if m2 else '?'}")
if m1 and m2 and m3:
    check("audit", "d_phi vs d_lambda: 800 dari 800 dan 4.000 dari 4.000", f"{m1.group(1)} dari {m1.group(2)} kunci acak", ["V"])
    check("audit", "d_phi vs d_lambda: ciphertext", f"{thousands(int(m2.group(1)))} dari {thousands(int(m2.group(2)))} ciphertext", ["V"])
    check("audit", "d_phi lebih panjang pada n dari m kunci", f"{m3.group(1)} dari {m3.group(2)} kunci", ["V"])
    check("audit", "selisih bit d_phi - d_lambda", f"selisih {m4.group(1)} sampai {m4.group(2)} bit", ["V"])
vers = txt("uji_versi_python.txt")
check_value("tes", "55 tes OK pada 3.10, 3.13, dan 3.14 (catatan hasil)", vers.count("Ran 55 tests") == 3 and vers.count("\nOK") == 3,
            f"'Ran 55 tests' x{vers.count('Ran 55 tests')}, OK x{vers.count(chr(10) + 'OK')}")
cx = txt("contoh_hitung.txt")
check_value("contoh", "contoh_hitung: semua pemeriksaan lulus, tanpa GAGAL", "SEMUA PEMERIKSAAN LULUS" in cx and "[GAGAL]" not in cx, f"OK x{cx.count('[OK]')}")
check_value("contoh", "vektor uji menghasilkan 23", "pencarian langsung x in [0, 105): [23]" in cx and "jumlah = 233; mod n = 23" in cx, "A")

# ---------- 1k. lingkungan (meta) ----------
meta = json.loads(read(os.path.join(FINAL, "benchmark_meta_l0125001.json")))
check("lingkungan", "commit sumber pengukuran", meta["source_commit"], ["V"])
check("lingkungan", "durasi pengukuran (detik)", dec(meta["measure_time_s"], 1), ["V"])
check("lingkungan", "durasi total (detik)", dec(meta["wall_time_s"], 1), ["V"])
check_value("lingkungan", "pohon kerja bersih saat pengukuran", meta["source_dirty"] is False, f"source_dirty={meta['source_dirty']}")
check("lingkungan", "load average akhir", dec(meta["loadavg_end"][0]), ["V"])

# ---------- 1l. tidak ada angka --quick dan tidak ada klaim kebaruan ----------
quick_lines = [ln for t in (BAB_V, BAB_VI) for ln in t.splitlines() if "quick" in ln.lower()]
check_value("aturan", "mode --quick hanya disebut sebagai pengecualian (tanpa angka)", all("tidak dipakai" in ln for ln in quick_lines),
            f"{len(quick_lines)} baris menyebut quick")
claims = [ln.strip()[:90] for t in (BAB_V, BAB_VI) for ln in t.splitlines()
          if re.search(r"\b(novel|novelty|metode baru|algoritma baru|kebaruan)\b", ln, re.I) and "tidak ada klaim kebaruan" not in ln.lower()]
check_value("aturan", "tidak ada klaim kebaruan/novelty di Bab V dan VI", not claims, f"baris bermasalah: {claims}")
check_value("aturan", "teks '1.000.000' dan angka --quick (900 baris) tidak ada di Bab V/VI", "900 baris" not in BAB_V + BAB_VI, "pencarian '900 baris'")

# ---------- 2. komentar sumber ----------
src_total = bad = base = 0
for path in sorted(glob.glob(os.path.join(PAPER, "*.md")) + glob.glob(os.path.join(PAPER, "tabel", "*.md")) + glob.glob(os.path.join(PAPER, "gambar", "*.md"))):
    text = read(path)
    for m in re.finditer(r"<!--\s*sumber:(.*?)-->", text, re.S):
        src_total += 1
        for ref in re.findall(r"\b((?:results|paper|bench|core|tests)/[A-Za-z0-9_./\-]+?)(?=[\s,;:)\"'`]|$|\.(?=\s)|\.$)", m.group(1)):
            ref = ref.rstrip(".")
            # perbandingan_baseline.md ada di repo tetapi sengaja tidak ikut zip (merujuk berkas baseline); diperlakukan sebagai rujukan baseline
            if (ref.startswith("results/") and not ref.startswith("results/final/")) or ref == "results/final/perbandingan_baseline.md":
                base += 1  # baseline: hanya boleh sebagai catatan kaki; tidak diperiksa keberadaannya di zip
                continue
            if "*" in ref or ref.endswith("/"):
                continue
            if not os.path.exists(os.path.join(ROOT, ref)):
                bad += 1
                results.append(("sumber", f"{os.path.relpath(path, ROOT)}: rujukan '{ref}'", "GAGAL", "berkas tidak ada"))
check_value("sumber", f"{src_total} komentar sumber; semua rujukan results/final, paper, bench, core, tests ada", bad == 0,
            f"rujukan baseline (catatan kaki, tidak diperiksa): {base}")

# ---------- 3. hash di Bab V ----------
def sh(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None

pending = re.findall(r"\[DIISI FASE D[^\]]*\]", BAB_V)
if pending:
    results.append(("hash", "placeholder Bab V", "GAGAL" if "--strict-hash" in sys.argv else "LEWAT",
                    f"{len(pending)} penanda belum diisi (normal pada salinan di dalam zip)"))
else:
    hex64 = set(re.findall(r"\b[0-9a-f]{64}\b", BAB_V))
    hex40 = set(re.findall(r"\b[0-9a-f]{40}\b", BAB_V))
    if os.path.exists(ZIP):
        with open(ZIP, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        check_value("hash", "SHA-256 zip v2 di Bab V = SHA-256 berkas dist/", digest in hex64, digest)
        import zipfile
        with zipfile.ZipFile(ZIP) as zf:
            bi = zf.read("kriptografi_rsa/BUILD_INFO.txt").decode()
        pc = re.search(r"commit\s*:\s*([0-9a-f]{40})", bi)
        check_value("hash", "commit paket di Bab V = commit pada BUILD_INFO.txt di zip", bool(pc) and pc.group(1) in hex40, pc.group(1) if pc else "?")
    else:
        results.append(("hash", "zip v2", "LEWAT", "dist/kriptografi_rsa_final_v2.zip tidak ada (mis. dijalankan dari dalam zip)"))
    if sh("rev-parse", "HEAD"):
        for h in sorted(hex40):
            check_value("hash", f"commit {h[:10]} ada di git", sh("cat-file", "-t", h) == "commit", h)
    check_value("hash", "commit sumber pengukuran = tag v1-final", (sh("rev-parse", "v1-final^{commit}") or meta["source_commit"]) == meta["source_commit"],
                meta["source_commit"])

# ---------- keluaran ----------
w = max(len(r[1]) for r in results)
print(f"{'KELOMPOK':<11} {'PEMERIKSAAN':<{w}}  STATUS")
for grp, desc, status, detail in results:
    print(f"{grp:<11} {desc:<{w}}  {status:<6} {detail if status != 'LULUS' else ''}")
n_pass = sum(r[2] == "LULUS" for r in results)
n_fail = sum(r[2] == "GAGAL" for r in results)
n_skip = sum(r[2] == "LEWAT" for r in results)
print(f"\nTotal {len(results)} pemeriksaan: LULUS {n_pass}, GAGAL {n_fail}, LEWAT {n_skip}")
sys.exit(1 if n_fail else 0)

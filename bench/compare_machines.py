#!/usr/bin/env python3
"""
Membandingkan hasil benchmark dari beberapa mesin: tabel speedup per mesin berdampingan. Hanya pustaka standar.

Pemakaian:
  python3 bench/compare_machines.py server=results/final/benchmark_raw_l0125001.csv laptopA=hasil/benchmark_raw_LAPTOP-A.csv
  python3 bench/compare_machines.py results/final/benchmark_raw_l0125001.csv hasil/*.csv --layer core --out perbandingan.md --csv perbandingan.csv

Tiap argumen: [LABEL=]BERKAS.csv. Tanpa LABEL, label diambil dari kolom hostname di CSV, atau dari nama berkas.
speedup = median(standar) / median(metode) pada lapisan dan (bits, k) yang sama, dihitung per mesin.
Sel yang tidak ada pada suatu mesin (mis. hasil --quick hanya memuat 512/1024/2048 bit dan k = 2, 3, 5) ditulis "-".
Banyak putaran per sel dapat berbeda antar mesin (kolom n); bandingkan hasil --quick hanya sebagai uji fungsi.
"""
import argparse
import csv
import os
import statistics as st
import sys
from collections import defaultdict

METHOD_ORDER = ["crt_garner", "crt_gauss", "crt_gauss_precomp"]
METHOD_NAME = {"crt_garner": "CRT-Garner", "crt_gauss": "CRT-Gauss (a) invers saat dekripsi",
               "crt_gauss_precomp": "CRT-Gauss (b) koefisien prekomputasi"}


def load(spec):
    if os.path.exists(spec):
        label, path = "", spec
    elif "=" in spec:
        label, _, path = spec.partition("=")
    else:
        sys.exit(f"berkas tidak ditemukan: {spec}")
    if not os.path.exists(path):
        sys.exit(f"berkas tidak ditemukan: {path}")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit(f"{path}: CSV kosong")
    for col in ("layer", "method", "bits_target", "k", "time_s", "correct"):
        if col not in rows[0]:
            sys.exit(f"{path}: kolom '{col}' tidak ada; bukan keluaran bench/benchmark.py?")
    if not label:
        label = rows[0].get("hostname") or os.path.splitext(os.path.basename(path))[0]
    times = defaultdict(list)
    for r in rows:
        times[(r["layer"], r["method"], int(r["bits_target"]), int(r["k"]))].append(float(r["time_s"]))
    meta = {f: rows[0].get(f, "") for f in ("cpu", "python_version", "os", "pinned_cpu")}
    meta["rows"] = len(rows)
    meta["all_correct"] = all(r["correct"] == "True" for r in rows)
    meta["runs_per_cell"] = sorted({len(v) for v in times.values()})
    return label, path, meta, times


def md_table(header, rows):
    out = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        out += "| " + " | ".join(str(x) for x in r) + " |\n"
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="[LABEL=]benchmark_raw*.csv")
    ap.add_argument("--layer", default="core", choices=["core", "lean", "builtin"])
    ap.add_argument("--methods", default=",".join(METHOD_ORDER))
    ap.add_argument("--min-bits", type=int, default=0, help="tampilkan hanya bits >= nilai ini (mis. 512 untuk tabel utama)")
    ap.add_argument("--out", default=None, help="tulis tabel Markdown ke berkas ini")
    ap.add_argument("--csv", default=None, help="tulis tabel panjang (CSV) ke berkas ini")
    a = ap.parse_args()

    machines = []
    for spec in a.inputs:
        label, path, meta, times = load(spec)
        if any(m[0] == label for m in machines):
            sys.exit(f"label ganda: {label}; beri label berbeda dengan LABEL=berkas.csv")
        machines.append((label, path, meta, times))

    lines = ["# Perbandingan antar mesin", "",
             f"Lapisan: **{a.layer}**; speedup = median(standar) / median(metode) per mesin; \"-\" = sel tidak ada pada mesin itu.", ""]
    lines.append(md_table(["label", "CPU", "Python", "OS", "CPU dipatok", "baris", "putaran/sel", "semua correct", "berkas"],
                          [[l, m["cpu"], m["python_version"], m["os"], m["pinned_cpu"] or "-", m["rows"],
                            "/".join(map(str, m["runs_per_cell"])), m["all_correct"], os.path.basename(p)] for l, p, m, _ in machines]))
    if any(not m["all_correct"] for _, _, m, _ in machines):
        lines.append("**PERINGATAN: ada mesin dengan hasil dekripsi salah (correct=False); hasilnya tidak valid.**\n")

    cells = sorted({(b, k) for _, _, _, t in machines for (ly, mt, b, k) in t if ly == a.layer and b >= a.min_bits})
    labels = [l for l, _, _, _ in machines]

    def med(times, method, b, k):
        v = times.get((a.layer, method, b, k))
        return st.median(v) if v else None

    long_rows = []
    lines += ["", "## Waktu median RSA standar (ms)", ""]
    lines.append(md_table(["bits", "k"] + labels,
                          [[b, k] + [f"{med(t, 'standard', b, k) * 1e3:.3f}" if med(t, "standard", b, k) else "-" for _, _, _, t in machines]
                           for b, k in cells]))
    for method in a.methods.split(","):
        lines += ["", f"## Speedup {METHOD_NAME.get(method, method)}", ""]
        body = []
        for b, k in cells:
            row = [b, k]
            for label, _, _, t in machines:
                s, m = med(t, "standard", b, k), med(t, method, b, k)
                if s and m:
                    row.append(f"{s / m:.2f}")
                    long_rows.append([label, a.layer, method, b, k, f"{m:.9g}", f"{s:.9g}", f"{s / m:.4f}", len(t[(a.layer, method, b, k)])])
                else:
                    row.append("-")
            body.append(row)
        lines.append(md_table(["bits", "k"] + labels, body))

    text = "\n".join(lines) + "\n"
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["machine", "layer", "method", "bits", "k", "median_method_s", "median_standard_s", "speedup", "n_runs"])
            w.writerows(long_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())

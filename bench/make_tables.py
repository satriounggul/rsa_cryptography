#!/usr/bin/env python3
"""Menghasilkan tabel Markdown (results/tables.md) dari CSV hasil benchmark/audit. Tanpa dependensi luar."""
import argparse
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ap = argparse.ArgumentParser(description="Tabel Markdown dari CSV hasil benchmark")
_ap.add_argument("--dir", default=os.path.join(ROOT, "results"), help="folder hasil (default results/); tables.md ditulis di sini")
RES = os.path.abspath(_ap.parse_args().dir)
BITS = [64, 128, 256, 512, 1024, 2048, 3072, 4096]
KS = [2, 3, 4, 5]

summ = list(csv.DictReader(open(os.path.join(RES, "benchmark_summary.csv"), encoding="utf-8")))
cost = list(csv.DictReader(open(os.path.join(RES, "benchmark_cost.csv"), encoding="utf-8")))
cross = list(csv.DictReader(open(os.path.join(RES, "benchmark_crossover.csv"), encoding="utf-8")))
_aud = os.path.join(RES, "audit_keygen_bits.csv")  # hanya ada pada hasil audit baseline
keyaud = list(csv.DictReader(open(_aud))) if os.path.exists(_aud) else []
S = {(r["layer"], r["method"], int(r["bits_target"]), int(r["k"])): r for r in summ}
C = {(r["method"], int(r["bits_target"]), int(r["k"])): r for r in cost}
out = {}


def table(header, rows):
    s = "| " + " | ".join(header) + " |\n|" + "|".join("---" for _ in header) + "|\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s


def sp(layer, method, b, k, ci=True):
    r = S[(layer, method, b, k)]
    v = float(r["speedup"])
    if not ci:
        return f"{v:.2f}"
    return f"{v:.2f} [{float(r['speedup_ci95_lo']):.2f}–{float(r['speedup_ci95_hi']):.2f}]"


# T_KEYGEN (hanya bila ada hasil audit baseline)
if keyaud:
    rows = []
    for b in (64, 128, 256, 512, 1024, 2048):
        row = [b]
        for k in KS:
            r = [x for x in keyaud if int(x["bits_target"]) == b and int(x["k"]) == k][0]
            row.append(f"{r['exact_pct']}% (n={r['n_keys']}; min {r['min_bits']})")
        rows.append(row)
    out["T_KEYGEN"] = table(["bits target"] + [f"k={k}" for k in KS], rows)

# T_STD_MS
out["T_STD_MS"] = table(["bits"] + [f"k={k}" for k in KS],
                        [[b] + [f"{float(S[('core', 'standard', b, k)]['median_s']) * 1e3:.3f}" for k in KS] for b in BITS])

for name, layer, method in (("T_CORE_GARNER", "core", "crt_garner"), ("T_CORE_GAUSS_A", "core", "crt_gauss"),
                            ("T_CORE_GAUSS_B", "core", "crt_gauss_precomp")):
    out[name] = table(["bits"] + [f"k={k}" for k in KS], [[b] + [sp(layer, method, b, k) for k in KS] for b in BITS])

out["T_LEAN_GARNER"] = table(["bits"] + [f"k={k}" for k in KS], [[b] + [sp("lean", "crt_garner", b, k, False) for k in KS] for b in BITS])
out["T_BUILTIN_GARNER"] = table(["bits"] + [f"k={k}" for k in KS], [[b] + [sp("builtin", "crt_garner", b, k, False) for k in KS] for b in BITS])
out["T_LEAN_GAUSS_A"] = table(["bits"] + [f"k={k}" for k in KS], [[b] + [sp("lean", "crt_gauss", b, k, False) for k in KS] for b in BITS])

# T_COST (garner & gauss a)
for name, m in (("T_COST_GARNER", "crt_garner"), ("T_COST_GAUSS_A", "crt_gauss")):
    out[name] = table(["bits"] + [f"k={k} (k²={k * k})" for k in KS],
                      [[b] + [f"{float(C[(m, b, k)]['speedup_literal']):.2f} / {float(C[(m, b, k)]['speedup_refined']):.2f}" for k in KS] for b in BITS])

# T_EFF: speedup terukur (core, Garner) dibagi k^2
out["T_EFF"] = table(["bits"] + [f"k={k}" for k in KS],
                     [[b] + [f"{100 * float(S[('core', 'crt_garner', b, k)]['speedup']) / (k * k):.0f}%" for k in KS] for b in BITS])

# T_OPS: op_counter vs waktu
rows = []
for b in (256, 1024, 4096):
    for k in (2, 5):
        r = S[("core", "crt_garner", b, k)]
        g = S[("core", "crt_gauss", b, k)]
        rows.append([b, k, f"{float(r['ops_ratio_standard_over_method']):.3f}", f"{float(r['speedup']):.2f}",
                     f"{float(g['ops_ratio_standard_over_method']):.3f}", f"{float(g['speedup']):.2f}"])
out["T_OPS"] = table(["bits", "k", "rasio op_counter standar/Garner", "speedup waktu Garner", "rasio op_counter standar/Gauss(a)", "speedup waktu Gauss(a)"], rows)

# T_OVERHEAD: core/lean
rows = []
for b in (64, 128, 256, 512, 1024, 4096):
    row = [b]
    for m, k in (("standard", 2), ("crt_garner", 2), ("crt_garner", 5), ("crt_gauss", 5)):
        row.append(f"{float(S[('core', m, b, k)]['median_s']) / float(S[('lean', m, b, k)]['median_s']):.2f}×")
    rows.append(row)
out["T_OVERHEAD"] = table(["bits", "standar (k=2)", "Garner (k=2)", "Garner (k=5)", "Gauss (a) (k=5)"], rows)

# T_GAUSS_AB: biaya waktu inversi pada Gauss (a) relatif (b)
out["T_GAUSS_AB"] = table(["bits"] + [f"k={k}" for k in KS],
                          [[b] + [f"{float(S[('core', 'crt_gauss', b, k)]['median_s']) / float(S[('core', 'crt_gauss_precomp', b, k)]['median_s']):.3f}" for k in KS] for b in BITS])
out["T_GARNER_VS_GAUSSB"] = table(["bits"] + [f"k={k}" for k in KS],
                                  [[b] + [f"{float(S[('core', 'crt_garner', b, k)]['median_s']) / float(S[('core', 'crt_gauss_precomp', b, k)]['median_s']):.3f}" for k in KS] for b in BITS])

# T_VSK2: Garner k>=3 vs CRT k=2 dan vs standar k=2 (core)
rows = []
for b in BITS:
    rows.append([b] + [f"{float(S[('core', 'crt_garner', b, k)]['speedup_vs_garner_k2']):.2f}" for k in (3, 4, 5)] +
                [f"{float(S[('core', 'crt_garner', b, k)]['speedup_vs_standard_k2']):.2f}" for k in KS])
out["T_VSK2"] = table(["bits", "vs CRT-2: k=3", "k=4", "k=5", "vs standar-2: k=2", "k=3", "k=4", "k=5"], rows)

# T_CROSS
rows = []
for r in cross:
    if r["layer"] == "builtin":
        continue
    rows.append([r["layer"], r["method"], r["k"], r["crossover_bits"], r["bits_median_speedup_le_1"], r["bits_ci95_lo_le_1"],
                 r["min_speedup"], r["max_speedup"]])
out["T_CROSS"] = table(["layer", "metode", "k", "titik silang (bit)", "bits dgn median≤1", "bits dgn CI95-bawah≤1", "min speedup", "maks speedup"], rows)

# T_POST: verifikasi pasca-perbaikan (kode inti baru), results/benchmark_raw_post.csv
post_path = os.path.join(RES, "benchmark_raw_post.csv")
if os.path.exists(post_path):
    import statistics as st
    post = list(csv.DictReader(open(post_path)))

    def pmed(m, b, k, layer="core"):
        return st.median(float(r["time_s"]) for r in post if r["layer"] == layer and r["method"] == m
                         and r["bits_target"] == str(b) and r["k"] == str(k))
    rows = []
    for b in (256, 1024, 2048):
        for k in (2, 3, 5):
            g = pmed("crt_garner", b, k)
            rows.append([b, k, f"{pmed('standard', b, k) * 1e3:.3f}", f"{g * 1e3:.3f}",
                         f"{pmed('crt_gauss', b, k) * 1e3:.3f} (×{pmed('crt_gauss', b, k) / g:.3f})",
                         f"{pmed('crt_gauss_default', b, k) * 1e3:.3f} (×{pmed('crt_gauss_default', b, k) / g:.3f})"])
    out["T_POST"] = table(["bits", "k", "standar (ms)", "Garner (ms)", "Gauss legacy (ms) (rasio thd Garner)", "Gauss default baru (ms) (rasio thd Garner)"], rows)

with open(os.path.join(RES, "tables.md"), "w") as fh:
    for k, v in out.items():
        fh.write(f"<!--{k}-->\n{v}\n")
print("tables:", ", ".join(out))

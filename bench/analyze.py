#!/usr/bin/env python3
"""
Ringkasan statistik, titik silang, dan grafik dari results/benchmark_raw.csv (+ benchmark_cost.csv).

Keluaran:
  results/benchmark_summary.csv    median, IQR, rata-rata, simpangan baku, speedup + CI95 bootstrap (1000x)
  results/benchmark_crossover.csv  titik silang per (layer, metode, k) sesuai definisi pra-registrasi
  results/figures/*.png            grafik 1-3

Jalankan dengan interpreter venv (matplotlib): bench/.venv/bin/python bench/analyze.py
Definisi titik silang (pra-registrasi): bits_target terkecil di grid yang untuk SEMUA bits_target >= itu
memiliki batas bawah CI95 speedup > 1.
"""
import argparse
import csv
import os
import random
import statistics as st
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "results")   # folder hasil; dapat diganti dengan --dir
FIG = os.path.join(RES, "figures")
RAW = os.path.join(RES, "benchmark_raw.csv")
BOOT = 1000
LAYERS = ["core", "lean", "builtin"]
COLORS = {"standard": "#2a78d6", "crt_garner": "#eb6834", "crt_gauss": "#1baf7a", "crt_gauss_precomp": "#eda100"}
KCOL = {2: "#2a78d6", 3: "#eb6834", 4: "#1baf7a", 5: "#eda100"}
LABEL = {"standard": "RSA standar", "crt_garner": "CRT-Garner", "crt_gauss": "CRT-Gauss (a) invers saat dekripsi",
         "crt_gauss_precomp": "CRT-Gauss (b) koefisien diprekomputasi"}
SHORT = {"crt_garner": "CRT-Garner", "crt_gauss": "CRT-Gauss (a)", "crt_gauss_precomp": "CRT-Gauss (b)"}


def quartiles(x):
    q = st.quantiles(x, n=4, method="inclusive")
    return q[0], q[2]


def boot_ratio(num, den, rng, B=BOOT):
    vals = []
    ln, ld = len(num), len(den)
    for _ in range(B):
        a = st.median(rng.choices(num, k=ln))
        b = st.median(rng.choices(den, k=ld))
        vals.append(a / b)
    vals.sort()
    return vals[int(0.025 * B)], vals[int(0.975 * B) - 1]


def load_raw():
    data = defaultdict(list)
    ops = defaultdict(list)
    actual = {}
    ok = defaultdict(lambda: True)
    meta = {}
    with open(RAW, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key = (r["layer"], r["method"], int(r["bits_target"]), int(r["k"]))
            data[key].append((int(r["run_id"]), float(r["time_s"])))
            if r["total_operations"] != "":
                ops[key].append(int(r["total_operations"]))
            actual[key] = int(r["bits_actual"])
            ok[key] &= (r["correct"] == "True")
            meta = {f: r[f] for f in ("python_version", "os", "cpu", "pinned_cpu", "hostname") if f in r}
    for key in data:
        data[key] = [t for _, t in sorted(data[key])]
    return data, ops, actual, ok, meta


def main() -> int:
    global RES, FIG, RAW
    ap = argparse.ArgumentParser(description="Ringkasan statistik, titik silang, dan grafik dari benchmark_raw*.csv")
    ap.add_argument("--dir", default=RES, help="folder hasil (keluaran ditulis di sini; default results/)")
    ap.add_argument("--raw", default=None, help="berkas CSV mentah (default <dir>/benchmark_raw.csv)")
    args = ap.parse_args()
    RES = os.path.abspath(args.dir)
    FIG = os.path.join(RES, "figures")
    RAW = os.path.abspath(args.raw) if args.raw else os.path.join(RES, "benchmark_raw.csv")
    data, ops, actual, ok, meta = load_raw()
    rng = random.Random(424242)
    bits_list = sorted({k[2] for k in data})
    k_list = sorted({k[3] for k in data})
    rows = []
    for (layer, method, bits, k), times in sorted(data.items(), key=lambda kv: (LAYERS.index(kv[0][0]), kv[0][1], kv[0][2], kv[0][3])):
        q1, q3 = quartiles(times)
        row = dict(layer=layer, method=method, bits_target=bits, bits_actual=actual[(layer, method, bits, k)], k=k,
                   n_runs=len(times), median_s=st.median(times), q1_s=q1, q3_s=q3, iqr_s=q3 - q1, mean_s=st.mean(times),
                   stdev_s=st.stdev(times), min_s=min(times), max_s=max(times))
        std = data[(layer, "standard", bits, k)]
        sp, lo, hi = "", "", ""
        if method != "standard":
            sp = st.median(std) / st.median(times)
            lo, hi = boot_ratio(std, times, rng)
        elif True:
            sp, lo, hi = 1.0, 1.0, 1.0
        row.update(speedup=sp, speedup_ci95_lo=lo, speedup_ci95_hi=hi)
        # pembanding lintas-k: standar k=2 dan CRT-Garner k=2 pada bits dan layer yang sama
        std2 = data.get((layer, "standard", bits, 2))
        g2 = data.get((layer, "crt_garner", bits, 2))
        for nm, ref in (("vs_standard_k2", std2), ("vs_garner_k2", g2)):
            if ref is None or (nm == "vs_standard_k2" and method == "standard" and k == 2) or \
                    (nm == "vs_garner_k2" and method == "crt_garner" and k == 2):
                row[f"speedup_{nm}"] = row[f"speedup_{nm}_lo"] = row[f"speedup_{nm}_hi"] = ""
                continue
            row[f"speedup_{nm}"] = st.median(ref) / st.median(times)
            a, b = boot_ratio(ref, times, rng)
            row[f"speedup_{nm}_lo"], row[f"speedup_{nm}_hi"] = a, b
        o = ops.get((layer, method, bits, k))
        row["mean_total_operations"] = st.mean(o) if o else ""
        so = ops.get((layer, "standard", bits, k))
        row["ops_ratio_standard_over_method"] = (st.mean(so) / st.mean(o)) if (o and so) else ""
        row["correct_all"] = ok[(layer, method, bits, k)]
        rows.append(row)
    fields = list(rows[0])
    with open(os.path.join(RES, "benchmark_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"summary: {len(rows)} baris; semua hasil benar = {all(r['correct_all'] for r in rows)}")

    # ---------------- titik silang ----------------
    idx = {(r["layer"], r["method"], r["bits_target"], r["k"]): r for r in rows}
    cross = []
    for layer in LAYERS:
        for method in ("crt_garner", "crt_gauss", "crt_gauss_precomp"):
            for k in k_list:
                if (layer, method, bits_list[0], k) not in idx:
                    continue
                series = [(b, idx[(layer, method, b, k)]) for b in bits_list if (layer, method, b, k) in idx]
                win = {b: r["speedup_ci95_lo"] > 1.0 for b, r in series}
                cross_bits = None
                for b, _ in series:
                    if all(win[b2] for b2, _ in series if b2 >= b):
                        cross_bits = b
                        break
                losers = [b for b, r in series if r["speedup"] <= 1.0]
                not_sig = [b for b, r in series if r["speedup_ci95_lo"] <= 1.0]
                cross.append(dict(layer=layer, method=method, k=k,
                                  crossover_bits=cross_bits if cross_bits is not None else "tidak ada",
                                  bits_median_speedup_le_1=" ".join(map(str, losers)) or "-",
                                  bits_ci95_lo_le_1=" ".join(map(str, not_sig)) or "-",
                                  min_speedup=round(min(r["speedup"] for _, r in series), 3),
                                  max_speedup=round(max(r["speedup"] for _, r in series), 3)))
    with open(os.path.join(RES, "benchmark_crossover.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cross[0]))
        w.writeheader()
        w.writerows(cross)
    print("crossover: ditulis", len(cross), "baris")

    # ---------------- grafik ----------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(FIG, exist_ok=True)
    plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                         "text.color": "#0b0b0b", "axes.labelcolor": "#52514e", "xtick.color": "#52514e",
                         "ytick.color": "#52514e", "axes.edgecolor": "#c3c2b7", "axes.spines.top": False,
                         "axes.spines.right": False, "grid.color": "#e4e3de", "grid.linewidth": 0.6, "font.size": 9})
    foot = (f"{meta['cpu']} | Python {meta['python_version']} | CPU dipatok #{meta['pinned_cpu']} | "
            f"median {len(next(iter(data.values())))} putaran" + (f" | host {meta['hostname']}" if "hostname" in meta else ""))

    def style(ax):
        ax.grid(True, which="major", axis="y")
        ax.set_axisbelow(True)

    # Grafik 1: waktu median vs bits (log-log), per k
    def fig_time(layers_methods, fname, title):
        fig, axes = plt.subplots(1, len(k_list), figsize=(3.6 * len(k_list), 3.7), sharey=True)
        for ax, k in zip(axes, k_list):
            for layer, method, ls, mk in layers_methods:
                pts = [(b, idx[(layer, method, b, k)]) for b in bits_list if (layer, method, b, k) in idx]
                if not pts:
                    continue
                xs = [b for b, _ in pts]
                med = [r["median_s"] for _, r in pts]
                lo = [r["q1_s"] for _, r in pts]
                hi = [r["q3_s"] for _, r in pts]
                lab = f"{LABEL[method]} [{layer}]" if layer != "core" or len(layers_methods) > 4 else LABEL[method]
                # garis/marker berbeda per metode: Garner dan Gauss (b) hampir berimpit, jangan saling menutupi
                sty = {"standard": ("-", "o", 5, 1.8), "crt_garner": ("-", "s", 6, 2.4),
                       "crt_gauss": ("--", "^", 5, 1.5), "crt_gauss_precomp": ((0, (1, 1.6)), "D", 3.5, 1.5)}[method]
                ax.plot(xs, med, linestyle=ls if layer != "core" else sty[0], color=COLORS[method], marker=sty[1] if layer == "core" else mk,
                        ms=sty[2], lw=sty[3], label=lab, zorder=3 if method == "crt_gauss_precomp" else 2)
                ax.fill_between(xs, lo, hi, color=COLORS[method], alpha=0.15, lw=0)
            ax.set_xscale("log", base=2)
            ax.set_yscale("log")
            ax.set_xticks(bits_list)
            ax.set_xticklabels([str(b) for b in bits_list], rotation=45)
            ax.minorticks_off()
            ax.set_title(f"k = {k}", fontsize=10, color="#0b0b0b")
            ax.set_xlabel("panjang modulus n (bit)")
            style(ax)
        axes[0].set_ylabel("waktu dekripsi median (detik)")
        h, l = axes[0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=min(len(l), 3), frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.045))
        fig.suptitle(title, fontsize=11, x=0.01, ha="left")
        fig.text(0.01, 0.005, foot, fontsize=6.5, color="#52514e", ha="left", va="bottom")
        fig.tight_layout(rect=(0, 0.2, 1, 0.94))
        fig.savefig(os.path.join(FIG, fname), dpi=150)
        plt.close(fig)

    fig_time([("core", m, "-", "o") for m in ("standard", "crt_garner", "crt_gauss", "crt_gauss_precomp")],
             "fig1_waktu_core.png", "Grafik 1a. Waktu dekripsi vs panjang modulus (kode core apa adanya; pita = IQR)")
    fig_time([("lean", m, "-", "o") for m in ("standard", "crt_garner", "crt_gauss", "crt_gauss_precomp")] +
             [("builtin", m, ":", "s") for m in ("standard", "crt_garner")],
             "fig1b_waktu_lean_builtin.png", "Grafik 1b. Waktu dekripsi: lean (tanpa instrumentasi, garis) dan pow() bawaan (titik-titik, informatif)")

    # Grafik 2: speedup vs bits, per metode, warna = k
    def fig_speed(layer, methods, fname, title):
        fig, axes = plt.subplots(1, len(methods), figsize=(3.9 * len(methods), 3.8), sharey=True, squeeze=False)
        for ax, method in zip(axes[0], methods):
            for k in k_list:
                pts = [(b, idx[(layer, method, b, k)]) for b in bits_list if (layer, method, b, k) in idx]
                if not pts:
                    continue
                xs = [b for b, _ in pts]
                ax.plot(xs, [r["speedup"] for _, r in pts], "-o", color=KCOL[k], ms=4, lw=1.6, label=f"k = {k}")
                ax.fill_between(xs, [r["speedup_ci95_lo"] for _, r in pts], [r["speedup_ci95_hi"] for _, r in pts],
                                color=KCOL[k], alpha=0.18, lw=0)
                ax.annotate(f"k={k}", (xs[-1], pts[-1][1]["speedup"]), xytext=(4, 0), textcoords="offset points",
                            fontsize=7, color="#52514e", va="center")
            ax.axhline(1.0, color="#52514e", lw=1, ls="--")
            ax.set_xscale("log", base=2)
            ax.set_xticks(bits_list)
            ax.set_xticklabels([str(b) for b in bits_list], rotation=45)
            ax.minorticks_off()
            ax.set_xlim(right=bits_list[-1] * 1.5)
            ax.set_title(SHORT.get(method, method) + (" (pow bawaan)" if layer == "builtin" else ""), fontsize=10)
            ax.set_xlabel("panjang modulus n (bit)")
            style(ax)
        axes[0][0].set_ylabel("speedup = median(standar) / median(metode)")
        h, l = axes[0][0].get_legend_handles_labels()
        axes[0][0].legend(h, l, frameon=False, fontsize=8, loc="upper left")
        fig.suptitle(title, fontsize=11, x=0.01, ha="left")
        fig.text(0.01, 0.005, foot + " | pita = CI95 bootstrap (1000x) | garis putus-putus: speedup = 1", fontsize=6.5,
                 color="#52514e", ha="left", va="bottom")
        fig.tight_layout(rect=(0, 0.04, 1, 0.93))
        fig.savefig(os.path.join(FIG, fname), dpi=150)
        plt.close(fig)

    fig_speed("core", ["crt_garner", "crt_gauss", "crt_gauss_precomp"], "fig2_speedup_core.png",
              "Grafik 2a. Speedup dekripsi terhadap RSA standar (kode core apa adanya)")
    fig_speed("lean", ["crt_garner", "crt_gauss", "crt_gauss_precomp"], "fig2b_speedup_lean.png",
              "Grafik 2b. Speedup dekripsi terhadap RSA standar (lean: tanpa instrumentasi)")
    fig_speed("builtin", ["crt_garner"], "fig2c_speedup_builtin.png",
              "Grafik 2c. Speedup dengan pow() bawaan (baseline informatif)")

    # Grafik 3: model biaya berbobot-bit
    cpath = os.path.join(RES, "benchmark_cost.csv")
    if os.path.exists(cpath):
        cost = defaultdict(dict)
        for r in csv.DictReader(open(cpath, encoding="utf-8")):
            cost[(r["method"], int(r["bits_target"]), int(r["k"]))] = r
        for field, tag, ttl in (("speedup_literal", "literal", "bl(a)xbl(b) untuk perkalian dan modulo (definisi tugas)"),
                                ("speedup_refined", "refined", "perkalian bl(a)xbl(b); modulo = kuosien x pembagi")):
            fig, axes = plt.subplots(1, 3, figsize=(11.7, 3.8), sharey=True)
            for ax, method in zip(axes, ["crt_garner", "crt_gauss", "crt_gauss_precomp"]):
                for k in k_list:
                    pts = [(b, float(cost[(method, b, k)][field])) for b in bits_list if (method, b, k) in cost]
                    if not pts:
                        continue
                    ax.plot([b for b, _ in pts], [v for _, v in pts], "-o", color=KCOL[k], ms=4, lw=1.6, label=f"k = {k}")
                    ax.axhline(k * k, color=KCOL[k], lw=0.8, ls=":")
                ax.set_xscale("log", base=2)
                ax.set_xticks(bits_list)
                ax.set_xticklabels([str(b) for b in bits_list], rotation=45)
                ax.minorticks_off()
                ax.set_title(SHORT[method], fontsize=10)
                ax.set_xlabel("panjang modulus n (bit)")
                style(ax)
            axes[0].set_ylabel("biaya relatif = biaya(standar) / biaya(metode)")
            h, l = axes[0].get_legend_handles_labels()
            fig.legend(h, l, loc="lower center", ncol=len(l), frameon=False, fontsize=8, bbox_to_anchor=(0.5, 0.045))
            fig.suptitle(f"Grafik 3 ({tag}). Biaya berbobot-bit relatif: {ttl}", fontsize=11, x=0.01, ha="left")
            fig.text(0.01, 0.005, "garis titik-titik berwarna: model ideal k^2 untuk k yang sama", fontsize=6.5,
                     color="#52514e", ha="left", va="bottom")
            fig.tight_layout(rect=(0, 0.12, 1, 0.93))
            fig.savefig(os.path.join(FIG, f"fig3_biaya_{tag}.png"), dpi=150)
            plt.close(fig)
    print("grafik ditulis ke", os.path.relpath(FIG, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())

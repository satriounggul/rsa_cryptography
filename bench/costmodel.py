#!/usr/bin/env python3
"""
Model biaya berbobot-bit untuk tiap metode dekripsi (tidak bergantung pada overhead interpreter Python).

Biaya tiap perkalian/modulo/pembagian dihitung dari panjang bit operan (lihat variants.Cost):
  literal : bl(a) * bl(b)                      (definisi tugas)
  refined : perkalian bl(a)*bl(b); modulo/pembagian = (panjang kuosien) x (panjang pembagi)
Kunci dan ciphertext identik dengan benchmark.py (kunci dari results/benchmark_keys.json, seed sama).

Keluaran: results/benchmark_cost.csv
Jalankan SETELAH benchmark selesai: PYTHONDONTWRITEBYTECODE=1 python3 bench/costmodel.py
"""
import argparse
import csv
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import variants as V  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-ct", type=int, default=30)
    ap.add_argument("--use", type=int, default=10, help="berapa ciphertext pertama yang dipakai (biaya hampir deterministik)")
    ap.add_argument("--seed", type=int, default=20261028)
    ap.add_argument("--tag", default="", help="(lama) akhiran berkas kunci/biaya pada results/")
    ap.add_argument("--dir", default=os.path.join(ROOT, "results"), help="folder keluaran (default results/)")
    ap.add_argument("--keys", default=None, help="berkas kunci benchmark (default <dir>/benchmark_keys<tag>.json)")
    ap.add_argument("--meta", default=None, help="benchmark_meta*.json; bila ada, seed diambil dari sini")
    a = ap.parse_args()
    suffix = f"_{a.tag}" if a.tag else ""
    out_dir = os.path.abspath(a.dir)
    keys_path = a.keys or os.path.join(out_dir, f"benchmark_keys{suffix}.json")
    if a.meta:
        with open(a.meta, encoding="utf-8") as fh:
            a.seed = json.load(fh)["config"]["seed"]
    with open(keys_path, encoding="utf-8") as fh:
        stored = json.load(fh)
    print(f"[biaya] kunci={keys_path} seed={a.seed} ciphertext_dipakai={a.use}", flush=True)
    out_rows = []
    for name in sorted(stored, key=lambda s: tuple(map(int, s.split("-")))):
        bits, k = map(int, name.split("-"))
        key = stored[name]["key"]
        priv = dict(key["private_key"])
        priv["gauss_coeffs"] = V.gauss_precompute(priv)
        ms, cs = V.make_plaintexts_and_ciphertexts(key, a.n_ct, seed=a.seed + bits * 10 + k)
        per_method = {}
        for mname, fn in V.COST_METHODS.items():
            lit, ref, nmul, nmod, ndiv, ok = [], [], [], [], [], True
            for c, m in zip(cs[:a.use], ms[:a.use]):
                res, cost = fn(c, priv)
                ok &= (res == m)
                lit.append(cost.lit)
                ref.append(cost.ref)
                nmul.append(cost.n_mul)
                nmod.append(cost.n_mod)
                ndiv.append(cost.n_div)
            per_method[mname] = dict(lit=st.mean(lit), ref=st.mean(ref), n_mul=st.mean(nmul), n_mod=st.mean(nmod),
                                     n_div=st.mean(ndiv), ok=ok)
        base = per_method["standard"]
        for mname, r in per_method.items():
            out_rows.append(dict(
                bits_target=bits, bits_actual=key["public_key"]["bits"], k=k, method=mname, n_ciphertexts=a.use,
                cost_literal=round(r["lit"]), cost_refined=round(r["ref"]),
                n_mul=round(r["n_mul"], 1), n_mod=round(r["n_mod"], 1), n_div=round(r["n_div"], 1),
                speedup_literal=round(base["lit"] / r["lit"], 3), speedup_refined=round(base["ref"] / r["ref"], 3),
                correct=r["ok"]))
            if not r["ok"]:
                print(f"[GAGAL] hasil salah pada model biaya: bits={bits} k={k} {mname}")
                return 2
        print(f"bits={bits:5d} k={k}: " + "  ".join(
            f"{m}: lit x{base['lit'] / r['lit']:.2f} ref x{base['ref'] / r['ref']:.2f}" for m, r in per_method.items() if m != "standard"),
            flush=True)
    path = os.path.join(out_dir, f"benchmark_cost{suffix}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)
    print("->", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

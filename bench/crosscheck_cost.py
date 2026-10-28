#!/usr/bin/env python3
"""
Pemeriksaan silang dua implementasi independen biaya berbobot-bit:
  (1) core.op_counter.OperationCounter(track_bits=True) yang dipanggil di dalam decrypt_* kode inti, dan
  (2) bench/variants.py (COST_METHODS), instrumentasi terpisah dengan urutan operasi yang ditulis ulang.
Untuk standar, Garner, dan Gauss (b) kedua angka (literal dan refined) HARUS identik.
Gauss (a) dikecualikan dari kesetaraan: penghitung inti tidak menghitung modinv, model bench menghitungnya.

Keluaran dicetak (disimpan ke results/final/costmodel_crosscheck.txt oleh pemanggil).
Pemakaian: python3 bench/crosscheck_cost.py --keys results/final/benchmark_keys_<host>.json --meta results/final/benchmark_meta_<host>.json
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import variants as V  # noqa: E402
from core.op_counter import OperationCounter  # noqa: E402
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--use", type=int, default=10)
    ap.add_argument("--n-ct", type=int, default=30)
    a = ap.parse_args()
    with open(a.meta, encoding="utf-8") as fh:
        seed = json.load(fh)["config"]["seed"]
    with open(a.keys, encoding="utf-8") as fh:
        stored = json.load(fh)

    checked = mismatched = 0
    gauss_a = []
    for name in sorted(stored, key=lambda s: tuple(map(int, s.split("-")))):
        bits, k = map(int, name.split("-"))
        key = stored[name]["key"]
        priv = dict(key["private_key"])
        priv.setdefault("gauss_coeffs", V.gauss_precompute(priv))
        n, d = priv["n"], priv["d"]
        ms, cs = V.make_plaintexts_and_ciphertexts(key, a.n_ct, seed=seed + bits * 10 + k)
        for c, m in list(zip(cs, ms))[:a.use]:
            core_runs = {
                "standard": lambda oc: decrypt_standard(c, d, n, op_counter=oc),
                "crt_garner": lambda oc: decrypt_crt_garner(c, priv, op_counter=oc),
                "crt_gauss_precomp": lambda oc: decrypt_crt_gauss(c, priv, op_counter=oc, use_precomputed=True),
            }
            for method, run in core_runs.items():
                out, steps = run(OperationCounter(track_bits=True))
                ops = steps["operation_counts"]
                res, cost = V.COST_METHODS[method](c, priv)
                same = (out == m == res and ops["weighted_cost"] == cost.lit and ops["weighted_cost_schoolbook"] == cost.ref)
                checked += 1
                if not same:
                    mismatched += 1
                    print(f"BEDA bits={bits} k={k} metode={method}: inti lit={ops['weighted_cost']} ref={ops['weighted_cost_schoolbook']} "
                          f"| bench lit={cost.lit} ref={cost.ref}")
            # Gauss (a): inti (tanpa modinv) vs bench (dengan modinv)
            out, steps = decrypt_crt_gauss(c, priv, op_counter=OperationCounter(track_bits=True), use_precomputed=False)
            ops = steps["operation_counts"]
            res, cost = V.COST_METHODS["crt_gauss"](c, priv)
            assert out == m == res
            gauss_a.append((bits, k, ops["weighted_cost"], cost.lit, ops["weighted_cost_schoolbook"], cost.ref))
    print(f"Pemeriksaan silang biaya berbobot-bit: {checked} perbandingan (32 kunci x {a.use} ciphertext x 3 metode)")
    print(f"identik (literal DAN refined, plus plaintext benar): {checked - mismatched} dari {checked}; berbeda: {mismatched}")
    extra = [(l1 and (b2 - l1) / b2) for (_, _, l1, b2, _, _) in gauss_a]
    print("Gauss (a): biaya literal inti < model bench pada semua kasus (modinv tidak dihitung inti):",
          all(g[2] < g[3] for g in gauss_a), f"| selisih relatif rata-rata = {100 * sum(extra) / len(extra):.2f}%")
    return 0 if mismatched == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

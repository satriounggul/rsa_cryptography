"""
Audit 1b: core/keygen.py. Read-only terhadap core/. pow() dipakai hanya sebagai oracle.

(1) sebaran n.bit_length() aktual vs target, per (bits, k)
(2) pemilihan e (65537 vs fallback)
(3) d dari phi vs lambda (ukuran d, kesamaan d_i)
(4) d_i = d mod (p_i-1): apakah cabang "di == 0 -> p_i-1" pernah aktif; uji eksaustif semua c untuk n kecil
(5) koefisien Garner t_i vs oracle pow(x,-1,m)

Jalankan: PYTHONDONTWRITEBYTECODE=1 python3 bench/audit_keygen.py
Keluaran ringkas ke results/audit_keygen_bits.csv
"""
import csv
import multiprocessing as mp
import os
import random
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.keygen import generate_keys, compute_lambda  # noqa: E402
from core.number_theory import modinv  # noqa: E402
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402


def one_key(args):
    bits, k = args
    key = generate_keys(bits, k)
    pub, priv = key["public_key"], key["private_key"]
    primes, e, d, n = priv["primes"], priv["e"], priv["d"], priv["n"]
    lam = compute_lambda(primes)
    d_lam = modinv(e, lam)
    same_di = all(d % (p - 1) == d_lam % (p - 1) for p in primes)
    di_zero = any(d % (p - 1) == 0 for p in primes)
    t_ok = True
    acc = primes[0]
    for idx, t in enumerate(priv["t_coeffs"]):
        p = primes[idx + 1]
        if t != pow(acc % p, -1, p):  # oracle
            t_ok = False
        acc *= p
    return (pub["bits"], e == 65537, d.bit_length(), d_lam.bit_length(), same_di, di_zero, t_ok,
            n.bit_length() == pub["bits"], len(set(primes)) == k)


def distribution():
    combos = []
    for bits in (64, 128, 256, 512, 1024, 2048):
        n_keys = 200 if bits <= 1024 else 100
        for k in (2, 3, 4, 5):
            combos.append((bits, k, n_keys))
    rows = []
    with mp.get_context("fork").Pool(12) as pool:
        for bits, k, n_keys in combos:
            res = pool.map(one_key, [(bits, k)] * n_keys, chunksize=4)
            actual = Counter(r[0] for r in res)
            miss = n_keys - actual.get(bits, 0)
            short_hist = {s: actual.get(bits - s, 0) for s in range(0, k + 1)}
            other = n_keys - sum(short_hist.values())
            e_std = sum(r[1] for r in res)
            dphi_minus_dlam = [r[2] - r[3] for r in res]
            row = dict(
                bits_target=bits, k=k, n_keys=n_keys,
                exact_pct=round(100 * actual.get(bits, 0) / n_keys, 1),
                short1_pct=round(100 * short_hist.get(1, 0) / n_keys, 1),
                short2_pct=round(100 * short_hist.get(2, 0) / n_keys, 1),
                short3_pct=round(100 * short_hist.get(3, 0) / n_keys, 1),
                short4plus_pct=round(100 * (sum(v for s, v in short_hist.items() if s >= 4) + other) / n_keys, 1),
                meleset_pct=round(100 * miss / n_keys, 1),
                min_bits=min(actual), max_bits=max(actual),
                e65537_pct=round(100 * e_std / n_keys, 1),
                dphi_minus_dlam_bits_mean=round(sum(dphi_minus_dlam) / n_keys, 2),
                dphi_minus_dlam_bits_max=max(dphi_minus_dlam),
                same_di_all=all(r[4] for r in res),
                di_zero_branch_hits=sum(r[5] for r in res),
                t_coeffs_all_correct=all(r[6] for r in res),
                primes_all_distinct=all(r[8] for r in res),
            )
            rows.append(row)
            print(f"bits={bits:5d} k={k} keys={n_keys:3d} | n tepat={row['exact_pct']:5.1f}%  meleset={row['meleset_pct']:5.1f}%"
                  f"  (-1:{row['short1_pct']}% -2:{row['short2_pct']}% -3:{row['short3_pct']}% >=4:{row['short4plus_pct']}%)"
                  f"  rentang aktual=[{row['min_bits']},{row['max_bits']}]  e=65537:{row['e65537_pct']}%"
                  f"  d_phi-d_lam(bit) mean={row['dphi_minus_dlam_bits_mean']} max={row['dphi_minus_dlam_bits_max']}"
                  f"  d_i sama={row['same_di_all']}  di==0:{row['di_zero_branch_hits']}  t_i benar={row['t_coeffs_all_correct']}",
                  flush=True)
    with open(os.path.join(ROOT, "results", "audit_keygen_bits.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# Uji eksaustif semua c in [0,n) dipindah ke bench/audit_exhaustive.py (versi lama memuat (16,4) yang membuat generate_keys menggantung;
# lihat bench/audit_keygen_hang.py).


def multiples_of_primes_large():
    print("\n=== Ciphertext kelipatan p_i pada kunci besar (c = j*p_i, plus c=0) ===")
    rng = random.Random(7)
    bad = Counter()
    cnt = 0
    for bits, k in [(256, 2), (256, 3), (512, 4), (1024, 5), (512, 2)]:
        key = generate_keys(bits, k)
        priv = key["private_key"]
        n, d = priv["n"], priv["d"]
        for p in priv["primes"]:
            for _ in range(10):
                c = (rng.randrange(1, n // p)) * p
                want = pow(c, d, n)
                cnt += 1
                if decrypt_crt_garner(c, priv)[0] != want:
                    bad["garner"] += 1
                if decrypt_crt_gauss(c, priv)[0] != want:
                    bad["gauss"] += 1
                if decrypt_standard(c, d, n)[0] != want:
                    bad["standard"] += 1
    print(f"uji={cnt}, kegagalan={dict(bad) or 'TIDAK ADA'}")


if __name__ == "__main__":
    print("=== (1)-(5): sebaran bit_length, e, d(phi vs lambda), d_i, t_i ===")
    distribution()
    multiples_of_primes_large()

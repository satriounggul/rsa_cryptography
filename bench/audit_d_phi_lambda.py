#!/usr/bin/env python3
"""
Membandingkan d berbasis phi(n) (yang dipakai kode) dengan d berbasis lambda(n) (rumusan RFC 8017) pada kunci acak kode final:
  (1) d_i = d mod (p_i - 1) identik untuk kedua d (setelah penyesuaian nol -> p_i - 1);
  (2) selisih panjang bit d_phi - d_lambda (hanya memengaruhi dekripsi standar, c^d mod n);
  (3) c^d_phi mod n = c^d_lambda mod n untuk 5 ciphertext per kunci (pembanding pow()).
Acak (secrets); hasil berbeda tiap jalan. Pemakaian: python3 bench/audit_d_phi_lambda.py > results/final/audit_d_phi_lambda.txt
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.keygen import generate_keys, compute_lambda  # noqa: E402
from core.number_theory import modinv  # noqa: E402

rng = random.Random(20261028)
N = 40
diffs, keys, same_di, same_dec, tot_ct = [], 0, 0, 0, 0
for bits in (64, 128, 256, 512, 1024):
    for k in (2, 3, 4, 5):
        for _ in range(N):
            priv = generate_keys(bits, k)["private_key"]
            n, e, d_phi, primes = priv["n"], priv["e"], priv["d"], priv["primes"]
            lam = compute_lambda(primes)
            d_lam = modinv(e, lam)
            keys += 1
            diffs.append(d_phi.bit_length() - d_lam.bit_length())
            di_phi = [(d_phi % (p - 1)) or (p - 1) for p in primes]
            di_lam = [(d_lam % (p - 1)) or (p - 1) for p in primes]
            same_di += di_phi == di_lam == priv["d_primes"]
            for _ in range(5):
                c = rng.randrange(0, n)
                tot_ct += 1
                same_dec += pow(c, d_phi, n) == pow(c, d_lam, n)
print(f"kunci acak: {keys} (bits 64..1024 x k 2..5 x {N}); ciphertext: {tot_ct}")
print(f"d_i identik (phi, lambda, dan d_primes di kunci): {same_di} dari {keys}")
print(f"c^d_phi mod n == c^d_lambda mod n: {same_dec} dari {tot_ct}")
print(f"selisih panjang bit d_phi - d_lambda: min {min(diffs)}, maks {max(diffs)}, d_phi lebih panjang pada {sum(x > 0 for x in diffs)} dari {keys} kunci; negatif pada {sum(x < 0 for x in diffs)}")
sys.exit(0 if same_di == keys and same_dec == tot_ct else 1)

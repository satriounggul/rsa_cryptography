#!/usr/bin/env python3
"""Sampel ukuran bit tiap prima dari generate_keys (kode final): rencana vs hasil. Acak (secrets); hasil berbeda tiap jalan.
Pemakaian: python3 bench/audit_prime_sizes.py > results/final/ukuran_prima_sampel.txt"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.keygen import generate_keys  # noqa: E402

N = 30
print(f"Sampel {N} kunci per konfigurasi; tiap sel = ukuran bit prima terurut -> banyak kunci; rencana = bits//k (+1 untuk sebagian prima)")
for bits, k in [(512, 5), (1024, 3), (2048, 4), (4096, 5)]:
    c = collections.Counter()
    exact = 0
    for _ in range(N):
        key = generate_keys(bits, k)["private_key"]
        exact += key["n"].bit_length() == bits
        c[tuple(sorted(p.bit_length() for p in key["primes"]))] += 1
    print(f"bits={bits} k={k}: n.bit_length()==bits pada {exact}/{N} kunci")
    for sizes, cnt in sorted(c.items(), key=lambda kv: -kv[1]):
        print(f"   {sizes}: {cnt}")

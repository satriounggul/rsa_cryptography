"""Uji eksaustif ringan: untuk kunci kecil, bandingkan 3 metode dengan pow(c,d,n) untuk SEMUA c in [0,n) (oracle pow)."""
import os, sys
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from core.keygen import generate_keys
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss
bad, total, keys = Counter(), 0, 0
dead_branch = 0
for bits, k in [(16, 2), (16, 3), (17, 2), (17, 3)]:
    for _ in range(3):
        key = generate_keys(bits, k); priv = key["private_key"]; n, d = priv["n"], priv["d"]
        if any(d % (p - 1) == 0 for p in priv["primes"]): dead_branch += 1
        keys += 1
        for c in range(n):
            want = pow(c, d, n); total += 1
            if decrypt_standard(c, d, n)[0] != want: bad["standard"] += 1
            if decrypt_crt_garner(c, priv)[0] != want: bad["garner"] += 1
            if decrypt_crt_gauss(c, priv)[0] != want: bad["gauss"] += 1
print(f"kunci={keys} (bits 16-17, k 2-3), total pasangan (kunci,c)={total}, semua c in [0,n) termasuk kelipatan p_i dan 0")
print("kegagalan:", dict(bad) or "TIDAK ADA", "| kunci dengan d mod (p_i-1)==0:", dead_branch)

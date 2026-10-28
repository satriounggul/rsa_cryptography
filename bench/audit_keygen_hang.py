"""Enumerasi kombinasi (bits,k) pada rentang API (bits 16..4096, k 2..8, bits//k>=4) yang TIDAK mungkin
dipenuhi: jumlah prima berpanjang s-bit yang berbeda < jumlah yang dibutuhkan -> loop 'prima berbeda' tak berakhir."""
import os, sys
from collections import Counter
def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
count = {s: sum(1 for x in range(1 << (s - 1), 1 << s) if is_prime(x)) for s in range(2, 15)}
bad = []
for k in range(2, 9):
    for bits in range(16, 4097):
        if bits // k < 4: continue
        base, rem = divmod(bits, k)
        need = Counter([base + 1] * rem + [base] * (k - rem))
        if any(s <= 14 and m > count[s] for s, m in need.items()):
            bad.append((bits, k))
print("jumlah prima tepat s-bit:", {s: count[s] for s in range(4, 9)})
print(f"kombinasi (bits,k) pada rentang API yang tak dapat dipenuhi: {len(bad)}")
print(bad)

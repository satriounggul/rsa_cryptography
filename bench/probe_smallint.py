"""Probe: apakah ada lonjakan biaya per iterasi modexp saat modulus melewati 30 bit (batas satu 'digit' int CPython)?"""
import os, sys, time, random, gc
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from core.number_theory import modexp, generate_prime
os.sched_setaffinity(0, {43})
end = time.perf_counter() + 2
while time.perf_counter() < end: pow(3, 10**5, 10**30 + 7)
rng = random.Random(1)
print("bits_modulus  iterasi_per_modexp  us_per_iterasi(median dari 15 kali x 300 modexp)")
gc.disable()
for pb in (8, 12, 16, 21, 26, 28, 29, 30, 31, 32, 42, 64, 96, 128):
    p = generate_prime(pb)
    exps = [rng.randrange(1 << (pb - 1), 1 << pb) | 1 for _ in range(300)]  # eksponen panjang pb bit
    bases = [rng.randrange(2, p) for _ in range(300)]
    samples = []
    for _ in range(15):
        t = time.perf_counter()
        for b, e in zip(bases, exps): modexp(b, e, p)
        samples.append(time.perf_counter() - t)
    samples.sort()
    med = samples[len(samples)//2]
    iters = sum(e.bit_length() for e in exps)
    print(f"{pb:12d}  {iters/300:18.1f}  {med/iters*1e6:8.4f}")

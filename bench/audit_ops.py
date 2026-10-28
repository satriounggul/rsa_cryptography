"""
Audit 1c/1d: apa yang dihitung di dalam timer tiap metode, dan seberapa jujur op_counter.
Read-only terhadap core/. Tidak mengubah file core; modinv dipasangi pembungkus penghitung secara runtime
(monkeypatch di proses ini saja) hanya untuk MENGUKUR seberapa banyak kerja yang tidak terhitung.

Jalankan: PYTHONDONTWRITEBYTECODE=1 python3 bench/audit_ops.py
"""
import os
import random
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import core.rsa as rsa_mod  # noqa: E402
import core.number_theory as nt  # noqa: E402
from core.keygen import generate_keys  # noqa: E402
from core.number_theory import modexp, modinv  # noqa: E402
from core.op_counter import OperationCounter  # noqa: E402
from core.rsa import encrypt, decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402


def make_key_exact(bits, k):
    while True:
        key = generate_keys(bits, k)
        if key["public_key"]["bits"] == bits:
            return key


print("=== A. Isi pekerjaan di dalam timer (dibaca dari kode) ===")
print("""decrypt_standard   (core/rsa.py:42-46): perf_counter -> modexp(c,d,n) -> perf_counter. Tanpa invers, tanpa dict langkah.
decrypt_crt_garner (core/rsa.py:82-159): c%p_i + modexp per prima (+ append dict per_prime), lalu Garner dengan t_i
                   yang DIBACA dari kunci (rsa.py:119) + append dict garner_steps.  TANPA modinv.
decrypt_crt_gauss  (core/rsa.py:194-257): c%p_i + modexp per prima (+ dict), lalu UNTUK TIAP PRIMA: N_i = n//p_i
                   (rsa.py:227), N_i % p_i (232), modinv(N_i mod p_i, p_i) (233) = extended_gcd Python murni, + dict gauss_steps,
                   lalu x % n atas jumlah besar (256).  modinv & n//p_i DIHITUNG ULANG TIAP DEKRIPSI.""")

print("\n=== B. Berapa porsi waktu Gauss (as shipped) yang dihabiskan untuk modinv + N_i? ===")
print(f"{'bits':>5} {'k':>2} | {'gauss total ms':>14} {'per-prima(modexp) ms':>21} {'rekombinasi ms':>15} {'- modinv ms':>12} {'- n//p_i, %p ms':>16} {'modinv %total':>14} {'iter egcd/modinv':>17}")
rng = random.Random(11)
for bits, k in [(512, 2), (1024, 2), (1024, 4), (2048, 2), (2048, 3), (2048, 5)]:
    key = make_key_exact(bits, k)
    priv = key["private_key"]
    n, e = priv["n"], priv["e"]
    cs = [encrypt(rng.randrange(2, n - 1), e, n) for _ in range(15)]
    primes, dps = priv["primes"], priv["d_primes"]
    tot, per_prime, recomb, t_inv, t_div = [], [], [], [], []
    egcd_iters = []
    for c in cs:
        t0 = time.perf_counter()
        decrypt_crt_gauss(c, priv)
        tot.append(time.perf_counter() - t0)
        # Bagian per-prima (persis isi loop pertama rsa.py:200-216 tanpa dict)
        t0 = time.perf_counter()
        ms = []
        for p, dp in zip(primes, dps):
            ms.append(modexp(c % p, dp, p))
        per_prime.append(time.perf_counter() - t0)
        # Rekombinasi Gauss (persis rsa.py:222-257)
        ti = td = 0.0
        t_all = time.perf_counter()
        x = 0
        for p, m_i in zip(primes, ms):
            a = time.perf_counter(); N_i = n // p; Nm = N_i % p; td += time.perf_counter() - a
            a = time.perf_counter(); M_i = modinv(Nm, p); ti += time.perf_counter() - a
            x += ((m_i * M_i) % p) * N_i
        x %= n
        recomb.append(time.perf_counter() - t_all)
        t_inv.append(ti); t_div.append(td)
    # jumlah iterasi extended_gcd pada satu modinv ukuran p
    p = primes[-1]
    Nm = (n // p) % p
    r0, r1, it = Nm, p, 0
    while r1:
        r0, r1 = r1, r0 % r1
        it += 1
    med = statistics.median
    print(f"{bits:>5} {k:>2} | {med(tot)*1e3:14.3f} {med(per_prime)*1e3:21.3f} {med(recomb)*1e3:15.3f} {med(t_inv)*1e3:12.3f} {med(t_div)*1e3:16.3f} {100*med(t_inv)/med(tot):13.1f}% {it:>17}")

print("\n=== C. op_counter: apa yang terhitung (satu ciphertext) ===")
for bits, k in [(1024, 2), (1024, 4), (2048, 2)]:
    key = make_key_exact(bits, k)
    priv = key["private_key"]
    n, e, d = priv["n"], priv["e"], priv["d"]
    c = encrypt(random.Random(5).randrange(2, n - 1), e, n)
    print(f"-- bits={bits} k={k}")
    for name, fn in [("standard", lambda: decrypt_standard(c, d, n)),
                     ("garner", lambda: decrypt_crt_garner(c, priv)),
                     ("gauss", lambda: decrypt_crt_gauss(c, priv))]:
        _, steps = fn()
        oc = steps["operation_counts"]
        print(f"   {name:9s} mul={oc['multiplications']:6d} mod={oc['modulo_ops']:6d} shift={oc['bit_shifts']:6d} add={oc['additions']:3d} div={oc['divisions']:3d} TOTAL={oc['total_operations']:6d}")

print("\n=== D. Operasi yang TIDAK terhitung pada Gauss: iterasi extended_gcd di modinv ===")
counter = {"calls": 0, "iters": 0}
orig_egcd = rsa_mod.modinv


def counting_modinv(a, m):
    counter["calls"] += 1
    r0, r1 = a % m if m else a, m
    # replika hitungan iterasi loop extended_gcd(a, m) tanpa mengubah hasil
    o, r = a, m
    while r:
        o, r = r, o % r
        counter["iters"] += 1
    return orig_egcd(a, m)


rsa_mod.modinv = counting_modinv  # hanya di proses ini
try:
    for bits, k in [(1024, 2), (2048, 2), (2048, 5)]:
        key = make_key_exact(bits, k)
        priv = key["private_key"]
        n, e = priv["n"], priv["e"]
        c = encrypt(random.Random(9).randrange(2, n - 1), e, n)
        counter.update(calls=0, iters=0)
        _, steps = decrypt_crt_gauss(c, priv)
        oc = steps["operation_counts"]
        # tiap iterasi egcd = 1 pembagian // + 3 perkalian (q*r, q*s, q*t) + 3 pengurangan -> operasi bignum yang tak tercatat
        unseen = counter["iters"] * 4
        print(f"bits={bits} k={k}: modinv dipanggil {counter['calls']}x, total iterasi extended_gcd={counter['iters']} "
              f"=> ~{unseen} operasi bignum (1 div + 3 mul per iterasi) TIDAK ada di total_operations={oc['total_operations']}")
finally:
    rsa_mod.modinv = orig_egcd

print("\n=== E. Apakah op_counter sadar ukuran bit? ===")
src = open(os.path.join(ROOT, "core", "op_counter.py")).read()
print("count_mul/mod menerima argumen 'count: int' saja (op_counter.py:23-27) -> tidak ada parameter ukuran operan.")
print("Dua perkalian 2048-bit dan 512-bit sama-sama menambah multiplications += 1.")
print("modinv/extended_gcd/miller_rabin tidak menerima op_counter (number_theory.py:31,49,110) -> tidak pernah terhitung.")

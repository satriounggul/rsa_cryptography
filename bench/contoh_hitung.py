#!/usr/bin/env python3
"""
Contoh hitung kecil untuk makalah, diperiksa dengan kode inti dan dengan pow() bawaan Python sebagai pembanding independen.

  A. Vektor uji CRT: p = (3, 5, 7), sisa m = (2, 3, 2) -> x = 23 (Garner, Gauss, dan pencarian langsung).
     Vektor yang sama dilewatkan lewat dekripsi RSA penuh: n = 105, e = 5, d = 29, m = 23 (sisanya tepat (2, 3, 2)).
  B. Contoh RSA multi-prime penuh: p = (11, 13, 17), e = 7, pesan m = 1234.
  C. Kasus p_i | m: n = 105, e = 5, d = 29, m = 21 (m_i = (0, 1, 0)).

Keluaran dicetak (disimpan ke results/final/contoh_hitung.txt oleh pemanggil). Keluar dengan kode 1 bila ada pemeriksaan gagal.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from core.keygen import compute_phi, compute_garner_coefficients, compute_gauss_coefficients  # noqa: E402
from core.number_theory import modinv  # noqa: E402
from core.rsa import encrypt, decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402

ok = True


def check(label, cond):
    global ok
    ok = ok and cond
    print(f"  [{'OK' if cond else 'GAGAL'}] {label}")


def build_priv(primes, e):
    n = 1
    for p in primes:
        n *= p
    phi = compute_phi(primes)
    d = modinv(e, phi)
    return {"n": n, "e": e, "d": d, "primes": primes, "k": len(primes), "phi": phi,
            "d_primes": [d % (p - 1) or (p - 1) for p in primes],
            "t_coeffs": compute_garner_coefficients(primes), "gauss_coeffs": compute_gauss_coefficients(primes)}


def garner_manual(primes, ms, t):
    x, P = ms[0], primes[0]
    print(f"  x1 = m1 = {x}; P1 = p1 = {P}")
    for i in range(1, len(primes)):
        u = ((ms[i] - x) * t[i - 1]) % primes[i]
        print(f"  i={i + 1}: u = (m{i + 1} - x) * t{i + 1} mod p{i + 1} = ({ms[i]} - {x}) * {t[i - 1]} mod {primes[i]} = {u}; x = {x} + {u} * {P} = {x + u * P}")
        x, P = x + u * P, P * primes[i]
    return x


def gauss_manual(primes, ms):
    n = 1
    for p in primes:
        n *= p
    total = 0
    for p, m in zip(primes, ms):
        N = n // p
        M = modinv(N % p, p)
        print(f"  p={p}: N={N}, M=N^-1 mod p={M}, m*N*M={m * N * M}")
        total += m * N * M
    print(f"  jumlah = {total}; mod n = {total % n}")
    return total % n


print("=== A. Vektor uji CRT: p = (3, 5, 7), sisa m = (2, 3, 2) ===")
primes, ms = [3, 5, 7], [2, 3, 2]
t = compute_garner_coefficients(primes)
print(f"koefisien Garner t = {t} (t2 = p1^-1 mod p2, t3 = (p1*p2)^-1 mod p3)")
xg = garner_manual(primes, ms, t)
print("Gauss (jumlah satu-sisa):")
xs = gauss_manual(primes, ms)
brute = [x for x in range(105) if [x % p for p in primes] == ms]
print(f"pencarian langsung x in [0, 105): {brute}")
check("Garner = 23", xg == 23)
check("Gauss = 23", xs == 23)
check("pencarian langsung menemukan tepat satu solusi, yaitu 23", brute == [23])

print("\nVektor yang sama lewat dekripsi RSA penuh (n = 105, e = 5):")
priv = build_priv(primes, 5)
print(f"  phi = {priv['phi']}, d = {priv['d']}, d_i = {priv['d_primes']}, t = {priv['t_coeffs']}, C_i (Gauss b) = {priv['gauss_coeffs']}")
c = encrypt(23, priv["e"], priv["n"])
print(f"  c = 23^5 mod 105 = {c}; sisa c_i = {[c % p for p in primes]}; m_i = {[pow(c % p, d_i, p) for p, d_i in zip(primes, priv['d_primes'])]}")
for name, fn in (("standar", lambda: decrypt_standard(c, priv["d"], priv["n"])), ("Garner", lambda: decrypt_crt_garner(c, priv)),
                 ("Gauss (a)", lambda: decrypt_crt_gauss(c, priv, use_precomputed=False)), ("Gauss (b)", lambda: decrypt_crt_gauss(c, priv, use_precomputed=True))):
    m, steps = fn()
    check(f"dekripsi {name} = 23 (pembanding pow: {pow(c, priv['d'], priv['n'])})", m == 23 == pow(c, priv["d"], priv["n"]))
check("m_i dari dekripsi = (2, 3, 2)", [pow(c % p, d_i, p) for p, d_i in zip(primes, priv["d_primes"])] == [2, 3, 2])

print("\n=== B. Contoh RSA multi-prime penuh: p = (11, 13, 17), e = 7, m = 1234 ===")
primes = [11, 13, 17]
priv = build_priv(primes, 7)
n, e, d = priv["n"], priv["e"], priv["d"]
print(f"n = 11*13*17 = {n}; phi(n) = 10*12*16 = {priv['phi']}; e = {e} (gcd(e, phi) = 1: {math.gcd(e, priv['phi']) == 1})")
print(f"d = e^-1 mod phi = {d}; cek e*d mod phi = {(e * d) % priv['phi']}")
print(f"d_i = d mod (p_i - 1) = {[d % (p - 1) for p in primes]} -> dipakai {priv['d_primes']}")
print(f"koefisien Garner t = {priv['t_coeffs']}; koefisien Gauss (b) C_i = N_i*M_i mod n = {priv['gauss_coeffs']}")
m = 1234
c = encrypt(m, e, n)
print(f"enkripsi: c = m^e mod n = {m}^{e} mod {n} = {c}")
ci = [c % p for p in primes]
mi = [pow(x, di, p) for x, di, p in zip(ci, priv["d_primes"], primes)]
print(f"c_i = c mod p_i = {ci}; m_i = c_i^d_i mod p_i = {mi}; (m mod p_i = {[m % p for p in primes]})")
print("Garner:")
xg = garner_manual(primes, mi, priv["t_coeffs"])
print("Gauss (a):")
xs = gauss_manual(primes, mi)
check("m_i sama dengan m mod p_i", mi == [m % p for p in primes])
check("Garner manual = 1234", xg == m)
check("Gauss manual = 1234", xs == m)
for name, fn in (("standar", lambda: decrypt_standard(c, d, n)), ("Garner", lambda: decrypt_crt_garner(c, priv)),
                 ("Gauss (a)", lambda: decrypt_crt_gauss(c, priv, use_precomputed=False)), ("Gauss (b)", lambda: decrypt_crt_gauss(c, priv, use_precomputed=True))):
    out, steps = fn()
    check(f"dekripsi {name} dengan kode inti = 1234 (total operasi tercatat: {steps['operation_counts']['total_operations']})", out == m)
check("pembanding pow(c, d, n) = 1234", pow(c, d, n) == m)
print("\n=== C. Kasus p_i | m: n = 105, e = 5, d = 29, m = 21 (3 | 21 dan 7 | 21) ===")
primes = [3, 5, 7]
priv = build_priv(primes, 5)
m = 21
c = encrypt(m, priv["e"], priv["n"])
mi = [pow(c % p, di, p) for p, di in zip(primes, priv["d_primes"])]
print(f"c = {c}; c_i = {[c % p for p in primes]}; d_i = {priv['d_primes']}; m_i = {mi}")
check("m_i = (0, 1, 0) = m mod p_i", mi == [m % p for p in primes] == [0, 1, 0])
check("Garner, Gauss (a), Gauss (b), dan standar memulihkan 21", all(
    fn()[0] == m for fn in (lambda: decrypt_standard(c, priv["d"], priv["n"]), lambda: decrypt_crt_garner(c, priv),
                            lambda: decrypt_crt_gauss(c, priv, use_precomputed=False), lambda: decrypt_crt_gauss(c, priv, use_precomputed=True))))
print("\nSEMUA PEMERIKSAAN LULUS" if ok else "\nADA PEMERIKSAAN GAGAL")
sys.exit(0 if ok else 1)

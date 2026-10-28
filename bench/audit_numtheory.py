"""
Audit 1a: edge case core/number_theory.py. Read-only terhadap core/.
pow/math dipakai di sini HANYA sebagai oracle pembanding (bench/ di luar audit AST test_forbidden).

Jalankan: PYTHONDONTWRITEBYTECODE=1 python3 bench/audit_numtheory.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.number_theory import (  # noqa: E402
    gcd, extended_gcd, modinv, modexp, miller_rabin, generate_prime, _SMALL_PRIMES,
)


def attempt(fn, *args):
    try:
        return ("ok", fn(*args))
    except Exception as exc:  # noqa: BLE001
        return ("EXC", f"{type(exc).__name__}: {exc}")


def oracle_inv(a, m):
    try:
        return pow(a, -1, m)
    except Exception as exc:  # noqa: BLE001
        return f"EXC {type(exc).__name__}"


print("=== gcd (bandingkan math.gcd) ===")
for a, b in [(0, 0), (0, 5), (5, 0), (-12, 18), (12, -18), (-12, -18), (1, 0), (2**200 + 1, 2**100 + 1)]:
    r = attempt(gcd, a, b)
    flag = "" if r == ("ok", math.gcd(a, b)) else "  <-- BEDA"
    print(f"gcd({a}, {b}) = {r[1]}   oracle={math.gcd(a, b)}{flag}")

print("\n=== extended_gcd: cek a*x+b*y == g dan g == gcd >= 0 ===")
for a, b in [(0, 0), (0, 5), (5, 0), (-3, 5), (3, -5), (-3, -5), (12, 18), (7, 7), (1, 1), (-12, 18)]:
    g, x, y = extended_gcd(a, b)
    bezout = (a * x + b * y == g)
    sign_ok = (g == math.gcd(a, b))
    print(f"extended_gcd({a:3}, {b:3}) -> g={g:3} x={x:3} y={y:3}  bezout={bezout}  g==gcd? {sign_ok}"
          + ("" if (bezout and sign_ok) else "  <-- ANOMALI"))

print("\n=== modinv (bandingkan pow(a,-1,m)) ===")
cases = [(3, 7), (0, 1), (5, 1), (1, 1), (10, 7), (-3, 7), (7, 7), (0, 7), (3, 0), (3, -7), (2, 4),
         (65537 + 1000003 * 5, 1000003), (123456789, 2**61 - 1)]
for a, m in cases:
    mine = attempt(modinv, a, m)
    orc = oracle_inv(a, m)
    same = (mine[0] == "ok" and mine[1] == orc) or (mine[0] == "EXC" and str(orc).startswith("EXC"))
    print(f"modinv({a}, {m}) = {mine[1]!s:<70.70} oracle={orc}  {'OK' if same else '<-- BEDA'}")

print("\n=== modexp (bandingkan pow(b,e,m)) ===")
cases = [(0, 0, 5), (0, 0, 1), (5, 0, 1), (5, 3, 1), (-2, 3, 7), (-2, 4, 7), (10, 3, 7), (7, 1, 13),
         (2, 10, 2), (3, 200, 2**127 - 1), (0, 5, 19), (5, -1, 7), (5, 3, 0), (5, 3, -7)]
for b, e, m in cases:
    mine = attempt(modexp, b, e, m)
    try:
        orc = pow(b, e, m)
    except Exception as exc:  # noqa: BLE001
        orc = f"EXC {type(exc).__name__}"
    same = (mine[0] == "ok" and mine[1] == orc) or (mine[0] == "EXC" and str(orc).startswith("EXC"))
    print(f"modexp({b}, {e}, {m}) = {mine[1]!s:<55.55} oracle={orc}  {'OK' if same else '<-- BEDA'}")

print("\n=== Miller-Rabin: semua n < 20000 terhadap sieve ===")
N = 20000
sieve = [True] * N
sieve[0:2] = [False, False]
for i in range(2, int(N ** 0.5) + 1):
    if sieve[i]:
        for j in range(i * i, N, i):
            sieve[j] = False
bad = [n for n in range(-5, N) if miller_rabin(n) != (n >= 0 and sieve[n] if n >= 0 else False)]
print(f"mismatch pada n in [-5, {N}): {bad[:20]} (total {len(bad)})")
print("n besar komposit: Carmichael 561,41041,825265, 3215031751 (strong pseudoprime basis 2,3,5,7):",
      [miller_rabin(x) for x in (561, 41041, 825265, 3215031751)])
print("n = p^2 untuk prima p: ", [miller_rabin(p * p) for p in (101, 10007, 1000003)])
print("n = 2^127-1 (Mersenne prime):", miller_rabin(2**127 - 1), " n = 2^127+1 (komposit):", miller_rabin(2**127 + 1))

print("\n=== generate_prime: panjang bit & bit kedua teratas ===")
for bits in (2, 3, 4, 5, 8, 16, 32, 64, 128, 256, 512):
    reps = 300 if bits <= 128 else 40
    lens, second_set, odd = set(), 0, 0
    for _ in range(reps):
        p = generate_prime(bits)
        lens.add(p.bit_length())
        if bits >= 2 and (p >> (bits - 2)) & 1:
            second_set += 1
        odd += p & 1
    print(f"bits={bits:4d} sampel={reps:3d} panjang_aktual={sorted(lens)}  bit_ke2_teratas_set={100*second_set/reps:5.1f}%  ganjil={odd}/{reps}")

print("\n=== Konfigurasi MR ===")
import inspect  # noqa: E402
import core.number_theory as nt  # noqa: E402
src = inspect.getsource(nt)
print("default rounds miller_rabin:", inspect.signature(miller_rabin).parameters['rounds'].default)
print("default rounds generate_prime:", inspect.signature(generate_prime).parameters['rounds'].default)
print("sumber acak: secrets.randbelow di MR =", 'secrets.randbelow(n - 3) + 2' in src,
      "; secrets.randbits di generate_prime =", 'secrets.randbits(bits)' in src,
      "; modul random dipakai =", 'import random' in src)
print("jumlah prima kecil penyaring:", len(_SMALL_PRIMES), "terbesar:", _SMALL_PRIMES[-1], "(2 tidak ada; kandidat selalu ganjil)")

"""
Varian dekripsi dan model biaya untuk benchmark. TIDAK mengubah core/.

Lapisan (layer) pengukuran:
  core    : fungsi core/rsa.py apa adanya (dengan OperationCounter dan pencatatan langkah di dalam timer),
            ditambah crt_gauss_precomp = salinan struktur decrypt_crt_gauss yang koefisien N_i*M_i-nya diprekomputasi.
  lean    : algoritma yang sama (modexp inti, op_counter=None) TANPA OperationCounter dan TANPA dict langkah,
            untuk memisahkan biaya algoritma dari biaya instrumentasi.
  builtin : pow(c,d,n) bawaan Python (C). HANYA baseline informatif, bukan pembanding klaim.

pow()/math dipakai di sini hanya sebagai oracle/baseline (bench/ di luar audit AST test_forbidden).
"""
import os
import random
import sys
from typing import Any, Dict, List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.number_theory import modexp, modinv  # noqa: E402
from core.op_counter import OperationCounter  # noqa: E402

# --------------------------------------------------------------------------------------
# Data bantu
# --------------------------------------------------------------------------------------


def gauss_precompute(priv: Dict[str, Any]) -> List[int]:
    """C_i = (N_i * M_i) mod n dengan N_i = n/p_i, M_i = N_i^-1 mod p_i. Dihitung SEKALI, di luar timer."""
    n = priv["n"]
    out = []
    for p in priv["primes"]:
        N_i = n // p
        M_i = modinv(N_i % p, p)
        out.append((N_i * M_i) % n)
    return out


def make_plaintexts_and_ciphertexts(key: Dict[str, Any], count: int, seed: int) -> Tuple[List[int], List[int]]:
    """count plaintext acak m in [2, n-2] (RNG berbenih -> dapat diulang) dan c = m^e mod n (oracle pow)."""
    priv = key["private_key"]
    n, e = priv["n"], priv["e"]
    rng = random.Random(seed)
    ms = [rng.randrange(2, n - 1) for _ in range(count)]
    cs = [pow(m, e, n) for m in ms]
    return ms, cs


# --------------------------------------------------------------------------------------
# Layer core: varian (b) Gauss dengan instrumentasi sejajar core.rsa.decrypt_crt_gauss
# --------------------------------------------------------------------------------------


def decrypt_crt_gauss_precomp(c: int, private_key: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """
    Gauss varian (b): x = sum(m_i * C_i) mod n dengan C_i = N_i*M_i mod n diprekomputasi (private_key["gauss_coeffs"]).
    Struktur, counter, dan pencatatan langkah SENGAJA dibuat sejajar core.rsa.decrypt_crt_gauss supaya
    selisihnya murni akibat pindahnya N_i dan modinv ke luar dekripsi (seperti t_i pada Garner).
    """
    primes = private_key["primes"]
    d_primes = private_key["d_primes"]
    coeffs = private_key["gauss_coeffs"]
    n = private_key["n"]
    k = private_key["k"]
    if c < 0 or c >= n:
        raise ValueError("c di luar rentang")
    counter = OperationCounter()
    per_prime_steps: List[Dict[str, Any]] = []
    m_list: List[int] = []
    for i in range(k):
        p_i = primes[i]
        d_i = d_primes[i]
        c_i = c % p_i
        counter.count_mod()
        m_i = modexp(c_i, d_i, p_i, op_counter=counter)
        m_list.append(m_i)
        per_prime_steps.append({"prime_index": i + 1, "p_i": p_i, "d_i": d_i, "c_i": c_i, "m_i": m_i})
    gauss_steps: List[Dict[str, Any]] = []
    x = 0
    for i in range(k):
        m_i = m_list[i]
        term = m_i * coeffs[i]
        counter.count_mul()
        x += term
        counter.count_add()
        gauss_steps.append({"step": i + 1, "p_i": primes[i], "m_i": m_i, "C_i": coeffs[i], "term": term})
    x = x % n
    counter.count_mod()
    return x, {"method": "crt_gauss_precomp", "operation_counts": counter.to_dict(),
               "per_prime": per_prime_steps, "gauss_steps": gauss_steps}


# --------------------------------------------------------------------------------------
# Layer lean: tanpa OperationCounter dan tanpa dict langkah
# --------------------------------------------------------------------------------------


def lean_standard(c: int, d: int, n: int) -> int:
    return modexp(c, d, n)


def lean_garner(c: int, priv: Dict[str, Any]) -> int:
    primes, d_primes, t = priv["primes"], priv["d_primes"], priv["t_coeffs"]
    k = priv["k"]
    m_list = [modexp(c % primes[i], d_primes[i], primes[i]) for i in range(k)]
    x = m_list[0]
    P = primes[0]
    for i in range(1, k):
        p = primes[i]
        u = (((m_list[i] - x) % p) * t[i - 1]) % p
        x = x + u * P
        P *= p
    if x >= priv["n"]:
        x %= priv["n"]
    return x


def lean_gauss(c: int, priv: Dict[str, Any]) -> int:
    """Varian (a): N_i dan invers dihitung saat dekripsi (perilaku core sekarang)."""
    primes, d_primes, n, k = priv["primes"], priv["d_primes"], priv["n"], priv["k"]
    m_list = [modexp(c % primes[i], d_primes[i], primes[i]) for i in range(k)]
    x = 0
    for i in range(k):
        p = primes[i]
        N_i = n // p
        M_i = modinv(N_i % p, p)
        x += ((m_list[i] * M_i) % p) * N_i
    return x % n


def lean_gauss_precomp(c: int, priv: Dict[str, Any]) -> int:
    """Varian (b): koefisien C_i = N_i*M_i mod n diprekomputasi."""
    primes, d_primes, n, k, coeffs = priv["primes"], priv["d_primes"], priv["n"], priv["k"], priv["gauss_coeffs"]
    x = 0
    for i in range(k):
        x += modexp(c % primes[i], d_primes[i], primes[i]) * coeffs[i]
    return x % n


# --------------------------------------------------------------------------------------
# Layer builtin: pow() bawaan, informatif saja
# --------------------------------------------------------------------------------------


def builtin_standard(c: int, d: int, n: int) -> int:
    return pow(c, d, n)


def builtin_garner(c: int, priv: Dict[str, Any]) -> int:
    primes, d_primes, t = priv["primes"], priv["d_primes"], priv["t_coeffs"]
    k = priv["k"]
    m_list = [pow(c % primes[i], d_primes[i], primes[i]) for i in range(k)]
    x = m_list[0]
    P = primes[0]
    for i in range(1, k):
        p = primes[i]
        u = (((m_list[i] - x) % p) * t[i - 1]) % p
        x = x + u * P
        P *= p
    return x % priv["n"]


# --------------------------------------------------------------------------------------
# Model biaya berbobot-bit
# --------------------------------------------------------------------------------------


def _bl(x: int) -> int:
    b = abs(x).bit_length()
    return b if b > 0 else 1


class Cost:
    """
    Dua definisi biaya, dihitung bersamaan:
      literal : perkalian a*b dan modulo/pembagian a%m, a//m dihitung bl(a)*bl(m)   (sesuai permintaan tugas)
      refined : perkalian bl(a)*bl(b); modulo/pembagian sekolah (panjang kuosien x panjang pembagi)
                = max(bl(a)-bl(m)+1, 1) * bl(m)
    'literal' melebih-lebihkan biaya pembagian ber-kuosien-kecil (mis. langkah algoritma Euclid),
    karena itu 'refined' dilaporkan sebagai pembanding sensitivitas.
    """

    __slots__ = ("lit", "ref", "n_mul", "n_mod", "n_div")

    def __init__(self) -> None:
        self.lit = 0
        self.ref = 0
        self.n_mul = 0
        self.n_mod = 0
        self.n_div = 0

    def mul(self, a: int, b: int) -> int:
        c = _bl(a) * _bl(b)
        self.lit += c
        self.ref += c
        self.n_mul += 1
        return a * b

    def mod(self, a: int, m: int) -> int:
        la, lm = _bl(a), _bl(m)
        self.lit += la * lm
        self.ref += max(la - lm + 1, 1) * lm
        self.n_mod += 1
        return a % m

    def div(self, a: int, m: int) -> int:
        la, lm = _bl(a), _bl(m)
        self.lit += la * lm
        self.ref += max(la - lm + 1, 1) * lm
        self.n_div += 1
        return a // m


def _c_modexp(cost: Cost, base: int, e: int, m: int) -> int:
    """Urutan operasi identik core.number_theory.modexp (LSB -> MSB)."""
    if m == 1:
        return 0
    if e == 0:
        return 1
    b = cost.mod(base, m)
    result = 1
    while e > 0:
        if e & 1:
            result = cost.mod(cost.mul(result, b), m)
        b = cost.mod(cost.mul(b, b), m)
        e >>= 1
    return result


def _c_modinv(cost: Cost, a: int, m: int) -> int:
    """Urutan operasi identik core.number_theory.extended_gcd + modinv."""
    old_r, r = a, m
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = cost.div(old_r, r)
        old_r, r = r, old_r - cost.mul(q, r)
        old_s, s = s, old_s - cost.mul(q, s)
        old_t, t = t, old_t - cost.mul(q, t)
    if old_r != 1:
        raise ValueError("invers tidak ada")
    return cost.mod(old_s, m)


def cost_standard(c: int, priv: Dict[str, Any]) -> Tuple[int, Cost]:
    cost = Cost()
    return _c_modexp(cost, c, priv["d"], priv["n"]), cost


def cost_garner(c: int, priv: Dict[str, Any]) -> Tuple[int, Cost]:
    cost = Cost()
    primes, d_primes, t, n, k = priv["primes"], priv["d_primes"], priv["t_coeffs"], priv["n"], priv["k"]
    m_list = []
    for i in range(k):
        c_i = cost.mod(c, primes[i])
        m_list.append(_c_modexp(cost, c_i, d_primes[i], primes[i]))
    x = m_list[0]
    P = primes[0]
    for i in range(1, k):
        p = primes[i]
        diff = cost.mod(m_list[i] - x, p)
        u = cost.mod(cost.mul(diff, t[i - 1]), p)
        x = x + cost.mul(u, P)
        P = cost.mul(P, p)  # core melakukan ini juga pada iterasi terakhir (rsa.py:151-152)
    if x >= n:
        x = cost.mod(x, n)
    return x, cost


def cost_gauss(c: int, priv: Dict[str, Any]) -> Tuple[int, Cost]:
    """Varian (a): N_i = n//p_i, N_i mod p_i, modinv dihitung saat dekripsi (seperti core)."""
    cost = Cost()
    primes, d_primes, n, k = priv["primes"], priv["d_primes"], priv["n"], priv["k"]
    m_list = []
    for i in range(k):
        c_i = cost.mod(c, primes[i])
        m_list.append(_c_modexp(cost, c_i, d_primes[i], primes[i]))
    x = 0
    for i in range(k):
        p = primes[i]
        N_i = cost.div(n, p)
        M_i = _c_modinv(cost, cost.mod(N_i, p), p)
        temp = cost.mod(cost.mul(m_list[i], M_i), p)
        x += cost.mul(temp, N_i)
    x = cost.mod(x, n)
    return x, cost


def cost_gauss_precomp(c: int, priv: Dict[str, Any]) -> Tuple[int, Cost]:
    """Varian (b): koefisien C_i diprekomputasi (di luar biaya dekripsi)."""
    cost = Cost()
    primes, d_primes, n, k, coeffs = priv["primes"], priv["d_primes"], priv["n"], priv["k"], priv["gauss_coeffs"]
    x = 0
    for i in range(k):
        c_i = cost.mod(c, primes[i])
        m_i = _c_modexp(cost, c_i, d_primes[i], primes[i])
        x += cost.mul(m_i, coeffs[i])
    x = cost.mod(x, n)
    return x, cost


COST_METHODS = {
    "standard": cost_standard,
    "crt_garner": cost_garner,
    "crt_gauss": cost_gauss,
    "crt_gauss_precomp": cost_gauss_precomp,
}

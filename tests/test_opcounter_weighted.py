"""Penghitung operasi: hitungan lama tidak berubah; biaya berbobot-bit opt-in dan benar."""
import random
import unittest

from core.keygen import generate_keys
from core.number_theory import modexp
from core.op_counter import OperationCounter
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss

LEGACY_KEYS = {"multiplications", "modulo_ops", "bit_shifts", "additions", "divisions", "total_operations"}


def reference_modexp_cost(base, e, m):
    """Implementasi independen: urutan operasi modexp (LSB->MSB) dan biayanya."""
    def bl(x):
        return abs(x).bit_length() or 1
    lit = sch = 0
    lit += bl(base) * bl(m)
    sch += max(bl(base) - bl(m) + 1, 1) * bl(m)
    b, result = base % m, 1
    while e > 0:
        if e & 1:
            prod = result * b
            lit += bl(result) * bl(b) + bl(prod) * bl(m)
            sch += bl(result) * bl(b) + max(bl(prod) - bl(m) + 1, 1) * bl(m)
            result = prod % m
        sq = b * b
        lit += bl(b) * bl(b) + bl(sq) * bl(m)
        sch += bl(b) * bl(b) + max(bl(sq) - bl(m) + 1, 1) * bl(m)
        b = sq % m
        e >>= 1
    return lit, sch


class TestOperationCounter(unittest.TestCase):

    def test_default_counter_output_is_unchanged(self):
        counter = OperationCounter()
        modexp(7, 12345, 10 ** 9 + 7, op_counter=counter)
        self.assertEqual(set(counter.to_dict()), LEGACY_KEYS)

    def test_plain_counts_follow_square_and_multiply_formula(self):
        rng = random.Random(3)
        for _ in range(50):
            m = rng.randrange(3, 2 ** 64)
            e = rng.randrange(1, 2 ** 40)
            counter = OperationCounter()
            modexp(rng.randrange(0, 2 ** 70), e, m, op_counter=counter)
            ones, length = bin(e).count("1"), e.bit_length()
            self.assertEqual(counter.bit_shifts, length)
            self.assertEqual(counter.multiplications, ones + length)
            self.assertEqual(counter.modulo_ops, 1 + ones + length)

    def test_tracking_bits_does_not_change_plain_counts(self):
        priv = generate_keys(256, 3)["private_key"]
        n, d = priv["n"], priv["d"]
        c = pow(31337, priv["e"], n)
        for fn in (lambda oc: decrypt_standard(c, d, n, op_counter=oc),
                   lambda oc: decrypt_crt_garner(c, priv, op_counter=oc),
                   lambda oc: decrypt_crt_gauss(c, priv, op_counter=oc)):
            plain = fn(OperationCounter())[1]["operation_counts"]
            tracked = fn(OperationCounter(track_bits=True))[1]["operation_counts"]
            self.assertEqual({k: v for k, v in tracked.items() if k in LEGACY_KEYS}, plain)
            self.assertIn("weighted_cost", tracked)
            self.assertNotIn("weighted_cost", plain)

    def test_weighted_cost_matches_independent_reference(self):
        rng = random.Random(4)
        for bits in (16, 64, 300):
            m = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
            e = rng.getrandbits(bits) | 1
            base = rng.randrange(0, m * 3)
            counter = OperationCounter(track_bits=True)
            modexp(base, e, m, op_counter=counter)
            lit, sch = reference_modexp_cost(base, e, m)
            self.assertEqual(counter.weighted_cost, lit)
            self.assertEqual(counter.weighted_cost_schoolbook, sch)

    def test_weighted_cost_shows_crt_advantage_that_plain_counts_hide(self):
        k = 4
        priv = generate_keys(512, k)["private_key"]
        n, d = priv["n"], priv["d"]
        c = pow(2 ** 300 + 12345, priv["e"], n)
        std = decrypt_standard(c, d, n, op_counter=OperationCounter(track_bits=True))[1]["operation_counts"]
        gar = decrypt_crt_garner(c, priv, op_counter=OperationCounter(track_bits=True))[1]["operation_counts"]
        # Perkalian/modulo polos hampir sama (alat hitung buta ukuran bit) ...
        self.assertAlmostEqual(std["total_operations"] / gar["total_operations"], 1.0, delta=0.1)
        # ... tetapi biaya berbobot-bit menunjukkan keunggulan sekitar k^2 (=16) untuk CRT.
        self.assertGreater(std["weighted_cost"] / gar["weighted_cost"], 8)
        self.assertGreater(std["weighted_cost_schoolbook"] / gar["weighted_cost_schoolbook"], 8)


if __name__ == "__main__":
    unittest.main()

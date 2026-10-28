"""
Panjang modulus tepat, k sampai 8, bits besar, dan parameter kecil yang dulu membuat generate_keys menggantung.
"""
import threading
import unittest

from core.keygen import generate_keys, validate_keys
from core.number_theory import generate_prime_in_range, miller_rabin

# Kombinasi (bits, k) dalam rentang API yang pada kode awal membuat loop "prima berbeda" tak berakhir
# (hasil enumerasi bench/audit_keygen_hang.py).
HANGING_IN_BASELINE = [
    (16, 4), (17, 4), (20, 5), (21, 5), (22, 5), (24, 6), (25, 6), (26, 6), (27, 6), (30, 6), (28, 7), (29, 7),
    (30, 7), (31, 7), (32, 7), (34, 7), (35, 7), (36, 7), (32, 8), (33, 8), (34, 8), (35, 8), (36, 8), (37, 8),
    (38, 8), (39, 8), (40, 8), (41, 8), (42, 8), (48, 8),
]


def run_with_timeout(fn, seconds):
    box = {}

    def target():
        try:
            box["value"] = fn()
        except Exception as exc:  # noqa: BLE001
            box["error"] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)
    return t.is_alive(), box


class TestExactBitLength(unittest.TestCase):

    def check(self, bits, k):
        keys = generate_keys(bits, k)
        pub, priv = keys["public_key"], keys["private_key"]
        self.assertEqual(pub["n"].bit_length(), bits, f"bits={bits} k={k}")
        self.assertEqual(pub["bits"], bits)
        self.assertEqual(priv["bits"], bits)
        self.assertEqual(len(set(priv["primes"])), k)
        self.assertEqual(priv["primes"], sorted(priv["primes"]))
        self.assertTrue(validate_keys(pub, priv))

    def test_exact_for_every_k_up_to_8(self):
        for k in range(2, 9):
            for bits in (64, 128, 256):
                for _ in range(12):
                    self.check(bits, k)

    def test_exact_for_small_moduli(self):
        for bits, k in [(16, 2), (16, 3), (18, 4), (23, 5), (24, 4), (64, 8)]:
            for _ in range(25):
                self.check(bits, k)

    def test_exact_for_large_moduli(self):
        for bits, k in [(1024, 2), (1024, 3), (1024, 5), (2048, 4)]:
            self.check(bits, k)

    def test_never_hangs_for_formerly_hanging_parameters(self):
        for bits, k in HANGING_IN_BASELINE:
            hung, box = run_with_timeout(lambda b=bits, kk=k: generate_keys(b, kk), 30)
            self.assertFalse(hung, f"generate_keys({bits}, {k}) did not finish")
            if "error" in box:
                self.assertIsInstance(box["error"], ValueError, f"({bits},{k}) raised {box['error']!r}")
            else:
                self.assertEqual(box["value"]["public_key"]["n"].bit_length(), bits)

    def test_impossible_parameters_raise_value_error(self):
        for bits, k in [(16, 4), (20, 5), (32, 8)]:
            with self.assertRaises(ValueError):
                generate_keys(bits, k)


class TestPrimeInRange(unittest.TestCase):

    def test_result_is_prime_within_range(self):
        for lo, hi in [(90, 100), (2, 3), (1000, 1100), (2 ** 200, 2 ** 201), (10 ** 30, 10 ** 30 + 5000)]:
            p = generate_prime_in_range(lo, hi)
            self.assertTrue(lo <= p <= hi)
            self.assertTrue(miller_rabin(p, rounds=30))

    def test_empty_or_primeless_interval_raises(self):
        with self.assertRaises(ValueError):
            generate_prime_in_range(10, 9)
        with self.assertRaises(ValueError):
            generate_prime_in_range(24, 28)  # 24..28 holds no prime


if __name__ == "__main__":
    unittest.main()

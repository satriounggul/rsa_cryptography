"""Kasus tepi teori bilangan (0, 1, a >= m, m = 1, negatif) dan Miller-Rabin terhadap sieve."""
import math
import unittest

from core.number_theory import gcd, extended_gcd, modinv, modexp, miller_rabin


class TestNumberTheoryEdges(unittest.TestCase):

    def test_gcd_signs_and_zero(self):
        for a, b in [(0, 0), (0, 5), (5, 0), (-12, 18), (12, -18), (-12, -18), (1, 0)]:
            self.assertEqual(gcd(a, b), math.gcd(a, b))

    def test_extended_gcd_bezout_holds_for_all_signs(self):
        for a, b in [(0, 0), (0, 5), (5, 0), (-3, 5), (3, -5), (-3, -5), (12, 18), (7, 7), (-12, 18)]:
            g, x, y = extended_gcd(a, b)
            self.assertEqual(a * x + b * y, g)
            self.assertEqual(abs(g), math.gcd(a, b))

    def test_modinv_edge_cases(self):
        self.assertEqual(modinv(0, 1), 0)
        self.assertEqual(modinv(5, 1), 0)
        self.assertEqual(modinv(10, 7), pow(10, -1, 7))   # a >= m
        self.assertEqual(modinv(-3, 7), pow(-3, -1, 7))   # a < 0
        for a, m in [(7, 7), (0, 7), (2, 4)]:
            with self.assertRaises(ValueError):
                modinv(a, m)
        for m in (0, -7):
            with self.assertRaises(ValueError):
                modinv(3, m)

    def test_modexp_edge_cases(self):
        for b, e, m in [(0, 0, 5), (0, 0, 1), (5, 3, 1), (-2, 3, 7), (-2, 4, 7), (10, 3, 7), (7, 1, 13), (2, 10, 2), (0, 5, 19)]:
            self.assertEqual(modexp(b, e, m), pow(b, e, m))
        for b, e, m in [(5, -1, 7), (5, 3, 0), (5, 3, -7)]:
            with self.assertRaises(ValueError):
                modexp(b, e, m)

    def test_miller_rabin_matches_sieve_below_10000(self):
        limit = 10000
        sieve = [True] * limit
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit ** 0.5) + 1):
            if sieve[i]:
                for j in range(i * i, limit, i):
                    sieve[j] = False
        for n in range(-3, limit):
            self.assertEqual(miller_rabin(n), n >= 0 and sieve[n], n)

    def test_miller_rabin_strong_pseudoprimes_and_squares(self):
        for c in (561, 41041, 825265, 3215031751, 101 * 101, 10007 * 10007):
            self.assertFalse(miller_rabin(c))
        self.assertTrue(miller_rabin(2 ** 127 - 1))


if __name__ == "__main__":
    unittest.main()

"""Koefisien Gauss prekomputasi: kebenaran, kompatibilitas kunci lama, dan kesetaraan dengan jalur lama."""
import random
import unittest

from core.keygen import generate_keys, validate_keys, compute_gauss_coefficients
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss


def legacy_key(priv):
    """Kunci dari versi lama: tanpa gauss_coeffs."""
    return {k: v for k, v in priv.items() if k != "gauss_coeffs"}


class TestGaussPrecompute(unittest.TestCase):

    def test_coefficients_are_crt_idempotents(self):
        for k in (2, 3, 5, 8):
            keys = generate_keys(256, k)
            priv = keys["private_key"]
            coeffs = priv["gauss_coeffs"]
            self.assertEqual(len(coeffs), k)
            self.assertEqual(coeffs, compute_gauss_coefficients(priv["primes"]))
            for i, c in enumerate(coeffs):
                self.assertTrue(0 < c < priv["n"])
                for j, p in enumerate(priv["primes"]):
                    self.assertEqual(c % p, 1 if i == j else 0)
            self.assertTrue(validate_keys(keys["public_key"], priv))

    def test_validate_rejects_tampered_coefficients(self):
        keys = generate_keys(128, 3)
        pub, priv = keys["public_key"], keys["private_key"]
        bad = dict(priv, gauss_coeffs=[priv["gauss_coeffs"][0] + 1] + priv["gauss_coeffs"][1:])
        self.assertFalse(validate_keys(pub, bad))
        self.assertFalse(validate_keys(pub, dict(priv, gauss_coeffs=priv["gauss_coeffs"][:-1])))

    def test_old_keys_without_coefficients_still_work(self):
        keys = generate_keys(256, 4)
        pub, priv = keys["public_key"], legacy_key(keys["private_key"])
        self.assertTrue(validate_keys(pub, priv))
        n, e, d = pub["n"], pub["e"], priv["d"]
        c = pow(123456789, e, n)
        m, steps = decrypt_crt_gauss(c, priv)
        self.assertEqual(m, 123456789)
        self.assertFalse(steps["precomputed"])
        with self.assertRaises(ValueError):
            decrypt_crt_gauss(c, priv, use_precomputed=True)

    def test_default_uses_precomputed_and_legacy_option_remains(self):
        keys = generate_keys(256, 3)
        priv = keys["private_key"]
        c = pow(987654321, priv["e"], priv["n"])
        m_pre, st_pre = decrypt_crt_gauss(c, priv)
        m_leg, st_leg = decrypt_crt_gauss(c, priv, use_precomputed=False)
        self.assertEqual((m_pre, m_leg), (987654321, 987654321))
        self.assertTrue(st_pre["precomputed"])
        self.assertFalse(st_leg["precomputed"])
        self.assertIn("C_i", st_pre["gauss_steps"][0])
        self.assertIn("N_i", st_leg["gauss_steps"][0])
        self.assertEqual(st_pre["operation_counts"]["divisions"], 0)
        self.assertEqual(st_leg["operation_counts"]["divisions"], priv["k"])

    def test_precomputed_equals_legacy_equals_standard_on_random_residues(self):
        rng = random.Random(2026)
        for bits, k in [(128, 3), (256, 5), (512, 2)]:
            priv = generate_keys(bits, k)["private_key"]
            n, d = priv["n"], priv["d"]
            cs = [rng.randrange(0, n) for _ in range(150)] + [0, 1, n - 1] + [p * rng.randrange(1, n // p) for p in priv["primes"]]
            for c in cs:
                want = pow(c, d, n)
                self.assertEqual(decrypt_crt_gauss(c, priv)[0], want)
                self.assertEqual(decrypt_crt_gauss(c, priv, use_precomputed=False)[0], want)


if __name__ == "__main__":
    unittest.main()

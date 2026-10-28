"""Konsistensi ketiga metode (plus varian Gauss) pada banyak ciphertext acak, dibandingkan dengan pow() sebagai oracle."""
import random
import unittest

from core.keygen import generate_keys
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss


class TestConsistencyMany(unittest.TestCase):

    def run_many(self, bits, k, count, seed):
        rng = random.Random(seed)
        priv = generate_keys(bits, k)["private_key"]
        n, d = priv["n"], priv["d"]
        # Dekripsi adalah fungsi pada SEMUA residu 0..n-1, bukan hanya ciphertext hasil enkripsi.
        cs = [rng.randrange(0, n) for _ in range(count)] + [0, 1, 2, n - 1, n - 2]
        for c in cs:
            want = pow(c, d, n)
            self.assertEqual(decrypt_standard(c, d, n)[0], want)
            self.assertEqual(decrypt_crt_garner(c, priv)[0], want)
            self.assertEqual(decrypt_crt_gauss(c, priv)[0], want)
            self.assertEqual(decrypt_crt_gauss(c, priv, use_precomputed=False)[0], want)

    def test_1000_random_ciphertexts_k3_256bit(self):
        self.run_many(256, 3, 1000, seed=1)

    def test_k_up_to_8(self):
        for k in range(2, 9):
            self.run_many(256, k, 150, seed=10 + k)

    def test_larger_moduli(self):
        self.run_many(1024, 4, 40, seed=21)
        self.run_many(2048, 5, 8, seed=22)

    def test_decrypt_rejects_out_of_range_ciphertext(self):
        priv = generate_keys(128, 3)["private_key"]
        n, d = priv["n"], priv["d"]
        for c in (-1, n, n + 7):
            with self.assertRaises(ValueError):
                decrypt_standard(c, d, n)
            with self.assertRaises(ValueError):
                decrypt_crt_garner(c, priv)
            with self.assertRaises(ValueError):
                decrypt_crt_gauss(c, priv)


if __name__ == "__main__":
    unittest.main()

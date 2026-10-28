"""Pengodean teks multi-blok, unicode, dan modulus sangat besar (regresi: panjang blok satu-byte)."""
import random
import unittest

from core.codec import text_to_blocks, blocks_to_text
from core.keygen import generate_keys
from core.rsa import encrypt, decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss


def fake_modulus(bits):
    return (1 << (bits - 1)) + 1  # hanya ukuran n yang dipakai codec


def random_text(rng, length):
    alphabet = "abcXYZ 0123456789é日本語😀🎉\n\x00\x01"
    return "".join(rng.choice(alphabet) for _ in range(length))


class TestCodecText(unittest.TestCase):

    def test_round_trip_multi_block_unicode(self):
        rng = random.Random(5)
        for bits in (17, 24, 32, 64, 128, 256, 1024, 2048):
            n = fake_modulus(bits)
            for length in (0, 1, 2, 3, 17, 100, 700):
                text = random_text(rng, length)
                blocks = text_to_blocks(text, n)
                self.assertTrue(all(0 <= b < n for b in blocks))
                self.assertEqual(blocks_to_text(blocks, n), text, f"bits={bits} len={length}")
            long_text = random_text(rng, 700)
            if bits <= 256:
                self.assertGreater(len(text_to_blocks(long_text, n)), 1)

    def test_round_trip_for_very_large_modulus(self):
        """Dulu ValueError('bytes must be in range(0, 256)') untuk n >= 2057 bit dan teks > 255 byte."""
        rng = random.Random(6)
        for bits in (2056, 2057, 2064, 3072, 4096):
            n = fake_modulus(bits)
            for text in ("A" * 300, "é" * 400, random_text(rng, 900)):
                blocks = text_to_blocks(text, n)
                self.assertTrue(all(0 <= b < n for b in blocks))
                self.assertEqual(blocks_to_text(blocks, n), text, f"bits={bits}")

    def test_block_format_unchanged_below_2057_bits(self):
        n = fake_modulus(1024)
        blocks = text_to_blocks("abc", n)
        self.assertEqual(blocks, [int.from_bytes(bytes([3]) + b"abc", "big")])

    def test_single_byte_mode_and_too_small_modulus(self):
        self.assertEqual(blocks_to_text(text_to_blocks("Hi!", 300), 300), "Hi!")
        with self.assertRaises(ValueError):
            text_to_blocks("a", 255)

    def test_full_encrypt_decrypt_text_all_methods(self):
        rng = random.Random(7)
        keys = generate_keys(256, 3)
        pub, priv = keys["public_key"], keys["private_key"]
        n, e, d = pub["n"], pub["e"], priv["d"]
        text = random_text(rng, 500)
        cts = [encrypt(b, e, n) for b in text_to_blocks(text, n)]
        self.assertGreater(len(cts), 10)
        for decrypt in (lambda c: decrypt_standard(c, d, n)[0], lambda c: decrypt_crt_garner(c, priv)[0],
                        lambda c: decrypt_crt_gauss(c, priv)[0],
                        lambda c: decrypt_crt_gauss(c, priv, use_precomputed=False)[0]):
            self.assertEqual(blocks_to_text([decrypt(c) for c in cts], n), text)


if __name__ == "__main__":
    unittest.main()

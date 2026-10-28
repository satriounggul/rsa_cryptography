"""
End-to-end HTTP: server lokal sungguhan (port acak di 127.0.0.1) diakses dengan http.client.
Mencakup alur kunci -> enkripsi -> dekripsi (semua metode), penolakan masukan (400/404/413) dan regresi keamanan/keandalan.
"""
import http.client
import json
import socket
import threading
import unittest

from server.app import RSAHandler
import http.server


class QuietHandler(RSAHandler):
    def log_message(self, *args):  # tanpa log akses saat tes
        pass


class QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):  # klien yang sengaja memutus koneksi bukan kegagalan tes
        pass


class TestHTTPEndToEnd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = QuietServer(("127.0.0.1", 0), QuietHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        status, cls.keys = cls.post("/keygen", {"bits": 128, "k": 3})
        assert status == 200

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    # ------------------------------------------------------------------ helpers
    @classmethod
    def raw(cls, method, path, body=None, headers=None, timeout=20):
        conn = http.client.HTTPConnection("127.0.0.1", cls.port, timeout=timeout)
        conn.putrequest(method, path, skip_accept_encoding=True)  # path dikirim apa adanya (tanpa normalisasi)
        data = body if isinstance(body, bytes) else (json.dumps(body).encode() if body is not None else None)
        for k, v in (headers or {}).items():
            conn.putheader(k, v)
        if data is not None and "Content-Length" not in (headers or {}):
            conn.putheader("Content-Length", str(len(data)))
        conn.endheaders(data)
        resp = conn.getresponse()
        payload = resp.read()
        conn.close()
        return resp.status, payload

    @classmethod
    def post(cls, path, body, **kw):
        status, payload = cls.raw("POST", path, body, {"Content-Type": "application/json"}, **kw)
        return status, json.loads(payload)

    # ------------------------------------------------------------------ alur normal
    def test_keygen_response_shape_and_exact_bits(self):
        pub, priv = self.keys["public_key"], self.keys["private_key"]
        self.assertEqual(int(pub["n"]).bit_length(), 128)
        self.assertEqual(len(priv["primes"]), 3)
        self.assertEqual(len(priv["gauss_coeffs"]), 3)

    def test_number_roundtrip_all_methods(self):
        pub, priv = self.keys["public_key"], self.keys["private_key"]
        m = int(pub["n"]) // 3 + 12345
        status, enc = self.post("/encrypt", {"n": pub["n"], "e": pub["e"], "message": str(m)})
        self.assertEqual(status, 200)
        for method in ("standard", "crt_garner", "crt_gauss", "crt_gauss_legacy"):
            status, dec = self.post("/decrypt", {"key_data": priv, "ciphertext": enc["ciphertext"], "method": method})
            self.assertEqual(status, 200, method)
            self.assertEqual(int(dec["plaintext"]), m, method)
        status, dec = self.post("/decrypt", {"key_data": priv, "ciphertext": enc["ciphertext"], "method": "crt_gauss"})
        self.assertTrue(dec["intermediate_steps"]["precomputed"])
        status, dec = self.post("/decrypt", {"key_data": priv, "ciphertext": enc["ciphertext"], "method": "crt_gauss_legacy"})
        self.assertFalse(dec["intermediate_steps"]["precomputed"])

    def test_text_roundtrip_multi_block_all_methods(self):
        pub, priv = self.keys["public_key"], self.keys["private_key"]
        text = "Matematika Diskrit: CRT & Garner — 日本語 😀 " * 6
        status, enc = self.post("/encrypt", {"n": pub["n"], "e": pub["e"], "message": text, "is_text": True})
        self.assertEqual(status, 200)
        self.assertGreater(int(enc["blocks_count"]), 5)
        for method in ("standard", "crt_garner", "crt_gauss", "crt_gauss_legacy"):
            status, dec = self.post("/decrypt", {"key_data": priv, "ciphertext": enc["ciphertext_blocks"],
                                                 "is_text": True, "method": method})
            self.assertEqual(status, 200, method)
            self.assertEqual(dec["recovered_text"], text, method)

    def test_old_key_without_gauss_coeffs_still_decrypts(self):
        pub, priv = self.keys["public_key"], dict(self.keys["private_key"])
        del priv["gauss_coeffs"]
        status, enc = self.post("/encrypt", {"n": pub["n"], "e": pub["e"], "message": "424242"})
        status, dec = self.post("/decrypt", {"key_data": priv, "ciphertext": enc["ciphertext"], "method": "crt_gauss"})
        self.assertEqual(status, 200)
        self.assertEqual(dec["plaintext"], "424242")
        self.assertFalse(dec["intermediate_steps"]["precomputed"])

    # ------------------------------------------------------------------ masukan tidak valid
    def test_invalid_input_is_400_not_500(self):
        pub, priv = self.keys["public_key"], self.keys["private_key"]
        n_plus = str(int(pub["n"]) + 5)
        cases = [
            ("/keygen", {"bits": 256, "k": 1}),
            ("/keygen", {"bits": 16, "k": 4}),                       # dulu menggantung selamanya
            ("/keygen", {"bits": 32, "k": 8}),
            ("/encrypt", {"n": pub["n"], "e": "-3", "message": "5"}),
            ("/decrypt", {"key_data": priv, "ciphertext": n_plus, "method": "crt_garner"}),
            ("/decrypt", {"key_data": priv, "ciphertext": n_plus, "method": "standard"}),
            ("/decrypt", {"key_data": priv, "ciphertext": ["abc"], "is_text": True, "method": "standard"}),
        ]
        for path, body in cases:
            status, payload = self.post(path, body)
            self.assertEqual(status, 400, f"{path} {body}")
            self.assertIn("error", payload)

    def test_booleans_stay_booleans_in_json(self):
        """serialize_bigints dulu mengubah True/False menjadi string 'True'/'False' (truthy di JavaScript)."""
        from server.app import serialize_bigints
        self.assertIs(serialize_bigints({"a": True, "b": [False], "c": 7})["a"], True)
        self.assertIs(serialize_bigints({"b": [False]})["b"][0], False)
        self.assertEqual(serialize_bigints({"c": 7}), {"c": "7"})

    def test_malformed_bodies(self):
        status, _ = self.raw("POST", "/keygen", b"[1,2,3]", {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        status, _ = self.raw("POST", "/keygen", b"{rusak", {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        status, _ = self.raw("POST", "/keygen", b"{}", {"Content-Length": "abc"})
        self.assertEqual(status, 400)
        status, _ = self.raw("POST", "/tidak-ada", b"{}", {"Content-Type": "application/json"})
        self.assertEqual(status, 404)

    def test_oversized_body_is_rejected_without_reading_it(self):
        status, _ = self.raw("POST", "/keygen", None, {"Content-Length": "5000000"})
        self.assertEqual(status, 413)

    # ------------------------------------------------------------------ keamanan & keandalan
    def test_static_files_served_and_path_traversal_blocked(self):
        for path in ("/", "/index.html", "/app.js", "/style.css"):
            status, body = self.raw("GET", path)
            self.assertEqual(status, 200, path)
            self.assertGreater(len(body), 100)
        for path in ("/../core/keygen.py", "/../README.md", "/../../etc/passwd", "/static/../core/rsa.py",
                     "/..%2fcore/keygen.py", "/../server/app.py"):
            status, body = self.raw("GET", path)
            self.assertEqual(status, 404, path)
            self.assertNotIn(b"def generate_keys", body)

    def test_stalled_connection_does_not_block_other_requests(self):
        stalled = socket.create_connection(("127.0.0.1", self.port))
        try:
            stalled.sendall(b"POST /keygen HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: 1000\r\n\r\n{")
            status, _ = self.raw("GET", "/", timeout=5)
            self.assertEqual(status, 200)
        finally:
            stalled.close()


if __name__ == "__main__":
    unittest.main()

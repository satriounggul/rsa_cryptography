"""
Audit 1e: core/codec.py + server/app.py (probe perilaku nyata). Read-only terhadap core/server/static.
Server dijalankan sebagai subprocess di port 8765 (127.0.0.1) lalu dimatikan.

Jalankan: PYTHONDONTWRITEBYTECODE=1 python3 bench/audit_codec_server.py
"""
import http.client
import json
import os
import random
import socket
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.codec import text_to_blocks, blocks_to_text  # noqa: E402
from core.keygen import generate_keys  # noqa: E402
from core.rsa import encrypt, decrypt_standard  # noqa: E402

print("=== CODEC ===")
rng = random.Random(3)
SAMPLES = ["", "a", "Halo Dunia!", "héllo wörld ñ", "日本語のテキスト", "emoji 😀🎉 campur", "\x00\x01\x02 kontrol", "x" * 300, "é" * 200,
           "".join(chr(rng.choice([0x41, 0xe9, 0x4e2d, 0x1f600])) for _ in range(500))]
for bits in (9, 12, 16, 17, 24, 32, 64, 128, 256, 1024, 2048, 2056, 2057, 2064, 3072, 4096):
    n = (1 << (bits - 1)) + 1  # n.bit_length() == bits; hanya ukuran yang dipakai codec
    ok = fail = err = 0
    first_err = None
    for t in SAMPLES:
        try:
            if blocks_to_text(text_to_blocks(t, n), n) == t:
                ok += 1
            else:
                fail += 1
        except Exception as exc:  # noqa: BLE001
            err += 1
            first_err = first_err or f"{type(exc).__name__}: {exc}"
    print(f"n={bits:5d} bit: round-trip ok={ok:2d}/{len(SAMPLES)} salah={fail} exception={err}" + (f"  -> {first_err}" if first_err else ""))

print("\n--- errors='replace': kunci/ciphertext salah tidak memunculkan error ---")
A = generate_keys(256, 2)["private_key"]
B = generate_keys(256, 2)["private_key"]
msg = "Pesan rahasia untuk Alice"
blocks = text_to_blocks(msg, A["n"])
cts = [encrypt(b, A["e"], A["n"]) for b in blocks]
# didekripsi dengan kunci milik B (n berbeda) -> nilai 'dekripsi' acak
wrong = [pow(c % B["n"], B["d"], B["n"]) for c in cts]
try:
    out = blocks_to_text(wrong, A["n"])
    print(f"dekripsi dengan kunci salah -> tidak ada exception; hasil repr={out!r}")
except Exception as exc:  # noqa: BLE001
    print(f"dekripsi dengan kunci salah -> exception {type(exc).__name__}: {exc}")
corrupt = list(blocks)
corrupt[0] ^= 0xFF
print(f"blok rusak 1 byte -> blocks_to_text = {blocks_to_text(corrupt, A['n'])!r}")

print("\n=== SERVER ===")
PORT = 8765
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
srv = subprocess.Popen([sys.executable, os.path.join(ROOT, "server", "app.py"), "--port", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
time.sleep(1.0)


def req(method, path, body=None, headers=None, raw_body=None, timeout=20):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=timeout)
    h = dict(headers or {})
    data = raw_body
    if body is not None:
        data = json.dumps(body).encode()
        h.setdefault("Content-Type", "application/json")
    conn.putrequest(method, path, skip_accept_encoding=True)
    for k, v in h.items():
        conn.putheader(k, v)
    if data is not None and "Content-Length" not in h:
        conn.putheader("Content-Length", str(len(data)))
    conn.endheaders(data)
    r = conn.getresponse()
    out = r.read()
    hdrs = dict(r.getheaders())
    conn.close()
    return r.status, hdrs, out


try:
    key = generate_keys(256, 3)
    priv = {k_: (str(v) if isinstance(v, int) else [str(x) for x in v] if isinstance(v, list) else v) for k_, v in key["private_key"].items()}
    n_s, e_s = str(key["public_key"]["n"]), str(key["public_key"]["e"])

    st, h, b = req("POST", "/keygen", {"bits": 64, "k": 3})
    print(f"[ok]   /keygen 64/3 -> {st}; CORS Allow-Origin={h.get('Access-Control-Allow-Origin')!r}")

    cases = [
        ("keygen k=1", "/keygen", {"bits": 256, "k": 1}),
        ("keygen bits=17 k=8 (bits//k<4)", "/keygen", {"bits": 17, "k": 8}),
        ("keygen bits='abc'", "/keygen", {"bits": "abc", "k": 3}),
        ("keygen k=9", "/keygen", {"bits": 256, "k": 9}),
        ("encrypt e negatif", "/encrypt", {"n": n_s, "e": "-3", "message": "5", "is_text": False}),
        ("encrypt n=0", "/encrypt", {"n": "0", "e": "3", "message": "5"}),
        ("encrypt n=1", "/encrypt", {"n": "1", "e": "3", "message": "0"}),
        ("encrypt teks n kecil (n=200)", "/encrypt", {"n": "200", "e": "3", "message": "abc", "is_text": True}),
        ("decrypt c >= n (angka)", "/decrypt", {"key_data": priv, "ciphertext": str(int(n_s) + 5), "method": "crt_garner"}),
        ("decrypt c >= n (standard)", "/decrypt", {"key_data": priv, "ciphertext": str(int(n_s) + 5), "method": "standard"}),
        ("decrypt ciphertext non-numerik", "/decrypt", {"key_data": priv, "ciphertext": "xyz", "method": "standard"}),
        ("decrypt teks, list berisi 'abc'", "/decrypt", {"key_data": priv, "ciphertext": ["abc"], "is_text": True, "method": "standard"}),
        ("decrypt metode tak dikenal", "/decrypt", {"key_data": priv, "ciphertext": "5", "method": "foo"}),
    ]
    for label, path, body in cases:
        st, h, b = req("POST", path, body)
        try:
            msg_ = json.loads(b).get("error", json.loads(b))
        except Exception:  # noqa: BLE001
            msg_ = b[:80]
        print(f"[{st}]  {label:38s} -> {str(msg_)[:110]}")

    # JSON bukan objek
    st, h, b = req("POST", "/keygen", raw_body=b"[1,2,3]", headers={"Content-Type": "application/json"})
    print(f"[{st}]  body JSON berupa list                  -> {b[:110]!r}")
    st, h, b = req("POST", "/keygen", raw_body=b"{rusak", headers={"Content-Type": "application/json"})
    print(f"[{st}]  body JSON rusak                        -> {b[:110]!r}")
    st, h, b = req("POST", "/keygen", raw_body=b"{}", headers={"Content-Length": "abc"})
    print(f"[{st}]  Content-Length non-numerik            -> {b[:110]!r}")

    # Kunci privat yang tidak konsisten diterima tanpa validasi?
    bad = dict(priv)
    bad["d_primes"] = [str(int(x) + 1) for x in priv["d_primes"]]
    c = encrypt(12345, key["public_key"]["e"], key["public_key"]["n"])
    st, h, b = req("POST", "/decrypt", {"key_data": bad, "ciphertext": str(c), "method": "crt_garner"})
    out = json.loads(b)
    print(f"[{st}]  decrypt dgn d_i dirusak (+1)           -> plaintext={out.get('plaintext')} (benar=12345) ; tidak ada validate_keys di server")

    # Path traversal
    for p in ["/../core/keygen.py", "/..%2fcore/keygen.py", "/../README.md", "/static/../core/rsa.py", "//etc/passwd"]:
        try:
            st, h, b = req("GET", p)
            print(f"[{st}]  GET {p:28s} -> {len(b)} byte; awal={b[:48]!r}")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERR]  GET {p:28s} -> {type(exc).__name__}: {exc}")

    # Server satu-thread: request lambat memblokir request lain
    print("\n--- Concurrency: HTTPServer (bukan ThreadingHTTPServer) ---")
    s = socket.create_connection(("127.0.0.1", PORT))
    s.sendall(b"POST /keygen HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: 1000\r\n\r\n{")  # body tidak pernah selesai
    time.sleep(0.5)
    t0 = time.perf_counter()
    try:
        st, h, b = req("GET", "/", timeout=3)
        print(f"GET / saat ada koneksi menggantung -> {st} dalam {time.perf_counter() - t0:.2f}s")
    except Exception as exc:  # noqa: BLE001
        print(f"GET / saat ada koneksi menggantung -> {type(exc).__name__} setelah {time.perf_counter() - t0:.2f}s (server terblokir)")
    s.close()
    time.sleep(0.5)
    st, h, b = req("GET", "/", timeout=3)
    print(f"setelah koneksi ditutup -> GET / = {st}")

    # Keygen 4096 bit/k=2: berapa lama, dan apakah memblokir?
    result = {}

    def slow():
        t = time.perf_counter()
        st, h, b = req("POST", "/keygen", {"bits": 4096, "k": 2}, timeout=300)
        result["keygen4096_s"] = time.perf_counter() - t
        result["status"] = st
        result["bits"] = json.loads(b)["public_key"]["bits"]

    th = threading.Thread(target=slow)
    th.start()
    time.sleep(0.5)
    t0 = time.perf_counter()
    try:
        st, h, b = req("GET", "/", timeout=120)
        print(f"GET / selagi keygen 4096 berjalan -> {st} setelah menunggu {time.perf_counter() - t0:.2f}s")
    except Exception as exc:  # noqa: BLE001
        print(f"GET / selagi keygen berjalan -> {type(exc).__name__}")
    th.join()
    print(f"keygen 4096/k=2 via HTTP: {result}")

    # Teks panjang pada kunci 4096 bit via API (bug codec)
    st, h, b = req("POST", "/keygen", {"bits": 2560, "k": 2})
    k2560 = json.loads(b)
    st, h, b = req("POST", "/encrypt", {"n": k2560["public_key"]["n"], "e": k2560["public_key"]["e"], "message": "A" * 300, "is_text": True})
    print(f"\n/encrypt teks 300 byte dengan kunci {k2560['public_key']['bits']} bit -> HTTP {st}: {b[:140]!r}")
finally:
    srv.terminate()
    try:
        srv.wait(timeout=5)
    except Exception:  # noqa: BLE001
        srv.kill()

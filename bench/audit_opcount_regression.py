#!/usr/bin/env python3
"""
Regresi hitungan operasi: kode inti BARU (ujung branch) vs kode inti BASELINE (git ref, default `main`) pada kunci dan
ciphertext yang sama. Untuk setiap (kunci, ciphertext, metode) dibandingkan plaintext dan operation_counts
(multiplications, modulo_ops, bit_shifts, additions, divisions, total_operations).

Metode: standar, CRT-Garner, dan CRT-Gauss jalur lama (use_precomputed=False); jalur Gauss default baru (koefisien dari kunci)
memang memberi hitungan berbeda dan tidak dibandingkan di sini.
Kode baseline diambil dari objek git (git archive) ke folder sementara, lalu dijalankan di subproses terpisah; tidak ada berkas
repo yang diubah. Kunci dibangkitkan oleh keygen baru (acak, secrets), jadi total tetap tetapi isi kunci berbeda tiap jalan.

Pemakaian: python3 bench/audit_opcount_regression.py [--ref main] > results/final/audit_opcount_regression.txt
"""
import argparse
import io
import json
import os
import random
import subprocess
import sys
import tarfile
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from core.keygen import generate_keys  # noqa: E402
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402

FIELDS = ("multiplications", "modulo_ops", "bit_shifts", "additions", "divisions", "total_operations")
HELPER = r"""
import json, sys
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss
cases = json.load(sys.stdin)
out = []
for cs in cases:
    priv = {key: ([int(x) for x in v] if isinstance(v, list) else int(v)) for key, v in cs["priv"].items()}
    n_, d_ = priv["n"], priv["d"]
    c = int(cs["c"])
    res = {}
    for name, fn in (("standard", lambda: decrypt_standard(c, d_, n_)),
                     ("garner", lambda: decrypt_crt_garner(c, priv)), ("gauss_lama", lambda: decrypt_crt_gauss(c, priv))):
        m, steps = fn()
        res[name] = {"m": str(m), "ops": steps["operation_counts"]}
    out.append(res)
json.dump(out, sys.stdout)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="main")
    ap.add_argument("--seed", type=int, default=20261028, help="seed untuk memilih ciphertext acak (kunci memakai secrets)")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", f"{a.ref}^{{commit}}"], capture_output=True, text=True, check=True).stdout.strip()
    head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    tar_bytes = subprocess.run(["git", "-C", ROOT, "archive", "--format=tar", commit, "core"], capture_output=True, check=True).stdout

    cases, new_results = [], []
    for bits in (64, 128, 256, 512, 1024, 2048):
        for k in (2, 3, 4, 5):
            priv = dict(generate_keys(bits, k)["private_key"])
            n, d, primes = priv["n"], priv["d"], priv["primes"]
            for c in [0, 1, n - 1] + [rng.randrange(2, n - 1) for _ in range(5)]:
                wire = {kk: ([str(x) for x in vv] if isinstance(vv, list) else str(vv)) for kk, vv in priv.items() if kk != "gauss_coeffs"}
                cases.append({"priv": wire, "c": str(c), "tag": f"{bits}-{k}"})
                new_results.append({
                    "standard": decrypt_standard(c, d, n),
                    "garner": decrypt_crt_garner(c, priv),
                    "gauss_lama": decrypt_crt_gauss(c, {kk: vv for kk, vv in priv.items() if kk != "gauss_coeffs"}, use_precomputed=False)})

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
            tf.extractall(tmp, filter="data") if sys.version_info >= (3, 12) else tf.extractall(tmp)
        env = dict(os.environ, PYTHONPATH=tmp, PYTHONDONTWRITEBYTECODE="1")
        res = subprocess.run([sys.executable, "-c", HELPER], input=json.dumps(cases), capture_output=True, text=True, env=env, cwd=tmp)
        if res.returncode != 0:
            sys.exit("subproses baseline gagal:\n" + res.stderr)
        base_results = json.loads(res.stdout)

    total = same = 0
    diffs = []
    for cs, new, base in zip(cases, new_results, base_results):
        for method in ("standard", "garner", "gauss_lama"):
            total += 1
            m_new, steps = new[method]
            ops_new = {f: steps["operation_counts"][f] for f in FIELDS}
            ok = str(m_new) == base[method]["m"] and ops_new == {f: base[method]["ops"][f] for f in FIELDS}
            same += ok
            if not ok:
                diffs.append((cs["tag"], cs["c"], method, ops_new, base[method]["ops"]))
    print(f"Regresi operation_counts: baseline {a.ref} ({commit[:7]}) vs kode baru HEAD ({head[:7]})")
    print(f"kunci: 24 (bits 64..2048 x k 2..5); ciphertext per kunci: 8 (0, 1, n-1, 5 acak); metode: standar, Garner, Gauss jalur lama")
    print(f"perbandingan: {total}; identik (plaintext DAN 6 bidang hitungan): {same} dari {total}; berbeda: {total - same}")
    for dd in diffs[:10]:
        print("BEDA", dd)
    return 0 if same == total else 1


if __name__ == "__main__":
    sys.exit(main())

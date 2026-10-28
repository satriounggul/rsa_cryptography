#!/usr/bin/env python3
"""
Benchmark dekripsi: RSA standar vs CRT-Garner vs CRT-Gauss (dua varian). TIDAK mengubah core/.

PRA-REGISTRASI (ditetapkan SEBELUM ada data; tidak diubah setelah melihat hasil)
  Grid       : bits_target in {64, 128, 256, 512, 1024, 2048, 3072, 4096} x k in {2, 3, 4, 5}.
               64 dan 128 ditambahkan di bawah rentang yang diminta (256-4096) HANYA agar titik silang
               (crossover) dapat dicari bila CRT sudah unggul di 256.
  Kunci      : satu kunci per (bits, k); generate_keys() diulang sampai n.bit_length() == bits_target.
  Ciphertext : 30 plaintext acak (RNG berbenih) -> 30 ciphertext yang SAMA dipakai semua metode.
  Protokol   : 3 putaran pemanasan (tidak dicatat); 30 putaran terukur; pada putaran r semua metode mendekripsi
               ciphertext ke-r dengan URUTAN METODE DIACAK; time.perf_counter; gc dimatikan selama pengukuran;
               proses dipatok ke satu CPU bila OS mendukung. Kunci dan ciphertext dibangkitkan di luar pengukuran.
  Validasi   : tiap hasil harus sama dengan plaintext asli; jika tidak -> ditandai correct=False dan program berhenti.
  Metrik     : speedup = median(standard) / median(metode) pada lapisan dan (bits,k) yang sama;
               CI 95% = bootstrap persentil 1000 kali (analyze.py).
  Titik silang: bits_target terkecil di grid yang untuk SEMUA bits_target >= itu memiliki batas bawah CI95 speedup > 1.
  Tidak ada parameter, metode, atau ukuran sampel yang dipilih ulang setelah melihat hasil.

Lapisan: core (fungsi core/rsa.py apa adanya), lean (algoritma sama tanpa instrumentasi), builtin (pow() bawaan,
baseline informatif saja). Lihat bench/variants.py.
Varian Gauss pada lapisan core:
  crt_gauss         = (a) N_i dan invers dihitung saat dekripsi  -> decrypt_crt_gauss(..., use_precomputed=False)
  crt_gauss_precomp = (b) koefisien prekomputasi dari keygen     -> decrypt_crt_gauss(...) DEFAULT kode inti
                      (pada kode inti lama tanpa opsi itu: salinan bench/variants.py)

Revisi harness (Fase A; protokol dan grid TIDAK berubah): varian (b) kini memakai default kode inti; penjaga untuk OS tanpa
sched_setaffinity (Windows, macOS) dan tanpa fork; mode --quick; nama berkas memuat hostname; menolak menimpa hasil;
meta mencatat hash commit, load average, hostname.

Jalankan penuh : PYTHONDONTWRITEBYTECODE=1 python3 bench/benchmark.py --out-dir results/final
Cepat (tim)    : python3 bench/benchmark.py --quick                  (bits 512,1024,2048; k 2,3,5; 10 putaran terukur)
Uji asap       : python3 bench/benchmark.py --bits 64,128 --reps 5 --tag smoke --out-dir <folder sementara>
Berkas keluaran: <out-dir>/benchmark_{raw,meta,keys}_<hostname>[_<tag>].{csv,json,json}
"""
import argparse
import csv
import datetime
import gc
import inspect
import json
import multiprocessing as mp
import os
import platform
import random
import re
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import variants as V  # noqa: E402
from core.keygen import generate_keys  # noqa: E402
from core.rsa import decrypt_standard, decrypt_crt_garner, decrypt_crt_gauss  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
OP_FIELDS = ["multiplications", "modulo_ops", "bit_shifts", "additions", "divisions", "total_operations"]
CSV_FIELDS = (["timestamp", "python_version", "os", "cpu", "hostname", "pinned_cpu", "layer", "bits_target", "bits_actual",
               "k", "method", "run_id", "time_s"] + OP_FIELDS + ["correct"])

FULL = dict(bits="64,128,256,512,1024,2048,3072,4096", k="2,3,4,5", reps=30)
QUICK = dict(bits="512,1024,2048", k="2,3,5", reps=10)

# Kode inti sesudah Fase 4: decrypt_crt_gauss otomatis memakai koefisien prekomputasi bila kunci memuat gauss_coeffs.
# Varian (a) "invers saat dekripsi" harus dipaksa lewat use_precomputed=False; pada kode inti lama parameter itu tidak ada.
_HAS_PRECOMP_OPT = "use_precomputed" in inspect.signature(decrypt_crt_gauss).parameters
_GAUSS_A_KW = {"use_precomputed": False} if _HAS_PRECOMP_OPT else {}


# ---------------------------------------------------------------------------------------------- lingkungan
def safe_hostname() -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", socket.gethostname()) or "host"


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    if sys.platform.startswith("win") and os.environ.get("PROCESSOR_IDENTIFIER"):
        return os.environ["PROCESSOR_IDENTIFIER"]
    return platform.processor() or platform.machine() or "unknown"


def load_average():
    """Load average 1/5/15 menit, atau None bila OS tidak menyediakannya (Windows)."""
    try:
        return [round(x, 2) for x in os.getloadavg()]
    except (AttributeError, OSError):
        return None


def source_commit():
    """(hash commit, ada perubahan pada berkas terlacak?) dari git; bila bukan repositori, dari BUILD_INFO.txt pada zip."""
    try:
        head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        if head.returncode == 0 and head.stdout.strip():
            dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--untracked-files=no"],
                                   capture_output=True, text=True, timeout=10).stdout.strip() != ""
            return head.stdout.strip(), dirty
    except (OSError, subprocess.SubprocessError):
        pass
    info = os.path.join(ROOT, "BUILD_INFO.txt")
    if os.path.exists(info):
        with open(info, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("commit"):
                    return line.split(":", 1)[1].strip() + " (dari BUILD_INFO.txt pada zip)", None
    return "tidak tersedia", None


def pin_cpu(requested, disabled):
    """Memaku proses ke satu CPU bila OS mendukung. Mengembalikan label CPU, atau 'none' (tanpa pemakuan)."""
    if disabled:
        return "none"
    if not (hasattr(os, "sched_setaffinity") and hasattr(os, "sched_getaffinity")):
        print("[ukur] PERINGATAN: OS ini tidak mendukung pemakuan CPU dari Python (Windows/macOS). Pengukuran tetap jalan; "
              "tutup aplikasi lain, colokkan daya, dan pilih mode kinerja tinggi agar noise kecil.", flush=True)
        return "none"
    allowed = sorted(os.sched_getaffinity(0))
    cpu = requested if requested is not None else allowed[-1]
    try:
        os.sched_setaffinity(0, {cpu})
        return str(cpu)
    except (OSError, ValueError) as exc:
        print(f"[ukur] PERINGATAN: gagal memaku ke CPU {cpu} ({exc}); lanjut tanpa pemakuan. CPU yang diizinkan: {allowed}", flush=True)
        return "none"


# ---------------------------------------------------------------------------------------------- kunci dan metode
def make_key_exact(args):
    bits, k = args
    attempts = 0
    t0 = time.perf_counter()
    while True:
        attempts += 1
        key = generate_keys(bits, k)
        if key["public_key"]["bits"] == bits:
            return bits, k, attempts, time.perf_counter() - t0, key


def build_methods(key):
    priv = dict(key["private_key"])
    if "gauss_coeffs" not in priv:  # kunci dari kode inti lama: prekomputasi di LUAR timer
        priv["gauss_coeffs"] = V.gauss_precompute(priv)
    n, d = priv["n"], priv["d"]

    def core_standard(c):
        m, s = decrypt_standard(c, d, n)
        return m, s["operation_counts"]

    def core_garner(c):
        m, s = decrypt_crt_garner(c, priv)
        return m, s["operation_counts"]

    def core_gauss_a(c):  # (a) invers dihitung saat dekripsi
        m, s = decrypt_crt_gauss(c, priv, **_GAUSS_A_KW)
        return m, s["operation_counts"]

    if _HAS_PRECOMP_OPT:
        def core_gauss_b(c):  # (b) default kode inti: koefisien dari kunci
            m, s = decrypt_crt_gauss(c, priv)
            return m, s["operation_counts"]
    else:
        def core_gauss_b(c):  # kode inti lama tanpa opsi: salinan di bench/variants.py
            m, s = V.decrypt_crt_gauss_precomp(c, priv)
            return m, s["operation_counts"]

    return priv, [
        ("core", "standard", core_standard),
        ("core", "crt_garner", core_garner),
        ("core", "crt_gauss", core_gauss_a),
        ("core", "crt_gauss_precomp", core_gauss_b),
        ("lean", "standard", lambda c: (V.lean_standard(c, d, n), None)),
        ("lean", "crt_garner", lambda c: (V.lean_garner(c, priv), None)),
        ("lean", "crt_gauss", lambda c: (V.lean_gauss(c, priv), None)),
        ("lean", "crt_gauss_precomp", lambda c: (V.lean_gauss_precomp(c, priv), None)),
        ("builtin", "standard", lambda c: (V.builtin_standard(c, d, n), None)),
        ("builtin", "crt_garner", lambda c: (V.builtin_garner(c, priv), None)),
    ]


def check_gauss_variants(priv, c):
    """Di luar pengukuran: pastikan (a) memang menghitung invers saat dekripsi dan (b) memang memakai koefisien kunci."""
    if not _HAS_PRECOMP_OPT:
        return
    _, sa = decrypt_crt_gauss(c, priv, use_precomputed=False)
    _, sb = decrypt_crt_gauss(c, priv)
    if sa["precomputed"] is not False or sb["precomputed"] is not True:
        raise RuntimeError("varian Gauss salah label: (a) harus precomputed=False dan (b) precomputed=True")


def exit_if_exists(path, overwrite):
    if os.path.exists(path) and not overwrite:
        sys.exit(f"Berkas sudah ada, tidak ditimpa: {path}\nPakai --tag lain, --out-dir lain, atau --overwrite bila memang disengaja.")


# ---------------------------------------------------------------------------------------------- utama
def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark dekripsi RSA standar vs CRT-Garner vs CRT-Gauss")
    ap.add_argument("--quick", action="store_true", help="mode cepat untuk tim: bits 512,1024,2048; k 2,3,5; 10 putaran terukur")
    ap.add_argument("--bits", default=None, help=f"daftar dipisah koma (default {FULL['bits']})")
    ap.add_argument("--k", default=None, help=f"daftar dipisah koma (default {FULL['k']})")
    ap.add_argument("--reps", type=int, default=None, help=f"putaran terukur per metode (default {FULL['reps']})")
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--n-ct", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261028)
    ap.add_argument("--cpu", type=int, default=None, help="CPU untuk dipatok (default: CPU terakhir yang diizinkan; diabaikan bila OS tak mendukung)")
    ap.add_argument("--no-pin", action="store_true", help="jangan patok CPU")
    ap.add_argument("--workers", type=int, default=12, help="proses paralel UNTUK PEMBANGKITAN KUNCI saja")
    ap.add_argument("--reuse-keys", action="store_true", help="pakai ulang kunci dari berkas kunci yang sudah ada")
    ap.add_argument("--tag", default="", help="akhiran nama berkas, mis. smoke")
    ap.add_argument("--out-dir", default=RESULTS, help="folder keluaran (default results/)")
    ap.add_argument("--overwrite", action="store_true", help="izinkan menimpa berkas keluaran yang sudah ada")
    a = ap.parse_args()

    base = QUICK if a.quick else FULL
    a.bits = a.bits or base["bits"]
    a.k = a.k or base["k"]
    a.reps = a.reps if a.reps is not None else base["reps"]
    bits_list = [int(x) for x in a.bits.split(",")]
    k_list = [int(x) for x in a.k.split(",")]

    host = safe_hostname()
    suffix = f"_{host}" + (f"_{a.tag}" if a.tag else "")
    out_dir = os.path.abspath(a.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    keys_path = os.path.join(out_dir, f"benchmark_keys{suffix}.json")
    raw_path = os.path.join(out_dir, f"benchmark_raw{suffix}.csv")
    meta_path = os.path.join(out_dir, f"benchmark_meta{suffix}.json")
    exit_if_exists(raw_path, a.overwrite)
    exit_if_exists(meta_path, a.overwrite)
    if not a.reuse_keys:
        exit_if_exists(keys_path, a.overwrite)

    t_wall = time.perf_counter()
    started = datetime.datetime.now().isoformat(timespec="seconds")
    load_start = load_average()
    commit, dirty = source_commit()
    print(f"[info] host={host} commit={commit} dirty={dirty} loadavg_awal={load_start}", flush=True)

    # ---------------- Fase A: kunci (di luar pengukuran) ----------------
    combos = [(b, k) for b in bits_list for k in k_list if b // k >= 4]
    keys, attempts = {}, {}
    if a.reuse_keys and os.path.exists(keys_path):
        with open(keys_path, encoding="utf-8") as fh:
            stored = json.load(fh)
        for name, rec in stored.items():
            b, k = map(int, name.split("-"))
            keys[(b, k)], attempts[(b, k)] = rec["key"], rec["attempts"]
    todo = [c for c in combos if c not in keys]
    t0 = time.perf_counter()
    if todo:
        todo.sort(key=lambda c: (-c[0], -c[1]))  # yang terberat dulu
        workers = max(1, min(a.workers, os.cpu_count() or 1, len(todo)))
        # fork hanya di Linux; macOS dan Windows memakai spawn (fork tidak tersedia/tidak aman)
        ctx = mp.get_context("fork" if sys.platform.startswith("linux") else "spawn")
        print(f"[kunci] membangkitkan {len(todo)} kunci dengan panjang n TEPAT ({workers} proses, {ctx.get_start_method()})...", flush=True)
        with ctx.Pool(workers) as pool:
            for b, k, att, dt, key in pool.imap_unordered(make_key_exact, todo):
                keys[(b, k)], attempts[(b, k)] = key, att
                print(f"[kunci] bits={b:5d} k={k} percobaan={att:4d} waktu={dt:7.1f}s", flush=True)
        with open(keys_path, "w", encoding="utf-8") as fh:
            json.dump({f"{b}-{k}": {"attempts": attempts[(b, k)], "key": keys[(b, k)]} for (b, k) in keys}, fh)
    print(f"[kunci] selesai dalam {time.perf_counter() - t0:.1f}s; disimpan di {keys_path}", flush=True)

    # ---------------- Fase B: pengukuran ----------------
    pinned = pin_cpu(a.cpu, a.no_pin)
    env = dict(timestamp=None, python_version=sys.version.split()[0], os=platform.platform(), cpu=cpu_model(), hostname=host,
               pinned_cpu=pinned)
    load_before = load_average()
    print(f"[ukur] python={env['python_version']} os={env['os']} cpu={env['cpu']} pin={pinned} loadavg={load_before}", flush=True)
    spin_end = time.perf_counter() + 3.0  # naikkan frekuensi CPU dari idle (tidak dicatat)
    while time.perf_counter() < spin_end:
        pow(3, 10 ** 5, 10 ** 30 + 7)

    rows_total, t_start, failed = 0, time.perf_counter(), False
    with open(raw_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for (bits, k) in combos:
            key = keys[(bits, k)]
            ms, cs = V.make_plaintexts_and_ciphertexts(key, a.n_ct, seed=a.seed + bits * 10 + k)
            for c in cs:
                assert 0 <= c < key["public_key"]["n"]
            priv, methods = build_methods(key)
            check_gauss_variants(priv, cs[0])
            rng = random.Random(f"{a.seed}-{bits}-{k}")
            for wu in range(a.warmup):  # pemanasan: tidak dicatat
                order = methods[:]
                rng.shuffle(order)
                for _, _, fn in order:
                    fn(cs[wu % len(cs)])
            rows = []
            gc.collect()
            gc.disable()
            try:
                for r in range(a.reps):
                    idx = r % len(cs)
                    order = methods[:]
                    rng.shuffle(order)  # urutan metode diacak tiap putaran
                    for layer, name, fn in order:
                        t_a = time.perf_counter()
                        res, ops = fn(cs[idx])
                        dt = time.perf_counter() - t_a
                        ok = (res == ms[idx])
                        row = dict(env, timestamp=datetime.datetime.now().isoformat(timespec="milliseconds"),
                                   layer=layer, bits_target=bits, bits_actual=key["public_key"]["bits"], k=k, method=name,
                                   run_id=r, time_s=repr(dt), correct=ok)
                        for f in OP_FIELDS:
                            row[f] = ops[f] if ops else ""
                        rows.append(row)
                        if not ok:
                            failed = True
                            print(f"[GAGAL] hasil salah: bits={bits} k={k} layer={layer} metode={name} run={r}", flush=True)
                            break
                    if failed:
                        break
            finally:
                gc.enable()
            w.writerows(rows)
            fh.flush()
            rows_total += len(rows)
            print(f"[ukur] bits={bits:5d} k={k} baris={len(rows):4d} total={rows_total:6d} elapsed={time.perf_counter() - t_start:7.1f}s",
                  flush=True)
            if failed:
                break

    meta = dict(config=vars(a), env=env, hostname=host, source_commit=commit, source_dirty=dirty,
                python_full=sys.version, platform=platform.platform(), cpu_count=os.cpu_count(),
                core_has_use_precomputed_option=_HAS_PRECOMP_OPT,
                gauss_b_source=("core.rsa.decrypt_crt_gauss (default; koefisien dari kunci)" if _HAS_PRECOMP_OPT
                                else "bench/variants.decrypt_crt_gauss_precomp (kode inti lama)"),
                keygen_attempts={f"{b}-{k}": v for (b, k), v in attempts.items()},
                loadavg_start=load_start, loadavg_before_measure=load_before, loadavg_end=load_average(),
                started=started, finished=datetime.datetime.now().isoformat(timespec="seconds"),
                wall_time_s=time.perf_counter() - t_wall, measure_time_s=time.perf_counter() - t_start,
                rows=rows_total, failed=failed)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    if failed:
        print("[GAGAL] benchmark dihentikan karena ada hasil dekripsi yang tidak cocok.", flush=True)
        return 2
    print(f"[selesai] {rows_total} baris -> {raw_path}", flush=True)
    print(f"[selesai] meta -> {meta_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

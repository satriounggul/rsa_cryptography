#!/usr/bin/env python3
"""
Membuat dist/kriptografi_rsa_final.zip dari sebuah commit/tag git (default: tag v1-final).

Berkas diambil dari objek commit (git archive), bukan dari folder kerja, sehingga isi zip identik dengan commit
dan tidak mungkin memuat berkas yang tidak di-commit. Zip bersifat deterministik (urutan berkas, cap waktu = waktu
commit, atribut tetap): membangun ulang dari commit yang sama menghasilkan SHA-256 yang sama.

Dikecualikan dari zip (sesuai permintaan):
  __pycache__, *.pyc, .venv (di mana pun, termasuk bench/.venv), .git,
  results/**/benchmark_keys*.json,
  Laporan_Proyek_Multi-Prime_RSA.md  (dokumen mata kuliah lain),
  docs/stitch-reference/             (tidak dipakai program),
  bahan INTERNAL (keputusan penyusun, 28 Okt 2026): REVIEW.md (taksiran nilai dan kritik), FINAL_CHECKLIST.md,
  results/final/perbandingan_baseline.md (merujuk berkas baseline yang tidak ikut di zip;
  tetap ada di repo), dan seluruh results/ KECUALI results/final/ (hasil baseline pra-perbaikan dan catatan audit).
  bench/, results/final/, dan paper/ (bahan makalah) dipertahankan.

Skrip ini tidak menghapus berkas apa pun dan menolak menimpa zip yang sudah ada bila isinya berbeda.

Pemakaian:
  python3 bench/make_submission_zip.py                       # dari tag v1-final -> dist/kriptografi_rsa_final.zip
  python3 bench/make_submission_zip.py --ref final-submission --out dist/kriptografi_rsa_final_v2.zip
"""
import argparse
import datetime
import fnmatch
import hashlib
import io
import os
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "kriptografi_rsa/"

EXCLUDE_DIR_NAMES = {"__pycache__", ".venv", ".git"}          # komponen path mana pun
EXCLUDE_SUFFIXES = (".pyc",)
EXCLUDE_BASENAME_GLOBS = ["benchmark_keys*.json"]              # nama berkas di kedalaman mana pun
EXCLUDE_EXACT = {"Laporan_Proyek_Multi-Prime_RSA.md", "REVIEW.md", "FINAL_CHECKLIST.md",
                 "results/final/perbandingan_baseline.md"}   # path relatif terhadap akar repo
EXCLUDE_PREFIXES = ("docs/stitch-reference/",)
KEEP_RESULTS_PREFIX = "results/final/"                         # dari results/ hanya sub-folder ini yang ikut

EXCLUSION_TEXT = ("__pycache__, *.pyc, .venv (termasuk bench/.venv), .git, benchmark_keys*.json, "
                  "Laporan_Proyek_Multi-Prime_RSA.md, docs/stitch-reference/, REVIEW.md, FINAL_CHECKLIST.md, "
                  "results/final/perbandingan_baseline.md, results/ kecuali results/final/")


def excluded(path):
    parts = path.split("/")
    if any(p in EXCLUDE_DIR_NAMES for p in parts):
        return True
    if path.endswith(EXCLUDE_SUFFIXES):
        return True
    if any(fnmatch.fnmatch(parts[-1], g) for g in EXCLUDE_BASENAME_GLOBS):
        return True
    if path in EXCLUDE_EXACT:
        return True
    if path.startswith("results/") and not path.startswith(KEEP_RESULTS_PREFIX):
        return True
    return path.startswith(EXCLUDE_PREFIXES)


def git(*args, binary=False):
    res = subprocess.run(["git", "-C", ROOT, *args], capture_output=True)
    if res.returncode != 0:
        sys.exit(f"git {' '.join(args)} gagal: {res.stderr.decode(errors='replace').strip()}")
    return res.stdout if binary else res.stdout.decode().strip()


def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="v1-final", help="commit, tag, atau branch sumber (default: v1-final)")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "kriptografi_rsa_final.zip"))
    ap.add_argument("--quiet", action="store_true", help="jangan cetak daftar isi")
    a = ap.parse_args()

    commit = git("rev-parse", "--verify", f"{a.ref}^{{commit}}")
    commit_time = int(git("show", "-s", "--format=%ct", commit))
    commit_iso = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    zip_time = datetime.datetime.fromtimestamp(commit_time, datetime.timezone.utc).timetuple()[:6]

    tar = tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", commit, binary=True)))
    members = sorted((m for m in tar.getmembers() if m.isfile() and not excluded(m.name)), key=lambda m: m.name)
    skipped = sorted(m.name for m in tar.getmembers() if m.isfile() and excluded(m.name))

    info = (f"Kriptografi RSA (Multi-Prime RSA) - paket pengumpulan\n"
            f"ref sumber     : {a.ref}\n"
            f"commit         : {commit}\n"
            f"waktu commit   : {commit_iso}\n"
            f"jumlah berkas  : {len(members)} (belum termasuk BUILD_INFO.txt)\n"
            f"dikecualikan   : {EXCLUSION_TEXT}\n"
            f"Verifikasi     : cd kriptografi_rsa && python -m unittest discover tests\n")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for m in members:
            zi = zipfile.ZipInfo(PREFIX + m.name, date_time=zip_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (0o755 if m.mode & 0o111 else 0o644) << 16
            zf.writestr(zi, tar.extractfile(m).read())
        zi = zipfile.ZipInfo(PREFIX + "BUILD_INFO.txt", date_time=zip_time)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        zf.writestr(zi, info)
    data = buf.getvalue()

    # pemeriksaan mandiri: tidak ada berkas terlarang di dalam zip
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n[len(PREFIX):] for n in zf.namelist()]
    bad = [n for n in names if n != "BUILD_INFO.txt" and excluded(n)]
    if bad:
        sys.exit(f"GAGAL: berkas terlarang ada di zip: {bad}")

    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        with open(out, "rb") as fh:
            if fh.read() != data:
                sys.exit(f"{out} sudah ada dengan isi berbeda; tidak ditimpa. Pakai --out lain atau hapus manual.")
        print(f"(zip sudah ada dan identik byte demi byte: {out})")
    else:
        with open(out, "wb") as fh:
            fh.write(data)
    digest = sha256_of(data)
    with open(out + ".sha256", "w", encoding="utf-8") as fh:
        fh.write(f"{digest}  {os.path.basename(out)}\n")

    print(f"ref={a.ref} commit={commit}")
    print(f"zip : {out} ({len(data)} byte, {len(names)} berkas)")
    print(f"SHA-256: {digest}")
    if not a.quiet:
        print(f"\nDikecualikan ({len(skipped)} berkas terlacak git): " + (", ".join(skipped) if skipped else "-"))
        print("\nIsi zip:")
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for zi in zf.infolist():
                print(f"  {zi.file_size:9d}  {zi.filename}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

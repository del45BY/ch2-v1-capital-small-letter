"""
CLI:  python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS

Membuat, dari sheet "Letters" dan "Templates" (template A..T):
  PRODUCTS/Alphabet_Tracing/<Key_Judul>/             PDF 1 halaman + Preview + Cover + Thumbnail  (satu per template)
  PRODUCTS/Alphabet_Tracing/<NamaPaket>/             PDF satu halaman per template (paket lengkap)
  PRODUCTS/qc_report.csv, manifest.csv, (image_prompts.csv)

Opsi:  --only A,C,T      hanya template tertentu          --no-pack     jangan buat paket lengkap
       --pack-name X     nama paket (default Alphabet_Tracing_Complete_Pack)   --no-templates  hanya paket
       --force           bangun ulang meski tidak berubah   --strict       peringatan dianggap gagal
       --workers 4       beberapa template sekaligus        --export-prompts  tulis image_prompts.csv (daftar PNG yang dibutuhkan)
"""
import argparse
import csv
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from .art import image_key
from .config import STYLE_NEGATIVE, STYLE_SUFFIX
from .database import load_library
from .qc import check_library, template_status, write_report
from .render import build_pack, build_template


def _job(args):
    t, lib, out, force = args
    return build_template(t, lib, out, force)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", required=True); ap.add_argument("--out", default="PRODUCTS")
    ap.add_argument("--only", help="kode template, mis. A,C,T")
    ap.add_argument("--no-pack", action="store_true"); ap.add_argument("--no-templates", action="store_true")
    ap.add_argument("--pack-name", default="Alphabet_Tracing_Complete_Pack")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--export-prompts", action="store_true")
    a = ap.parse_args(argv)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    lib, templates = load_library(a.db)
    print(f"Dibaca {len(templates)} template dan {len(lib)} huruf dari {a.db}")

    # 1. QC
    issues = check_library(lib, templates)
    status = template_status(templates, issues)
    write_report(issues, out / "qc_report.csv")
    for t in templates:
        print(f"  [{status[t.key]:4}] {t.key}  {t.type:8} {t.title_en}")
    for i in issues:
        if i.level != "INFO":
            print(f"         {i.level} {i.scope} ({i.check}): {i.message}")
    n_info = sum(1 for i in issues if i.level == "INFO")
    if n_info:
        print(f"  (INFO: {n_info} catatan, mis. gambar PNG belum ada -> kotak teks demo; lihat qc_report.csv)")

    if a.export_prompts:
        with open(out / "image_prompts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Letter", "Word_EN", "Word_ID", "Filename", "Prompt", "Negative"])
            for ch in sorted(lib):
                e = lib[ch]
                w.writerow([ch, e.word_en, e.word_id, image_key(e.word_en, e.image) + ".png",
                            f"{e.prompt}, {STYLE_SUFFIX}", STYLE_NEGATIVE])

    # 2. Pilih template
    ok = {"PASS"} if a.strict else {"PASS", "WARN"}
    only = {x.strip().upper() for x in a.only.split(",")} if a.only else None
    if only and (only - {t.key for t in templates}):
        sys.exit(f"Template tidak ada di database: {sorted(only - {t.key for t in templates})}")
    chosen = [t for t in templates if status[t.key] in ok and (not only or t.key in only)]
    skipped = [t.key for t in templates if t not in chosen and (not only or t.key in only)]

    # 3. Bangun
    results = []
    if not a.no_templates:
        jobs = [(t, lib, out, a.force) for t in chosen]
        if a.workers > 1:
            with ProcessPoolExecutor(a.workers) as ex:
                results = [f.result() for f in as_completed([ex.submit(_job, j) for j in jobs])]
        else:
            results = [_job(j) for j in jobs]
        results.sort(key=lambda r: r["key"])
    if not a.no_pack and chosen:
        results.append(build_pack(chosen, lib, a.pack_name, out, a.force))

    with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Template", "Name", "Folder", "Rebuilt", "Pages", "QC"])
        for r in results:
            w.writerow([r["key"], r["name"], r["folder"], r["built"], r["pages"], status.get(r["key"], "PACK")])
    built = sum(r["built"] for r in results)
    print(f"\nSelesai: {built} dibangun, {len(results) - built} tidak berubah, "
          f"{len(skipped)} dilewati ({', '.join(skipped) or '-'}).  Hasil: {out.resolve()}")


if __name__ == "__main__":
    main()

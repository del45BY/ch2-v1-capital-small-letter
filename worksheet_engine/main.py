"""
CLI:  python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS

Membuat, dari sheet "Database" (1 tema = 1 template A..J = 5 kata):
  PRODUCTS/Tracing_Words/<NN_Tema>/                 PDF 1 halaman + Preview + Cover + Thumbnail  (satu per tema)
  PRODUCTS/Tracing_Words/<NamaPaket>/               PDF satu halaman per tema (paket lengkap)
  PRODUCTS/qc_report.csv, manifest.csv, (image_prompts.csv)

Opsi:  --only A,C        hanya template tertentu          --no-pack     jangan buat paket lengkap
       --pack-name X     nama paket (default Tracing_Words_Complete_Pack)   --no-themes   hanya paket
       --force           bangun ulang meski tidak berubah   --strict       peringatan dianggap gagal
       --workers 4       beberapa tema sekaligus            --export-prompts  tulis image_prompts.csv
"""
import argparse
import csv
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from .config import STYLE_NEGATIVE, STYLE_SUFFIX
from .database import load_themes
from .qc import check_themes, theme_status, write_report
from .render import build_pack, build_theme


def _job(args):
    theme, out, force = args
    return build_theme(theme, out, force)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", required=True); ap.add_argument("--out", default="PRODUCTS")
    ap.add_argument("--only", help="kode template, mis. A,C")
    ap.add_argument("--no-pack", action="store_true"); ap.add_argument("--no-themes", action="store_true")
    ap.add_argument("--pack-name", default="Tracing_Words_Complete_Pack")
    ap.add_argument("--force", action="store_true"); ap.add_argument("--strict", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--export-prompts", action="store_true")
    a = ap.parse_args(argv)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    themes = load_themes(a.db)
    print(f"Dibaca {len(themes)} tema ({sum(len(t.words) for t in themes)} kata) dari {a.db}")

    # 1. QC
    issues = check_themes(themes)
    status = theme_status(themes, issues)
    write_report(issues, out / "qc_report.csv")
    for t in themes:
        print(f"  [{status[t.key]:4}] {t.key}  {t.num} {t.en} / {t.idn}: " + ", ".join(w.en for w in t.words))
    for i in issues:
        print(f"         {i.level} {i.theme}/{i.ref} ({i.check}): {i.message}")

    if a.export_prompts:
        with open(out / "image_prompts.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Template", "ID", "Word", "Prompt", "Negative", "Filename"])
            for t in themes:
                for wd in t.words:
                    w.writerow([t.key, wd.wid, wd.en, f"{wd.prompt}, {STYLE_SUFFIX}", STYLE_NEGATIVE, f"{wd.en.lower()}.png"])

    # 2. Pilih tema yang dibangun
    ok = {"PASS"} if a.strict else {"PASS", "WARN"}
    only = {x.strip().upper() for x in a.only.split(",")} if a.only else None
    if only and (only - {t.key for t in themes}):
        sys.exit(f"Template tidak ada di database: {sorted(only - {t.key for t in themes})}")
    chosen = [t for t in themes if status[t.key] in ok and (not only or t.key in only)]
    skipped = [t.key for t in themes if t not in chosen and (not only or t.key in only)]

    # 3. Bangun
    results = []
    if not a.no_themes:
        jobs = [(t, out, a.force) for t in chosen]
        if a.workers > 1:
            with ProcessPoolExecutor(a.workers) as ex:
                results = [f.result() for f in as_completed([ex.submit(_job, j) for j in jobs])]
        else:
            results = [_job(j) for j in jobs]
        results.sort(key=lambda r: r["key"])
    if not a.no_pack and chosen:
        results.append(build_pack(chosen, a.pack_name, out, a.force))

    with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Template", "Name", "Folder", "Rebuilt", "Pages", "QC"])
        for r in results:
            w.writerow([r["key"], r["name"], r["folder"], r["built"], r["pages"],
                        status.get(r["key"], "PACK")])
    built = sum(r["built"] for r in results)
    print(f"\nSelesai: {built} dibangun, {len(results) - built} tidak berubah, "
          f"{len(skipped)} dilewati ({', '.join(skipped) or '-'}).  Hasil: {out.resolve()}")


if __name__ == "__main__":
    main()

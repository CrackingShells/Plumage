#!/usr/bin/env python3
"""Convert digital-native PDFs to Markdown with correctly-positioned images.

pandoc cannot read PDF directly -- it only writes Markdown. This tool supplies
the missing half: pdftohtml for clean reflowed page-anchored text, pdfimages
for page-tagged figure extraction, a splice step that interleaves <img> tags
at the right page, then pandoc to do the HTML -> Markdown conversion.

Subcommands: convert (one file), batch (a directory tree, parallel), check
(spot-check a batch's output). See SKILL.md for usage and rationale.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

REQUIRED_TOOLS = ["pdftohtml", "pdftotext", "pdfinfo", "pdfimages", "pandoc"]

# Below this, a PDF is treated as scanned/image-only (needs OCR, out of scope
# here) rather than digital-native. Real academic papers in this pipeline's
# corpus land around 1500-5400 chars/page; near-zero is the scanned signal.
MIN_CHARS_PER_PAGE = 200

# Extracted images smaller than this on either axis are treated as icons/logos
# rather than genuine figures. This is a heuristic, not a guarantee -- `check`
# flags large filtering ratios for human review rather than trusting it blindly.
MIN_IMAGE_DIM = 60

EXIT_OK = 0
EXIT_HARD_FAIL = 1
EXIT_SKIPPED_SCANNED = 2

IMG_FILENAME_RE = re.compile(r"^img-(\d+)-(\d+)\.png$")
PAGE_DIV_RE = re.compile(r"page(\d+)-div")
PAGE_WRAPPER_LINE_RE = re.compile(r'^(<div id="page\d+-div"[^>]*>|</div>)\s*$')
# Paper filenames sometimes contain literal parens (e.g. "plants(2)-annotated",
# "Peptides (CRPs)"), and pandoc doesn't percent-encode them -- CommonMark link
# destinations allow one level of balanced nested parens unescaped. A naive
# "[^)]+" capture stops at the first ")" inside the filename itself, so this
# pattern explicitly allows one balanced nested group before the real closer.
MD_IMAGE_REF_RE = re.compile(r"!\[[^\]]*\]\(((?:[^()]|\([^()]*\))*)\)")

_print_lock = threading.Lock()


def log(message: str) -> None:
    with _print_lock:
        print(message, flush=True)


def missing_dependencies() -> list:
    return [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]


def require_dependencies() -> None:
    missing = missing_dependencies()
    if missing:
        print(f"Missing required tools: {', '.join(missing)}", file=sys.stderr)
        print("See references/install.md for how to install poppler-utils + pandoc.", file=sys.stderr)
        sys.exit(EXIT_HARD_FAIL)


@dataclass
class ConvertResult:
    src: Path
    status: str  # "ok" | "skipped" | "failed"
    message: str
    figure_count: int = 0
    warnings: list = field(default_factory=list)


def classify(src: Path) -> tuple:
    """Return (pages, chars, chars_per_page)."""
    info = subprocess.run(["pdfinfo", str(src)], capture_output=True, text=True, errors="replace")
    pages = 1
    for line in info.stdout.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
            break
    text = subprocess.run(["pdftotext", str(src), "-"], capture_output=True, text=True, errors="replace")
    chars = len(text.stdout)
    return pages, chars, chars / max(pages, 1)


def parse_pdfimages_list(src: Path) -> dict:
    """Return {(page, index): (width, height)} for every embedded raster image."""
    proc = subprocess.run(["pdfimages", "-list", "-q", str(src)], capture_output=True, text=True, errors="replace")
    dims = {}
    lines = proc.stdout.splitlines()
    for line in lines[2:]:  # skip header + separator row
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            page, index = int(parts[0]), int(parts[1])
            width, height = int(parts[3]), int(parts[4])
        except ValueError:
            continue
        dims[(page, index)] = (width, height)
    return dims


def convert_one(src: Path, out_dir: Path) -> ConvertResult:
    src = src.resolve()
    base = src.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        pages, chars, chars_per_page = classify(src)
    except Exception as exc:
        return ConvertResult(src, "failed", f"classify error: {exc}")

    if chars_per_page < MIN_CHARS_PER_PAGE:
        return ConvertResult(
            src, "skipped",
            f"looks scanned/image-only ({chars_per_page:.0f} chars/page over {pages} pages) -- needs OCR, out of scope",
        )

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        # pdftohtml -s appends "-html" to the given stem before the extension.
        html_arg = tmp / "clean.html"
        html_result = subprocess.run(
            ["pdftohtml", "-s", "-i", "-q", str(src), str(html_arg)],
            capture_output=True, text=True, errors="replace",
        )
        html_file = tmp / "clean-html.html"
        if not html_file.exists():
            return ConvertResult(src, "failed", f"pdftohtml produced no output: {html_result.stderr.strip()}")

        subprocess.run(
            ["pdfimages", "-png", "-p", "-q", str(src), str(tmp / "img")],
            capture_output=True, text=True, errors="replace",
        )
        dims = parse_pdfimages_list(src)

        page_images = {}  # page -> [markdown-relative image path, ...]
        images_dir = out_dir / "images"
        for image_file in sorted(tmp.glob("img-*.png")):
            match = IMG_FILENAME_RE.match(image_file.name)
            if not match:
                continue
            page, index = int(match.group(1)), int(match.group(2))
            width, height = dims.get((page, index), (0, 0))
            if width >= MIN_IMAGE_DIM and height >= MIN_IMAGE_DIM:
                images_dir.mkdir(parents=True, exist_ok=True)
                dest_name = f"{base}_{image_file.name}"
                shutil.copyfile(image_file, images_dir / dest_name)
                page_images.setdefault(page, []).append(f"images/{dest_name}")

        html_text = html_file.read_text(encoding="utf-8", errors="replace")
        spliced_lines = []
        for line in html_text.split("\n"):
            spliced_lines.append(line)
            match = PAGE_DIV_RE.search(line)
            if match:
                page = int(match.group(1))
                for image_path in page_images.get(page, []):
                    spliced_lines.append(f'<p><img src="{image_path}" alt="figure page {page}"></p>')
        spliced_html = tmp / "spliced.html"
        spliced_html.write_text("\n".join(spliced_lines), encoding="utf-8")

        raw_md = tmp / "raw.md"
        pandoc_result = subprocess.run(
            ["pandoc", str(spliced_html), "-f", "html", "-t", "gfm", "--wrap=none", "-o", str(raw_md)],
            capture_output=True, text=True, errors="replace",
        )
        if not raw_md.exists():
            return ConvertResult(src, "failed", f"pandoc failed: {pandoc_result.stderr.strip()}")

        warnings = []
        stderr_lower = pandoc_result.stderr.lower()
        if "latin1" in stderr_lower or "not utf-8" in stderr_lower:
            warnings.append(f"pandoc encoding fallback: {pandoc_result.stderr.strip()}")

        final_text = "\n".join(
            line for line in raw_md.read_text(encoding="utf-8", errors="replace").split("\n")
            if not PAGE_WRAPPER_LINE_RE.match(line)
        )
        # A small number of older PDFs embed subset fonts whose glyph-to-codepoint
        # mapping is broken, so pdftohtml emits genuinely invalid UTF-8 for a
        # character or two (usually an accented name in a reference list). This
        # is replaced with U+FFFD when read above rather than silently passed
        # through -- surface that here so the affected file is easy to find.
        replacement_count = final_text.count("�")
        if replacement_count:
            warnings.append(
                f"{replacement_count} character(s) could not be decoded as UTF-8 "
                "(subset-font encoding issue in the source PDF) -- replaced with "
                "U+FFFD; search the output for the replacement character to locate them"
            )
        (out_dir / f"{base}.md").write_text(final_text, encoding="utf-8")

    figure_count = sum(len(v) for v in page_images.values())
    return ConvertResult(src, "ok", f"{figure_count} figures", figure_count=figure_count, warnings=warnings)


def write_sidecar_log(dest_dir: Path, base: str, result: ConvertResult) -> None:
    lines = [f"STATUS: {result.status}", f"MESSAGE: {result.message}"]
    for warning in result.warnings:
        lines.append(f"WARNING: {warning}")
    (dest_dir / f"{base}.convert.log").write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_pdfs(src_root: Path) -> list:
    return sorted(p for p in src_root.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")


def cmd_convert(args) -> int:
    require_dependencies()
    result = convert_one(Path(args.src), Path(args.out_dir))
    if result.status == "ok":
        print(f"OK: {result.src} -> {result.figure_count} figures")
        for warning in result.warnings:
            print(f"  WARNING: {warning}", file=sys.stderr)
        return EXIT_OK
    if result.status == "skipped":
        print(f"SKIPPED: {result.src}: {result.message}", file=sys.stderr)
        return EXIT_SKIPPED_SCANNED
    print(f"FAILED: {result.src}: {result.message}", file=sys.stderr)
    return EXIT_HARD_FAIL


def cmd_batch(args) -> int:
    require_dependencies()
    src_root = Path(args.src_root).resolve()
    dest_root = Path(args.dest_root).resolve()
    pdfs = find_pdfs(src_root)
    if not pdfs:
        print(f"No PDFs found under {src_root}", file=sys.stderr)
        return EXIT_HARD_FAIL

    tally = {"ok": 0, "skipped": 0, "failed": 0}
    total_figures = 0

    def process(pdf: Path):
        rel = pdf.relative_to(src_root)
        dest_dir = dest_root / rel.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        result = convert_one(pdf, dest_dir)
        write_sidecar_log(dest_dir, pdf.stem, result)
        return result

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(process, pdf): pdf for pdf in pdfs}
        for future in as_completed(futures):
            pdf = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                tally["failed"] += 1
                log(f"FAILED: {pdf}: unhandled error: {exc}")
                continue
            tally[result.status] += 1
            total_figures += result.figure_count
            tag = {"ok": "OK", "skipped": "SKIPPED", "failed": "FAILED"}[result.status]
            log(f"{tag}: {result.src}: {result.message}")

    print()
    print(f"Done: {tally['ok']} ok, {tally['skipped']} skipped (scanned), {tally['failed']} failed, {total_figures} figures total")
    print(f"Run `check {src_root} {dest_root}` to spot-check the output.")
    return EXIT_OK if tally["failed"] == 0 else EXIT_HARD_FAIL


def cmd_check(args) -> int:
    src_root = Path(args.src_root).resolve()
    dest_root = Path(args.dest_root).resolve()
    pdfs = find_pdfs(src_root)
    if not pdfs:
        print(f"No PDFs found under {src_root}", file=sys.stderr)
        return EXIT_HARD_FAIL

    counts = {"ok": 0, "warn": 0, "fail": 0}

    for pdf in pdfs:
        rel = pdf.relative_to(src_root)
        dest_dir = dest_root / rel.parent
        md_path = dest_dir / f"{rel.stem}.md"
        log_path = dest_dir / f"{rel.stem}.convert.log"
        reasons = []
        level = "OK"

        log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        if "STATUS: skipped" in log_text:
            log(f"SKIPPED: {rel}: classified as scanned, out of scope")
            continue

        if not md_path.exists():
            log(f"FAIL: {rel}: no corresponding Markdown file at {md_path}")
            counts["fail"] += 1
            continue

        md_text = md_path.read_text(encoding="utf-8", errors="replace")
        if len(md_text.strip()) < 100:
            level = "FAIL"
            reasons.append("Markdown file is suspiciously small (<100 chars) -- possible botched extraction")

        actual_refs = MD_IMAGE_REF_RE.findall(md_text)
        dims = parse_pdfimages_list(pdf)
        total_raw = len(dims)
        expected_kept = sum(1 for (w, h) in dims.values() if w >= MIN_IMAGE_DIM and h >= MIN_IMAGE_DIM)

        if len(actual_refs) != expected_kept:
            level = "FAIL"
            reasons.append(f"image count mismatch: markdown has {len(actual_refs)}, expected {expected_kept} kept (of {total_raw} raw)")
        elif total_raw > 0 and expected_kept / total_raw < 0.5:
            if level == "OK":
                level = "WARN"
            reasons.append(f"heavy image filtering: {expected_kept}/{total_raw} kept -- verify manually this is expected")

        for ref in actual_refs:
            # pandoc percent-encodes spaces/special chars in link targets (e.g.
            # "img%20name.png"); the file on disk has the literal characters.
            image_path = (md_path.parent / unquote(ref)).resolve()
            if not image_path.exists():
                level = "FAIL"
                reasons.append(f"referenced image missing on disk: {ref}")
            elif image_path.stat().st_size == 0:
                level = "FAIL"
                reasons.append(f"referenced image is 0 bytes: {ref}")

        if "could not be decoded as UTF-8" in log_text or "�" in md_text:
            if level == "OK":
                level = "WARN"
            reasons.append("subset-font encoding gotcha: source PDF had undecodable bytes, replaced with U+FFFD ('�') -- check those spots")

        counts[level.lower()] += 1
        suffix = f": {'; '.join(reasons)}" if reasons else ""
        log(f"{level}: {rel}{suffix}")

    print()
    print(f"Done: {counts['ok']} ok, {counts['warn']} warn, {counts['fail']} fail")
    return EXIT_OK if counts["fail"] == 0 else EXIT_HARD_FAIL


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert one PDF to Markdown + images")
    convert_parser.add_argument("src", help="Source PDF path")
    convert_parser.add_argument("out_dir", help="Output directory for the .md file and images/")
    convert_parser.set_defaults(func=cmd_convert)

    batch_parser = subparsers.add_parser("batch", help="Convert every PDF under a directory tree, mirroring structure")
    batch_parser.add_argument("src_root", help="Root directory to search for PDFs")
    batch_parser.add_argument("dest_root", help="Root directory to mirror output into")
    batch_parser.add_argument("--jobs", "-j", type=int, default=4, help="Parallel worker count (default: 4)")
    batch_parser.set_defaults(func=cmd_batch)

    check_parser = subparsers.add_parser("check", help="Spot-check a batch conversion's output")
    check_parser.add_argument("src_root", help="Root directory of source PDFs")
    check_parser.add_argument("dest_root", help="Root directory of converted output")
    check_parser.set_defaults(func=cmd_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

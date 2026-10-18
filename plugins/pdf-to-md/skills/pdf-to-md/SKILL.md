---
name: pdf-to-md
description: >
  Converts digital-native (non-scanned) PDFs into Markdown with figures embedded
  at their correct position in the text, using a poppler + pandoc pipeline with
  automatic scanned-PDF detection and a spot-check pass. Use this whenever asked
  to convert, extract, or turn a PDF (or a folder of PDFs) into Markdown --
  especially phrases like "convert this PDF to markdown", "extract this paper to
  markdown with images", "pdf to md", "batch convert these PDFs", or "give me a
  markdown version of this paper with the figures". Trigger this even if the user
  just says "use pandoc on this PDF" -- pandoc cannot read PDF directly
  (`pandoc --list-input-formats` has no `pdf` entry; it only writes Markdown), so
  any PDF-to-Markdown request needs this skill's pipeline, not pandoc alone.
---

# PDF to Markdown

## Why pandoc alone doesn't work

Pandoc converts *between* structured document formats -- it has no PDF reader.
Run `pandoc --list-input-formats` and PDF isn't in the list. The actual
PDF-to-Markdown conversion needs poppler's tools to pull structured content out of
the PDF first (`pdftohtml` for reflowed text, `pdfimages` for embedded figures);
pandoc only does the last step, turning that intermediate HTML into Markdown.
`scripts/pdf_to_md.py` runs the whole chain.

## One-time setup

Read `references/install.md` and confirm two things are in place: an isolated
Python (prefer `uv run`, see that file for the fallback chain) and poppler-utils +
pandoc on `PATH`. The script checks for all five CLI tools itself and tells you
exactly what's missing if setup isn't done.

## Step 1: classification happens automatically

Before doing any conversion work, the script compares `pdfinfo`'s page count
against `pdftotext`'s extracted character count. Real digital-native academic
papers land around 1500-5400 chars/page; a PDF that's actually a scan of pages
(no real text layer) reads near-zero. Below ~200 chars/page, the script treats
the PDF as scanned/image-only and skips it with a clear message instead of
silently producing a near-empty Markdown file -- scanned PDFs need OCR, which is
a different job outside this skill's scope.

## Step 2: convert

**One file:**
```bash
uv run scripts/pdf_to_md.py convert path/to/paper.pdf path/to/out_dir
```
Writes `out_dir/paper.md` and, if the PDF has genuine figures, `out_dir/images/`.
Prints the figure count on success, or an explanation if the PDF was skipped as
scanned.

**A whole folder, in parallel:**
```bash
uv run scripts/pdf_to_md.py batch path/to/pdfs/ path/to/markdown_out/ --jobs 4
```
Mirrors `pdfs/`'s directory structure under `markdown_out/`, converting every
`*.pdf` it finds. `--jobs` controls how many conversions run concurrently
(default 4) -- safe to raise since each worker mostly waits on the external
`pdftohtml`/`pdfimages`/`pandoc` subprocesses, not CPU. Prints a running log plus
a final OK/SKIPPED/FAILED tally, and writes a `<paper>.convert.log` sidecar next
to each output for `check` to read later.

## Step 3: spot-check the output

```bash
uv run scripts/pdf_to_md.py check path/to/pdfs/ path/to/markdown_out/
```
Don't skip this -- it's what catches the class of silent failure that otherwise
requires manual debugging (see Known limitations below). For every source PDF it
checks:
- a corresponding `.md` file exists and isn't suspiciously small
- the Markdown's image-reference count matches what the filter should have kept,
  given a fresh `pdfimages -list` read of the source (an exact mismatch is a real
  bug and prints `FAIL`; a large filter ratio -- e.g. a math-heavy PDF with
  hundreds of tiny rasterized glyph fragments -- prints `WARN` so you can eyeball
  whether that's expected rather than treating it as broken)
- every referenced image file actually exists on disk and is non-zero bytes
- the sidecar log for that file, if any, for the encoding-fallback marker
  described below

Prints one `OK`/`WARN`/`FAIL` line per file plus a summary count.

## How the pipeline works, under the hood

For each PDF: `pdftohtml -s -i -q` produces clean, reflowed, page-anchored HTML
(`-i` skips pdftohtml's own image handling, which otherwise rasterizes whole
pages as a "background image" false-positive whenever a journal template uses
vector graphics it can't represent as text). `pdfimages -png -p -q` separately
extracts every genuine embedded raster figure, page-tagged in the filename.
`pdfimages -list` is parsed directly for widths/heights per (page, index) -- the
same numbering the `-p` flag encodes into filenames -- to decide which images
clear the ~60x60px figure-vs-icon bar, with no per-image subprocess needed. The
surviving `<img>` tags are spliced into the HTML immediately after each page's
div anchor, so figures land next to the text that references them instead of
being dumped at the end. Finally `pandoc -f html -t gfm --wrap=none` does the
HTML-to-Markdown conversion, and a last cleanup pass strips the now-redundant
page-wrapper `<div>` lines pandoc leaves behind as raw HTML.

Batch conversion runs this whole per-file pipeline across a thread pool
(`--jobs`) rather than a process pool, because each worker spends nearly all its
time blocked on the external subprocesses -- Python releases the GIL during that
wait, so threads parallelize the actual bottleneck without process-spawn or
pickling overhead.

## Known limitations

- **Subset-font encoding gotcha**: a small number of older PDFs embed subset
  fonts whose glyph-to-codepoint mapping is broken in a way that makes
  `pdftohtml` emit genuinely invalid UTF-8 for one or two characters (usually an
  accented author name in a reference list). Pandoc then falls back to latin1
  for that file and those characters render wrong (e.g. "Ferré" becomes
  "FerrÃ¨"). This is a poppler font-decoding limitation, not something this
  pipeline can reliably fix -- `check` surfaces it as a `WARN` so you know to
  glance at that specific file rather than trust it blindly.
- **The ~60x60px image filter is a heuristic**, not ground truth. It's tuned
  against a real corpus where 24/30 papers pass every image through untouched
  and 3 heavily filter (one from 415 raw images down to 19) because they're
  math/diagram-heavy PDFs with hundreds of tiny rasterized glyph fragments --
  legitimate filtering, not a bug. `check` flags large filter ratios for human
  review rather than treating them as failures, since the right call depends on
  the paper.
- **Scanned PDFs are out of scope.** The classification step skips them rather
  than guessing; if you need one converted, OCR it first (e.g. `pytesseract` +
  `pdf2image`) and feed the result through a different path.

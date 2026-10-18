# Installing pdf-to-md's dependencies

Two things need to be in place: an isolated Python to run `scripts/pdf_to_md.py`
through, and five CLI tools (poppler-utils + pandoc) on `PATH`. The script itself
has zero third-party Python dependencies (only `subprocess`, `pathlib`, `re`,
`shutil`, `argparse`, `concurrent.futures` -- all stdlib).

## 1. Isolated Python

Never invoke the script through the base/system interpreter, even though it has no
dependencies to resolve -- the isolation habit is the point, not just dependency
avoidance. In order of preference:

### uv (preferred)

No setup needed. Just run the script through `uv run`, which provisions an
ephemeral isolated environment per invocation:

```bash
uv run scripts/pdf_to_md.py convert some_paper.pdf out/
```

### conda / mamba (fallback)

Create a named environment once:

```bash
mamba create -n pdf-to-md python=3.11 -y
```

Then always invoke through it -- never the bare interpreter:

```bash
mamba run -n pdf-to-md python scripts/pdf_to_md.py convert some_paper.pdf out/
```

(`conda` works identically if you don't have `mamba`.)

### vanilla venv (last resort)

Bootstrap the venv once (this is the one acceptable use of a bare `python3` --
it's creating the isolation, not bypassing it):

```bash
python3 -m venv .venv
```

Then always invoke through the venv's own interpreter:

```bash
.venv/bin/python scripts/pdf_to_md.py convert some_paper.pdf out/      # macOS/Linux
.venv\Scripts\python.exe scripts\pdf_to_md.py convert some_paper.pdf out\   # Windows
```

## 2. poppler-utils + pandoc

These are prebuilt CLI tools, not Python packages -- no build/compile step.

**macOS (Homebrew):**
```bash
brew install poppler pandoc
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt install poppler-utils pandoc
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install poppler-utils pandoc
```

**Windows (choco):**
```powershell
choco install poppler pandoc
```

**Windows (scoop):**
```powershell
scoop install poppler pandoc
```

Windows installers are also available directly from the
[poppler for Windows](https://github.com/oschwartz10612/poppler-windows) releases
and [pandoc.org/installing.html](https://pandoc.org/installing.html) if you'd
rather not use a package manager.

## Verifying

Run any subcommand's `--help` -- the script checks for `pdftohtml`, `pdftotext`,
`pdfinfo`, `pdfimages`, and `pandoc` on `PATH` before doing any work, and will tell
you exactly which ones are missing if setup isn't complete:

```bash
uv run scripts/pdf_to_md.py convert --help
```

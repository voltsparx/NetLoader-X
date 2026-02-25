NetLoader-X Binary Build (Cross-Platform)
=========================================

This project includes a small PyInstaller setup for standalone binaries.

Script:

`scripts/install-netloader-x-binary.py`

Important
---------
PyInstaller does not reliably cross-compile from one OS to another.
Build on each target OS to get a native binary:
- Windows -> `.exe`
- Linux -> ELF binary
- macOS -> Mach-O binary


Quick Build
-----------

1) Install build dependency:

```bash
pip install -r requirements-build.txt
```

2) Build in test mode (build only, no install changes):

```bash
python scripts/install-netloader-x-binary.py --mode test --clean-dist --verify
```

3) Output location:
- Build output: `bin/netloader-x(.exe)` by default


Modes
-----

- `--mode test`:
  Build only. No PATH changes, no persistent config writes.

- `--mode install`:
  Build, then install:
  1) choose destination (`local/bin` recommended or custom)
  2) add destination to PATH
  3) configure persistent output directory

Default persistent output directory:

`$HOME/netloader-x-output`

You can override with `--output-dir`.


Build Options
-------------

- `--onedir`:
  Build a directory bundle instead of a single file.

- `--name <value>`:
  Change output binary name.

- `--dist-dir <path>`:
  Choose build output directory (default: `bin`).

- `--work-dir <path>`:
  Choose PyInstaller work directory.

- `--clean-dist`:
  Remove previous `dist/` and `build/` outputs before building.

- `--verify`:
  Run the built binary with `--version` after build.


Examples
--------

One-file build:

```bash
python scripts/install-netloader-x-binary.py --mode test --clean-dist --verify
```

Install mode (interactive):

```bash
python scripts/install-netloader-x-binary.py --mode install --clean-dist
```

Install mode (non-interactive with explicit paths):

```bash
python scripts/install-netloader-x-binary.py --mode install --non-interactive --destination ~/.local/bin --output-dir ~/netloader-x-output
```


GitHub Actions
--------------

A CI workflow is included at:

`/.github/workflows/build-binaries.yml`

It builds binaries on Windows, Linux, and macOS, then uploads artifacts.

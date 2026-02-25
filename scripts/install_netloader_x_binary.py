#!/usr/bin/env python3
"""
Install/Build helper for NetLoader-X standalone binaries.

Modes:
- install: build binary, copy to install destination, add destination to PATH,
  and configure persistent output directory.
- test: build binary only (no installation, no PATH/output config changes).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.user_settings import default_output_dir_home, set_persistent_output_dir


MODULES_TO_COLLECT = ["core", "ui", "utils", "targets", "plugins", "filters"]
RESOURCE_FILES = [
    Path("cluster-config-example.yaml"),
    Path("cluster-config-example.json"),
    Path("docs/Usage.txt"),
    Path("docs/BinaryBuild.md"),
    Path("README.md"),
]


def data_separator(os_name: Optional[str] = None) -> str:
    return ";" if (os_name or os.name) == "nt" else ":"


def add_data_argument(src: Path, dst: str, os_name: Optional[str] = None) -> str:
    return f"{src}{data_separator(os_name)}{dst}"


def build_pyinstaller_command(
    project_root: Path,
    name: str,
    onefile: bool,
    dist_dir: Path,
    work_dir: Path,
) -> List[str]:
    entrypoint = project_root / "netloader-x.py"
    if not entrypoint.exists():
        raise FileNotFoundError(f"Entrypoint not found: {entrypoint}")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--console",
        "--name",
        name,
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
    ]
    command.append("--onefile" if onefile else "--onedir")

    for module_name in MODULES_TO_COLLECT:
        command.extend(["--collect-submodules", module_name])

    for relative_path in RESOURCE_FILES:
        src = project_root / relative_path
        if not src.exists():
            continue
        dst = str(relative_path.parent) if str(relative_path.parent) != "." else "."
        command.extend(["--add-data", add_data_argument(src, dst)])

    command.append(str(entrypoint))
    return command


def expected_binary_path(dist_dir: Path, name: str, onefile: bool) -> Path:
    ext = ".exe" if os.name == "nt" else ""
    if onefile:
        return dist_dir / f"{name}{ext}"
    return dist_dir / name / f"{name}{ext}"


def local_bin_dir(os_name: Optional[str] = None) -> Path:
    if (os_name or os.name) == "nt":
        return Path.home() / "AppData" / "Local" / "bin"
    return Path.home() / ".local" / "bin"


def run_command(command: List[str], cwd: Path):
    print("Running:")
    print("  " + " ".join(command))
    subprocess.run(command, cwd=str(cwd), check=True)


def verify_binary(binary_path: Path):
    if not binary_path.exists():
        raise FileNotFoundError(f"Binary not found after build: {binary_path}")
    proc = subprocess.run(
        [str(binary_path), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    print("Verification output:")
    print(proc.stdout.strip() or proc.stderr.strip())


def _normalized(path_value: Path) -> str:
    return str(path_value.expanduser().resolve()).rstrip("\\/").lower()


def _path_contains(target_dir: Path) -> bool:
    target_norm = _normalized(target_dir)
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry.strip():
            continue
        if _normalized(Path(entry)) == target_norm:
            return True
    return False


def update_path_windows(target_dir: Path) -> str:
    if _path_contains(target_dir):
        return f"PATH already contains: {target_dir}"

    get_cmd = "[Environment]::GetEnvironmentVariable('Path','User')"
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", get_cmd],
        check=True,
        capture_output=True,
        text=True,
    )
    current_user_path = proc.stdout.strip()
    parts = [p for p in current_user_path.split(";") if p]
    target_str = str(target_dir)
    if target_str not in parts:
        parts.append(target_str)
    new_value = ";".join(parts)
    escaped = new_value.replace("'", "''")
    set_cmd = f"[Environment]::SetEnvironmentVariable('Path', '{escaped}', 'User')"
    subprocess.run(["powershell", "-NoProfile", "-Command", set_cmd], check=True)

    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + target_str
    return f"Added to user PATH: {target_dir}"


def _append_line_once(rc_file: Path, line: str):
    rc_file.parent.mkdir(parents=True, exist_ok=True)
    if rc_file.exists():
        text = rc_file.read_text(encoding="utf-8")
    else:
        text = ""
    if line in text:
        return
    with rc_file.open("a", encoding="utf-8") as handle:
        if text and not text.endswith("\n"):
            handle.write("\n")
        handle.write(line + "\n")


def update_path_posix(target_dir: Path) -> str:
    if _path_contains(target_dir):
        return f"PATH already contains: {target_dir}"

    target = str(target_dir)
    export_line = f'export PATH="$PATH:{target}"'

    shell_name = Path(os.environ.get("SHELL", "")).name.lower()
    rc_files = [Path.home() / ".profile"]
    if shell_name == "bash":
        rc_files.append(Path.home() / ".bashrc")
    elif shell_name == "zsh":
        rc_files.append(Path.home() / ".zshrc")

    for rc in rc_files:
        _append_line_once(rc, export_line)

    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + target
    touched = ", ".join(str(p) for p in rc_files)
    return f"Added PATH export in: {touched}"


def update_path(target_dir: Path) -> str:
    if os.name == "nt":
        return update_path_windows(target_dir)
    return update_path_posix(target_dir)


def prompt_destination(interactive: bool, default_dir: Path) -> Path:
    if not interactive:
        return default_dir

    print("\nSelect installation destination:")
    print("  1) local/bin (recommended)")
    print("  2) custom directory")
    choice = input("Choice [1/2]: ").strip() or "1"
    if choice == "2":
        raw = input("Enter custom destination directory: ").strip()
        if raw:
            return Path(raw).expanduser().resolve()
    return default_dir


def prompt_output_dir(interactive: bool, default_output: str, provided: Optional[str]) -> Path:
    if provided:
        return Path(provided).expanduser().resolve()
    if not interactive:
        return Path(default_output).expanduser().resolve()

    raw = input(f"Output directory [{default_output}]: ").strip()
    return Path(raw or default_output).expanduser().resolve()


def install_artifact(built_path: Path, destination_dir: Path, onefile: bool, name: str) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)

    if onefile:
        target_path = destination_dir / built_path.name
        shutil.copy2(built_path, target_path)
        if os.name != "nt":
            target_path.chmod(0o755)
        return target_path

    source_dir = built_path.parent
    target_dir = destination_dir / name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    return target_dir


def main():
    parser = argparse.ArgumentParser(
        description="Build/install NetLoader-X standalone binary with test/install modes."
    )
    parser.add_argument("--mode", choices=["install", "test"], default="install")
    parser.add_argument("--name", default="netloader-x", help="Output binary name")
    parser.add_argument("--onedir", action="store_true", help="Build one-dir bundle instead of one-file")
    parser.add_argument("--dist-dir", default="bin", help="Build output directory (default: bin)")
    parser.add_argument("--work-dir", default="build-binary", help="PyInstaller work directory")
    parser.add_argument("--clean-dist", action="store_true", help="Delete dist/work directories before build")
    parser.add_argument("--verify", action="store_true", help="Run built binary with --version")
    parser.add_argument("--destination", default=None, help="Install destination directory (install mode)")
    parser.add_argument("--output-dir", default=None, help="Persistent NetLoader-X output directory")
    parser.add_argument("--skip-path-update", action="store_true", help="Skip PATH update in install mode")
    parser.add_argument("--non-interactive", action="store_true", help="Disable prompts and use defaults")
    args = parser.parse_args()

    project_root = PROJECT_ROOT
    dist_dir = (project_root / args.dist_dir).resolve()
    work_dir = (project_root / args.work_dir).resolve()
    onefile = not args.onedir

    if args.clean_dist:
        shutil.rmtree(dist_dir, ignore_errors=True)
        shutil.rmtree(work_dir, ignore_errors=True)

    command = build_pyinstaller_command(
        project_root=project_root,
        name=args.name,
        onefile=onefile,
        dist_dir=dist_dir,
        work_dir=work_dir,
    )
    run_command(command, cwd=project_root)

    built_binary = expected_binary_path(dist_dir=dist_dir, name=args.name, onefile=onefile)
    print(f"\nBuilt artifact: {built_binary}")
    if args.verify:
        verify_binary(built_binary)

    if args.mode == "test":
        print("\nTest mode complete. No installation changes were made.")
        return

    interactive = bool(not args.non_interactive and sys.stdin.isatty())
    default_dest = local_bin_dir()
    chosen_dest = Path(args.destination).expanduser().resolve() if args.destination else prompt_destination(
        interactive=interactive,
        default_dir=default_dest,
    )
    installed_path = install_artifact(
        built_path=built_binary,
        destination_dir=chosen_dest,
        onefile=onefile,
        name=args.name,
    )
    print(f"Installed artifact: {installed_path}")

    if args.skip_path_update:
        print("PATH update skipped by flag.")
    else:
        message = update_path(chosen_dest)
        print(message)
        if os.name == "nt":
            print("Open a new terminal session for PATH changes to take effect.")

    default_output = default_output_dir_home()
    chosen_output = prompt_output_dir(
        interactive=interactive,
        default_output=default_output,
        provided=args.output_dir,
    )
    chosen_output.mkdir(parents=True, exist_ok=True)
    saved = set_persistent_output_dir(str(chosen_output))
    print(f"Persistent output directory configured: {saved}")


if __name__ == "__main__":
    main()

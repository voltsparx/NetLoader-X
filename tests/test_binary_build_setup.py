from pathlib import Path

from scripts.install_netloader_x_binary import (
    add_data_argument,
    build_pyinstaller_command,
    data_separator,
    local_bin_dir,
)


def test_data_separator_by_platform():
    assert data_separator("nt") == ";"
    assert data_separator("posix") == ":"


def test_add_data_argument_uses_platform_separator():
    src = Path("C:/tmp/demo.txt")
    assert add_data_argument(src, ".", os_name="nt").endswith(";.")
    assert add_data_argument(src, ".", os_name="posix").endswith(":.")


def test_build_pyinstaller_command_contains_core_parts():
    project_root = Path(__file__).resolve().parent.parent
    cmd = build_pyinstaller_command(
        project_root=project_root,
        name="netloader-x",
        onefile=True,
        dist_dir=project_root / "dist",
        work_dir=project_root / "build",
    )

    assert "--onefile" in cmd
    assert "--collect-submodules" in cmd
    assert "core" in cmd
    assert str(project_root / "netloader-x.py") in cmd


def test_local_bin_dir_by_platform():
    assert ".local" in str(local_bin_dir("posix"))
    assert "AppData" in str(local_bin_dir("nt"))

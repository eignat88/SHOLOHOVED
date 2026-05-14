"""Cross-platform helpers for opening files and folders."""

import os
import platform
import subprocess
from os import PathLike
from typing import Union

PathValue = Union[str, bytes, PathLike[str], PathLike[bytes]]


def _open_path(path: PathValue) -> None:
    """Open *path* with the platform-default application without using a shell."""
    path_value = os.fspath(path)
    system = platform.system()

    if system == "Windows":
        os.startfile(path_value)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", path_value], check=False)
    else:
        subprocess.run(["xdg-open", path_value], check=False)


def open_file(path: PathValue) -> None:
    """Open a file with the platform-default application."""
    _open_path(path)


def open_folder(path: PathValue) -> None:
    """Open a folder with the platform-default file manager."""
    _open_path(path)

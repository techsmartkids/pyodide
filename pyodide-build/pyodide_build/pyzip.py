import shutil
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from ._py_compile import _compile
from .common import make_zip_archive


def default_filterfunc(
    root: Path, excludes: list[str], stubs: list[str], verbose: bool = False
) -> Callable[[str, list[str]], set[str]]:
    """
    The default filter function used by `create_zipfile`.

    This function filters out several modules that are:

    - not supported in Pyodide due to browser limitations (e.g. `tkinter`)
    - unvendored from the standard library (e.g. `sqlite3`)
    """

    def _should_skip(path: Path) -> bool:
        """Skip common files that are not needed in the zip file."""
        name = path.name

        if path.is_dir() and name in ("__pycache__", "dist"):
            return True

        if path.is_dir() and name.endswith((".egg-info", ".dist-info")):
            return True

        if path.is_file() and name in (
            "LICENSE",
            "LICENSE.txt",
            "setup.py",
            ".gitignore",
        ):
            return True

        if path.is_file() and name.endswith(("pyi", "toml", "cfg", "md", "rst")):
            return True

        return False

    def filterfunc(path: Path | str, names: list[str]) -> set[str]:
        filtered_files = {(root / f).resolve() for f in excludes}

        # We have JS implementations of these modules, so we don't need to
        # include the Python ones. Checking the name of the root directory
        # is a bit of a hack, but it works...
        if root.name.startswith("python3"):
            filtered_files.update({root / f for f in stubs})

        path = Path(path).resolve()

        if _should_skip(path):
            return set(names)
        
        # Exclude as many encodings as possible
        if path.name == 'encodings':
            return set([n for n in names if n not in [
                '__init__.py',
                'aliases.py',
                'utf_8.py',
            ]])

        _names = []
        for name in names:
            fullpath = path / name

            if _should_skip(fullpath) or fullpath in filtered_files:
                if verbose:
                    print(f"Skipping {fullpath}")

                _names.append(name)

        return set(_names)

    return filterfunc


def create_zipfile(
    libdirs: list[Path],
    excludes: list[str] | None = None,
    stubs: list[str] | None = None,
    output: Path | str = "python",
    pycompile: bool = False,
    filterfunc: Callable[[str, list[str]], set[str]] | None = None,
    compression_level: int = 6,
) -> None:
    """
    Bundle Python standard libraries into a zip file.

    The basic idea of this function is similar to the standard library's
    {ref}`zipfile.PyZipFile` class.

    However, we need some additional functionality for Pyodide. For example:

    - We need to remove some unvendored modules, e.g. `sqlite3`
    - We need an option to "not" compile the files in the zip file

    hence this function.

    Parameters
    ----------
    libdirs
        List of paths to the directory containing the Python standard library or extra packages.

    excludes
        List of files to exclude from the zip file.

    stubs
        List of files that are replaced by JS implementations.

    output
        Path to the output zip file. Defaults to python.zip.

    pycompile
        Whether to compile the .py files into .pyc, by default False

    filterfunc
        A function that filters the files to be included in the zip file.
        This function will be passed to {ref}`shutil.copytree` 's ignore argument.
        By default, Pyodide's default filter function is used.

    compression_level
        Level of zip compression to apply. 0 means no compression. If a strictly
        positive integer is provided, ZIP_DEFLATED option is used.

    Returns
    -------
    BytesIO
        A BytesIO object containing the zip file.
    """

    archive = Path(output)
    excludes = excludes or []
    stubs = stubs or []

    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        for libdir in libdirs:
            libdir = Path(libdir)

            if filterfunc is None:
                _filterfunc = default_filterfunc(libdir, excludes, stubs)

            shutil.copytree(libdir, temp_dir, ignore=_filterfunc, dirs_exist_ok=True)

        make_zip_archive(
            archive,
            temp_dir,
            compression_level=compression_level,
        )

    if pycompile:
        _compile(
            archive,
            archive,
            verbose=False,
            keep=False,
            compression_level=compression_level,
        )

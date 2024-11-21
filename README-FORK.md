# TechSmart Pyodide

This repository contains a fork of Pyodide, adapted for running inside the
TechSmart Platform.

## Features

* Small Size
    - Many Python standard library modules have been removed.
    - Some Pyodide features have been removed.
* Secure
    - Python code cannot access JavaScript objects directly.
      In particular `from js import ...` does not work.
    - Python code cannot access the Pyodide API directly.
      In particular `from pyodide_js import ...` does not work.

## Branches

Changes should be made on top of the default "stable" branch.
Prefer keeping a linear history so that future Pyodide upgrades are easier.

The local "stable" branch was forked from the upstream "stable" branch when
it was pointing at the "0.26.3" tag. For convenience that divergence point is
marked with the "stable-initial" branch.

To upgrade the underlying version of Pyodide, you must rebase all commits between
"stable-initial" and "stable" onto a new released version of Pyodide (such as
the "0.26.3" tag) and retest.

## Building

Use the build process documented at 
[docs/development/building-from-sources.md](docs/development/building-from-sources.md).

In particular, on an ARM Mac running macOS 14.6 Sonoma,
the following commands should work:

```
$ xcode-select --install
$ conda env create -f environment.yml
$ conda activate pyodide-env
$ pip install -r requirements.txt
$ make
$ dist/python
Python 3.12.1 (main, Oct 30 2024, 11:10:51) [Clang 19.0.0git (https:/github.com/llvm/llvm-project 0a8cd1ed1f4f35905df318015b on emscripten
Type "help", "copyright", "credits" or "license" for more information.
>>> sum([1,2,3])
6
>>> ^D
```

## Testing

1. Ensure the build completes successfully:

```
$ make
```

2. Ensure the resulting Python binary can run simple code:

```
$ dist/python
Python 3.12.1 (main, Oct 30 2024, 11:10:51) [Clang 19.0.0git (https:/github.com/llvm/llvm-project 0a8cd1ed1f4f35905df318015b on emscripten
Type "help", "copyright", "credits" or "license" for more information.
>>> sum([1,2,3])
6
>>> ^D
```

The upstream testing process is documented at 
[docs/development/testing.md](docs/development/testing.md)
but cannot be used for this fork because various Pyodide features have been
removed and related tests would fail.

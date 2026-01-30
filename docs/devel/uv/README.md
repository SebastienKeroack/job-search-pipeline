
# Python Environment Setup with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast Python dependency management and virtual environment creation.

## 1. Install uv

```bash
pip install -U uv
```

## 2. Create a virtual environment (Python 3.12)

```bash
uv venv --python=3.12 .venv
```

## 3. Install project dependencies

```bash
uv pip install -e .
uv pip install --group dev
```
The first command installs your package in editable mode; the second installs all development dependencies.

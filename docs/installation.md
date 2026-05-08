# Installation

## Requirements

Typical requirements include:

- Python 3
- access to a compatible SAS Viya environment
- [SWAT for Python](https://github.com/sassoftware/python-swat)
- valid SAS backend credentials

Depending on the features you use, the following Python dependencies may also be required:

- `numpy`
- `pandas`
- `matplotlib`
- `mayavi`
- `PyQt5`
- `requests`

## Install from PyPI

```bash
pip install sas-cvpy
```

## Install from source

```bash
git clone https://github.com/sassoftware/python-cvpy.git
cd python-cvpy
pip install .
```

## Recommended virtual environment setup

### venv

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install sas-cvpy
```

### conda

```bash
conda create --name cvpy python=3.8
conda activate cvpy
pip install sas-cvpy
```

## Visualization dependencies

Visualization features rely on packages such as Mayavi, VTK, Matplotlib, and PyQt. These dependencies can be platform-sensitive.

A typical installation path is:

```bash
pip install mayavi PyQt5 matplotlib
```

In some environments, VTK version pinning may be necessary.

## Notes

- SAS-side functionality depends on the target Viya environment and available licenses.
- Visualization support may require a local GUI-capable environment.
- Notebook-based examples may also require Jupyter.

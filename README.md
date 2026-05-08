# python-cvpy

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

`python-cvpy` is a high-level Python library for working with SAS Viya Computer Vision that offers image and biomedical image analytics. It provides Python-facing abstractions and utilities around SAS image action sets, with emphasis on image retrieval, array conversion, visualization, annotation workflows, and CAS execution utilities.

The package is distributed on PyPI as `sas-cvpy` and is intended for use alongside SAS Viya and the [SAS SWAT](https://github.com/sassoftware/python-swat) Python client.


## Overview

`python-cvpy` is designed to make SAS image analytics more accessible from Python by exposing higher-level APIs over CAS-backed image data and related workflows.

The library primarily targets the following usage patterns:

- interacting with SAS Viya image and biomedical image tables
- converting CAS image data tables into Python/numpy-friendly structures
- visualizing 2D and 3D image content using open-source Python tooling
- supporting image annotation-related workflows, including CVAT integration
- assisting with CAS performance tuning for image workloads

## Requirements

To use `python-cvpy`, you typically need:

- Python 3
- access to a SAS Viya environment
- the `swat` Python package
- valid SAS backend credentials

Some features also require visualization dependencies such as:

- `numpy`
- `pandas`
- `matplotlib`
- `mayavi`
- `PyQt5`

## Installation

Install from PyPI:

```bash
pip install sas-cvpy
```

Or install from source:

```bash
git clone https://github.com/sassoftware/python-cvpy.git
cd python-cvpy
pip install .
```

## Documentation

Additional documentation is organized by topic:

- [Installation](docs/installation.md)
- [Architecture](docs/architecture.md)
- [API Overview](docs/api/overview.md)
- [Annotation APIs](docs/api/annotation.md)
- [Image APIs](docs/api/image.md)
- [Biomedical Image APIs](docs/api/biomedimage.md)
- [Utilities](docs/api/utils.md)
- [Visualization](docs/api/visualization.md)

Generated API documentation is also available at:

- https://sassoftware.github.io/python-cvpy/

## Examples

Example material is available in the repository under:

- `examples/biomedimage`
- `examples/thread_optimization`

## Contributing

Contributions are welcome. Please review:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SUPPORT.md](SUPPORT.md)

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Additional Resources

- [SAS SWAT for Python](https://github.com/sassoftware/python-swat)
- [SAS Viya documentation](https://support.sas.com/documentation/onlinedoc/viya/index.html)
- [Image action set documentation](https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=default&docsetId=casactml&docsetTarget=casactml_image_toc.htm)
- [Biomedimage action set documentation](https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=default&docsetId=casactml&docsetTarget=casactml_biomedimage_toc.htm)
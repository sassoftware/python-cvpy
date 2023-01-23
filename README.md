# CVPy - SAS Viya Computer Vision API for Python

## Overview

CVPy is a Python package that makes SAS image analytics more accessible to Python users in a variety of different ways. This high-level Python library provides helpful APIs that assist with the processing, analyzing, and visualization of images. This allows users of the image and biomedimage action set in SAS Viya to have more flexibilty when working in Python.

Currently available within CVPy are visualization APIs that allow users to easily be able to move images out of CAS and into common open source tools such as Mayavi and Matplotlib. These APIs streamline the visualization of image data fetched from a CAS table and can assist with further image analysis.

### Prerequisites

- Python version 3 or greater is required
- Install SAS Scripting Wrapper for Analytics Transfer (SWAT) for Python using pip install swat or conda install -c sas-institute swat
- Access to a SAS Viya 3.5 environment with Visual Data Mining and Machine Learning (VDMML) is required
- A user login to your SAS Viya back-end is required. See your system administrator for details if you do not have a SAS Viya account.
- Install Mayavi for scientific data visualization in Python

### Create a New Python Environment [Optional]

Follow the steps below to create a new Python 3.8 environment for your CVPy installation named "cvpy".

`conda create --name cvpy python=3.8`

`activate cvpy`

### Mayavi Installation

Mayavi is a heavy, complex package that is required by CVPy. If you do not already have Mayavi installed, follow the steps below to install it.

`pip install mayavi`

Install PyQt, a GUI toolkit needed to run Mayavi.

`pip install PyQt5`

### CVPy Installation

To install CVPy, use the following command:

`pip install sas-cvpy`

### Install and Run Jupyter Notebook

To install and start Jupyter Notebook, run the following steps:

`pip install jupyter`

`python -m ipykernel install --user --name cvpy`

`jupyter notebook`

## Contributing

We welcome your contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit contributions to this project.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources

* [Python-CVPy API Documentation](https://sassoftware.github.io/python-cvpy/)
* [Biomedimage action set](https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=default&docsetId=casactml&docsetTarget=casactml_biomedimage_toc.htm)
* [Image action set](https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=default&docsetId=casactml&docsetTarget=casactml_image_toc.htm)

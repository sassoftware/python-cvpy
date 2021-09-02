# CVPy - SAS Viya Computer Vision API for Python

## Overview

This high-level Python library assists with the image and biomedimage action sets by providing helpful visualization APIs. These APIs allow users to easily be able to move images out of CAS and into common open source tools such as Mayavi and Matplotlib. This streamlines the visualization of image data fetched from a CAS table and allows for further image analysis.

### Prerequisites

- Python version 3 or greater is required
- Install SAS Scripting Wrapper for Analytics Transfer (SWAT) for Python using pip install swat or conda install -c sas-institute swat
- Access to a SAS Viya 3.5 environment with Visual Data Mining and Machine Learning (VDMML) is required
- A user login to your SAS Viya back-end is required. See your system administrator for details if you do not have a SAS Viya account.
- Install Mayavi for scientific data visualization in Python

### Mayavi Installation

Mayavi is a heavy, complex package that is required by CVPy. If you do not already have Mayavi installed, follow the steps below to install it.

Install VTK, a critical dependency for Mayavi.

`pip install VTK‑8.1.2‑cp37‑cp37m‑win_amd64.whl`

or

`pip install VTK==8.1.2`

Note that a specific version of is VTK used. You can download the wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk).

Install Mayavi

`pip install mayavi`

You may see an error message about numpy, like “Numpy is required to build Mayavi correctly, please install it first.” Ignore that message.

Install PyQt, a GUI toolkit needed to run Mayavi

`pip install PyQt5`

### CVPy Installation

To install CVPy, use the following command:

`pip install git+https://github.com/sassoftware/python-cvpy.git`

## Contributing

We welcome your contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit contributions to this project.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Additional Resources

* Biomedimage action set https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=9.4_3.5&docsetId=casactml&docsetTarget=casactml_biomedimage_toc.htm&locale=en
* Image action set https://go.documentation.sas.com/?cdcId=pgmsascdc&cdcVersion=9.4_3.5&docsetId=casactml&docsetTarget=casactml_image_toc.htm&locale=en

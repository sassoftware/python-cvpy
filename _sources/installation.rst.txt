.. Copyright SAS Institute

============
Installation
============

Prerequisites
-------------

To access the full capabilities of CVPy, you need the following: 

- Python version 3 or greater (You can install the `Anaconda <https://www.anaconda.com/products/individual>`_ 
  distribution or another distribution of your choice.) 
- `SAS Scripting Wrapper for Analytics Transfer <https://github.com/sassoftware/python-swat>`_ (SWAT) package for Python 
- `SAS Viya 3.5+ <https://www.sas.com/en_us/software/viya.html>`_ with an active 
  `Visual Data Mining and Machine Learning <https://www.sas.com/en_us/software/visual-data-mining-machine-learning.html>`_ (VDMML) license
- `Mayavi <https://docs.enthought.com/mayavi/mayavi/>`_ for scientific data visualization in Python.

You also need valid user credentials to access the SAS Viya backend. See your system administrator for details if you do not have a SAS Viya account.

The examples in the repository are written using Jupyter notebooks. If you wish to run the notebooks in your own environment, you must also
have `Jupyter <https://jupyter.org/>`_ installed. If you do not wish to install Jupyter, you can still view the examples in your browser on the 
`GitHub <https://github.com/sassoftware/python-cvpy/tree/main/examples>`_ website.

Mayavi Installation
-------------------

Mayavi is a heavy, complex package that is required by CVPy. If you do not already have Mayavi installed, follow the steps below to install it.

1. Install VTK, a critical dependency for Mayavi.

:code:`pip install VTK‑8.1.2‑cp37‑cp37m‑win_amd64.whl`

or

:code:`pip install VTK==8.1.2`

Note that a specific version of is VTK used. You can download the wheel file from `here <https://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk>`_.

2. Install Mayavi

:code:`pip install mayavi`

You may see an error message about numpy, like “Numpy is required to build Mayavi correctly, please install it first.” Ignore that message.

3. Install PyQt, a GUI toolkit needed to run Mayavi

:code:`pip install PyQt5`

CVPy Installation
-----------------

To install CVPy, use the following command:

:code:`pip install git+https://github.com/sassoftware/python-cvpy.git`

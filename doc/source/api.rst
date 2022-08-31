.. Copyright SAS Institute


=============
API Reference
=============

.. currentmodule:: cvpy

Annotations
-----------

Projects
~~~~~~~~

.. currentmodule:: cvpy.annotation.base.Project

.. autosummary:: 
    :toctree: generated/

    Project
    Project.post_images
    Project.get_annotations
    Project.save
    Project.resume

.. currentmodule:: cvpy.annotation.cvat.CVATProject

.. autosummary::
    :toctree: generated/

    CVATProject
    CVATProject.post_images
    CVATProject.get_annotations
    CVATProject.save
    CVATProject.resume

Authentication
~~~~~~~~~~~~~~

.. currentmodule:: cvpy.annotation.base.Credentials

.. autosummary::
    :toctree: generated/

    Credentials

Image
-----

.. currentmodule:: cvpy.image

.. autosummary::
    :toctree: generated/

    get_image_array_from_row
    get_image_array
    convert_to_CAS_column
    fetch_image_array
    fetch_geometry_info
    get_image_array_const_ctype


Visualization Reference
-----------------------

.. currentmodule:: cvpy.visualization

.. autosummary::
    :toctree: generated/

    display_image_slice
    display_3D_image_slices_from_array
    display_3D_image_slices
    display_3D_surface


CAS Thread Tuner
----------------

.. currentmodule:: cvpy.utils.CASThreadTuner

.. autosummary::
    :toctree: generated/

    tune_thread_count


CAS Thread Tuner Results
------------------------

.. currentmodule:: cvpy.base.CASThreadTunerResults

.. autosummary::
    :toctree: generated/

    plot_exec_times
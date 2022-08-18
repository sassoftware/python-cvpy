.. Copyright SAS Institute


=============
API Reference
=============

.. currentmodule:: cvpy


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

Biomedical Images
-----------------

.. currentmodule:: cvpy.biomedimage.BiomedImage
    
.. autosummary::
    :toctree: generated/

    BiomedImage
    BiomedImage.quantify_sphericity

CAS Thread Tuner
----------------

.. currentmodule:: cvpy.utils.CASThreadTuner

.. autosummary::
    :toctree: generated/

    CASThreadTuner.tune_thread_count


CAS Thread Tuner Results
------------------------

.. currentmodule:: cvpy.base.CASThreadTunerResults

.. autosummary::
    :toctree: generated/

    CASThreadTunerResults
    CASThreadTunerResults.plot_exec_times

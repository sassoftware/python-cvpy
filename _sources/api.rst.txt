.. Copyright SAS Institute


=============
API Reference
=============

.. currentmodule:: cvpy

Biomedical Images
-----------------

.. currentmodule:: cvpy.biomedimage.BiomedImage
    
.. autosummary::
    :toctree: ../build/generated

    BiomedImage
    BiomedImage.quantify_sphericity

CAS Thread Tuner
----------------

.. currentmodule:: cvpy.utils.CASThreadTuner

.. autosummary::
    :toctree: ../build/generated

    CASThreadTuner
    CASThreadTuner.tune_thread_count


CAS Thread Tuner Results
------------------------

.. currentmodule:: cvpy.base.CASThreadTunerResults

.. autosummary::
    :toctree: ../build/generated

    CASThreadTunerResults
    CASThreadTunerResults.plot_exec_times

Image
-----

.. currentmodule:: cvpy.image.Image

.. autosummary::
    :toctree: ../build/generated

    Image
    Image.convert_to_CAS_column
    Image.convert_wide_to_numpy
    Image.fetch_geometry_info
    Image.fetch_image_array
    Image.get_image_array_from_row
    Image.get_image_array
    Image.get_image_array_const_ctype


ImageTable
----------

.. currentmodule:: cvpy.base.ImageTable

.. autosummary::
    :toctree: ../build/generated

    ImageTable
    ImageTable.as_dict
    ImageTable.has_decoded_images


Visualization Reference
-----------------------

.. currentmodule:: cvpy.visualization

.. autosummary::
    :toctree: ../build/generated

    display_image_slice
    display_3D_image_slices_from_array
    display_3D_image_slices
    display_3D_surface

.. Copyright SAS Institute


=============
API Reference
=============

.. currentmodule:: cvpy

Biomedical Image Table
----------------------

.. currentmodule:: cvpy.biomedimage.BiomedImageTable
    
.. autosummary::
    :toctree: generated/

    BiomedImageTable
    ImageTable.as_dict
    BiomedImageTable.fetch_image_array
    BiomedImageTable.fetch_geometry_info
    BiomedImageTable.from_table
    ImageTable.has_decoded_images
    BiomedImageTable.load
    BiomedImageTable.sphericity
    BiomedImageTable.morphological_gradient

CAS Thread Tuner
----------------

.. currentmodule:: cvpy.utils.CASThreadTuner

.. autosummary::
    :toctree: generated/

    CASThreadTuner
    CASThreadTuner.tune_thread_count


CAS Thread Tuner Results
------------------------

.. currentmodule:: cvpy.base.CASThreadTunerResults

.. autosummary::
    :toctree: generated/

    CASThreadTunerResults
    CASThreadTunerResults.plot_exec_times

Image Table
-----------

.. currentmodule:: cvpy.base.ImageTable

.. autosummary::
    :toctree: generated/

    ImageTable
    ImageTable.as_dict
    ImageTable.has_decoded_images
    ImageTable.load
    ImageTable.from_table

Image Utilities
---------------

.. currentmodule:: cvpy.utils.ImageUtils

.. autosummary::
    :toctree: generated/

    ImageUtils
    ImageUtils.convert_numpy_to_wide
    ImageUtils.convert_to_CAS_column
    ImageUtils.convert_wide_to_numpy
    ImageUtils.get_image_array
    ImageUtils.get_image_array_const_ctype
    ImageUtils.get_image_array_from_row


Natural Image Table
-------------------

.. currentmodule:: cvpy.image.NaturalImageTable

.. autosummary::
    :toctree: generated/

    NaturalImageTable
    NaturalImageTable.as_dict
    NaturalImageTable.has_decoded_images
    NaturalImageTable.from_table
    NaturalImageTable.load
    NaturalImageTable.mask_image


Visualization Reference
-----------------------

.. currentmodule:: cvpy.visualization

.. autosummary::
    :toctree: generated/

    display_image_slice
    display_3D_image_slices_from_array
    display_3D_image_slices
    display_3D_surface

Annotations
-----------

Projects
~~~~~~~~

.. currentmodule:: cvpy.annotation.base.Project

.. autosummary::
    :toctree: generated/

    Project
    Project.as_dict
    Project.get_annotations
    Project.post_images
    Project.resume
    Project.save
    Project.to_json

.. currentmodule:: cvpy.annotation.cvat.CVATProject

.. autosummary::
    :toctree: generated/

    CVATProject
    CVATProject.as_dict
    CVATProject.from_json
    CVATProject.get_annotations
    CVATProject.post_images
    CVATProject.save
    CVATProject.resume
    CVATProject.to_json

Tasks
~~~~~

.. currentmodule:: cvpy.annotation.cvat.CVATTask

.. autosummary::
    :toctree: generated/

    CVATTask
    CVATTask.from_dict
    

Authentication
~~~~~~~~~~~~~~

.. currentmodule:: cvpy.annotation.base.Credentials

.. autosummary::
    :toctree: generated/

    Credentials

.. currentmodule:: cvpy.annotation.cvat.CVATAuthenticator

.. autosummary::
    :toctree: generated/

    CVATAuthenticator
    CVATAuthenticator.authenticate
    CVATAuthenticator.generate_cvat_token
    

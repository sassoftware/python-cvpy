.. Copyright SAS Institute


=============
API Reference
=============

**********
Annotation
**********

Base
====

Credentials
-----------

.. currentmodule:: cvpy.annotation.base.Credentials

.. autosummary::
    :toctree: generated/

    Credentials

CVAT
====

.. currentmodule:: cvpy.annotation.cvat

CVAT Project
------------

.. currentmodule:: cvpy.annotation.cvat.CVATProject

.. autosummary::
    :toctree: generated/

    CVATProject
    CVATProject.get_annotations
    CVATProject.post_images
    CVATProject.save
    CVATProject.resume

CVAT Authentication
-------------------

.. currentmodule:: cvpy.annotation.cvat.CVATAuthenticator

.. autosummary::
    :toctree: generated/

    CVATAuthenticator
    CVATAuthenticator.generate_cvat_token

******
Tables
******

Biomedical Image Table
======================

.. currentmodule:: cvpy.biomedimage.BiomedImageTable
    
.. autosummary::
    :toctree: generated/

    BiomedImageTable
    BiomedImageTable.as_dict
    BiomedImageTable.fetch_image_array
    BiomedImageTable.fetch_geometry_info
    BiomedImageTable.has_decoded_images
    BiomedImageTable.sphericity
    BiomedImageTable.morphological_gradient

Image Table
===========

.. currentmodule:: cvpy.base.ImageTable

.. autosummary::
    :toctree: generated/

    ImageTable
    ImageTable.as_dict
    ImageTable.has_decoded_images
    ImageTable.load
    ImageTable.from_table

Natural Image Table
===================

.. currentmodule:: cvpy.image.NaturalImageTable

.. autosummary::
    :toctree: generated/

    NaturalImageTable
    NaturalImageTable.as_dict
    NaturalImageTable.has_decoded_images
    NaturalImageTable.mask_image

*********
Utilities
*********

CAS Thread Tuner
================

.. currentmodule:: cvpy.utils.CASThreadTuner

.. autosummary::
    :toctree: generated/

    CASThreadTuner
    CASThreadTuner.tune_thread_count


CAS Thread Tuner Results
========================

.. currentmodule:: cvpy.base.CASThreadTunerResults

.. autosummary::
    :toctree: generated/

    CASThreadTunerResults
    CASThreadTunerResults.plot_exec_times

Image Utilities
===============

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

*************
Visualization
*************

.. currentmodule:: cvpy.visualization

.. autosummary::
    :toctree: generated/

    display_image_slice
    display_3D_image_slices_from_array
    display_3D_image_slices
    display_3D_surface

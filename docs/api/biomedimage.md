# Biomedical Image APIs

## Overview

The biomedical image API area supports SAS biomedical image table workflows, including geometry-aware image access and morphology-oriented operations.

## Key classes

Published APIs include:

- `cvpy.biomedimage.BiomedImageTable`
  - `as_dict`
  - `fetch_image_array`
  - `fetch_geometry_info`
  - `has_decoded_images`
  - `sphericity`
  - `morphological_gradient`

## Responsibilities

These APIs are intended to support:

- biomedical image table representation
- conversion of image content into array form
- geometry metadata retrieval
- morphology-related analysis helpers

## Usage notes

Biomedical image workflows often require careful handling of:

- dimensions
- orientations
- resolutions
- geometry metadata
- slice and volume semantics

These APIs are designed to make those interactions easier from Python when the underlying data resides in CAS.

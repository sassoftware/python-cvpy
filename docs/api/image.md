# Image APIs

## Overview

The image API area focuses on natural image table workflows and general image table abstractions backed by SAS CAS data.

## Key classes

Published APIs include:

- `cvpy.base.ImageTable`
  - `as_dict`
  - `has_decoded_images`
  - `load`
  - `from_table`

- `cvpy.image.NaturalImageTable`
  - `as_dict`
  - `has_decoded_images`
  - `mask_image`

## Responsibilities

These APIs support tasks such as:

- representing image tables in Python
- loading and materializing table-backed image content
- determining whether images are already decoded
- applying image-related transformations or masks

## Usage model

In most cases, image workflows begin with a CAS-backed table and proceed through a `cvpy` abstraction that makes retrieval and manipulation easier from Python code.

## Related docs

- [Utilities](utils.md)
- [Visualization](visualization.md)

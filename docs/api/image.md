# Image APIs

## Overview

The image API focuses on natural image table pipelines and general image
table abstractions backed by SAS CAS data.

## Responsibilities

These APIs support tasks such as:

- representing image tables in Python
- loading and materializing table-backed image content
- determining whether images are already decoded
- applying image-related transformations or masks

## Usage model

In most cases, image analysis pipelines begin with a CAS table and proceed through a
`cvpy` abstraction that makes retrieval and manipulation easier from Python code.

## Related docs

- [Utilities](utils.md)
- [Visualization](visualization.md)

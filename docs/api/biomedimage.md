# Biomedical Image APIs

## Overview

The biomedical image API supports SAS biomedical image table workflows, including geometry-aware image access and morphology-oriented operations.

## Responsibilities

These APIs are intended to support:

- biomedical image table representation
- conversion of image content into array form
- geometry metadata retrieval
- morphology-related analysis helpers

## Usage notes

Biomedical image analysis pipelines often require careful handling of:

- dimensions
- orientations
- resolutions
- geometry metadata
- slice and volume semantics

These APIs are designed to make those interactions easier from Python when the
underlying data resides in CAS.

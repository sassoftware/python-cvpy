# Utilities

## Overview

The utility APIs provide lower-level helpers used across image analytics workflows.

## Key APIs

Published utilities include:

- `cvpy.utils.CASThreadTuner`
  - `tune_thread_count`

- `cvpy.base.CASThreadTunerResults`
  - `plot_exec_times`

- `cvpy.utils.ImageUtils`
  - `convert_numpy_to_wide`
  - `convert_to_CAS_column`
  - `convert_wide_to_numpy`
  - `get_image_array`
  - `get_image_array_const_ctype`
  - `get_image_array_from_row`

## Responsibilities

These helpers support:

- conversion between numpy arrays and SAS/CAS-compatible layouts
- extraction of image content from CAS row or column structures
- thread tuning and performance-oriented experimentation for CAS workloads

## When to use

Use these APIs when you need more control over:

- image data representation
- conversion pipelines
- lower-level integration between Python and CAS table structures
- performance tuning experiments

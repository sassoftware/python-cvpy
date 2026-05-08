# Architecture

## Overview

`python-cvpy` provides higher-level Python interfaces for SAS Viya image analytics workflows. It sits between Python client code and SAS CAS-backed image processing capabilities.

At a high level, the architecture is:

```text
Python application code
    │
    ├── cvpy
    │     ├── table abstractions
    │     ├── image conversion utilities
    │     ├── visualization helpers
    │     ├── annotation integration
    │     └── CAS tuning helpers
    │
    ├── SWAT client
    │
    └── SAS Viya / CAS
          ├── image action set
          └── biomedimage action set
```

## Design goals

The package is designed to:

- reduce low-level handling of SAS-hosted image data in Python
- expose more convenient abstractions for image tables
- support conversion into numpy-friendly forms
- integrate visualization tools commonly used in Python workflows
- support annotation-related workflows where external tooling is required

## Major package areas

- `cvpy.annotation` — annotation models and CVAT-oriented integration
- `cvpy.base` — shared base types and cross-cutting abstractions
- `cvpy.image` — natural image table support
- `cvpy.biomedimage` — biomedical image table support
- `cvpy.utils` — conversion and helper utilities
- `cvpy.visualization` — display and rendering functions

## Operational model

In most workflows:

1. a user authenticates to SAS Viya through SWAT
2. CAS tables holding image data are loaded or referenced
3. `cvpy` APIs are used to fetch, transform, or visualize data
4. optional downstream annotation or optimization utilities are applied

## Scope

`python-cvpy` is not a replacement for SWAT or CAS action sets. Instead, it provides a Python-friendly layer over common image analytics workflows that would otherwise require more manual manipulation.

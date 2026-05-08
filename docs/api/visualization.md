# Visualization

## Overview

The visualization layer provides helper functions for rendering image content using common Python visualization libraries.

## Key functions

Published functions include:

- `display_image_slice`
- `display_3D_image_slices_from_array`
- `display_3D_image_slices`
- `display_3D_surface`

## Dependencies

Visualization support relies on libraries such as:

- `numpy`
- `pandas`
- `matplotlib`
- `mayavi`
- `PyQt5`

## Rendering model

The visualization implementation supports both:

- direct rendering from numpy arrays
- rendering of image content fetched from SAS/CAS-backed tables

## Example

```python
import numpy as np
from cvpy.visualization import display_3D_image_slices_from_array

volume = np.random.rand(32, 32, 32)
display_3D_image_slices_from_array(volume)
```

## Notes

Visualization functionality may require a GUI-capable local environment. In headless or remote execution environments, additional configuration may be necessary.

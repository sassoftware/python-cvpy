# Visualization

## Overview

The visualization layer provides helper functions for rendering image content using common Python visualization libraries.

## Rendering model

The visualization implementation supports both:

- direct rendering from numpy arrays
- rendering of image content fetched from CAS tables

## Example

```python
import numpy as np
from cvpy.visualization import display_3D_image_slices_from_array

volume = np.random.rand(32, 32, 32)
display_3D_image_slices_from_array(volume)
```

## Notes

Visualization functionality may require a GUI-capable local environment. In headless or remote execution environments, additional configuration may be necessary.

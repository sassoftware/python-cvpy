## Publish to PyPI

Before publishing to PyPI, follow the steps below to ensure a successful release.

1. Bump the version number in setup.py and cvpy/__init__.py and push to GitHub. This typically means removing the '-dev' portion (e.g., 1.1.1-dev => 1.1.1), or incrementing to the next minor value (e.g., 1.1.1-dev => 1.2.0).

2. Run the Computer_Vision_CVPy_Tests Jenkins job. A progress bar on the left bottom part should be triggered. When it is completed without error, the color of the sphere should be blue.

3. Before uploading to PyPI, first try uploading the package to Test PyPI. On the CVPy Github page, navigate to Actions -> "Publish Package to Test PyPI" -> "Run workflow" -> "Run workflow"

4. If this is successful, upload the package to PyPI. On the CVPy Github page, navigate to Actions -> "Publish Package to PyPI" -> "Run workflow" -> "Run workflow"

5. Increment the version number in setup.py and cvpy/__init__.py to the next '-dev' version (e.g., 1.2.0 => 1.2.1-dev), and push it to GitHub.

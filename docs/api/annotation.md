# Annotation APIs

## Overview

The annotation area provides models and integrations for annotation-centric workflows, including CVAT-related functionality.

## Responsibilities

This part of the package is intended to support:

- annotation metadata representation
- credential handling
- CVAT authentication
- project-based annotation workflows
- retrieval and persistence of annotation state

## Documented APIs

Examples from the published API reference include:

- `cvpy.annotation.base.Credentials`
- `cvpy.annotation.cvat.CVATProject`
  - `get_annotations`
  - `post_images`
  - `save`
  - `resume`
- `cvpy.annotation.cvat.CVATAuthenticator`
  - `generate_cvat_token`

## Typical workflow

A typical annotation workflow may involve:

1. configuring credentials
2. authenticating to the annotation backend
3. creating or resuming a project
4. posting images for annotation
5. retrieving annotations for downstream processing

## Notes

Because annotation systems are external integrations, exact behavior depends on deployment topology, endpoint configuration, authentication policy, and dataset conventions.

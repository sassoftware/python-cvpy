#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' BioMedImage analysis tools '''

from typing import List
from swat import CAS, CASTable
from cvpy.base.ImageTable import ImageTable
from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
from cvpy.utils.RandomNameGenerator import RandomNameGenerator
from enum import *

class BiomedImageTable(ImageTable):
    """
    Implement biomedical image processing functions.

     Parameters
     ----------
     cas_session
          Specifies the CAS session.

     Returns
     -------
     :class:`BiomedImage`
    """

    def __init__(self, table: CASTable = None, image: str = None, dimension: str = None, resolution: str = None,
                 imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
                 type: str = None) -> None:

        ## Call the constructor from parent class - ImageTable
        super().__init__(table=table, image=image, dimension=dimension, resolution=resolution, imageFormat=imageFormat,
                         path=path, label=label, id=id, size=size, type=type)

        ## Load the actionsets
        self.connection.loadactionset('image')
        self.connection.loadactionset('biomedimage')
        self.connection.loadactionset('fedsql')

    def morphological_gradient(self, kernel_width: int = 3, kernel_height: int = 3,
                               copy_vars: List[str] = None, output_table_parms: Dict[str,str] = {}) -> ImageTable:
        """
        Compute the morphological gradient for each 3D grayscale image in the image table.

        Parameters
        ------------
        images : :class:'ImageTable'
            Specifies the image table that contains 3D grayscale images.
        kernel_width : :class:'int'
            Specifies the kernel width.
        kernel_height : :class:'int'
            Specifies the kernel height.
        copy_vars : :class:'List[str]'
            Specifies which columns to copy to the output image table.

        Returns
        ------------
        :class:'ImageTable'

        Examples
        --------
        >>> # Import classes
        >>> from swat import CAS
        >>> from cvpy.base.ImageTable import ImageTable
        >>> from cvpy.biomedimage.BiomedImage import BiomedImage
        >>> ## Connect to CAS
        >>> s = swat.CAS("example.com", 5570)
        >>> # Construct Biomed object
        >>> biomed = BiomedImage(s)
        >>> # Construct table to be passed to the morphological_gradient API
        >>> image_table = s.CASTable(...)
        >>> input_table = ImageTable(image_table)
        >>> # Call the API
        >>> output_table = biomed.quantify_sphericity(input_table,...)
        """

        conn = self._cas_session
        random_name_generator = RandomNameGenerator()

        if copy_vars is None:
            copy_vars_with_biomed_vars = ['_biomedid_','_biomeddimension_','_sliceindex_']
        else:
            copy_vars_with_biomed_vars = []
            copy_vars_with_biomed_vars += copy_vars

            if '_biomedid_' not in copy_vars_with_biomed_vars:
                copy_vars_with_biomed_vars.append('_biomedid_')
            if '_biomeddimension_' not in copy_vars_with_biomed_vars:
                copy_vars_with_biomed_vars.append('_biomeddimension_')
            if '_sliceindex_' not in copy_vars_with_biomed_vars:
                copy_vars_with_biomed_vars.append('_sliceindex_')

        # Export images from 3d to 2d
        name_image_2d = random_name_generator.generate_name()
        image_2d = conn.CASTable(name=name_image_2d, replace=True)
        conn.biomedimage.processbiomedimages(images=dict(table=images.table),
                                             steps=[dict(stepparameters=dict(steptype='export'))],
                                             casout=image_2d,
                                             copyvars=copy_vars)

        # Compute morphological gradient of 2d images
        name_morph_grad_2d = random_name_generator.generate_name()
        morph_grad_2d = conn.CASTable(name=name_morph_grad_2d, replace=True)
        conn.image.processImages(table=image_2d,
                                 steps=[
                                     {'options': {
                                         'functiontype': 'MORPHOLOGY',
                                         'method': 'GRADIENT',
                                         'kernelWidth': kernel_width,
                                         'kernelHeight': kernel_height,
                                     }}],
                                 casout=morph_grad_2d,
                                 copyvars=copy_vars_with_biomed_vars)

        # Import gradient images from 2d to 3d
        name_morph_grad_3d = random_name_generator.generate_name()
        morph_grad_3d = conn.CASTable(name=name_morph_grad_3d, replace=True)
        conn.biomedimage.processbiomedimages(images=dict(table={'name': name_morph_grad_2d}),
                                             steps=[dict(stepparameters=dict(steptype='import', targetdimension=3))],
                                             casout=morph_grad_3d,
                                             copyvars=copy_vars)

        # Delete our temporary tables
        conn.table.dropTable(image_2d)
        conn.table.dropTable(morph_grad_2d)

        return ImageTable(morph_grad_3d)

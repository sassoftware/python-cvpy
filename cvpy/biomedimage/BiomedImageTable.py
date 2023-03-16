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

""" BioMedImage analysis tools """

from typing import Dict, List
import struct
import numpy
from swat import CASTable
from cvpy.base.ImageTable import ImageTable
from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
from cvpy.utils.RandomNameGenerator import RandomNameGenerator
from cvpy.utils.ImageUtils import ImageUtils


class BiomedImageTable(ImageTable):
    """
    Implement biomedical image processing functions.

    Parameters
    ----------
    table:
        Specifies the input table that contains image data.
    image:
        Specifies the name of the column that contains image binaries.
    dimension:
        Specifies the name of the column that contains dimensions of images.
    resolution:
        Specifies the name of the column that contains resolutions of images.
    imageFormat:
        Specifies the name of the column that contains formats of image binaries.
    path:
        Specifies the name of the column that contains file paths.
    label:
        Specifies the name of the column that contains labels of images.
    id:
        Specifies the name of the variable that identifies each image.
    size:
        Specifies the name of the column that contains byte lengths of image binaries.
    type:
        Specifies the name of the column that contains the image type.

    Returns
    -------
    :class:'BiomedImageTable'
    """

    def __init__(self, table: CASTable = None, image: str = None, dimension: str = None, resolution: str = None,
                 imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
                 type: str = None) -> None:

        super().__init__(table=table, image=image, dimension=dimension, resolution=resolution, imageFormat=imageFormat,
                         path=path, label=label, id=id, size=size, type=type)

        # Load the actionsets
        if self.connection:
            self.connection.loadactionset('image')
            self.connection.loadactionset('biomedimage')
            self.connection.loadactionset('fedsql')

    def fetch_image_array(self, n: int = 0, qry: str = None, image: str = '_image_', dim: str = '_dimension_',
                          res: str = '_resolution_', ctype: str = '_channelType_', ccount: int = 1) -> numpy.ndarray:
        """
        Fetch image array from this BiomedImageTable.

        Parameters
        ----------
        n : :class:`int`
            Specifies the number of additional images.
        qry : :class:`str`
            Specifies the query.
        image : :class:`str`
            Specifies the image format.
        dim : :class:`str`
            Specifies the image dimension.
        res : :class:`str`
            Specifies the image resolution.
        ctype : :class:`str`
            Specifies the channel type.
        ccount : :class:`int`
            Specifies the number of channels of the image.
        Returns
        -------
        :class:'numpy.ndarray'

        """

        if qry != '':
            example_rows = self.table.query(qry).to_frame(to=n + 1)
        else:
            example_rows = self.table.to_frame(to=n + 1)

        medical_dimensions = example_rows[dim]
        medical_formats = example_rows[ctype]
        medical_binaries = example_rows[image]
        medical_resolutions = example_rows[res]

        return ImageUtils.get_image_array(medical_binaries, medical_dimensions, medical_resolutions, medical_formats, n,
                                     ccount)

    def fetch_geometry_info(self, n: int = 0, qry: str = None, posCol: str = '_position_', oriCol: str = '_orientation_',
                            spaCol: str = '_spacing_', dimCol: str = '_dimension_') -> tuple:

        """
        Fetch geometry information from this BiomedImageTable.

        Parameters
        ----------
        n : :class:`int`
            Specifies the number of images.
        qry : :class:`str`
            Specifies the query.
        posCol : :class:`str`
            Specifies the position column.
        oriCol : :class:`str`
            Specifies the orientation column.
        spaCol : :class:`str`
            Specifies the spacing column.
        dimCol : :class:`str`
            Specifies the dimension column.

        Returns
        -------
        :class:`tuple`, (position, orientation, spacing)

        """

        # Check if geometry info exists in CAS table query before fetching
        if not {'_position_', '_spacing_', '_orientation_'}.issubset(self.table.columns):
            return ((), (), ())

        if (qry != ''):
            example_rows = self.table[[dimCol, posCol, oriCol, spaCol]].query(qry).to_frame(to=n)
        else:
            example_rows = self.table[[dimCol, posCol, oriCol, spaCol]].to_frame(to=n)

        dim = example_rows[dimCol][0]
        pos = struct.unpack('=%sd' % dim, example_rows[posCol][0][0:dim * 8])
        ori = struct.unpack('=%sd' % (dim * dim), example_rows[oriCol][0][0:dim * dim * 8])
        spa = struct.unpack('=%sd' % dim, example_rows[spaCol][0][0:dim * 8])

        return pos, ori, spa

    def sphericity(self, use_spacing: bool, input_background: float,
                   label_connectivity: LabelConnectivity, output_table_parms: Dict[str, str] = None) -> CASTable:
        """
        Quantify the sphericity for the given component from this BiomedImageTable.

        Parameters
        ----------
        use_spacing: :class:'bool'
            When set to True, use image spacing in the sphericity calculation.
        input_background: :class:'float'
            Specifies the background value in input images.
        label_connectivity: LabelConnectivity.FACE | LabelConnectivity.VERTEX
            Specifies the level of connectivity for connected components: LabelConnectivity.FACE or LabelConnectivity.VERTEX
        output_table_parms : :class:'Dict[str,str]'
            Specifies the parameters in the output image table.

        Returns
        -------
        :class:'CASTable'

        Examples
        --------
        >>> # Import classes
        >>> from swat import CAS
        >>> from cvpy.biomedimage.BiomedImageTable import BiomedImageTable
        >>> from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
        >>> ## Connect to CAS
        >>> s = CAS("example.com", 5570)
        >>> # Construct tables that are parameters to the sphericity API
        >>> image_table = s.CASTable(...)
        >>> # Construct Biomed object
        >>> biomed = BiomedImageTable(image_table)
        >>> # Call the API
        >>> output_table = biomed.sphericity(use_spacing, ...., label_connectivity)

        """

        # If output_table_parms is not passed, set it as an empty dict
        if not output_table_parms:
            output_table_parms = dict()

        random_name_generator = RandomNameGenerator()

        # Quantify the volume and perimeter of the given component.
        self.connection.biomedimage.quantifybiomedimages(images=dict(table=self.table),
                                                         copyvars=['_path_'],
                                                         region='COMPONENT',
                                                         quantities=[
                                                             dict(quantityparameters=dict(quantitytype='perimeter')),
                                                             dict(quantityparameters=dict(quantitytype='content',
                                                                                          useSpacing=use_spacing))
                                                             ],
                                                         labelparameters=dict(labelType='basic',
                                                                              connectivity=label_connectivity.name),
                                                         inputbackground=input_background,
                                                         casout=dict(name='quantify'),
                                                         )

        if 'name' not in output_table_parms:
            output_table_parms['name'] = random_name_generator.generate_name()

        sphericity = self.connection.CASTable(**output_table_parms)

        # Compute sphericity based on perimeter and volume of the lesion
        self.connection.fedsql.execdirect(f'''
                    create table "{sphericity.name}" as 
                    select _path_,_perimeter_,_content_, (power(pi(), 1.0/3.0) * power(6*_content_, 2.0/3.0))/_perimeter_ as 
                    sphericity from quantify
                    ''')

        # Delete the quantify table
        self.connection.table.dropTable(name='quantify')

        return sphericity

    def morphological_gradient(self, kernel_width: int = 3, kernel_height: int = 3, copy_vars: List[str] = None,
                               output_table_parms: Dict[str, str] = None):
        """
        Compute the morphological gradient for each 3D grayscale image in this BiomedImageTable.

        Parameters
        ------------
        kernel_width : :class:'int'
            Specifies the kernel width.
        kernel_height : :class:'int'
            Specifies the kernel height.
        copy_vars : :class:'List[str]'
            Specifies which columns to copy to the output image table.
        output_table_parms : :class:'Dict[str,str]'
            Specifies the parameters in the output image table.

        Returns
        ------------
        :class:'cvpy.biomedimage.BiomedImageTable'

        Examples
        --------
        >>> # Import classes
        >>> from swat import CAS
        >>> from cvpy.biomedimage.BiomedImageTable import BiomedImageTable
        >>> from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
        >>> ## Connect to CAS
        >>> s = CAS("example.com", 5570)
        >>> # Construct table to be passed to the morphological_gradient API
        >>> image_table = s.CASTable(...)
        >>> # Construct Biomed object
        >>> biomed = BiomedImageTable(image_table)
        >>> # Call the API
        >>> output_table = biomed.morphological_gradient(kernel_width,...)
        """

        # If output_table_parms is not passed, set it as an empty dict
        if not output_table_parms:
            output_table_parms = dict()

        random_name_generator = RandomNameGenerator()

        if copy_vars is None:
            copy_vars_with_biomed_vars = ['_biomedid_', '_biomeddimension_', '_sliceindex_']
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
        image_2d = self.connection.CASTable(name=name_image_2d, replace=True)
        self.connection.biomedimage.processbiomedimages(images=dict(table=self.table),
                                                        steps=[dict(stepparameters=dict(steptype='export'))],
                                                        casout=image_2d,
                                                        copyvars=copy_vars)

        # Compute morphological gradient of 2d images
        name_morph_grad_2d = random_name_generator.generate_name()
        morph_grad_2d = self.connection.CASTable(name=name_morph_grad_2d, replace=True)
        self.connection.image.processImages(table=image_2d,
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
        if 'name' not in output_table_parms:
            output_table_parms['name'] = random_name_generator.generate_name()
        morph_grad_3d = self.connection.CASTable(**output_table_parms)
        self.connection.biomedimage.processbiomedimages(images=dict(table={'name': name_morph_grad_2d}),
                                                        steps=[dict(
                                                            stepparameters=dict(steptype='import', targetdimension=3))],
                                                        casout=morph_grad_3d,
                                                        copyvars=copy_vars)

        # Delete our temporary tables
        self.connection.table.dropTable(image_2d)
        self.connection.table.dropTable(morph_grad_2d)

        return BiomedImageTable(morph_grad_3d)

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

import sys
import struct
import numpy as np
from typing import List
from warnings import warn
from swat import CAS, CASTable

from cvpy.base.ImageTable import ImageTable
from cvpy.biomedimage.LabelConnectivity import LabelConnectivity

class BiomedImage(object):
    '''
    Implement biomedical image processing functions. 

     Parameters
     ----------
     cas_session
          Specifies the CAS session.

     Returns
     -------
     :class:`BiomedImage`
    '''

    def __init__(self, cas_session: CAS = None) -> None:
        self._cas_session = cas_session
        ## Load the actionsets
        self._cas_session.loadactionset('image')
        self._cas_session.loadactionset('biomedimage')
        self._cas_session.loadactionset('fedsql')
    
    @property
    def cas_session(self) -> CAS:
        return self._cas_session

    @cas_session.setter
    def cas_session(self, cas_session) -> None:
        self._cas_session = cas_session


    def quantify_sphericity(self, image_table: ImageTable, use_spacing: bool, input_background: float,
                            label_connectivity: LabelConnectivity, sphericity: CASTable) -> None:
        '''
        Quantify the sphericity for the given component from a CAS table. 

        Parameters
        -----------
        image_table: ImageTable
             Specifies the CAS table that contains the image binaries.
        use_spacing: bool
             When set to True, use image spacing in the sphericity calculation.
        input_background: float
             Specifies the background value in input images.
        label_connectivity: LabelConnectivity.FACE | LabelConnectivity.VERTEX
             Specifies the level of connectivity for connected components: LabelConnectivity.FACE or LabelConnectivity.VERTEX
        sphericity: CASTable
             Specifies the output CAS table.

        Examples
        --------
        >>> ## Import classes
        >>> from swat import CAS
        >>> from cvpy.base.ImageTable import ImageTable
        >>> from cvpy.biomedimage.BiomedImage import BiomedImage
        >>> from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
        >>> ## Connect to CAS
        >>> s = swat.CAS("example.com", 5570)
        >>> ## Construct Biomed object
        >>> biomed = BiomedImage(s)
        >>> ## Construct tables that are paramters to the quantify_sphericity API
        >>> image_table = s.CASTable(...)
        >>> input_table = ImageTable(image_table)
        >>> output_table = s.CASTable(...)
        >>> ## Call the API
        >>> BiomedImage.quantify_sphericity(input_table.table,....,output_table)

        '''
        conn = self._cas_session

        ## Quantify the volume and perimeter of the given component.
        conn.biomedimage.quantifybiomedimages(images=dict(table= image_table.table),
                                              copyvars=['_path_'],
                                              region='COMPONENT',
                                              quantities=[dict(quantityparameters=dict(quantitytype='perimeter')),
                                              dict(quantityparameters=dict(quantitytype='content',useSpacing = use_spacing))
                                              ],
                                              labelparameters=dict(labelType='basic',connectivity=label_connectivity.name), 
                                              inputbackground=input_background,
                                              casout=dict(name='quantify'),
                                              )

        ## Compute sphericity based on perimeter and volume of the lesion
        conn.fedsql.execdirect(f'''
            create table {sphericity.name} as 
            select _path_,_perimeter_,_content_, (power(pi(), 1.0/3.0) * power(6*_content_, 2.0/3.0))/_perimeter_ as 
            sphericity from quantify
            ''')
        
        ## Delete the quantify table
        conn.table.dropTable(name='quantify')

    

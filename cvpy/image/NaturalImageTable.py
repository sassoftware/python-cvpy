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

''' Image analysis tools '''

import sys
import struct
import numpy as np
from typing import List, Dict
from warnings import warn
from swat import CASTable
from cvpy.base.ImageTable import ImageTable
from cvpy.utils.RandomNameGenerator import RandomNameGenerator
from enum import *


class NaturalImageTable(ImageTable):
    """
    Implement image processing functions.

     Parameters
     ----------
     cas_session
          Specifies the CAS session.

     Returns
     -------
     :class:`Image`
    """

    def __init__(self, table: CASTable = None, image: str = None, dimension: str = None, resolution: str = None,
             imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
             type: str = None) -> None:
        super().__init__(table=table, image=image, dimension=dimension, resolution=resolution, imageFormat=imageFormat,
                        path=path, label=label, id=id, size=size, type=type)
        ## Load the actionsets
        self.connection.loadactionset('image')
        self.connection.loadactionset('fedsql')

    @staticmethod
    def __reverse(a, axis=0):

        '''
        Reverses a numpy array along a given axis.

        Parameters
        ----------
        a : :class:`numpy.ndarray`
            Specifies the array to be reversed.
        axis : int
            Specifies the axis along which the array should be reversed.

        Returns
        -------
        :class:`numpy.ndarray`
        '''

        idx = [slice(None)] * len(a.shape)
        idx[axis] = slice(None, None, -1)
        return a[tuple(idx)]

    def mask_image(self, mask: ImageTable, decode: bool = False,
                   add_columns: List(str) = None, copy_vars: List(str) = None,
                   output_table_parms: Dict[str,str] = {}) -> ImageTable:
        """
        Applies masking to an ImageTable.

        Parameters
        ------------
        mask : :class:`cvpy.ImageTable`
            Specifies the image table that will be used for masking.
        decode : :class:`bool`
            Specifies whether to decode the output image table.
        add_columns : :class:'List(str)'
            Specifies extra columns to add to the output table.
        copy_vars : :class:`List(str)`
            Specifies which columns to copy to the output image table.
        output_table_parms : :class:`Dict[str,str]`
            Specifies the parameters in the output image table.
        Returns
        ------------
        :class:`cvpy.ImageTable`
        """

        conn = self._cas_session

        ###############################################
        ########### Mask Tbl Decoded ##################
        ###############################################
        if mask.has_decoded_images():

            # List of columns that will be alternated
            alter_columns = [dict(name=mask.image, rename="seg"),
                             dict(name=mask.dimension, rename="dim"),
                             dict(name=mask.resolution, rename="res"),
                             dict(name=mask.imageFormat, rename="form")]

            # SQL string to create the mask table
            fed_sql_str = f'''create table _images_to_mask_ {{options replace=true}} as 
                select a.seg, a.dim, a.res, a.form, b.* 
                from {mask.table.name} as a right join {self.image.table.name} as b 
                on a._id_=b._id_ '''

            # Dictionary for specifying information in our binary operation
            binary_operation_dict = dict(binaryOperationType="MASK_SPECIFIC",
                                         image="seg", 
                                         dimension="dim",
                                         resolution="res", 
                                         imageFormat="form")

            # Mini method for renaming columns in ImageTable object
            # *This step must be completed AFTER the alter table command*
            def rename_columns():
                mask.image = "seg"
                mask.dimension = "dim"
                mask.resolution = "res"
                mask.imageFormat = "form"

        ###############################################
        ############# Mask Tbl Encoded ################
        ###############################################
        else:
            # Create CAS Table
            if 'name' not in output_table_parms:
                output_table_parms['name'] = RandomNameGenerator().generate_name()
            
            cas_table = conn.CASTable(**output_table_parms)

            # List of columns that will be alternated
            alter_columns = [dict(name=mask.image, rename="seg")]

            # SQL string to create the mask table
            fed_sql_str = f'''create table _images_to_mask_ {{options replace=true}} as 
                select a.seg, b.* 
                from {mask.table.name} as a right join {self.image.table.name} as b 
                on a._id_=b._id_ '''

            # Dictionary for specifying information in our binary operation
            binary_operation_dict = dict(binaryOperationType="MASK_SPECIFIC", image="seg")

            # Mini method for renaming columns in ImageTable Object
            # *This step must be completed AFTER the alter table command*
            def rename_columns():
                mask.image = "seg"

        ###############################################
        ############### Masking Step ##################
        ###############################################

        # Change column names so that we can merge tables
        conn.table.altertable(name=mask.table, columns=alter_columns)

        # Create Images to Mask Table
        _images_to_mask_ = conn.CASTable("_images_to_mask_", replace=True)

        # SQL Statement to join tables
        conn.fedsql.execdirect(fed_sql_str)

        # Masking step
        conn.image.processimages(
            table=_images_to_mask_,
            steps=[dict(step=dict(stepType="BINARY_OPERATION",
                                  binaryOperation=binary_operation_dict)
                        )],
            decode=decode,
            addColumns= add_columns,
            casout=cas_table,
            copyVars=copy_vars
        )

        # Delete our temporary table
        conn.table.dropTable(_images_to_mask_)

        # Change column names in the ImageTable
        rename_columns()

        return ImageTable(cas_table)

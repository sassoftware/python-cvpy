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

    def mask_image(self, mask: ImageTable, decode: bool = False,
                   add_columns: List[str] = None, copy_vars: List[str] = None,
                   output_table_parms: Dict[str,str] = None) -> ImageTable:
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

        if not output_table_parms:
            output_table_parms = dict()

        # Create CAS Table
        if 'name' not in output_table_parms:
            output_table_parms['name'] = RandomNameGenerator().generate_name()
            
        cas_table = self.connection.CASTable(**output_table_parms)

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
                from "{mask.table.name}" as a right join "{self.table.name}" as b 
                on a._id_=b._id_ '''

            # Dictionary for specifying information in our binary operation
            binary_operation_dict = dict(binaryOperationType="MASK_SPECIFIC",
                                         image="seg", 
                                         dimension="dim",
                                         resolution="res", 
                                         imageFormat="form")

        ###############################################
        ############# Mask Tbl Encoded ################
        ###############################################
        else:
            # List of columns that will be alternated
            alter_columns = [dict(name=mask.image, rename="seg")]

            # SQL string to create the mask table
            fed_sql_str = f'''create table _images_to_mask_ {{options replace=true}} as 
                select a.seg, b.* 
                from "{mask.table.name}" as a right join "{self.table.name}" as b 
                on a._id_=b._id_ '''

            # Dictionary for specifying information in our binary operation
            binary_operation_dict = dict(binaryOperationType="MASK_SPECIFIC", image="seg")

        ###############################################
        ############### Masking Step ##################
        ###############################################

        # Change column names so that we can merge tables
        self.connection.table.altertable(name=mask.table, columns=alter_columns)

        # Create Images to Mask Table
        _images_to_mask_ = self.connection.CASTable("_images_to_mask_", replace=True)

        # SQL Statement to join tables
        self.connection.fedsql.execdirect(fed_sql_str)

        # Masking step
        self.connection.image.processimages(
            table=_images_to_mask_,
            steps=[dict(step=dict(stepType="BINARY_OPERATION",
                                  binaryOperation=binary_operation_dict)
                        )],
            decode=decode,
            addColumns= add_columns,
            casout=cas_table.name,
            copyVars=copy_vars
        )

        # Delete our temporary table
        self.connection.table.dropTable(_images_to_mask_)

        return ImageTable(cas_table)

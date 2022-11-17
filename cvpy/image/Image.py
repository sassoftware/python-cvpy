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
from typing import List
from warnings import warn
from swat import CAS, CASTable
from cvpy.base.ImageDataType import ImageDataType
from cvpy.base.ImageTable import ImageTable
from enum import *


class Image(object):
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
        return a[idx]

    @staticmethod
    def get_image_array_from_row(image_binary, dimension, resolution, myformat, channel_count=1):

        """
        Get a 3D image from a row.

        Parameters
        ----------
        image_binary : :class:`bytes`
            Specifies the image binary.
        dimension : :class:`int`
            Specifies the dimension of the image.
        resolution : :class:`numpy.ndarray`
            Specifies the resolution of the image.
        myformat : :class:`str`
            Specifies the format of the image.
        channel_count : :class:`int`, optional
            Specifies the number of channels that the image has.

        Returns
        -------
        :class:`numpy.ndarray`
        """

        num_cells = np.prod(resolution)
        if myformat == '32S':
            image_array = np.array(struct.unpack('=%si' % num_cells, image_binary[0:4 * num_cells])).astype(np.int32)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '32F':
            image_array = np.array(struct.unpack('=%sf' % num_cells, image_binary[0:4 * num_cells])).astype(np.float32)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '64F':
            image_array = np.array(struct.unpack('=%sd' % num_cells, image_binary[0:8 * num_cells])).astype(np.float64)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '64U':
            image_array = np.array(struct.unpack('=%sQ' % num_cells, image_binary[0:8 * num_cells])).astype(np.uint64)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '16S':
            image_array = np.array(struct.unpack('=%sh' % num_cells, image_binary[0:2 * num_cells])).astype(np.int16)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '16U':
            image_array = np.array(struct.unpack('=%sH' % num_cells, image_binary[0:2 * num_cells])).astype(np.uint16)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '8U' and channel_count == 3:
            image_array = np.array(bytearray(image_binary[0:(num_cells * 3)])).astype(np.uint8)
            image_array = np.reshape(image_array, (resolution[0], resolution[1], 3))[:, :, 0:3]
            image_array = Image.__reverse(image_array, 2)
        elif myformat == '8S':
            image_array = np.array(struct.unpack('=%sb' % num_cells, image_binary[0:num_cells])).astype(np.int8)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '8U':
            image_array = np.array(struct.unpack('=%sB' % num_cells, image_binary[0:num_cells])).astype(np.uint8)
            image_array = np.reshape(image_array, resolution)
        else:
            image_array = np.array(bytearray(image_binary)).astype(np.uint8)
            image_array = np.reshape(image_array, (resolution[0], resolution[1], 3))
            image_array = Image.__reverse(image_array, 2)
        return image_array

    @staticmethod
    def get_image_array(image_binaries, dimensions, resolutions, formats, n, channel_count=1):

        """
        Get an image from a fetched array.

        Parameters
        ----------
        image_binaries : :class:`pandas.Series`
            Specifies the image binaries
        dimensions : :class:`pandas.Series`
            Specifies the dimensions of the images.
        resolutions : :class:`pandas.Series`
            Specifies the resolutions of the images.
        formats : :class:`pandas.Series`
            Specifies the image formats.
        n : :class:`int`
            Specifies the dimension index.
        channel_count : :class:`int`, optional
            Specifies the number of channels that the image has.

        Returns
        -------
        :class:`numpy.ndarray`
        """

        dimension = int(dimensions[n])
        resolution = np.array(struct.unpack('=%sq' % dimension, resolutions[n][0:dimension * 8]))
        resolution = resolution[::-1]
        myformat = formats[n]
        return Image.get_image_array_from_row(image_binaries[n], dimension, resolution, myformat, channel_count)

    @staticmethod
    def convert_to_CAS_column(s):

        """
        Convert a string to CAS column name.

        Parameters
        ----------
        s : :class:`str`
            Specifies the column name to be converted.

        Returns
        -------
        :class:`str`
        """

        s = str.replace(str.replace(s, '{', '_'), '}', '_')
        return '_' + s + '_'

    @staticmethod
    def fetch_image_array(imdata, n=0, qry='', image='_image_', dim='_dimension_', res='_resolution_',
                          ctype='_channelType_', ccount=1):

        """
        Fetch image array from a CAS table.

        Parameters
        ----------
        imdata : :class:`str`
            Specifies the image data.
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
        :class:`numpy.ndarray`
        """

        if (qry != ''):
            example_rows = imdata.query(qry).to_frame(to=n + 1)
        else:
            example_rows = imdata.to_frame(to=n + 1)
        medical_dimensions = example_rows[dim]
        medical_formats = example_rows[ctype]
        medical_binaries = example_rows[image]
        medical_resolutions = example_rows[res]
        return Image.get_image_array(medical_binaries, medical_dimensions, medical_resolutions, medical_formats, n,
                                     ccount)

    @staticmethod
    def fetch_geometry_info(imdata, n=0, qry='', posCol='_position_', oriCol='_orientation_', spaCol='_spacing_',
                            dimCol='_dimension_'):

        """
        Fetch geometry information from a CAS table.

        Parameters
        ----------
        imdata : :class:`swat.CASTable <swat.cas.table.CASTable>`
            Specifies the CASTable that contains the image.
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
        if not {'_position_', '_spacing_', '_orientation_'}.issubset(imdata.columns):
            return ((), (), ())

        if (qry != ''):
            example_rows = imdata[[dimCol, posCol, oriCol, spaCol]].query(qry).to_frame(to=n)
        else:
            example_rows = imdata[[dimCol, posCol, oriCol, spaCol]].to_frame(to=n)
        dim = example_rows[dimCol][0]
        pos = struct.unpack('=%sd' % dim, example_rows[posCol][0][0:dim * 8])
        ori = struct.unpack('=%sd' % (dim * dim), example_rows[oriCol][0][0:dim * dim * 8])
        spa = struct.unpack('=%sd' % dim, example_rows[spaCol][0][0:dim * 8])
        return pos, ori, spa

    @staticmethod
    def get_image_array_const_ctype(image_binaries, dimensions, resolutions, ctype, n, channel_count=1):

        """
        Get an image array with a constant channel type from a CAS table.

        Parameters
        ----------
        image_binaries : :class:`pandas.Series`
            Specifies the image binaries.
        dimensions : :class:`pandas.Series`
            Specifies the dimensions of the images.
        resolutions : :class:`pandas.Series`
            Specifies the resolutions of the images.
        ctype : :class:`str`
            Specifies the channel type of the image.
        n : :class:`int`
            Specifies the dimension index.
        channel_count : :class:`int`
            Specifies the channel count of the image.

        Returns
        -------
        :class:`numpy.ndarray`
        """
        dimension = int(dimensions[n])
        resolution = np.array(struct.unpack('=%sq' % dimension, resolutions[n][0:dimension * 8]))
        resolution = resolution[::-1]
        num_cells = np.prod(resolution)

        return Image.get_image_array_from_row(image_binaries[n], dimension, resolution, ctype, channel_count)

    @staticmethod
    def convert_wide_to_numpy(wide_image) -> np.ndarray:

        """
        Convert a wide image to a numpy image array.

        Parameters
        ----------
        wide_image: bytes buffer
             Specifies the wide image byte buffer

        Returns
        -------
        numpy.ndarray

        """

        # Get the width and height from the input buffer
        width = np.frombuffer(wide_image[8:2 * 8], dtype=np.int64)[0]
        height = np.frombuffer(wide_image[2 * 8:3 * 8], dtype=np.int64)[0]
        data_type = np.frombuffer(wide_image[3 * 8:4 * 8], dtype=np.int64)[0]

        # Get the number of channels and the numpy data type
        if data_type == ImageDataType.CV_8UC1.value:
            num_channels = 1
            np_data_type = np.uint8
        elif data_type == ImageDataType.CV_8UC3.value:
            num_channels = 3
            np_data_type = np.uint8
        elif data_type == ImageDataType.CV_32FC1.value:
            num_channels = 1
            np_data_type = np.float32
        elif data_type == ImageDataType.CV_32FC3.value:
            num_channels = 3
            np_data_type = np.float32
        elif data_type == ImageDataType.CV_64FC1.value:
            num_channels = 1
            np_data_type = np.float64
        elif data_type == ImageDataType.CV_64FC3.value:
            num_channels = 3
            np_data_type = np.float64

        # Return the numpy array
        return np.frombuffer(wide_image[4 * 8:], dtype=np_data_type).reshape(height, width, num_channels)

    def mask_image(self, image: ImageTable, mask: ImageTable, casout: CASTable, decode: bool = False,
                   copy_vars: list(Enum) = None):
        """
        Applies masking to an ImageTable.
        Parameters
        ------------
        image : :class:`cvpy.ImageTable`
            Specifies the input image table to be masked.
        mask : :class:`cvpy.ImageTable`
            Specifies the image table that will be used for masking.
        casout : :class:`swat.CASTable`
            Specifies the output image table.
        decode : :class:`bool`
            Specifies whether to decode the output image table.
        copy_vars : :class:`list[enum.Enum]`
            Specifies which columns to copy to the output image table.
        Returns
        ------------
        None
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
                from {mask.table.name} as a right join {image.table.name} as b 
                on a._id_=b._id_ '''

            # Dictionary for specifying information in our binary operation
            binary_operation_dict = dict(binaryOperationType="MASK_SPECIFIC",
                                         image="seg", dimension="dim",
                                         resolution="res", imageFormat="form")

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

            # List of columns that will be alternated
            alter_columns = [dict(name=mask.image, rename="seg")]

            # SQL string to create the mask table
            fed_sql_str = f'''create table _images_to_mask_ {{options replace=true}} as 
                select a.seg, b.* 
                from {mask.table.name} as a right join {image.table.name} as b 
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
            casout=casout,
            copyVars=copy_vars
        )

        # Delete our temporary table
        conn.table.dropTable(_images_to_mask_)

        # Change column names in the ImageTable
        rename_columns()

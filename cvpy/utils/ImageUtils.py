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

''' Image analysis util tools'''

import sys
import struct
import numpy as np
from warnings import warn
from swat.cas import CAS

from cvpy.base.ImageDataType import ImageDataType

class ImageUtils(object):

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
            image_array = ImageUtils.__reverse(image_array, 2)
        elif myformat == '8S':
            image_array = np.array(struct.unpack('=%sb' % num_cells, image_binary[0:num_cells])).astype(np.int8)
            image_array = np.reshape(image_array, resolution)
        elif myformat == '8U':
            image_array = np.array(struct.unpack('=%sB' % num_cells, image_binary[0:num_cells])).astype(np.uint8)
            image_array = np.reshape(image_array, resolution)
        else:
            image_array = np.array(bytearray(image_binary)).astype(np.uint8)
            image_array = np.reshape(image_array, (resolution[0], resolution[1], 3))
            image_array = ImageUtils.__reverse(image_array, 2)
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
        return ImageUtils.get_image_array_from_row(image_binaries[n], dimension, resolution, myformat, channel_count)

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

        return ImageUtils.get_image_array_from_row(image_binaries[n], dimension, resolution, ctype, channel_count)

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

    @staticmethod
    def convert_numpy_to_wide(numpy_array: np.ndarray) -> bytes:

        """
        Convert a numpy image array to a wide image.

        Parameters
        ----------
        numpy_array: np.ndarray
             Specifies the numpy image array.

        Returns
        -------
        bytes
        """

        # Get the width, height, number of channels, and data type from the numpy image array
        (width, height, num_channels) = numpy_array.shape
        np_data_type = numpy_array.dtype

        # Assign the appropriate ImageDataType
        if num_channels == 1 and np_data_type == np.dtype(np.uint8):
            data_type = ImageDataType.CV_8UC1.value
        elif num_channels == 3 and np_data_type == np.dtype(np.uint8):
            data_type = ImageDataType.CV_8UC3.value
        elif num_channels == 1 and np_data_type == np.dtype(np.float32):
            data_type = ImageDataType.CV_32FC1.value
        elif num_channels == 3 and np_data_type == np.dtype(np.float32):
            data_type = ImageDataType.CV_32FC3.value
        elif num_channels == 1 and np_data_type == np.dtype(np.float64):
            data_type = ImageDataType.CV_64FC1.value
        elif num_channels == 3 and np_data_type == np.dtype(np.float64):
            data_type = ImageDataType.CV_64FC3.value

        # Create the wide image
        wide_prefix = np.array([-1, height, width, data_type], dtype=np.int64)
        return wide_prefix.tobytes() + numpy_array.tobytes()
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

import os
import unittest
import xmlrunner
import struct
import swat
import sys
import numpy as np

from cvpy.image.Image import Image
from cvpy.base.ImageDataType import ImageDataType

def create_numpy_array_and_wide_image(image, num_channels):
    # Get the image data
    image_rows = image.to_frame()
    image_binary = image_rows['_image_'][0]
    width = image_rows['_width_'][0]
    height = image_rows['_height_'][0]

    # Create the original numpy image array
    image_array = np.array(bytearray(image_binary[0:(width * height * num_channels)])).astype(np.uint8)
    numpy_image_array = np.reshape(image_array, (width, height, num_channels))

    # Get the data type of the image from num_channels
    if num_channels == 1:
        data_type = ImageDataType.CV_8UC1.value
    elif num_channels == 3:
        data_type = ImageDataType.CV_8UC3.value

    # Convert the numpy array to a wide image
    wide_prefix = np.array([-1, height, width, data_type], dtype=np.int64)

    # Return both the array and the wide image
    return (numpy_image_array, (wide_prefix.tobytes() + numpy_image_array.tobytes()))

class TestImage(unittest.TestCase):

    def test_convert_to_CAS_column(self):
        self.assertTrue(Image.convert_to_CAS_column("id") == "_id_")

    def test_fetch_image_array(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')

        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        image = self.s.CASTable('image', replace=True)
        self.s.image.loadImages(path='biomedimg/simple.png',
                            casOut=dict(name='image', replace='TRUE'),
                            addColumns={"WIDTH", "HEIGHT", "DEPTH", "CHANNELTYPE", "SPACING"},
                            caslib='dlib',
                            decode=True)

        self.assertTrue(np.array_equal(Image.fetch_image_array(image), np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

        # Close the connection
        self.s.close()

    def test_get_image_array(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        self.s.image.loadImages(path='biomedimg/simple.png',
                                casOut=dict(name='image', replace='TRUE'),
                                addColumns={"WIDTH", "HEIGHT", "DEPTH", "CHANNELTYPE", "SPACING"},
                                caslib='dlib',
                                decode=True)

        imageRows = self.s.fetch(table='image', sastypes=False)['Fetch']

        medicalDimensions = imageRows["_dimension_"]
        medicalFormats = imageRows["_channelType_"]
        medicalBinaries = imageRows["_image_"]
        medicalResolutions = imageRows["_resolution_"]

        medicalImageArray = Image.get_image_array(medicalBinaries, medicalDimensions, medicalResolutions, medicalFormats, 0)
        self.assertTrue(np.array_equal(medicalImageArray, np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

        # Close the connection
        self.s.close()

    def test_get_image_array_from_row(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        self.s.image.loadImages(path='biomedimg/simple.png',
                                casOut=dict(name='image', replace='TRUE'),
                                addColumns={"WIDTH", "HEIGHT", "DEPTH", "CHANNELTYPE", "SPACING"},
                                caslib='dlib',
                                decode=True)

        imageRows = self.s.fetch(table='image', sastypes=False)['Fetch']

        medicalDimensions = imageRows["_dimension_"]
        medicalFormats = imageRows["_channelType_"]
        medicalBinaries = imageRows["_image_"]
        medicalResolutions = imageRows["_resolution_"]

        n=0
        dimension = int(medicalDimensions[n])
        resolution = np.array(struct.unpack('=%sq' % dimension, medicalResolutions[n][0:dimension * 8]))
        resolution = resolution[::-1]
        myformat = medicalFormats[n]
        medicalImageArray = Image.get_image_array_from_row(medicalBinaries[n], dimension, resolution, myformat, 1)

        self.assertTrue(np.array_equal(medicalImageArray, np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

        # Close the connection
        self.s.close()

    def test_get_image_array_from_row_dtypes(self):
        test_pass = True
        width = 2

        # Test all single channel data types
        img_dtypes = ['32S', '32F', '64F', '64U', '16U', '16S', '8U', '8S']
        np_dtypes = [np.int32, np.float32, np.float64, np.uint64, np.uint16, np.int16, np.uint8, np.int8, np.uint8]
        for (img_dtype, np_dtype) in zip(img_dtypes, np_dtypes):
            image = np.arange(0,width*width).reshape([width,width]).astype(np_dtype)
            resolution = image.shape[:2]
            imageArray = Image.get_image_array_from_row(bytes(image), 2, resolution, img_dtype, 1)
            test_pass = test_pass and np.array_equal(image, imageArray)
            test_pass = test_pass and (imageArray.dtype == np_dtype)

        # Test all multi-channel data types
        img_dtypes = ['8U', '']
        np_dtypes = [np.uint8, np.uint8]
        for (img_dtype, np_dtype) in zip(img_dtypes, np_dtypes):
            image = np.arange(0,width*width*3).reshape([width,width,3]).astype(np_dtype)
            resolution = image.shape[:2]
            imageArray = Image.get_image_array_from_row(bytes(np.flip(image, 2)), 2, resolution, img_dtype, 3)
            test_pass = test_pass and np.array_equal(image, imageArray)
            test_pass = test_pass and (imageArray.dtype == np_dtype)

        self.assertTrue(test_pass)

    def test_fetch_geometry_info_no_geometry(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        image = self.s.CASTable("image", replace=True)
        self.s.image.loadImages(path='biomedimg/simple.png',
                                casOut=image,
                                caslib='dlib',
                                decode=True)

        self.assertTrue(Image.fetch_geometry_info(image) == ((),(),()))

        # Close the connection
        self.s.close()

    def test_fetch_geometry_info(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load an image with geometry data
        imgray = self.s.CASTable("imgray", replace=True)
        self.s.image.loadimages(path="biomedimg/simple.png",
                                casout=imgray,
                                decode=True,
                                caslib="dlib",
                                addcolumns={"position", "orientation", "spacing"},
                                )

        self.assertTrue(Image.fetch_geometry_info(imgray) == ((0, 0), (1.0, 0.0, 0.0, 1.0), (1.0, 1.0)))

        # Close the connection
        self.s.close()
    
    def test_get_image_array_const_ctype(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.loadactionset('biomedimage')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)
        
        # Load the image
        cdata = self.s.CASTable('cdata')
        self.s.image.loadimages(path='biomedimg/simple.png',
                                casout=cdata,
                                caslib='dlib',
                                decode=True)
        
        example_rows = cdata.to_frame()
        medical_dimensions = example_rows['_dimension_']
        medical_binaries = example_rows['_image_']
        medical_resolutions = example_rows['_resolution_']
        
        image_array = Image.get_image_array_const_ctype(medical_binaries, medical_dimensions, medical_resolutions, ctype='8U', n=0, channel_count=1)
        
        self.assertTrue(np.array_equal(image_array, np.array([[0, 0, 0, 0, 0],[0, 255, 0, 0, 0],[0, 255, 0, 150, 0],[0, 0, 0, 0, 50],[0, 0, 0, 0, 0]])))

        # Close the connection
        self.s.close()

    def test_convert_wide_to_numpy_3_channel(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')

        # Add caslib
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        image = self.s.CASTable('image', replace=True)
        self.s.image.loadImages(path='images/Sas_c.jpg',
                                casOut=dict(name='image', replace='TRUE'),
                                addColumns={"WIDTH", "HEIGHT"},
                                caslib='dlib',
                                decode=True)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 3)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    def test_convert_wide_to_numpy_1_channel(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')

        # Add caslib
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load the image
        image = self.s.CASTable('image', replace=True)
        self.s.image.loadImages(path='unittest/gray_3x3.png',
                                casOut=dict(name='image', replace='TRUE'),
                                addColumns={"WIDTH", "HEIGHT"},
                                caslib='dlib',
                                decode=True)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 1)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:

        TestImage.dataPath = sys.argv.pop()
        TestImage.password = sys.argv.pop()
        TestImage.username = sys.argv.pop()
        TestImage.casPort = sys.argv.pop()
        TestImage.casHost = sys.argv.pop()

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

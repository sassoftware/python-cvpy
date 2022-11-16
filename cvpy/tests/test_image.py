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
from cvpy.base.ImageTable import ImageTable
from cvpy.image.Image import Image
from cvpy.base.ImageDataType import ImageDataType


def load(self, path):
    # Load the image
    image = self.s.CASTable('image', replace=True)
    self.s.image.loadImages(path=path,
                            casOut=dict(name='image', replace='TRUE'),
                            addColumns={"WIDTH", "HEIGHT"},
                            caslib='dlib',
                            decode=True)
    return image


def rescale(self, image, rescale_type):

    # Determine the desired rescale type
    if rescale_type == ImageDataType.CV_8UC1.value or rescale_type == ImageDataType.CV_8UC3.value:
        rescale_params = "TO_8U"
    elif rescale_type == ImageDataType.CV_32FC1.value or rescale_type == ImageDataType.CV_32FC3.value:
        rescale_params = "TO_32F"
    elif rescale_type == ImageDataType.CV_64FC1.value or rescale_type == ImageDataType.CV_64FC3.value:
        rescale_params = "TO_64F"

    # Rescale the image
    self.s.image.processimages(
        table=image,
        casout=image,
        steps=[
            {
                'step':
                    {
                        'stepType': 'RESCALE',
                        'type': rescale_params
                    }
            }
        ],
        copyVars = {"_width_", "_height_"},
        decode=True
    )

    return image


def create_numpy_array_and_wide_image(image, num_channels, data_type):
    # Get the image data
    image_rows = image.to_frame()
    image_binary = image_rows['_image_'][0]
    width = image_rows['_width_'][0]
    height = image_rows['_height_'][0]

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

    # Create the original numpy image array
    image_array = np.array(bytearray(image_binary[0:(width * height * num_channels)])).astype(np_data_type)
    numpy_image_array = np.reshape(image_array, (width, height, num_channels))

    # Convert the numpy array to a wide image
    wide_prefix = np.array([-1, height, width, data_type], dtype=np.int64)

    # Return both the array and the wide image
    return numpy_image_array, (wide_prefix.tobytes() + numpy_image_array.tobytes())


class TestImage(unittest.TestCase):

    def setUp(self) -> None:
        # Set up CAS connection
        self.s = swat.CAS(TestImage.CAS_HOST, TestImage.CAS_PORT, TestImage.USERNAME,
                     TestImage.PASSWORD)
        self.s.loadactionset("image")
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=TestImage.DATAPATH, dataSource='PATH',
                         subdirectories=True)

    def tearDown(self) -> None:
        self.s.close()

    def test_convert_to_CAS_column(self):
        self.assertTrue(Image.convert_to_CAS_column("id") == "_id_")

    def test_fetch_image_array(self):
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
        self.s.loadactionset('biomedimage')

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

    # Test convert_wide_to_numpy() function for a CV_8UC3 image
    def test_convert_wide_to_numpy_CV_8UC3(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'images/Sas_c.jpg')
        image = rescale(self, image, ImageDataType.CV_8UC3.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 3, ImageDataType.CV_8UC3.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    # Test convert_wide_to_numpy() function for a CV_8UC1 image
    def test_convert_wide_to_numpy_CV_8UC1(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'unittest/gray_3x3.png')
        image = rescale(self, image, ImageDataType.CV_8UC1.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 1, ImageDataType.CV_8UC1.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    # Test convert_wide_to_numpy() function for a CV_32FC1 image
    def test_convert_wide_to_numpy_CV_32FC1(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'unittest/gray_3x3.png')
        image = rescale(self, image, ImageDataType.CV_32FC1.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 1, ImageDataType.CV_32FC1.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    # Test convert_wide_to_numpy() function for a CV_32FC3 image
    def test_convert_wide_to_numpy_CV_32FC3(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'images/Sas_c.jpg')
        image = rescale(self, image, ImageDataType.CV_32FC3.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 3, ImageDataType.CV_32FC3.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    # Test convert_wide_to_numpy() function for a CV_64FC1 image
    def test_convert_wide_to_numpy_CV_64FC1(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'unittest/gray_3x3.png')
        image = rescale(self, image, ImageDataType.CV_64FC1.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 1, ImageDataType.CV_64FC1.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    # Test convert_wide_to_numpy() function for a CV_64FC3 image
    def test_convert_wide_to_numpy_CV_64FC3(self):
        # Load and rescale the input image to the desired type
        image = load(self, 'images/Sas_c.jpg')
        image = rescale(self, image, ImageDataType.CV_64FC3.value)

        # Use the image data to create the original numpy array and the wide image to be converted
        (numpy_image_array, wide_byte_buffer) = create_numpy_array_and_wide_image(image, 3, ImageDataType.CV_64FC3.value)

        # Use the convert_wide_to_numpy() function to convert the wide image back to numpy
        output_array = Image.convert_wide_to_numpy(wide_byte_buffer)

        # Compare these arrays to make sure they are equal
        self.assertTrue(np.array_equal(numpy_image_array, output_array))

        # Close the connection
        self.s.close()

    def test_mask_encoded_image_encoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_natural_image.png', casout=img, decode=False)
        self.s.image.processimages(
            table={'name': 'image'},
            casout={'name': 'image', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_32F'}}]
        )
        img_table = ImageTable(img)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_mask_image.png', casout=smask, decode=False)
        self.s.image.processimages(
            table={'name': 'smask'},
            casout={'name': 'smask', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_32F'}}]
        )
        smask_table = ImageTable(smask)

        # New Image Table
        new_img = self.s.CASTable('new_img', replace=True)

        # Construct Image object
        image = Image(cas_session=self.s)

        # Masking
        image.mask_image(img_table, smask_table, new_img, decode=False)

        test_arr = np.asarray([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 64, 32, 0],
            [0, 0, 75, 210, 0]
        ])

        new_img_arr = np.asarray(self.s.image.fetchImages(table='new_img').Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))

    def test_mask_decoded_image_decoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_3x3.png", casout=img, decode=True)
        img_table = ImageTable(img)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_2_3x3.png", casout=smask, decode=True)
        smask_table = ImageTable(smask)

        # New Image Table
        new_img = self.s.CASTable('new_img', replace=True)

        # Construct Image object
        image = Image(cas_session=self.s)

        # Masking
        image.mask_image(img_table, smask_table, new_img, decode=False)

        test_arr = np.array(
            [[0, 0, 255],
             [0, 255, 255],
             [0, 128, 0]]
        )

        new_img_arr = np.asarray(self.s.image.fetchImages(table='new_img').Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))

    def test_mask_decoded_image_encoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_natural_image.png', casout=img, decode=True)
        self.s.image.processimages(
            table={'name': 'image'},
            casout={'name': 'image', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_64F'}}]
        )
        img_table = ImageTable(img)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_mask_image.png', casout=smask, decode=False)
        self.s.image.processimages(
            table={'name': 'smask'},
            casout={'name': 'smask', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_64F'}}]
        )
        smask_table = ImageTable(smask)

        # New Image Table
        new_img = self.s.CASTable('new_img', replace=True)

        # Construct Image object
        image = Image(cas_session=self.s)

        # Masking
        image.mask_image(img_table, smask_table, new_img, decode=False)

        test_arr = np.asarray([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 64, 32, 0],
            [0, 0, 75, 210, 0]
        ])

        new_img_arr = np.asarray(self.s.image.fetchImages(table='new_img').Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))

    def test_mask_encoded_image_decoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_3x3.png", casout=img, decode=False)
        img_table = ImageTable(img)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_2_3x3.png", casout=smask, decode=True)
        smask_table = ImageTable(smask)

        # New Image Table
        new_img = self.s.CASTable('new_img', replace=True)

        # Construct Image object
        image = Image(cas_session=self.s)

        # Masking
        image.mask_image(img_table, smask_table, new_img, decode=False)

        test_arr = np.array(
            [[0, 0, 255],
             [0, 255, 255],
             [0, 128, 0]]
        )

        new_img_arr = np.asarray(self.s.image.fetchImages(table='new_img').Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestImage.DATAPATH = sys.argv.pop()
        TestImage.PASSWORD = sys.argv.pop()
        TestImage.USERNAME = sys.argv.pop()
        TestImage.CAS_PORT = sys.argv.pop()
        TestImage.CAS_HOST = sys.argv.pop()

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

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

import sys
import unittest

import numpy as np
import xmlrunner
from swat import CAS

from cvpy.base.ImageTable import ImageTable
from cvpy.base.ImageType import ImageType
from cvpy.biomedimage.LabelConnectivity import LabelConnectivity


class TestBiomedImage(unittest.TestCase):
    CAS_HOST = None
    CAS_PORT = None
    USERNAME = None
    PASSWORD = None
    DATAPATH = None

    def setUp(self) -> None:
        # Set up CAS connection
        self.s = CAS(TestBiomedImage.CAS_HOST, TestBiomedImage.CAS_PORT, TestBiomedImage.USERNAME,
                     TestBiomedImage.PASSWORD, protocol=TestBiomedImage.CAS_PROTOCOL)
        self.s.loadactionset("image")
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=TestBiomedImage.DATAPATH, dataSource='PATH',
                         subdirectories=True)

    def tearDown(self) -> None:
        self.s.close()

    def test_fetch_image_array(self):
        # Load the image
        image = ImageTable.load(self.s, path='biomedimg/simple.png',
                                load_parms={'caslib': 'dlib', 'decode': True,
                                            'addColumns': {"WIDTH", "HEIGHT", "DEPTH", "CHANNELTYPE", "SPACING"},
                                            'image_type': ImageType.BIOMED},
                                output_table_parms={'replace': True})

        image_array = image.fetch_image_array()

        self.assertTrue(np.array_equal(image_array, np.array(
            [[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

    def test_fetch_geometry_info_no_geometry(self):
        # Load the image
        image = ImageTable.load(self.s, path='biomedimg/simple.png',
                                load_parms={'caslib': 'dlib', 'decode': True,
                                            'image_type': ImageType.BIOMED},
                                output_table_parms={'replace': True})

        self.assertTrue(image.fetch_geometry_info() == ((), (), ()))

    def test_fetch_geometry_info(self):
        # Load an image with geometry data
        imgray = ImageTable.load(self.s, path='biomedimg/simple.png',
                                 load_parms={'caslib': 'dlib', 'decode': True,
                                             'addColumns': {'position', 'orientation', 'spacing'},
                                             'image_type': ImageType.BIOMED},
                                 output_table_parms={'replace': True})

        self.assertTrue(imgray.fetch_geometry_info() == ((0, 0), (1.0, 0.0, 0.0, 1.0), (1.0, 1.0)))

    # Load a biomed image and quantify sphericity use default input background, use spacing,
    # and FACE for label connectivity.
    def test_quantify_sphericity_from_casTable(self):
        # Load the input image
        input = ImageTable.load(self.s, path='biomedimg/Prostate3T-01-0001.nii',
                                load_parms={'caslib': 'dlib', 'decode': True})

        # Compute the sphericity
        output = input.sphericity(use_spacing=True, input_background=0, label_connectivity=LabelConnectivity.FACE,
                                  output_table_parms={'replace': True})

        image_rows = output.fetch()['Fetch']

        # Assert the sphericity result
        self.assertTrue(output is not None)
        self.assertAlmostEqual(image_rows['SPHERICITY'][0], 0.5542345330101192)

    # Load a biomed image and quantify sphericity using custom input background of -20.
    def test_quantify_sphericity_from_casTable_custom_input_background(self):
        # Load the input image
        input = ImageTable.load(self.s, path='biomedimg/Prostate3T-01-0001.nii',
                                load_parms={'caslib': 'dlib', 'decode': True})

        # Compute the sphericity
        output = input.sphericity(use_spacing=True, input_background=20, label_connectivity=LabelConnectivity.FACE,
                                  output_table_parms={'replace': True})

        image_rows = output.fetch()['Fetch']

        # Assert the sphericity result
        self.assertTrue(output is not None)
        self.assertAlmostEqual(image_rows['SPHERICITY'][0], 0.31121426716017353)

    def test_morphological_gradient_3d_grayscale_image(self):
        # Load the input image
        input = ImageTable.load(self.s, path='TestMasking/simpleGray.nii', load_parms={'caslib': 'dlib'})

        # Compute Morphological Gradient
        output = input.morphological_gradient(output_table_parms={'replace': True})

        # Correct Image Array
        test_arr = np.array([[176, 57, 0, 104, 192],
                             [127, 0, 0, 131, 1],
                             [130, 127, 129, 0, 0],
                             [128, 128, 127, 2, 2],
                             [127, 131, 0, 0, 0]])

        # Export the biomedical image
        export_image = self.s.CASTable('export_image')
        self.s.biomedimage.processbiomedimages(
            images=dict(table={'name': output.table.to_table_name()}),
            steps=[
                dict(stepparameters=dict(steptype='export', encodetype='PNG'))
            ],
            decode=False,
            casout=export_image
        )

        # Create an array from the exported image
        export_img_arr = np.asarray(self.s.image.fetchImages(table='export_image').Images.Image[0])

        # Compare the arrays
        return np.array_equal(export_img_arr, test_arr)

    def test_morphological_gradient_2d_image(self):
        # Load the input image
        input = ImageTable.load(self.s, path='images/famous_selfie.jpg',
                                load_parms={'caslib': 'dlib', 'image_type': ImageType.BIOMED})

        # Compute Morphological Gradient
        output = input.morphological_gradient(output_table_parms={'replace': True})

        # Assert the output
        self.assertFalse(output.table)

    def test_morphological_gradient_invalid_parameters(self):
        # Load the input image
        input = ImageTable.load(self.s, path='TestMasking/simpleGray.nii', load_parms={'caslib': 'dlib'})

        # Compute Morphological Gradient
        output = input.morphological_gradient(kernel_width=11,
                                              kernel_height=13, copy_vars=['invalid', '_id_'],
                                              output_table_parms={'replace': True})

        # Assert the output
        self.assertTrue(output.table)

    def test_morphological_gradient_duplicate_copyvars(self):
        # Load the input image
        input = ImageTable.load(self.s, path='TestMasking/simpleGray.nii', load_parms={'caslib': 'dlib'})

        # Compute Morphological Gradient
        output = input.morphological_gradient(kernel_width=11, kernel_height=13,
                                              copy_vars=['_biomedid_', '_biomeddimension_', '_sliceindex_'],
                                              output_table_parms={'replace': True})

        # Assert the output
        self.assertTrue(output.table)

    def test_morphological_gradient_valid_copyvars(self):
        # Load the input image
        input = ImageTable.load(self.s, path='TestMasking/simpleGray.nii', load_parms={'caslib': 'dlib'})

        # Compute Morphological Gradient
        output = input.morphological_gradient(copy_vars=['_id_', '_path_'],
                                              output_table_parms={'replace': True})

        # Assert the output
        self.assertTrue(output.table)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestBiomedImage.DATAPATH = sys.argv.pop()
        TestBiomedImage.PASSWORD = sys.argv.pop()
        TestBiomedImage.USERNAME = sys.argv.pop()
        TestBiomedImage.CAS_PROTOCOL = sys.argv.pop()
        TestBiomedImage.CAS_PORT = sys.argv.pop()
        TestBiomedImage.CAS_HOST = sys.argv.pop()

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

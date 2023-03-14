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
from cvpy.image.NaturalImageTable import NaturalImageTable


def load(self, path):
    # Load the image
    image = self.s.CASTable('image', replace=True)
    self.s.image.loadImages(path=path,
                            casOut=dict(name='image', replace='TRUE'),
                            addColumns={"WIDTH", "HEIGHT"},
                            caslib='dlib',
                            decode=True)
    return image

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

    def test_mask_encoded_image_encoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_natural_image.png', casout=img, decode=False)
        self.s.image.processimages(
            table={'name': 'image'},
            casout={'name': 'image', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_32F'}}]
        )

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_mask_image.png', casout=smask, decode=False)
        self.s.image.processimages(
            table={'name': 'smask'},
            casout={'name': 'smask', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_32F'}}]
        )
        smask_table = ImageTable(smask)

        # Masking
        new_img = NaturalImageTable.mask_image(smask_table, decode=False)

        test_arr = np.asarray([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 64, 32, 0],
            [0, 0, 75, 210, 0]
        ])

        new_img_arr = np.asarray(new_img.Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))

    def test_mask_decoded_image_decoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_3x3.png", casout=img, decode=True)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_2_3x3.png", casout=smask, decode=True)
        smask_table = ImageTable(smask)

        # Masking
        new_img = NaturalImageTable.mask_image(smask_table, decode=False)

        test_arr = np.array(
            [[0, 0, 255],
             [0, 255, 255],
             [0, 128, 0]]
        )

        new_img_arr = np.asarray(new_img.Images.Image[0])
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

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path='TestMasking/simple_mask_image.png', casout=smask, decode=False)
        self.s.image.processimages(
            table={'name': 'smask'},
            casout={'name': 'smask', 'replace': True},
            steps=[{'step': {'stepType': 'RESCALE', 'type': 'TO_64F'}}]
        )
        smask_table = ImageTable(smask)

        # Masking
        new_img = NaturalImageTable.mask_image(smask_table, decode=False)

        test_arr = np.asarray([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 64, 32, 0],
            [0, 0, 75, 210, 0]
        ])

        new_img_arr = np.asarray(new_img.Images.Image[0])
        self.assertTrue(np.array_equal(new_img_arr, test_arr))

    def test_mask_encoded_image_decoded_mask(self):
        # Load the image
        img = self.s.CASTable('image', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_3x3.png", casout=img, decode=False)

        # Load the mask image
        smask = self.s.CASTable('smask', replace=True)
        self.s.image.loadimages(caslib='dlib', path="imagetypes/gray_2_3x3.png", casout=smask, decode=True)
        smask_table = ImageTable(smask)

        # Masking
        new_img = NaturalImageTable.mask_image(smask_table, decode=False)

        test_arr = np.array(
            [[0, 0, 255],
             [0, 255, 255],
             [0, 128, 0]]
        )

        new_img_arr = np.asarray(new_img.Images.Image[0])
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

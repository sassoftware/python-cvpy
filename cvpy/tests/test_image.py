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
import swat
import sys
import numpy as np
from cvpy.image import *

class TestImage(unittest.TestCase):

    def test_convert_to_CAS_column(self):
        self.assertTrue(convert_to_CAS_column("id") == "_id_")

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

        self.assertTrue(np.array_equal(fetch_image_array(image), np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

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

        medicalImageArray = get_image_array(medicalBinaries, medicalDimensions, medicalResolutions, medicalFormats, 0)
        self.assertTrue(np.array_equal(medicalImageArray, np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

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
        num_cells = np.prod(resolution)
        medicalImageArray = get_image_array_from_row(medicalBinaries[n], dimension, resolution, myformat, 1)

        self.assertTrue(np.array_equal(medicalImageArray, np.array([[0, 0, 0, 0, 0], [0, 255, 0, 0, 0], [0, 255, 0, 150, 0], [0, 0, 0, 0, 50], [0, 0, 0, 0, 0]])))

    def test_fetch_geometry_info(self):
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

        # Load an image with geometry data
        imgray = self.s.CASTable("imgray", replace=True)
        self.s.image.loadimages(
            path="dicomdata/ExpertSegScans/CAESAR007/1",
            recurse=True,
            casout=imgray,
            decode=True,
            caslib="dlib",
            addcolumns={"position", "orientation", "spacing"},
        )

        self.assertTrue(fetch_geometry_info(imgray) == ((-173.63671875, -290.63671875, -775.5), (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),(0.7265625, 0.7265625, 3.0)))

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

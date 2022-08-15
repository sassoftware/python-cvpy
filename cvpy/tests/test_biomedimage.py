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
import sys
import unittest

import xmlrunner
from swat import CAS, CASTable

from cvpy.base.ImageTable import ImageTable

from cvpy.biomedimage.LabelConnectivity import LabelConnectivity
from cvpy.biomedimage.BiomedImage import BiomedImage


class TestBiomedImage(unittest.TestCase):
    CAS_HOST = None
    CAS_PORT = None
    USERNAME = None
    PASSWORD = None
    DATAPATH = None

    def setUp(self) -> None:
        ## Set up CAS connection
        self.s = CAS(TestBiomedImage.CAS_HOST, TestBiomedImage.CAS_PORT, TestBiomedImage.USERNAME,
                     TestBiomedImage.PASSWORD)
        self.s.loadactionset("image")
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=TestBiomedImage.DATAPATH, dataSource='PATH',
                         subdirectories=True)
    
    def tearDown(self) -> None:
        self.s.close()
    
    # Load a biomed image and quantify sphericity use default input background, use spacing, and FACE for label connectivity.
    def test_quantify_sphericity_from_casTable(self):

        # Load the input image
        input = self.s.CASTable('input')
        self.s.image.loadimages(casout = input,
                                path = 'biomedimg/Prostate3T-01-0001.nii',
                                caslib = 'dlib',
                                decode = True)

        input_table = ImageTable(input)

        # Construct Biomed object
        biomed = BiomedImage(cas_session=self.s)

        # Compute the sphericity
        output_sph = self.s.CASTable('output_sph')
        biomed.quantify_sphericity(image_table = input_table, 
                                   use_spacing = True, 
                                   input_background = 0,  
                                   label_connectivity = LabelConnectivity.FACE,
                                   sphericity = output_sph)

        imageRows = self.s.fetch(table='output_sph')['Fetch']
        
        ## Assert the sphericity result
        self.assertTrue(output_sph is not None)
        self.assertEqual(imageRows['SPHERICITY'][0], 0.5542345330101192)
    
    # Load a biomed image and quantify sphericity using custom input background of -20. 
    def test_quantify_sphericity_from_casTable_custom_input_background(self):

        # Load the input image
        input = self.s.CASTable('input')
        self.s.image.loadimages(casout = input,
                                path = 'biomedimg/Prostate3T-01-0001.nii',
                                caslib = 'dlib',
                                decode = True)

        input_table = ImageTable(input)

        # Construct Biomed object
        biomed = BiomedImage(cas_session=self.s)

        # Compute the sphericity
        output_sph = self.s.CASTable('output_sph')
        biomed.quantify_sphericity(image_table = input_table, 
                                   use_spacing = True, 
                                   input_background = -20,  
                                   label_connectivity = LabelConnectivity.FACE,
                                   sphericity = output_sph)

        imageRows = self.s.fetch(table='output_sph')['Fetch']
        
        ## Assert the sphericity result
        self.assertTrue(output_sph is not None)
        self.assertEqual(imageRows['SPHERICITY'][0], 0.31121426716017353)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestBiomedImage.DATAPATH = sys.argv.pop()
        TestBiomedImage.PASSWORD = sys.argv.pop()
        TestBiomedImage.USERNAME = sys.argv.pop()
        TestBiomedImage.CAS_PORT = sys.argv.pop()
        TestBiomedImage.CAS_HOST = sys.argv.pop()

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

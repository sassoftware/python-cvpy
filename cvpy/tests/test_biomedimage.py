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
from cvpy.biomedimage.BiomedImage import BiomedImage
# from cvpy.biomedimage.LabelConnectivity import LabelConnectivity

class TestBiomedimage(unittest.TestCase):

    def setUp(self):
        ## Set up CAS connection
        self.s = swat.CAS(self.casHost, self.casPort, self.username, self.password)
        self.s.loadactionset("image")
        
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=self.dataPath, dataSource='PATH', subdirectories=True)

    def test_quantify_sphericity_from_casTable(self):

        # Load the input image
        input = self.s.CASTable('input', replace=True)
        self.s.image.loadimages(casout=dict(name='input', replace='TRUE'),
                                path = 'biomedimg/Prostate3T-01-0001.nii',
                                caslib='dlib',
                                decode=True)
        ## Create the output table
        output_sph = self.s.CASTable('output_sph', replace=True)

        # Construct Biomed object
        biomed = BiomedImage(cas_session=self.s)

        # Compute the sphericity
        biomed.quantify_sphericity(image_table = input, 
                                   use_spacing = True, 
                                   input_background = 0, 
                                   label_connectivity = 'FACE', 
                                #    label_connectivity = LabelConnectivity.FACE, 
                                   sphericity= output_sph)

        self.assertTrue(output_sph is not None)


if __name__ == '__main__':
    if len(sys.argv) > 1:

        TestBiomedimage.dataPath = sys.argv.pop()
        TestBiomedimage.password = sys.argv.pop()
        TestBiomedimage.username = sys.argv.pop()
        TestBiomedimage.casPort = sys.argv.pop()
        TestBiomedimage.casHost = sys.argv.pop()

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )
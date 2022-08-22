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

import xmlrunner
from swat import CAS

from cvpy.base.ImageTable import ImageTable
from cvpy.tests.casutils import assert_contains_message


class TestImageTable(unittest.TestCase):
    CAS_HOST = None
    CAS_PORT = None
    USERNAME = None
    PASSWORD = None
    DATAPATH = None

    def setUp(self) -> None:
        self.s = CAS(TestImageTable.CAS_HOST, TestImageTable.CAS_PORT, TestImageTable.USERNAME,
                     TestImageTable.PASSWORD)
        self.s.loadactionset('image')
        self.s.addcaslib(name='dlib', activeOnAdd=False, path=TestImageTable.DATAPATH, dataSource='PATH',
                         subdirectories=True)

    def tearDown(self) -> None:
        self.s.close()

    # Create an imagetable object with default column names
    def test_imagetable_constructor_default_columns(self):
        # Load the images in a CAS Table
        cdata_decoded = self.s.CASTable('cdata_decoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_decoded,
                                caslib='dlib',
                                decode=True)

        image_table = ImageTable(cdata_decoded)
        self.assertEqual(image_table.table, cdata_decoded)
        self.assertEqual(image_table.image, '_image_')
        self.assertEqual(image_table.dimension, '_dimension_')
        self.assertEqual(image_table.resolution, '_resolution_')
        self.assertEqual(image_table.imageFormat, '_imageFormat_')
        self.assertEqual(image_table.path, '_path_')
        self.assertEqual(image_table.label, '_label_')
        self.assertEqual(image_table.id, '_id_')
        self.assertEqual(image_table.size, '_size_')
        self.assertEqual(image_table.type, '_type_')

    # Create an imagetable object with custom column names
    def test_imagetable_constructor_custom_columns(self):
        cdata_decoded = self.s.CASTable('cdata_decoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_decoded,
                                caslib='dlib',
                                decode=True)

        column_rename = []
        for col in ['_image_', '_dimension_', '_resolution_', '_imageFormat_',
                    '_path_', '_label_', '_id_', '_size_', '_type_']:
            column_rename.append(dict(name=col, rename=f'new{col}'))

        self.s.table.altertable(name=cdata_decoded.name, columns=column_rename)

        image_table = ImageTable(cdata_decoded, image='new_image_', dimension='new_dimension_',
                                 resolution='new_resolution_', imageFormat='new_imageFormat_', path='new_path_',
                                 label='new_label_', id='new_id_', size='new_size_', type='new_type_')
        self.assertEqual(image_table.table, cdata_decoded)
        self.assertEqual(image_table.image, 'new_image_')
        self.assertEqual(image_table.dimension, 'new_dimension_')
        self.assertEqual(image_table.resolution, 'new_resolution_')
        self.assertEqual(image_table.imageFormat, 'new_imageFormat_')
        self.assertEqual(image_table.path, 'new_path_')
        self.assertEqual(image_table.label, 'new_label_')
        self.assertEqual(image_table.id, 'new_id_')
        self.assertEqual(image_table.size, 'new_size_')
        self.assertEqual(image_table.type, 'new_type_')

    # Create imagetable object with a CAS table containing decoded images and call has_decoded_images
    def test_imagetable_decoded(self):
        cdata_decoded = self.s.CASTable('cdata_decoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_decoded,
                                caslib='dlib',
                                decode=True)

        image_table = ImageTable(cdata_decoded)
        self.assertTrue(image_table.has_decoded_images())

    # Create imagetable object with a CAS table containing encoded images and call has_decoded_images
    def test_imagetable_encoded(self):
        cdata_encoded = self.s.CASTable('cdata_encoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_encoded,
                                caslib='dlib',
                                decode=False)

        image_table = ImageTable(cdata_encoded)
        self.assertFalse(image_table.has_decoded_images())

    # Call processImages action using imagetable.as_dict() function
    def test_imagetable_with_process_images(self):
        cdata_encoded = self.s.CASTable('cdata_encoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_encoded,
                                caslib='dlib',
                                decode=False)

        image_table = ImageTable(cdata_encoded)

        ptable = self.s.CASTable('process_images', replace=True)
        r = self.s.image.processimages(
            images=image_table.as_dict(),
            casout=ptable,
            imageFunctions=[
                {'functionoptions': {'width': 200, 'height': 200, 'functiontype': 'RESIZE'}}
            ]
        )

        assert_contains_message(r, '5 of 5 images were processed successfully')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestImageTable.CAS_HOST = sys.argv.pop(1)
        TestImageTable.CAS_PORT = sys.argv.pop(1)
        TestImageTable.USERNAME = sys.argv.pop(1)
        TestImageTable.PASSWORD = sys.argv.pop(1)
        TestImageTable.DATAPATH = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

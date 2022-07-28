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

import unittest

import xmlrunner
from swat.cas import CASTable

from cvpy.base.ImageTable import ImageTable


class TestImageTable(unittest.TestCase):

    # Create an imagetable object with all default column names
    def test_imagetable_constructor(self):
        cas_table = CASTable(name="test")
        image_table = ImageTable(cas_table)
        self.assertEqual(image_table.table, cas_table)

        self.assertEqual(image_table.image, 'image')
        self.assertEqual(image_table.dimension, 'dimension')
        self.assertEqual(image_table.resolution, 'resolution')
        self.assertEqual(image_table.imageFormat, 'imageFormat')
        self.assertEqual(image_table.path, '_path_')
        self.assertEqual(image_table.label, '_label_')
        self.assertEqual(image_table.id, '_id_')
        self.assertEqual(image_table.size, '_size_')
        self.assertEqual(image_table.type, '_type_')


if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

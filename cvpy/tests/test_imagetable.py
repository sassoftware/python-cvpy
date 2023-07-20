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
from cvpy.biomedimage.BiomedImageTable import BiomedImageTable
from cvpy.image.NaturalImageTable import NaturalImageTable
from cvpy.tests.casutils import assert_contains_message


class TestImageTable(unittest.TestCase):
    CAS_HOST = None
    CAS_PORT = None
    USERNAME = None
    PASSWORD = None
    PROTOCOL = None
    DATAPATH = None

    def setUp(self) -> None:
        self.s = CAS(TestImageTable.CAS_HOST, TestImageTable.CAS_PORT, TestImageTable.USERNAME,
                     TestImageTable.PASSWORD, protocol=TestImageTable.PROTOCOL)
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

    # Validate imagetable column names and datatypes
    def _test_imagetable_column_validations(self):
        cdata_decoded = self.s.CASTable('cdata_decoded')
        self.s.image.loadimages(path='images',
                                labellevels=5,
                                casout=cdata_decoded,
                                caslib='dlib',
                                decode=True)

        self.s.loadactionset('fedsql')
        test_image_table = self.s.CASTable('test_image_table')

        col_value = [123, 'abc', 123, 'abc', 123, 123, 'abc', 'abc', 123]
        col_name = ['image', 'dimension', 'resolution', 'imageFormat', 'path', 'label', 'id', 'size', 'type']
        col_dtype = [None, ImageTable.INT64_TYPE, ImageTable.VARBINARY_TYPE, ImageTable.INT64_TYPE,
                     ImageTable.VARCHAR_TYPE,
                     ImageTable.VARCHAR_TYPE, ImageTable.INT64_TYPE, ImageTable.INT64_TYPE, ImageTable.CHAR_TYPE]

        for a_col_name, a_col_value, a_col_dtype in zip(col_name, col_value, col_dtype):

            # Check column-exists validation
            try:
                parms = {'table': cdata_decoded, a_col_name: 'test'}
                ImageTable(**parms)
            except Exception as e:
                assert str(e) == 'Column test is not present in the table.'

            # Check column data-type validation
            if a_col_name == 'image':
                invalid_dtype_msg = 'Column test_image has an unsupported data type. ' \
                                    'The supported datatypes for this column are: (varbinary(image), varchar).'
            else:
                invalid_dtype_msg = f'Column test_{a_col_name} has an unsupported data type. ' \
                                    f'The supported datatype for this column is: {a_col_dtype}.'

            parms = {'table': test_image_table, a_col_name: f'test_{a_col_name}'}

            try:
                if type(a_col_value) == str:
                    query = f'''
                        create table test_image_table {{options replace=True}} as 
                        select *, '{a_col_value}' as "test_{a_col_name}" from cdata_decoded
                    '''
                else:
                    query = f'''
                        create table test_image_table {{options replace=True}} as 
                        select *, {a_col_value} as "test_{a_col_name}" from cdata_decoded
                    '''
                self.s.fedsql.execdirect(query)
                ImageTable(**parms)
            except Exception as e:
                assert str(e) == invalid_dtype_msg

    #
    def test_imagetable_load_natural_images(self):
        load_parms = {'caslib': 'dlib'}
        image_table = ImageTable.load(self.s, path='images', load_parms=load_parms)
        assert type(image_table) == NaturalImageTable

    # Create imagetable by loading natural images from a path with output table parms
    def test_imagetable_load_natural_images_output_table_parms(self):
        load_parms = {'caslib': 'dlib'}

        cas_table_name = 'imgs'
        output_table_parms = {'name': cas_table_name, 'caslib': 'dlib', 'replace': True}
        image_table = ImageTable.load(self.s, path='images', load_parms=load_parms,
                                      output_table_parms=output_table_parms)
        assert image_table.table.name == cas_table_name
        assert image_table.table.caslib == 'dlib'
        assert type(image_table) == NaturalImageTable

    # Create imagetable by loading biomed images from a path
    def test_imagetable_load_biomed_images(self):
        load_parms = {'caslib': 'dlib'}
        image_table = ImageTable.load(self.s, path='biomedimg', load_parms=load_parms)
        assert type(image_table) == BiomedImageTable

    # Create imagetable by loading natural images from a path with output table parms
    def test_imagetable_load_biomed_images_output_table_parms(self):
        load_parms = {'caslib': 'dlib'}

        cas_table_name = 'imgs'
        output_table_parms = {'name': cas_table_name, 'caslib': 'dlib', 'replace': True}
        image_table = ImageTable.load(self.s, path='biomedimg', load_parms=load_parms,
                                      output_table_parms=output_table_parms)
        assert image_table.table.name == cas_table_name
        assert image_table.table.caslib == 'dlib'
        assert type(image_table) == BiomedImageTable

    def test_imagetable_from_table_natural_images(self):
        cas_table = self.s.CASTable('imgs')

        self.s.image.loadimages(path='images', labellevels=5, casout=cas_table, caslib='dlib', decode=False)

        image_table = ImageTable.from_table(cas_table)

        assert image_table.table.name == cas_table.name
        assert type(image_table) == NaturalImageTable

    def test_imagetable_from_table_biomed_images(self):
        cas_table = self.s.CASTable('imgs')

        self.s.image.loadimages(path='biomedimg', labellevels=5, casout=cas_table, caslib='dlib', decode=False)

        image_table = ImageTable.from_table(cas_table)

        assert image_table.table.name == cas_table.name
        assert type(image_table) == BiomedImageTable

    def test_imagetable_from_table_custom_col_names(self):
        cas_table = self.s.CASTable('imgs')

        self.s.image.loadimages(path='images', labellevels=5, casout=cas_table, caslib='dlib', decode=False)

        self.s.altertable(name=cas_table, columns=[dict(name='_image_', rename='image_new'),
                                                   dict(name='_size_', rename='size_new'),
                                                   dict(name='_path_', rename='path_new')])

        image_table = ImageTable.from_table(cas_table, image='image_new', size='size_new', path='path_new')

        assert image_table.table.name == cas_table.name
        assert type(image_table) == NaturalImageTable

    # Load client images and server images using load_client_images and loadImages and compare results
    def test_imagetable_load_client_images(self):
        # Path to the directory the function will load images from
        path = f"{TestImageTable.DATAPATH}images/"

        # Test loading images fron both client and server and ensure images match
        ImageTable.load_client_images(
            output_table_parms={'name': 'imgsClient', 'caslib': 'CASUSER(user)'},
            data=path,
            connection=self.s,
            subdirs=False
        )
        self.s.CASTable('imgsServer', replace=True)
        self.s.image.loadimages(
            path="images/",
            caslib="dlib",
            casout={'name' : 'imgsServer'}
        )

        # Check if the images from both tables match
        result = self.s.image.compareImages(
            casout={'name': 'compare', 'replace': True},
            sourceImages={'table': 'imgsClient'},
            referenceImages={'table': 'imgsServer'},
            paironpath=False
        )

        assert result.pop('OutputCasTables')['Rows'][0] == 5
    
    def test_imagetable_load_client_images_nonexistent_path(self):
        # Attempt to load images from a nonexistent path
        ImageTable.load_client_images(
            output_table_parms={'name': 'imgsClientNonexistent', 'caslib': 'CASUSER(user)'},
            data='path/does/not/exist',
            connection=self.s,
            subdirs=False
        )

        # Assert that the tables created are empty
        assert len(self.s.fetchimages('imgsClientNonexistent').Images.Image) == 0
    
    def test_imagetable_load_client_images_empty_path(self):
        # Attempt to load images from an empty path
        ImageTable.load_client_images(
            output_table_parms={'name': 'imgsClientEmpty', 'caslib': 'CASUSER(user)'},
            data='',
            connection=self.s,
            subdirs=False
        )

        # Assert that the tables created are empty
        assert len(self.s.fetchimages('imgsClientEmpty').Images.Image) == 0
    
    def test_imagetable_load_client_images_output_biomed_image_table_type(self):
        # Path to the directory the function will load images from
        bioPath = f"{TestImageTable.DATAPATH}dicom/"
        
        # Load biomed images from the path
        biomed = ImageTable.load_client_images(
            output_table_parms={'name': 'biomedTable'},
            data=bioPath,
            connection=self.s,
            subdirs=False,
        )

        # Assert that each table is of the correct type
        assert isinstance(biomed, BiomedImageTable)

    def test_imagetable_load_client_images_output_natural_image_table_type(self):
        # Path to the directory the function will load images from
        natPath = f"{TestImageTable.DATAPATH}images/"

        # Load natural images from the path
        natural = ImageTable.load_client_images(
            output_table_parms={'name': 'imgsClient', 'caslib': 'CASUSER(user)'},
            data=natPath,
            connection=self.s,
            subdirs=False
        )

        # Assert that each table is of the correct type
        assert isinstance(natural, NaturalImageTable)
    
    def test_imagetable_load_client_images_nonexistent_caslib(self):
        ImageTable.load_client_images(
            output_table_parms={'name': 'libNonexistent', 'caslib': 'doesNotExist'},
            data='',
            connection=self.s,
            subdirs=False
        )

        assert len(self.s.tableinfo(caslib='CASUSER').pop('TableInfo')['Name']) == 1
    
    def test_imagetable_load_client_images_empty_caslib(self):
        ImageTable.load_client_images(
            output_table_parms={'name': 'libEmpty', 'caslib': ''},
            data='',
            connection=self.s,
            subdirs=False
        )

        assert len(self.s.tableinfo(caslib='CASUSER').pop('TableInfo')['Name']) == 1

    def test_imagetable_load_client_images_none_type_caslib(self):
        ImageTable.load_client_images(
            output_table_parms={'name': 'libNone', 'caslib': None},
            data='',
            connection=self.s,
            subdirs=False
        )
        
        assert len(self.s.tableinfo(caslib='CASUSER').pop('TableInfo')['Name']) == 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestImageTable.CAS_HOST = sys.argv.pop(1)
        TestImageTable.CAS_PORT = sys.argv.pop(1)
        TestImageTable.USERNAME = sys.argv.pop(1)
        TestImageTable.PASSWORD = sys.argv.pop(1)
        TestImageTable.PROTOCOL = sys.argv.pop(1)
        TestImageTable.DATAPATH = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

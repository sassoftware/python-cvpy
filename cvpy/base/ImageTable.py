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
from swat import CASTable


class ImageTable(object):
    '''
    Interface with a CASTable of images.

    table:
        Specifies the input table that contains image data.
    image:
        Specifies the name of the column that contains image binaries.
    dimension:
        Specifies the name of the column that contains dimensions of images.
    resolution:
        Specifies the name of the column that contains resolutions of images.
    imageFormat:
        Specifies the name of the column that contains formats of image binaries.
    path:
        Specifies the name of the column that contains file paths.
    label:
        Specifies the name of the column that contains labels of images.
    id:
        Specifies the name of the variable that identifies each image.
    size:
        Specifies the name of the column that contains byte lengths of image binaries.
    type:
        Specifies the name of the column that contains the image type.
    '''

    IMAGE_COL = '_image_'
    DIMENSION_COL = '_dimension_'
    RESOLUTION_COL = '_resolution_'
    FORMAT_COL = '_imageFormat_'
    PATH_COL = '_path_'
    LABEL_COL = '_label_'
    ID_COL = '_id_'
    SIZE_COL = '_size_'
    TYPE_COL = '_type_'

    VARBINARY_TYPE = 'varbinary'
    VARBINARY_IMAGE_TYPE = 'varbinary(image)'
    VARCHAR_TYPE = 'varchar'
    INT64_TYPE = 'int64'
    CHAR_TYPE = 'char'

    def __init__(self, table: CASTable, image: str = None, dimension: str = None, resolution: str = None,
                 imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
                 type: str = None):

        # Add _table attribute and set the table property
        self._table = None
        self.table = table

        # Add an attribute for each column and then set the corresponding property
        self._image = None
        self.image = image

        self._dimension = None
        self.dimension = dimension

        self._resolution = None
        self.resolution = resolution

        self._imageFormat = None
        self.imageFormat = imageFormat

        self._path = None
        self.path = path

        self._label = None
        self.label = label

        self._id = None
        self.id = id

        self._size = None
        self.size = size

        self._type = None
        self.type = type

    # Function to validate and set column attribute on ImageTable
    def validate_set_column(self, column, column_name, default_column_name, valid_column_datatypes):

        if self.table is None:
            # No validations are possible if table is not set
            if column_name:
                # Set the column attribute to user specified column_name
                setattr(self, f'_{column}', column_name)
            else:
                # Set the column attribute to default_column_name
                setattr(self, f'_{column}', default_column_name)
            return

        # Validate presence of the column and its datatype
        if column_name:
            # Check if column is present in the table
            if column_name.lower() not in self._column_dtype_lookup.keys():
                raise Exception(f'Column {column_name} is not present in the table.')
        else:
            # Check if default column name is present in the table
            if default_column_name.lower() in self._column_dtype_lookup.keys():
                column_name = default_column_name

        setattr(self, f'_{column}', column_name)

        # Data type validation
        if column_name and self._column_dtype_lookup.get(column_name.lower()) not in valid_column_datatypes:
            if len(valid_column_datatypes) == 1:
                message = f'Column {column_name} has an unsupported data type. ' \
                          f'The supported datatype for this column is: {valid_column_datatypes[0]}.'
            else:
                message = f'Column {column_name} has an unsupported data type. ' \
                          f'The supported datatypes for this column are: ({", ".join(valid_column_datatypes)}).'

            raise Exception(message)

    @property
    def table(self) -> CASTable:
        return self._table

    @table.setter
    def table(self, table) -> None:
        self._column_dtype_lookup = None
        if table is not None:
            self._column_dtype_lookup = \
                table.columninfo()['ColumnInfo'][['Column', 'Type']].set_index('Column').to_dict()['Type']
            # Lowercase keys in _column_dtype_lookup
            self._column_dtype_lookup = {k.lower(): v.lower() for k, v in self._column_dtype_lookup.items()}
        self._table = table

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, image) -> None:
        self.validate_set_column('image', image, ImageTable.IMAGE_COL,
                                 [ImageTable.VARBINARY_IMAGE_TYPE, ImageTable.VARCHAR_TYPE])

    @property
    def dimension(self) -> str:
        return self._dimension

    @dimension.setter
    def dimension(self, dimension) -> None:
        self.validate_set_column('dimension', dimension, ImageTable.DIMENSION_COL, [ImageTable.INT64_TYPE])

    @property
    def resolution(self) -> str:
        return self._resolution

    @resolution.setter
    def resolution(self, resolution) -> None:
        self.validate_set_column('resolution', resolution, ImageTable.RESOLUTION_COL, [ImageTable.VARBINARY_TYPE])

    @property
    def imageFormat(self) -> str:
        return self._imageFormat

    @imageFormat.setter
    def imageFormat(self, imageFormat) -> None:
        self.validate_set_column('imageFormat', imageFormat, ImageTable.FORMAT_COL, [ImageTable.INT64_TYPE])

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path) -> None:
        self.validate_set_column('path', path, ImageTable.PATH_COL, [ImageTable.VARCHAR_TYPE])

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label) -> None:
        self.validate_set_column('label', label, ImageTable.LABEL_COL, [ImageTable.VARCHAR_TYPE])

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id) -> None:
        self.validate_set_column('id', id, ImageTable.ID_COL, [ImageTable.INT64_TYPE])

    @property
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, size) -> None:
        self.validate_set_column('size', size, ImageTable.SIZE_COL, [ImageTable.INT64_TYPE])

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type) -> None:
        self.validate_set_column('type', type, ImageTable.TYPE_COL, [ImageTable.CHAR_TYPE])

    def as_dict(self) -> dict:
        '''
        Create a dictionary representation of this object.

        Returns
        -------
        d: :class:`dict`
            Contains all of the properties as keys and the property values as values
        '''
        d = {}
        for k, v in vars(self).items():
            if k != '_column_dtype_lookup':
                d[k[1:]] = v
        return d

    def has_decoded_images(self) -> bool:
        '''
        Check if this table contains decoded images or encoded images.

        Returns
        -------
        b: :class:`bool`:
            Returns True if the table contains decoded images. Otherwise, returns False.
        '''
        return (self.dimension is not None) and (self.resolution is not None) and (self.imageFormat is not None)

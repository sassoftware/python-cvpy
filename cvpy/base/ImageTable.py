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
        self._table = table

        # Get the column data types
        column_dtype_lookup = dict()
        if table:
            column_dtype_lookup = \
                table.columninfo()['ColumnInfo'][['Column', 'Type']].set_index('Column').to_dict()['Type']

        # Set various columns if specified, or set them to their default values
        # Verify the columns have supported data types
        self._image = None
        if image:
            self._image = image
            if table and self._image not in table.columns:
                raise Exception(f'Column {self._image} is not present in the table.')
        elif table and ImageTable.IMAGE_COL in table.columns:
            self._image = ImageTable.IMAGE_COL

        if self._image and table:
            if column_dtype_lookup[self._image].lower() not in (ImageTable.VARBINARY_IMAGE_TYPE,
                                                                ImageTable.VARCHAR_TYPE):
                raise Exception(f'Column {self._image} has an unsupported data type. '
                                f'The supported datatypes for this column are: ({ImageTable.VARBINARY_IMAGE_TYPE}, '
                                f'{ImageTable.VARCHAR_TYPE})')

        self._dimension = None
        if dimension:
            self._dimension = dimension
            if table and self._dimension not in table.columns:
                raise Exception(f'Column {self._dimension} is not present in the table.')
        elif table and ImageTable.DIMENSION_COL in table.columns:
            self._dimension = ImageTable.DIMENSION_COL

        if self._dimension and table:
            if column_dtype_lookup[self._dimension].lower() != ImageTable.INT64_TYPE:
                raise Exception(f'Column {self._dimension} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.INT64_TYPE}.')

        self._resolution = None
        if resolution:
            self._resolution = resolution
            if table and self._resolution not in table.columns:
                raise Exception(f'Column {self._resolution} is not present in the table.')
        elif table and ImageTable.RESOLUTION_COL in table.columns:
            self._resolution = ImageTable.RESOLUTION_COL

        if self._resolution and table:
            if column_dtype_lookup[self._resolution].lower() != ImageTable.VARBINARY_TYPE:
                raise Exception(f'Column {self._resolution} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.VARBINARY_TYPE}.')

        self._imageFormat = None
        if imageFormat:
            self._imageFormat = imageFormat
            if table and self._imageFormat not in table.columns:
                raise Exception(f'Column {self._imageFormat} is not present in the table.')
        elif table and ImageTable.FORMAT_COL in table.columns:
            self._imageFormat = ImageTable.FORMAT_COL

        if self._imageFormat and table:
            if column_dtype_lookup[self._imageFormat].lower() != ImageTable.INT64_TYPE:
                raise Exception(f'Column {self._imageFormat} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.INT64_TYPE}.')

        self._path = None
        if path:
            self._path = path
            if table and self._path not in table.columns:
                raise Exception(f'Column {self._path} is not present in the table.')
        elif table and ImageTable.PATH_COL in table.columns:
            self._path = ImageTable.PATH_COL

        if self._path and table:
            if column_dtype_lookup[self._path].lower() != ImageTable.VARCHAR_TYPE:
                raise Exception(f'Column {self._path} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.VARCHAR_TYPE}.')

        self._label = None
        if label:
            self._label = label
            if table and self._label not in table.columns:
                raise Exception(f'Column {self._label} is not present in the table.')
        elif table and ImageTable.LABEL_COL in table.columns:
            self._label = ImageTable.LABEL_COL

        if self._label and table:
            if column_dtype_lookup[self._label].lower() != ImageTable.VARCHAR_TYPE:
                raise Exception(f'Column {self._label} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.VARCHAR_TYPE}.')

        self._id = None
        if id:
            self._id = id
            if table and self._id not in table.columns:
                raise Exception(f'Column {self._id} is not present in the table.')
        elif table and ImageTable.ID_COL in table.columns:
            self._id = ImageTable.ID_COL

        if self._id and table:
            if column_dtype_lookup[self._id].lower() != ImageTable.INT64_TYPE:
                raise Exception(f'Column {self._id} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.INT64_TYPE}.')

        self._size = None
        if size:
            self._size = size
            if table and self._size not in table.columns:
                raise Exception(f'Column {self._size} is not present in the table.')
        elif table and ImageTable.SIZE_COL in table.columns:
            self._size = ImageTable.SIZE_COL

        if self._size and table:
            if column_dtype_lookup[self._size].lower() != ImageTable.INT64_TYPE:
                raise Exception(f'Column {self._size} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.INT64_TYPE}.')

        self._type = None
        if type:
            self._type = type
            if table and self._type not in table.columns:
                raise Exception(f'Column {self._type} is not present in the table.')
        elif table and ImageTable.TYPE_COL in table.columns:
            self._type = ImageTable.TYPE_COL

        if self._type and table:
            if column_dtype_lookup[self._type].lower() != ImageTable.CHAR_TYPE:
                raise Exception(f'Column {self._type} has an unsupported data type. '
                                f'The supported datatype for this column is: {ImageTable.CHAR_TYPE}.')

    @property
    def table(self) -> CASTable:
        return self._table

    @table.setter
    def table(self, table) -> None:
        self._table = table

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, image) -> None:
        if image not in self.table.columns:
            raise Exception(f'Column "{image}" is not present in the table.')
        self._image = image

    @property
    def dimension(self) -> str:
        return self._dimension

    @dimension.setter
    def dimension(self, dimension) -> None:
        if dimension not in self.table.columns:
            raise Exception(f'Column "{dimension}" is not present in the table.')
        self._dimension = dimension

    @property
    def resolution(self) -> str:
        return self._resolution

    @resolution.setter
    def resolution(self, resolution) -> None:
        if resolution not in self.table.columns:
            raise Exception(f'Column "{resolution}" is not present in the table.')
        self._resolution = resolution

    @property
    def imageFormat(self) -> str:
        return self._imageFormat

    @imageFormat.setter
    def imageFormat(self, imageFormat) -> None:
        if imageFormat not in self.table.columns:
            raise Exception(f'Column "{imageFormat}" is not present in the table.')
        self._imageFormat = imageFormat

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path) -> None:
        if path not in self.table.columns:
            raise Exception(f'Column "{path}" is not present in the table.')
        self._path = path

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label) -> None:
        if label not in self.table.columns:
            raise Exception(f'Column "{label}" is not present in the table.')
        self._label = label

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id) -> None:
        if id not in self.table.columns:
            raise Exception(f'Column "{id}" is not present in the table.')
        self._id = id

    @property
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, size) -> None:
        if size not in self.table.columns:
            raise Exception(f'Column "{size}" is not present in the table.')
        self._size = size

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type) -> None:
        if type not in self.table.columns:
            raise Exception(f'Column "{type}" is not present in the table.')
        self._type = type

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

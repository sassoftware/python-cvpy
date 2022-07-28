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
    A class for the images table.
    '''

    def __init__(self, table: CASTable, image: str = 'image', dimension: str = 'dimension',
                 resolution: str = 'resolution', imageFormat: str = 'imageFormat', path: str = '_path_',
                 label: str = '_label_', id: str = '_id_', size: str = '_size_', type: str = '_type_'):
        '''

        :param table: specifies the input table that contains image data.
        :param image: specifies the name of the column that contains image binaries.
        :param dimension: specifies the name of the column that contains dimensions of images.
        :param resolution: specifies the name of the column that contains resolutions of images.
        :param imageFormat: specifies the name of the column that contains formats of image binaries.
        :param path: specifies the name of the column that contains file paths.
        :param label: specifies the name of the column that contains labels of images.
        :param id: specifies the name of the variable that identifies each image.
        :param size: specifies the name of the column that contains byte lengths of image binaries.
        :param type: specifies the name of the column that contains the image type.
        '''
        self._table = table
        self._image = image
        self._dimension = dimension
        self._resolution = resolution
        self._imageFormat = imageFormat
        self._path = path
        self._label = label
        self._id = id
        self._size = size
        self._type = type

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
        self._image = image

    @property
    def dimension(self) -> str:
        return self._dimension

    @dimension.setter
    def dimension(self, dimension) -> None:
        self._dimension = dimension

    @property
    def resolution(self) -> str:
        return self._resolution

    @resolution.setter
    def resolution(self, resolution) -> None:
        self._resolution = resolution

    @property
    def imageFormat(self) -> str:
        return self._imageFormat

    @imageFormat.setter
    def imageFormat(self, imageFormat) -> None:
        self._imageFormat = imageFormat

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path) -> None:
        self._path = path

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label) -> None:
        self._label = label

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id) -> None:
        self._id = id

    @property
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, size) -> None:
        self._size = size

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type) -> None:
        self._type = type

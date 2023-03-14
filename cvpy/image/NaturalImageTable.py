from typing import List, Dict

from swat import CASTable

from cvpy.base.ImageTable import ImageTable


class NaturalImageTable(ImageTable):

    def __init__(self, table: CASTable = None, image: str = None, dimension: str = None, resolution: str = None,
                 imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
                 type: str = None) -> None:
        super().__init__(table=table, image=image, dimension=dimension, resolution=resolution, imageFormat=imageFormat,
                         path=path, label=label, id=id, size=size, type=type)
        ## Load the actionsets
        self.connection.loadactionset('image')
        self.connection.loadactionset('fedsql')

    def mask(self, mask: ImageTable, decode: bool = False, add_columns: List[str] = None, copy_vars: List[str] = None,
             output_table_parms: Dict[str, str] = None) -> ImageTable:
        pass

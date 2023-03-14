from typing import Dict, List

from swat import CASTable

from cvpy.base.ImageTable import ImageTable
from cvpy.biomedimage.LabelConnectivity import LabelConnectivity


class BiomedImageTable(ImageTable):

    def __init__(self, table: CASTable = None, image: str = None, dimension: str = None, resolution: str = None,
                 imageFormat: str = None, path: str = None, label: str = None, id: str = None, size: str = None,
                 type: str = None) -> None:
        super().__init__(table=table, image=image, dimension=dimension, resolution=resolution, imageFormat=imageFormat,
                         path=path, label=label, id=id, size=size, type=type)
        ## Load the actionsets
        self.connection.loadactionset('image')
        self.connection.loadactionset('biomedimage')
        self.connection.loadactionset('fedsql')

    def sphericity(self, use_spacing: bool, input_background: float,
                   label_connectivity: LabelConnectivity, output_table_parms: Dict[str, str] = None) -> CASTable:
        pass

    def mask(self, mask: ImageTable, input_background: int = 0, output_background: int = 0, decode: bool = False,
             add_columns: List[str] = None, copy_vars: List[str] = None,
             output_table_parms: Dict[str, str] = None) -> ImageTable:
        pass

    def morphological_gradient(self, kernel_width: int = 3, kernel_height: int = 3, copy_vars: List[str] = None,
                               output_table_parms: Dict[str, str] = None) -> ImageTable:
        pass

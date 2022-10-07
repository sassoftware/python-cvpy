from cvpy.base.ImageTable import ImageTable
from cvpy.annotation.base.Project import Project


class Task(object):

    def __init__(self, image_table: ImageTable, project: Project) -> None:
        self._task_id = None
        self._project = project
        self._image_table = image_table
        self._start_image_id = 0
        self._end_image_id = image_table.table.tableinfo().TableInfo.Rows.values[0] - 1

    @property
    def task_id(self) -> str:
        return self._task_id

    @task_id.setter
    def task_id(self, task_id: str) -> None:
        self._task_id = task_id

    @property
    def start_image_id(self) -> str:
        return self._start_image_id

    @start_image_id.setter
    def start_image_id(self, start_image_id: str) -> None:
        self._start_image_id = start_image_id

    @property
    def end_image_id(self) -> str:
        return self._end_image_id

    @end_image_id.setter
    def end_image_id(self, end_image_id: str) -> None:
        self._end_image_id = end_image_id

    @property
    def image_table(self) -> str:
        return self._image_table

    @image_table.setter
    def image_table(self, image_table: str) -> None:
        self._image_table = image_table

    @property
    def project(self) -> str:
        return self._project

    @project.setter
    def project(self, project: str) -> None:
        self._project = project

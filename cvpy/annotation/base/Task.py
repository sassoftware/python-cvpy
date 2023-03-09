from cvpy.annotation.base.Project import Project
from cvpy.base.ImageTable import ImageTable


class Task(object):

    def __init__(self, image_table: ImageTable = None, project: Project = None) -> None:
        self._task_id = None
        self._project = project
        self._image_table = image_table
        self._start_image_id = 0
        if image_table:
            self._image_table_name = image_table.table.to_table_name()
            self._end_image_id = int(image_table.table.tableinfo().TableInfo.Rows.values[0] - 1)
        else:
            self._image_table_name = None
            self._end_image_id = 0

    @property
    def task_id(self) -> str:
        return self._task_id

    @task_id.setter
    def task_id(self, task_id: str) -> None:
        self._task_id = task_id

    @property
    def start_image_id(self) -> int:
        return self._start_image_id

    @start_image_id.setter
    def start_image_id(self, start_image_id: int) -> None:
        self._start_image_id = start_image_id

    @property
    def end_image_id(self) -> int:
        return self._end_image_id

    @end_image_id.setter
    def end_image_id(self, end_image_id: int) -> None:
        self._end_image_id = end_image_id

    @property
    def image_table(self) -> ImageTable:
        return self._image_table

    @image_table.setter
    def image_table(self, image_table: ImageTable) -> None:
        self._image_table = image_table

    @property
    def image_table_name(self) -> str:
        return self._image_table_name

    @image_table_name.setter
    def image_table_name(self, image_table_name: str) -> None:
        self._image_table_name = image_table_name

    @property
    def project(self) -> Project:
        return self._project

    @project.setter
    def project(self, project: Project) -> None:
        self._project = project

    def as_dict(self):
        """
        Creates a dictionary representation of this object.

        Returns
        -------
        d:
            A dictionary with all of the properties as keys and the property values as values.
            The CAS connection is not added in the dictionary.
        """
        d = {}
        for k, v in vars(self).items():
            if isinstance(v, ImageTable):
                image_table_dict = v.as_dict()
                del image_table_dict['table']
                d[k[1:]] = image_table_dict
            elif isinstance(v, Project):
                continue
            else:
                d[k[1:]] = v
        return d

    @staticmethod
    def from_dict(object_dict):
        """
        Creates a Task object from a dictionary.

        Parameters
        ----------
        object_dict:
            A dictionary with all of the properties as keys and the property values as values.

        Returns
        -------
        task:
            A Task object with all of the properties set from the specified dictionary.
        """
        task = Task()
        task.task_id = object_dict.get('task_id')
        task.image_table_name = object_dict.get('image_table_name')
        image_table_json = object_dict.get('image_table')
        image_table = ImageTable(None, image=image_table_json.get('image'),
                                 dimension=image_table_json.get('dimension'),
                                 resolution=image_table_json.get('resolution'),
                                 imageFormat=image_table_json.get('imageFormat'),
                                 path=image_table_json.get('path'),
                                 label=image_table_json.get('label'),
                                 id=image_table_json.get('id'),
                                 size=image_table_json.get('size'),
                                 type=image_table_json.get('type'))
        task.image_table = image_table
        task.start_image_id = object_dict.get('start_image_id')
        task.end_image_id = object_dict.get('end_image_id')
        return task

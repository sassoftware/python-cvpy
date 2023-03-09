from __future__ import annotations

import uuid
from http import HTTPStatus

import requests
from cvpy.annotation.base.Project import Project
from cvpy.annotation.base.Task import Task
from cvpy.base.ImageTable import ImageTable


class CVATTask(Task):
    """ Defines a class to interact with with a CVAT Task.
    
    Parameters
    ----------
    image_table: 
        Specifies the image table for this task.
    project: 
        Specifies the project that this task belongs to.
    """

    def __init__(self, image_table: ImageTable = None, project: Project = None) -> None:
        super().__init__(image_table=image_table, project=project)

        if project and project.url:
            # Create the actual task in CVAT.
            self._create_task_in_cvat()

    def _create_task_in_cvat(self) -> None:
        # Create the task name based on the projects CAS session ID and a generated unique ID.
        session_id = self.project.cas_connection.sessionid().session
        task_uuid = str(uuid.uuid4())
        task_name = f"CAS_{session_id}_UUID_{task_uuid}"

        # Actually create the task in CVAT.
        response = requests.post(f"{self.project.url}/api/tasks",
                                 headers=self.project.credentials.get_auth_header(),
                                 json=dict(name=task_name, project_id=self.project.project_id))

        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Unable to create the task in the CVAT project: {response.reason}')

        # Save the task ID that CVAT generated for this task.
        self.task_id = response.json()['id']

    @staticmethod
    def from_dict(object_dict) -> CVATTask:
        """
        Creates a CVATTask object from a dictionary.

        Parameters
        ----------
        object_dict:
            A dictionary with all of the properties as keys and the property values as values.
        Returns
        -------
        task:
            A CVATTask object with all of the properties set from the specified dictionary.
        """
        task = CVATTask()
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

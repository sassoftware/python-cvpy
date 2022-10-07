import uuid
from http import HTTPStatus

import requests

from cvpy.base.ImageTable import ImageTable
from cvpy.annotation.base.Task import Task
from cvpy.annotation.base.Project import Project


class CVATTask(Task):
    """ Defines a class to interact with with a CVAT Task.
    
    Parameters
    ----------
    image_table: 
        Specifies the image table for this task.
    project: 
        Specifies the project that this task belongs to."""

    def __init__(self, image_table: ImageTable = None, project: Project = None) -> None:
        super().__init__(image_table=image_table, project=project)

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

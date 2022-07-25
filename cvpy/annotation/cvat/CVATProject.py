import json
from http import HTTPStatus
from typing import List

import requests
from swat.cas import CAS, CASTable

from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.base.Project import Project


class CVATProject(Project):

    def __init__(self, cas_connection: CAS = None, url: str = None, credentials: Credentials = None,
                 project_name: str = None, annotation_type: AnnotationType = None,
                 labels: List[AnnotationLabel] = None) -> None:
        super().__init__(cas_connection, url, credentials, project_name, annotation_type, labels)

        # Authenticate with the CVAT server
        self._authenticate()

        # Create a project in the CVAT server
        self._create_project_in_cvat()

    def _authenticate(self) -> None:
        # No need to authenticate if token is set
        if self.credentials.token:
            return

        # Authenticates with the CVAT server and sets the token
        response = requests.post(f'{self.url}/auth/login',
                                 data=dict(username=self.credentials.username, password=self.credentials.password))

        if response.status_code != HTTPStatus.OK:
            response_json = json.loads(response.text)
            if 'non_field_errors' in response_json:
                message = response_json['non_field_errors']
            else:
                message = response.text
            raise Exception(f'Unable to authenticate: {message}')

        self.credentials.token = response.json()['key']

    def _create_project_in_cvat(self) -> None:
        # Creates a project in the CVAT server and sets the project_id
        response = requests.post(f'{self.url}/projects',
                                 headers=self.credentials.get_auth_header(),
                                 data=dict(name=self.project_name))

        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Unable to create the project in the CVAT server: {response.reason}')

        self.project_id = response.json()['id']

    def _delete_project_in_cvat(self) -> None:
        # Deletes the project from the CVAT server
        response = requests.delete(f'{self.url}/projects/{self.project_id}',
                                   headers=self.credentials.get_auth_header())

        if response.status_code != HTTPStatus.NO_CONTENT:
            raise Exception(f'Unable to delete the project in the CVAT server: {response.reason}')

    def post_images(self, image_table: CASTable) -> None:
        '''
        Create a CVAT task under the project and upload images from a CAS table to that task
        :param image_table: the input CAS table containing encoded images to be uploaded
        :return:
        '''
        pass

    def get_annotations(self, annotated_table: CASTable, image_table: CASTable) -> None:
        '''
        Fetches annotations from CVAT corresponding to the images in a CAS table
        :param annotated_table: the output CAS table where the images and the corresponding annotations will be stored
        :param image_table: the input CAS table containing encoded images that was used in a call to post_images()
                            on this CVATProject object.
        :return:
        '''
        pass

    def save(self, caslib: str, relative_path: str) -> None:
        '''
        Saves an annotation session
        :param caslib: the caslib under which the CAS tables are saved
        :param relative_path: the path relative to the caslib where the project will be saved
        :return:
        '''
        pass

    def resume(self, cas_connection: CAS, caslib: str, relative_path: str, credentials: Credentials) -> None:
        '''
        Resumes an annotation session
        :param cas_connection: the CAS connection in which the project will be resumed
        :param caslib: the caslib under which CAS tables were saved
        :param relative_path: the path relative to caslib where project was saved
        :param credentials: the credentials to connect to CVAT server
        :return: None
        '''
        pass

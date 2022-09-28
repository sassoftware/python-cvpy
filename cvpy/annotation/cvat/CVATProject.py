from http import HTTPStatus
from typing import List

import requests
from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.base.Project import Project
from cvpy.annotation.cvat.CVATAuthenticator import CVATAuthenticator
from swat.cas import CAS, CASTable


class CVATProject(Project):
    """ Defines a class to interact with with a CVAT Project.
    
    Parameters
    ----------
    cas_connection: 
        Specifies the CAS connection for this project.
    url: 
        Specifies the url of the CVAT server for calling the REST APIs.
    credentials: 
        Specifies the login credentials to connect to the CVAT server.
    project_name: 
        Specifies name of the project.
    annotation_type: 
        Specifies the type of the annotation project.
    labels: 
        Specifies a list of AnnotationLabel objects."""

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
        success, message, response = CVATAuthenticator.authenticate(self.url, self.credentials)
        if success:
            self.credentials.token = response.json()['key']
        else:
            raise Exception(message)

    def _create_project_in_cvat(self) -> None:
        # Creates a project in the CVAT server and sets the project_id
        response = requests.post(f'{self.url}/api/projects',
                                 headers=self.credentials.get_auth_header(),
                                 data=dict(name=self.project_name))

        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Unable to create the project in the CVAT server: {response.reason}')

        self.project_id = response.json()['id']

    def _delete_project_in_cvat(self) -> None:
        # Deletes the project from the CVAT server
        response = requests.delete(f'{self.url}/api/projects/{self.project_id}',
                                   headers=self.credentials.get_auth_header())

        if response.status_code != HTTPStatus.NO_CONTENT:
            raise Exception(f'Unable to delete the project in the CVAT server: {response.reason}')

    def post_images(self, image_table: CASTable) -> None:
        '''
        Create a CVAT task under the project and upload images from a CAS table to that task.

        Parameters
        ----------
        image_table: 
            Specifies the input CAS table that contains encoded images to be uploaded.
        
        '''
        pass

    def get_annotations(self, annotated_table: CASTable, image_table: CASTable) -> None:
        '''
        Fetch annotations from CVAT corresponding to the images in a CAS table.

        Parameters
        ----------
        annotated_table: 
            Specifies the output CAS table where the images and the corresponding annotations will be stored.
        image_table: 
            Specifies the input CAS table containing encoded images that was used in a call to post_images()
            on this CVATProject object.
        
        '''
        pass

    def save(self, caslib: str, relative_path: str) -> None:
        '''
        Saves an annotation session.

        Parameters
        ----------
        caslib: 
            Specifies the caslib under which the CAS tables are saved.
        relative_path: 
            Specifies the path relative to the caslib where the project will be saved.

        '''
        pass

    def resume(self, cas_connection: CAS, caslib: str, relative_path: str, credentials: Credentials) -> None:
        '''
        Resumes an annotation session.

        Parameters
        ----------
        cas_connection: 
            Specifies the CAS connection in which the project will be resumed.
        caslib: 
            SPecifies the caslib under which CAS tables were saved.
        relative_path: 
            Specifies the path relative to caslib where project was saved.
        credentials: 
            Specifies the credentials to connect to CVAT server.
        
        '''
        pass

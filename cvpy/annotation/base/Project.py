from typing import List

from swat.cas import CAS, CASTable

from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.image.base.ImageTable import ImageTable


class Project(object):
    '''
    This is a base class for a project in an annotation tool. It has several abstract methods that must be
    implemented by a subclass.
    '''

    def __init__(self, cas_connection: CAS = None, url: str = None, credentials: Credentials = None,
                 project_name: str = None, annotation_type: AnnotationType = None,
                 lables: List[AnnotationLabel] = None) -> None:
        '''
        Constructor for Project class
        :param cas_connection: the CAS connection for this project
        :param url: the url of the CVAT server for calling REST APIs
        :param credentials: the login credentials to connect to the CVAT server
        :param project_name: name of the project
        :param annotation_type: the type of the annotation project
        :param lables: a list of AnnotationLabel objects
        '''
        self._cas_connection = cas_connection
        self._url = url
        self._credentials = credentials
        self._project_name = project_name
        self._annotation_type = annotation_type
        self._labels = lables
        self._project_id = None
        self._tasks = []

    @property
    def cas_connection(self) -> CAS:
        return self._cas_connection

    @cas_connection.setter
    def cas_connection(self, cas_connection) -> None:
        self._cas_connection = cas_connection

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @credentials.setter
    def credentials(self, credentials: Credentials) -> None:
        self._credentials = credentials

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, project_name: str) -> None:
        self._project_name = project_name

    @property
    def annotation_type(self):
        return self._annotation_type

    @annotation_type.setter
    def annotation_type(self, annotation_type: AnnotationType) -> None:
        self._annotation_type = annotation_type

    @property
    def labels(self) -> List[AnnotationLabel]:
        return self._labels

    @labels.setter
    def labels(self, labels: List[AnnotationLabel]):
        self.labels = labels

    @property
    def project_id(self) -> str:
        return self._project_id

    @project_id.setter
    def project_id(self, project_id: str):
        self._project_id = project_id

    def add_task(self, task):
        self._tasks.append(task)

    def get_tasks(self):
        return self._tasks

    def post_images(self, image_table: ImageTable) -> None:
        '''
        Create a CVAT task under the project and upload images from a CAS table to that task
        :param image_table: the input CAS table containing encoded images to be uploaded
        :return:
        '''
        raise NotImplementedError

    def get_annotations(self, annotated_table: CASTable, image_table: ImageTable) -> None:
        '''
        Fetches annotations from CVAT corresponding to the images in a CAS table
        :param annotated_table: the output CAS table where the images and the corresponding annotations will be stored
        :param image_table: the input CAS table containing encoded images that was used in a call to post_images()
                            on this CVATProject object.
        :return:
        '''
        raise NotImplementedError

    def save(self, caslib: str, relative_path: str) -> None:
        '''
        Saves an annotation session
        :param caslib: the caslib under which the CAS tables are saved
        :param relative_path: the path relative to the caslib where the project will be saved
        :return:
        '''
        raise NotImplementedError

    def resume(self, cas_connection: CAS, caslib: str, relative_path: str, credentials: Credentials):
        '''
        Resumes an annotation session
        :param cas_session: the CAS session in which the project will be resumed
        :param caslib: the caslib under which CAS tables were saved
        :param relative_path: the path relative to caslib where project was saved
        :param credentials: the credentials to connect to CVAT server
        :return: None
        '''
        raise NotImplementedError

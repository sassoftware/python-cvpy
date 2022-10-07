from typing import List

from swat.cas import CAS, CASTable

from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.base.ImageTable import ImageTable


class Project(object):
    '''
    Defines a base class to interface with a project in an annotation tool. 
    
    The :class:`Project` class has several abstract methods that must be
    implemented by a subclass. Required abstract methods include: 
    get_annotations, post_images, resume, and save. 

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
        Specifies a list of AnnotationLabel objects.

    '''

    def __init__(self, cas_connection: CAS = None, url: str = None, credentials: Credentials = None,
                 project_name: str = None, annotation_type: AnnotationType = None,
                 labels: List[AnnotationLabel] = None) -> None:
        self._cas_connection = cas_connection
        self._url = url
        self._credentials = credentials
        self._project_name = project_name
        self._annotation_type = annotation_type
        self._labels = labels
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
        Create a CVAT task under the project and upload images from a CAS table to that task.

        Parameters
        ----------
        image_table: 
            Specifies the input CAS table that contains encoded images to be uploaded.

        '''
        raise NotImplementedError

    def get_annotations(self, annotated_table: CASTable, image_table: ImageTable) -> None:
        '''
        Fetch annotations from CVAT that correspond to the images in a CAS table.

        Parameters
        ----------
        annotated_table: 
            Specifies the output CAS table where the images and the corresponding annotations will be stored.
        image_table: 
            Specifies the input CAS table that contains encoded images that were used in a call to post_images()
            on this CVATProject object.

        '''
        raise NotImplementedError

    def save(self, caslib: str, relative_path: str) -> None:
        '''
        Save an annotation session.

        Parameters
        ----------
        caslib: 
            Specifies the caslib under which the CAS tables are saved.
        relative_path: 
            Specifies the path relative to the caslib where the project will be saved.
        
        '''
        raise NotImplementedError

    def resume(self, cas_connection: CAS, caslib: str, relative_path: str, credentials: Credentials):
        '''
        Resume an annotation session.

        Parameters
        ----------
        cas_session: 
            Specifies the CAS session in which the project will be resumed.
        caslib: 
            Specifies the caslib under which CAS tables were saved.
        relative_path: 
            Specifies the path relative to caslib where project was saved.
        credentials: 
            Specifies the credentials to connect to CVAT server.

        '''
        raise NotImplementedError

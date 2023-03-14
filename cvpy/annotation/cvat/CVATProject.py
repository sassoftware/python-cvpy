from __future__ import annotations

import io
import json
from http import HTTPStatus
from typing import List

import pandas as pd
import requests
from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.base.Project import Project
from cvpy.annotation.cvat.CVATAuthenticator import CVATAuthenticator
from cvpy.annotation.cvat.CVATTask import CVATTask
from cvpy.base.ImageTable import ImageTable
from swat.cas import CAS, CASTable


class CVATProject(Project):
    """ Defines a class to interact with a CVAT Project.
    
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

        self.project_version = 1

        if url:
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
        if self.annotation_type == AnnotationType.OBJECT_DETECTION or \
                self.annotation_type == AnnotationType.CLASSIFICATION:
            # Create a serializable list of labels used in this project.
            labels = [label.as_dict() for label in self._labels]
            payload = dict(name=self.project_name, labels=labels)
        else:
            payload = dict(name=self.project_name)

        # Creates a project in the CVAT server and sets the project_id
        response = requests.post(f'{self.url}/api/projects',
                                 headers=self.credentials.get_auth_header(),
                                 json=payload)

        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Unable to create the project in the CVAT server: {response.reason}')

        self.project_id = response.json()['id']

    def _delete_project_in_cvat(self) -> None:
        # Deletes the project from the CVAT server
        response = requests.delete(f'{self.url}/api/projects/{self.project_id}',
                                   headers=self.credentials.get_auth_header())

        if response.status_code != HTTPStatus.NO_CONTENT:
            raise Exception(f'Unable to delete the project in the CVAT server: {response.reason}')

    def post_images(self, image_table: ImageTable) -> None:
        """
        Create a CVAT task under the project and upload images from a CAS table to that task.

        Parameters
        ----------
        image_table:
            Specifies the input table that contains images to be uploaded.
        
        """
        # Check that the image_table contains the required columns for posting images to CVAT.
        if image_table.id is None:
            raise Exception('Provided ImageTable is missing a required column: id')
        if image_table.image is None:
            raise Exception('Provided ImageTable is missing a required column: image')
        if image_table.type is None:
            raise Exception('Provided ImageTable is missing a required column: type')

        # Fetch the image table that will be posted to CVAT.
        image_table_fetched = image_table.table.fetchImages(fetchImagesVars=["_id_", "_type_"])

        # Create a CVATTask for this set of images.
        task = CVATTask(image_table, self)

        # Build a dictionary of images to upload to CVAT.
        # The dictionary keys are of the form: client_files[image_frame_number]
        # where "client_files" is a CVAT REST API keyword and image_frame_number is an index
        # within the range [task.start_image_id, task.end_image_id].
        # The dictionary values are tuples: (image_name, image_bytes)
        # where image_name is the _id_ column from the image CAS table and appended
        # with the appropriate file extension, and image_bytes is the encoded image byte buffer.
        cvat_image_dict = dict()
        for index, row in image_table_fetched['Images'].iterrows():
            cvat_key = f"client_files[{index}]"

            # Get the image buffer from the Pillow object. To access the bytes directly we must
            # 'save' the image to an in-memory file object.
            # Note 1: Pillow uses the key 'JPEG' and cannot interpret 'jpg'.
            # Note 2: The image.fetchImages action applies JPEG encoding to all images in a
            #         decoded image table regardless of the 'type' column (if it even exists).
            image_bytes = io.BytesIO()
            pillow_format = 'JPEG'
            image_extension = 'jpg'
            if not image_table.has_decoded_images() and (row['_type_'] != 'jpg'):
                pillow_format = image_extension = row['_type_']

            row['Image'].save(image_bytes, format=pillow_format)
            cvat_image_dict[cvat_key] = (f"{row['_id_']}.{image_extension}", image_bytes.getbuffer())

        # Post the images to CVAT.
        response = requests.post(f'{self.url}/api/tasks/{task.task_id}/data',
                                 headers=self.credentials.get_auth_header(),
                                 files=cvat_image_dict,
                                 data=dict(image_quality=100, start_frame=task.start_image_id,
                                           stop_frame=task.end_image_id))

        if response.status_code != HTTPStatus.ACCEPTED:
            raise Exception(f'Unable to post images to the CVAT task: {response.reason}')

        # Images successfully posted for this task, add it to the projects task list.
        self.add_task(task)

    def get_annotations(self, image_table: ImageTable, annotated_table: CASTable) -> None:
        """
        Fetch annotations from CVAT corresponding to the images in a CAS table.

        Parameters
        ----------
        image_table:
            Specifies the ImageTable that was used to post images to the CVATProject object.
        annotated_table:
            Specifies the output CAS table where the images and the corresponding annotations will be stored.

        """

        # Determine which unique CVAT task is associated with the input image table.
        tasks = self.get_tasks()
        for task in tasks:
            if task.image_table == image_table:
                main_task = task

        # Get the tasks from CVAT.
        task_response = requests.get(f'{self.url}/api/tasks/{main_task.task_id}',
                                     headers=self.credentials.get_auth_header())

        # Raise an exception if there was a problem getting the tasks.
        if task_response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Unable to get the tasks from the CVAT server: {task_response.reason}')
            return

        task_id = task_response.json()['id']
        task_labels = pd.json_normalize(task_response.json()['labels'])[['id', 'name']]

        # Get the image metadata from CVAT.
        data_response = requests.get(f'{self.url}/api/tasks/' + str(task_id) + '/data/meta',
                                     headers=self.credentials.get_auth_header())

        # Raise an exception if there was a problem getting the data.
        if data_response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Unable to get the meta data from the CVAT server: {data_response.reason}')
            return

        task_frames = pd.json_normalize(data_response.json()['frames'])[['name']]

        # Get the annotations from CVAT.
        annotations_response = requests.get(f'{self.url}/api/tasks/' + str(task_id) + '/annotations',
                                            headers=self.credentials.get_auth_header())

        # Raise an exception if there was a problem getting the annotations.
        if annotations_response.status_code != HTTPStatus.OK:
            raise Exception(
                f'Unable to get the annotations from the CVAT server: {annotations_response.reason}')
            return

        # Check if the annotation type is classification.
        if self.annotation_type == AnnotationType.CLASSIFICATION:

            # If tags are detected in the annotation data, process the data.
            if len(annotations_response.json()['tags']):
                task_annotations = pd.json_normalize(annotations_response.json()['tags'])[
                    ['frame', 'label_id']]
                task_frames_annotations = task_annotations.join(task_frames, on='frame', how='inner')[
                    ['name', 'label_id']]
                image_annotations = task_frames_annotations.join(task_labels.set_index('id'),
                                                                 on='label_id', lsuffix='_image',
                                                                 rsuffix='_tag')[['name_image', 'name_tag']]

            else:
                print('No annotations have been detected.')
                return

        # Check if the annotation type is object detection.
        elif self.annotation_type == AnnotationType.OBJECT_DETECTION:

            # If shapes are detected in the annotation data, process the data.
            if len(annotations_response.json()['shapes']):
                task_annotations_pre_filter = pd.json_normalize(annotations_response.json()['shapes'])
                task_annotations = task_annotations_pre_filter[task_annotations_pre_filter['type'] == 'rectangle'][
                    ['frame', 'label_id', 'points']]
                task_frames_annotations = task_annotations.join(task_frames, on='frame', how='inner')[
                    ['name', 'label_id', 'points']]
                image_annotations = task_frames_annotations.join(task_labels.set_index('id'),
                                                                 on='label_id', lsuffix='_image',
                                                                 rsuffix='_tag')[['name_image', 'name_tag', 'points']]

                image_annotations_aggregate = image_annotations.groupby('name_image').agg(
                    {'name_tag': list, 'points': sum})
                image_annotations_aggregate['_nObjects_'] = image_annotations_aggregate['name_tag'].str.len()
                max_objects = image_annotations_aggregate['_nObjects_'].max()
                object_name_columns = []
                object_box_columns = []

                # For each object in the image, create a column name for each coordinate.
                for i in range(max_objects):
                    object_prefix = '_Object' + str(i)
                    object_name_columns.append(object_prefix + '_')
                    object_box_columns += [object_prefix + '_xMin', object_prefix + '_yMin',
                                           object_prefix + '_xMax', object_prefix + '_yMax', ]

                # Create the data frame with the annotation data.
                object_names_data_frame = image_annotations_aggregate.name_tag.apply(pd.Series)
                object_names_data_frame.columns = object_name_columns
                image_annotations_aggregate[object_name_columns] = object_names_data_frame
                points_data_frame = image_annotations_aggregate.points.apply(pd.Series)
                points_data_frame.columns = object_box_columns
                image_annotations_aggregate[object_box_columns] = points_data_frame
                image_annotations = image_annotations_aggregate.drop(['name_tag', 'points'], axis=1).reset_index()

            else:
                raise Exception("No annotations detected.")
                return

        # If the annotation type is semantic segmentation, print a message and return.
        elif self.annotation_type == AnnotationType.SEMANTIC_SEGMENTATION:
            raise Exception("Semantic Segmentation is not supported yet.")
            return

        # If any other annotation type is specified, print a message and return.
        else:
            raise Exception("Annotation type is not supported.")
            return

        # Create a new CAS table with the created annotation data.
        image_annotations_castable = self.cas_connection.CASTable('image_annotations_castable')
        self.cas_connection.upload(image_annotations, casout=image_annotations_castable)

        # Load the fedsql action set.
        self.cas_connection.loadactionset('fedsql')

        # If the annotation type is classification, merge the tables with the annotated tags.
        if self.annotation_type == AnnotationType.CLASSIFICATION:
            self.cas_connection.fedsql.execdirect(f'''
            create table {annotated_table.to_table_name()} {{options replace=true}}
            as
            (select a._id_, a._image_, a._path_, b.name_tag as _label_
            from {image_table.table.to_table_name()} as a
            inner join image_annotations_castable as b
            on compress(put(a._id_, best.) || '.' || a._type_)=b.name_image)
            ''')

            # Rename the label column to be lowercase
            self.cas_connection.table.altertable(
                table=annotated_table.to_table_name(),
                columns=[dict(name='_LABEL_', rename='_label_')]
            )

        # If the annotation type is object detection, merge the tables with the coordinate columns.
        elif self.annotation_type == AnnotationType.OBJECT_DETECTION:
            self.cas_connection.fedsql.execdirect(f'''
            create table {annotated_table.to_table_name()} {{options replace=true}}
            as
            (select a._id_, a._image_, a._path_, b.* 
            from {image_table.table.to_table_name()} as a
            inner join image_annotations_castable as b
            on compress(put(a._id_, best.) || '.' || a._type_)=b.name_image)
            ''')

        # Drop the cas table that was created.
        self.cas_connection.table.dropTable(name=image_annotations_castable)

    def save(self, caslib: str = None, relative_path: str = None, replace: bool = False) -> None:
        """
        Saves a CVATProject in the specified caslib and relative path.

        Parameters
        ----------
        caslib:
            Specifies the caslib under which the CAS tables are saved.
        relative_path:
            Specifies the path relative to the caslib where the project will be saved.
        replace:
            When set to True, the CAS tables are replaced if they are already present in the specified path.
        """
        # If caslib was not specified, set to default active caslib
        if caslib is None:
            caslibinfo = self.cas_connection.caslibinfo()['CASLibInfo']
            caslib = caslibinfo[caslibinfo.Active == 1].Name.values[0]

        # Create file path variable
        path = f'{self.project_name}'
        
        # If relative path was specified, prepend to path variable
        if relative_path is not None:
            path = f'{relative_path}/{path}'
        
        # Create a sub directory for the path
        self.cas_connection.addcaslibsubdir(path=path, name=caslib)
        
        # Get a JSON representation of this project
        project_json = self.to_json()

        # Upload the JSON representation in a CAS Table
        df = pd.DataFrame({'project_json': [project_json]})
        self.cas_connection.upload(df, importoptions=dict(vars=[dict(name='project_json', type='varchar')]),
                                   casout=dict(name=self.project_name, replace=True))
        project_table = self.cas_connection.CASTable(self.project_name)

        # Save the project table in the specified caslib and relative path
        project_table.save(name=f'{path}/{self.project_name}.sashdat', caslib=caslib, replace=replace)

        # Save the image tables from each task
        for task in self.get_tasks():
            task.image_table.table.save(name=f'{path}/{task.image_table_name}.sashdat', caslib=caslib,
                                        replace=replace)

    @staticmethod
    def resume(project_name: str, cas_connection: CAS, caslib: str, relative_path: str) -> CVATProject:
        """
        Resumes a CVATProject by reading it from the specified caslib and relative path.

        Parameters
        ----------
        project_name:
            Specifies the project name to be resumed.
        cas_connection:
            Specifies the CAS connection in which the project will be resumed.
        caslib:
            Specifies the caslib under which CAS tables were saved.
        relative_path:
            Specifies the path relative to caslib where project was saved.

        Returns
        -------
        project:
            A CVATProject object with all of the properties set from the specified JSON string.
        """

        # Load the project table
        project_table = cas_connection.CASTable(project_name)
        cas_connection.loadtable(f'{relative_path}/{project_name}.sashdat', caslib=caslib,
                                 casout=project_name)

        # Fetch the JSON representation of the project
        project_json = project_table.fetch().Fetch.project_json.values[0]

        # Deserialize CVAT Project from the JSON representation
        cvat_project = CVATProject.from_json(project_json)

        cvat_project.cas_connection = cas_connection

        # Load the image tables
        for task in cvat_project.get_tasks():
            # Load the images CAS table
            cas_connection.loadtable(f'{relative_path}/{task.image_table_name}.sashdat', caslib=caslib,
                                     casout=task.image_table_name)
            image_cas_table = cas_connection.CASTable(task.image_table_name)

            # Create ImageTable object
            task.image_table.table = image_cas_table

            # Set project pointer
            task.project = cvat_project

        # Return the resumed project object
        return cvat_project

    @staticmethod
    def from_json(project_json_str):
        """
        Creates a CVATProject object from a JSON representation of a project.

        Parameters
        ----------
        project_json_str:
            A JSON string with all of the properties as keys and the property values as values.

        Returns
        -------
        project:
            A CVATProject object with all of the properties set from the specified JSON string.
        """
        project_dict = json.loads(project_json_str)

        project = CVATProject()

        project.url = project_dict.get('url')
        project.project_id = project_dict.get('project_id')
        project.project_name = project_dict.get('project_name')
        project.project_version = project_dict.get('project_version')
        project.credentials = Credentials.from_dict(project_dict.get('credentials'))
        project.annotation_type = AnnotationType(project_dict.get('annotation_type'))
        project.labels = [AnnotationLabel.from_dict(label) for label in project_dict.get('labels')]

        project.tasks = [CVATTask.from_dict(task) for task in project_dict.get('tasks')]

        return project

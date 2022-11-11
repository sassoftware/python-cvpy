import io
import sys
import time
import unittest
from http import HTTPStatus

import requests
import swat
import xmlrunner

from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.cvat.CVATProject import CVATProject
from cvpy.base.ImageTable import ImageTable


class TestCVATProject(unittest.TestCase):

    # Create an instance of CVATProject
    def test_cvat_project(self):
        url = TestCVATProject.cvat_url

        cas_connection = swat.CAS(TestCVATProject.cas_host, TestCVATProject.cas_port, protocol='http')

        project_name = 'Test Project'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials()
        cvat_project = CVATProject(url=url, cas_connection=cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        self.assertEqual(cvat_project.url, url)
        self.assertEqual(cvat_project.cas_connection, cas_connection)
        self.assertEqual(cvat_project.credentials, credentials)
        self.assertEqual(cvat_project.project_name, project_name)
        self.assertEqual(cvat_project.annotation_type, annotation_type)
        self.assertEqual(cvat_project.labels, labels)

        self.assertIsNotNone(cvat_project.project_id)

        # Delete the project from CVAT
        cvat_project._delete_project_in_cvat()

    # Create an instance of CVATProject with invalid CVAT credentials
    def test_cvat_project_invalid_user_password(self):
        url = TestCVATProject.cvat_url
        credentials = Credentials(username='foo', password='bar')
        try:
            cvat_project = CVATProject(url=url, credentials=credentials)
        except Exception as e:
            self.assertRegex(str(e), 'Unable to log in with provided credentials')

    # Post images to a project.
    def test_cvat_project_post_images(self):

        # Setup CAS and create ImageTable's for decoded and encoded CAS image tables.
        cas_connection = swat.CAS(TestCVATProject.cas_host, TestCVATProject.cas_port, protocol='http')
        cas_connection.loadactionset('image')
        cas_connection.addcaslib(name='dlib',
                                 activeOnAdd=False,
                                 path=TestCVATProject.datapath,
                                 dataSource='PATH',
                                 subdirectories=True)

        cas_table_encoded = cas_connection.CASTable('cas_table_encoded')
        cas_connection.image.loadimages(labellevels=5,
                                        casout=cas_table_encoded,
                                        caslib='dlib',
                                        decode=False)

        cas_table_decoded = cas_connection.CASTable('cas_table_decoded')
        cas_connection.image.loadimages(labellevels=5,
                                        casout=cas_table_decoded,
                                        caslib='dlib',
                                        decode=True)

        image_table_encoded = ImageTable(cas_table_encoded)
        image_table_decoded = ImageTable(cas_table_decoded)

        # Create a CVATProject.
        url = TestCVATProject.cvat_url

        project_name = 'Test Project'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials(self.cvat_username, self.cvat_password)
        cvat_project = CVATProject(url=url, cas_connection=cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Post the images to the CVATProject.
        cvat_project.post_images(image_table_encoded)
        cvat_project.post_images(image_table_decoded)

        # Note: CVAT will throw an internal server error exception if we attempt to access the tasks
        #       data to soon after an upload. So we have a sleep here to prevent the issue.
        time.sleep(5)

        # Get the CVATTask objects we created and verify what was populated.
        tasks = cvat_project.get_tasks()
        self.assertEqual(len(tasks), 2)

        for task in tasks:
            # Get the task metadata from CVAT and then verify that it matches the tasks post_images created.
            self.assertIsNotNone(task.task_id)

            response = requests.get(f'{url}/api/tasks/{task.task_id}/data/meta', headers=credentials.get_auth_header())
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.json()['size'], task.image_table.table.tableinfo().TableInfo.Rows.values[0])
            self.assertEqual(response.json()['start_frame'], task.start_image_id)
            self.assertEqual(response.json()['stop_frame'], task.end_image_id)

            # Verify the image data and metadata between CAS and CVAT.
            cvat_frames = response.json()['frames']
            cas_images = task.image_table.table.fetchImages(fetchImagesVars=["_id_", "_type_"]).Images
            for index, frame_number in enumerate(range(task.start_image_id, task.end_image_id + 1)):
                # Check the image names.
                expected_extension = 'jpg' if (task.image_table.has_decoded_images()) else cas_images.iloc[index]._type_
                expected_name = f'{cas_images.iloc[index]._id_}.{expected_extension}'
                self.assertEqual(cvat_frames[index]['name'], expected_name)

                # Check the image bytes. (We have to GET the image from CVAT first.)
                response = requests.get(f'{url}/api/tasks/{task.task_id}/data',
                                        headers=credentials.get_auth_header(),
                                        params=dict(quality='original', number=frame_number, type='frame'))

                self.assertEqual(response.status_code, HTTPStatus.OK)
                cvat_image_bytes = io.BytesIO(response.content)

                cas_image_bytes = io.BytesIO()
                pillow_format = 'JPEG' if expected_extension == 'jpg' else expected_extension
                cas_images.iloc[index].Image.save(cas_image_bytes, format=pillow_format)
                self.assertEqual(cvat_image_bytes.getvalue(), cas_image_bytes.getvalue())

        # Delete the project from CVAT (which will also delete tasks associated with the project).
        cvat_project._delete_project_in_cvat()

    def test_cvat_project_save(self):

        # Setup CAS and create ImageTable's for decoded and encoded CAS image tables.
        cas_connection = swat.CAS(TestCVATProject.cas_host, TestCVATProject.cas_port, protocol='http')
        cas_connection.loadactionset('image')
        cas_connection.addcaslib(name='dlib',
                                 activeOnAdd=False,
                                 path=TestCVATProject.datapath,
                                 dataSource='PATH',
                                 subdirectories=True)

        cas_table_encoded = cas_connection.CASTable('cas_table_encoded')
        cas_connection.image.loadimages(labellevels=5,
                                        casout=cas_table_encoded,
                                        caslib='dlib',
                                        decode=False)

        cas_connection.addcaslib(name='bigdata',
                                 activeOnAdd=False,
                                 path='/bigdisk/lax/patela/data',
                                 dataSource='PATH',
                                 subdirectories=True)

        # Create a CVATProject.
        url = TestCVATProject.cvat_url

        project_name = 'MyDemoProject'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials(self.cvat_username, self.cvat_password)
        cvat_project = CVATProject(url=url, cas_connection=cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Post the images to the CVATProject.
        image_table_encoded = ImageTable(cas_table_encoded)
        cvat_project.post_images(image_table_encoded)

        # Note: CVAT will throw an internal server error exception if we attempt to access the tasks
        #       data to soon after an upload. So we have a sleep here to prevent the issue.
        time.sleep(5)

        cvat_project.save('bigdata', 'cvat_test', replace=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCVATProject.cvat_url = sys.argv.pop(1)
        TestCVATProject.cas_host = sys.argv.pop(1)
        TestCVATProject.cas_port = sys.argv.pop(1)
        TestCVATProject.cvat_username = sys.argv.pop(1)
        TestCVATProject.cvat_password = sys.argv.pop(1)
        TestCVATProject.datapath = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

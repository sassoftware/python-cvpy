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

    def setUp(self) -> None:
        self.cas_connection = swat.CAS(hostname=TestCVATProject.cas_host, port=TestCVATProject.cas_port,
                                       username=TestCVATProject.cas_username, password=TestCVATProject.cas_password,
                                       protocol=TestCVATProject.cas_protocol)

        self.cas_connection.loadactionset('image')

        self.caslib_name = 'dlib'

        self.cas_connection.addcaslib(name=self.caslib_name,
                                      activeOnAdd=False,
                                      path=TestCVATProject.datapath,
                                      dataSource='PATH',
                                      subdirectories=True)

    def tearDown(self) -> None:
        self.cas_connection.close()

    # Create an instance of CVATProject
    def test_cvat_project(self):
        url = TestCVATProject.cvat_url

        project_name = 'Test Project'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials()
        cvat_project = CVATProject(url=url, cas_connection=self.cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        self.assertEqual(cvat_project.url, url)
        self.assertEqual(cvat_project.cas_connection, self.cas_connection)
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

        cas_table_encoded = self.cas_connection.CASTable('cas_table_encoded')
        self.cas_connection.image.loadimages(path='images',
                                             labellevels=5,
                                             casout=cas_table_encoded,
                                             caslib=self.caslib_name,
                                             decode=False)

        cas_table_decoded = self.cas_connection.CASTable('cas_table_decoded')
        self.cas_connection.image.loadimages(path='images',
                                             labellevels=5,
                                             casout=cas_table_decoded,
                                             caslib=self.caslib_name,
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

        credentials = Credentials(TestCVATProject.cvat_username, TestCVATProject.cvat_password)
        cvat_project = CVATProject(url=url, cas_connection=self.cas_connection, credentials=credentials,
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

        cas_table_encoded = self.cas_connection.CASTable('cas_table_encoded_save_test')
        self.cas_connection.image.loadimages(path='images',
                                             labellevels=5,
                                             casout=cas_table_encoded,
                                             caslib=self.caslib_name,
                                             decode=False)

        # Create a CVATProject.
        url = TestCVATProject.cvat_url

        project_name = 'MyDemoProject_SaveTest'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials(TestCVATProject.cvat_username, TestCVATProject.cvat_password)
        cvat_project = CVATProject(url=url, cas_connection=self.cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Post the images to the CVATProject.
        image_table_encoded = ImageTable(cas_table_encoded)
        cvat_project.post_images(image_table_encoded)

        # Save the project
        cvat_project.save(self.caslib_name, 'cvpy', replace=True)

    def test_cvat_project_resume(self):

        # Resume a test project
        cvat_project = CVATProject.resume(project_name='MyDemoProject', cas_connection=self.cas_connection,
                                          caslib=self.caslib_name, relative_path='cvpy')

        # Verify all project attributes are set correctly
        assert cvat_project.project_version == 1
        assert cvat_project.project_name == 'MyDemoProject'
        assert cvat_project.project_id == 285
        assert cvat_project.annotation_type == AnnotationType.OBJECT_DETECTION
        assert cvat_project.credentials.username is None
        assert cvat_project.credentials.password is None
        assert len(cvat_project.labels) == 2

        for label in cvat_project.labels:
            if label.name == 'Mountain':
                assert label.color == 'orange'
            elif label.name == 'Person':
                assert label.color == 'green'
            else:
                assert False

        for task in cvat_project.tasks:
            assert task.image_table_name == 'cas_table_encoded'
            assert task.image_table.table.tableinfo().TableInfo.Rows.values[0] == 5


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCVATProject.cas_host = sys.argv.pop(1)
        TestCVATProject.cas_port = sys.argv.pop(1)
        TestCVATProject.cas_username = sys.argv.pop(1)
        TestCVATProject.cas_password = sys.argv.pop(1)
        TestCVATProject.cas_protocol = sys.argv.pop(1)
        TestCVATProject.datapath = sys.argv.pop(1)
        TestCVATProject.cvat_url = sys.argv.pop(1)
        TestCVATProject.cvat_username = sys.argv.pop(1)
        TestCVATProject.cvat_password = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

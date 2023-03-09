import io
import sys
import time
import unittest
from http import HTTPStatus

import requests
import swat
import xmlrunner
import numpy as np
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

    def test_cvat_project_get_annotation_classification(self):

        # Load the images to post to CVAT.
        cas_table_encoded = self.cas_connection.CASTable('cas_table_encoded')
        self.cas_connection.image.loadimages(labellevels=5,
                                             path='images',
                                             casout=cas_table_encoded,
                                             caslib=self.caslib_name,
                                             decode=False)

        # Create a CVATProject.
        url = "https://cvdata.unx.sas.com:8080"
        project_name = 'ClassificationTest'
        annotation_type = AnnotationType.CLASSIFICATION

        # Define the labels for the CVAT project.
        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')
        labels = [mountain_label, person_label]

        # Get authentication information for CVAT.
        credentials = Credentials()

        # Post the images to the CVATProject.
        image_table_encoded = ImageTable(cas_table_encoded)

        # Create the CVAT Project.
        cvat_project = CVATProject(url=url, cas_connection=self.cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Post the images to the project.
        cvat_project.post_images(image_table_encoded)

        # Wait before trying to access the project.
        time.sleep(5)

        # Get the task response.
        tasks = cvat_project.get_tasks()
        for task in tasks:
            if task.image_table == image_table_encoded:
                main_task = task
        task_response = requests.get(f'{cvat_project.url}/api/tasks/' + str(main_task.task_id),
                                     headers=cvat_project.credentials.get_auth_header())

        # Get the label ids for each of the labels.
        mountain_label = task_response.json()['labels'][0]['id']
        person_label = task_response.json()['labels'][1]['id']

        # Define the manual annotations to send to the project.
        annotations = {'version': 0,
                       'tags': [{'id': 17,
                                 'frame': 0,
                                 'label_id': person_label,
                                 'group': 0,
                                 'source': 'manual',
                                 'attributes': []},
                                {'id': 18,
                                 'frame': 1,
                                 'label_id': mountain_label,
                                 'group': 0,
                                 'source': 'manual',
                                 'attributes': []},
                                {'id': 20,
                                 'frame': 2,
                                 'label_id': person_label,
                                 'group': 0,
                                 'source': 'manual',
                                 'attributes': []},
                                {'id': 21,
                                 'frame': 3,
                                 'label_id': mountain_label,
                                 'group': 0,
                                 'source': 'manual',
                                 'attributes': []},
                                {'id': 22,
                                 'frame': 4,
                                 'label_id': mountain_label,
                                 'group': 0,
                                 'source': 'manual',
                                 'attributes': []}],
                       'shapes': [],
                       'tracks': []}

        # Manually add annotations for each of the images.
        put_response = requests.put(f'{cvat_project.url}/api/tasks/' + str(main_task.task_id) + '/annotations',
                                    headers=credentials.get_auth_header(),
                                    json=annotations)

        # Create the output annotations table.
        output_annotations = self.cas_connection.CASTable('output_annotations')

        # Call the get_annotations() API.
        cvat_project.get_annotations(image_table_encoded, output_annotations)

        # Delete the CVAT project.
        cvat_project._delete_project_in_cvat()

        # Assert that the images have been copied over correctly
        self.assertTrue(np.all(output_annotations.to_frame()['_image_'] == cas_table_encoded.to_frame()['_image_']))

        # Assert that the annotations are correct.
        self.assertEqual(output_annotations.to_frame().iloc[0]['_label_'], 'Person')
        self.assertEqual(output_annotations.to_frame().iloc[1]['_label_'], 'Mountain')
        self.assertEqual(output_annotations.to_frame().iloc[2]['_label_'], 'Person')
        self.assertEqual(output_annotations.to_frame().iloc[3]['_label_'], 'Mountain')
        self.assertEqual(output_annotations.to_frame().iloc[4]['_label_'], 'Mountain')

    def test_cvat_project_get_annotation_objectdetection(self):

        # Load the images to post to CVAT.
        cas_table_encoded = self.cas_connection.CASTable('cas_table_encoded_save_test')
        self.cas_connection.image.loadimages(path='images',
                                             labellevels=5,
                                             casout=cas_table_encoded,
                                             caslib=self.caslib_name,
                                             decode=False)

        project_name = 'ObjectDetection'
        annotation_type = AnnotationType.OBJECT_DETECTION

        # Define the labels for the CVAT project.
        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')
        labels = [mountain_label, person_label]

        # Get authentication information for CVAT.
        credentials = Credentials()

        # Post the images to the CVATProject.
        image_table_encoded = ImageTable(cas_table_encoded)

        # Create the CVAT Project.
        cvat_project = CVATProject(url=TestCVATProject.cvat_url, cas_connection=self.cas_connection,
                                   credentials=credentials, project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Post the images to the project.
        cvat_project.post_images(image_table_encoded)

        # Wait before trying to access the project.
        time.sleep(5)

        # Get the task response.
        tasks = cvat_project.get_tasks()
        for task in tasks:
            if task.image_table == image_table_encoded:
                main_task = task
        task_response = requests.get(f'{cvat_project.url}/api/tasks/' + str(main_task.task_id),
                                     headers=cvat_project.credentials.get_auth_header())

        # Get the label ids for each of the labels.
        mountain_label = task_response.json()['labels'][0]['id']
        person_label = task_response.json()['labels'][1]['id']

        # Define the manual annotations to send to the project.
        annotations = {'version': 0,
                       'tags': [],
                       'shapes': [{'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [275.5446428571413,
                                              43.85649350649146,
                                              426.08035714285506,
                                              197.1292207792194],
                                   'id': 282,
                                   'frame': 0,
                                   'label_id': person_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [584.8271103896095,
                                              26.065909090908463,
                                              731.2573051948038,
                                              227.2363636363625],
                                   'id': 283,
                                   'frame': 0,
                                   'label_id': person_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [321.93652597402615,
                                              140.7501623376629,
                                              446.32938311688304,
                                              334.2501623376629],
                                   'id': 284,
                                   'frame': 1,
                                   'label_id': person_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [385.49659090909154,
                                              240.6090909090908,
                                              702.9852272727276,
                                              306.0863636363629],
                                   'id': 285,
                                   'frame': 2,
                                   'label_id': mountain_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [439.77077922078024,
                                              453.1831168831177,
                                              558.9915584415594,
                                              599.2285714285717],
                                   'id': 286,
                                   'frame': 3,
                                   'label_id': person_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [1846.5759740259746,
                                              733.351948051948,
                                              2016.465584415584,
                                              933.0467532467537],
                                   'id': 287,
                                   'frame': 3,
                                   'label_id': person_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []},
                                  {'type': 'rectangle',
                                   'occluded': False,
                                   'z_order': 0,
                                   'rotation': 0.0,
                                   'points': [981.298828125, 893.5068359375, 1656.623046875, 1238.9609375],
                                   'id': 288,
                                   'frame': 4,
                                   'label_id': mountain_label,
                                   'group': 0,
                                   'source': 'manual',
                                   'attributes': []}],
                       'tracks': []}

        # Manually add annotations for each of the images.
        put_response = requests.put(f'{cvat_project.url}/api/tasks/' + str(main_task.task_id) + '/annotations',
                                    headers=credentials.get_auth_header(),
                                    json=annotations)

        # Create the output annotations table.
        output_annotations = self.cas_connection.CASTable('output_annotations')

        # Call the get_annotations() API.
        cvat_project.get_annotations(image_table_encoded, output_annotations)

        # Delete the CVAT project.
        cvat_project._delete_project_in_cvat()

        # Assert that the images have been copied over correctly
        self.assertTrue(np.all(output_annotations.to_frame()['_image_'] == cas_table_encoded.to_frame()['_image_']))

        # Assert that the first image's annotations are correct.
        first_image = output_annotations.to_frame().iloc[0]
        self.assertEqual(first_image['_Object0_'], 'Person')
        self.assertEqual(first_image['_Object1_'], 'Person')
        self.assertEqual(first_image['_nObjects_'], 2)
        self.assertAlmostEqual(first_image['_Object0_xMin'], 275.544642, 2)
        self.assertAlmostEqual(first_image['_Object0_yMin'], 43.8564935, 2)
        self.assertAlmostEqual(first_image['_Object0_xMax'], 426.080357, 2)
        self.assertAlmostEqual(first_image['_Object0_yMax'], 197.12922, 2)
        self.assertAlmostEqual(first_image['_Object1_xMin'], 584.82711, 2)
        self.assertAlmostEqual(first_image['_Object1_yMin'], 26.0659090, 2)
        self.assertAlmostEqual(first_image['_Object1_xMax'], 731.257305, 2)
        self.assertAlmostEqual(first_image['_Object1_yMax'], 227.236363, 2)

        # Assert that the second image's annotations are correct.
        second_image = output_annotations.to_frame().iloc[1]
        self.assertEqual(second_image['_Object0_'], 'Person')
        self.assertEqual(second_image['_nObjects_'], 1)
        self.assertAlmostEqual(second_image['_Object0_xMin'], 321.936526, 2)
        self.assertAlmostEqual(second_image['_Object0_yMin'], 140.750162, 2)
        self.assertAlmostEqual(second_image['_Object0_xMax'], 446.329383, 2)
        self.assertAlmostEqual(second_image['_Object0_yMax'], 334.250162, 2)
        self.assertTrue(np.isnan(second_image['_Object1_xMin']))

        # Assert that the third image's annotations are correct.
        third_image = output_annotations.to_frame().iloc[2]
        self.assertEqual(third_image['_Object0_'], 'Mountain')
        self.assertEqual(third_image['_nObjects_'], 1)
        self.assertAlmostEqual(third_image['_Object0_xMin'], 385.496591, 2)
        self.assertAlmostEqual(third_image['_Object0_yMin'], 240.609091, 2)
        self.assertAlmostEqual(third_image['_Object0_xMax'], 702.985227, 2)
        self.assertAlmostEqual(third_image['_Object0_yMax'], 306.086363, 2)
        self.assertTrue(np.isnan(third_image['_Object1_xMin']))

        # Assert that the fourth image's annotations are correct.
        fourth_image = output_annotations.to_frame().iloc[3]
        self.assertEqual(fourth_image['_Object0_'], 'Person')
        self.assertEqual(fourth_image['_Object1_'], 'Person')
        self.assertEqual(fourth_image['_nObjects_'], 2)
        self.assertAlmostEqual(fourth_image['_Object0_xMin'], 439.770779, 2)
        self.assertAlmostEqual(fourth_image['_Object0_yMin'], 453.183117, 2)
        self.assertAlmostEqual(fourth_image['_Object0_xMax'], 558.991558, 2)
        self.assertAlmostEqual(fourth_image['_Object0_yMax'], 599.228571, 2)
        self.assertAlmostEqual(fourth_image['_Object1_xMin'], 1846.575974, 2)
        self.assertAlmostEqual(fourth_image['_Object1_yMin'], 733.351948, 2)
        self.assertAlmostEqual(fourth_image['_Object1_xMax'], 2016.465584, 2)
        self.assertAlmostEqual(fourth_image['_Object1_yMax'], 933.046753, 2)

        ## Assert that the fifth image's annotations are correct.
        fifth_image = output_annotations.to_frame().iloc[4]
        self.assertEqual(fifth_image['_Object0_'], 'Mountain')
        self.assertEqual(fifth_image['_nObjects_'], 1)
        self.assertAlmostEqual(fifth_image['_Object0_xMin'], 981.298828, 2)
        self.assertAlmostEqual(fifth_image['_Object0_yMin'], 893.506836, 2)
        self.assertAlmostEqual(fifth_image['_Object0_xMax'], 1656.623047, 2)
        self.assertAlmostEqual(fifth_image['_Object0_yMax'], 1238.960938, 2)
        self.assertTrue(np.isnan(fifth_image['_Object1_xMin']))

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

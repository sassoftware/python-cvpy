import sys
import unittest

import swat
import xmlrunner
from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.base.Task import Task
from cvpy.annotation.cvat.CVATProject import CVATProject


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
            self.assertEqual(str(e), "Unable to log in with provided credentials.")

    # Add a task to a project
    def test_cvat_project_add_task(self):

        url = TestCVATProject.cvat_url

        project_name = 'Test Project'

        credentials = Credentials(username=TestCVATProject.cvat_username, password=TestCVATProject.cvat_password)
        cvat_project = CVATProject(url=url, credentials=credentials, project_name=project_name)

        task_1 = Task(task_id='1', start_image_id='5', end_image_id='10')
        task_2 = Task(task_id='2', start_image_id='11', end_image_id='20')
        cvat_project.add_task(task_1)
        cvat_project.add_task(task_2)

        tasks = cvat_project.get_tasks()

        self.assertEqual(tasks[0], task_1)
        self.assertEqual(tasks[1], task_2)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCVATProject.cvat_url = sys.argv.pop(1)
        TestCVATProject.cas_host = sys.argv.pop(1)
        TestCVATProject.cas_port = sys.argv.pop(1)
        TestCVATProject.cvat_username = sys.argv.pop(1)
        TestCVATProject.cvat_password = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

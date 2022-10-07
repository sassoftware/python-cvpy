import sys
import unittest
from http import HTTPStatus

import swat
import requests
import xmlrunner

from cvpy.base.ImageTable import ImageTable
from cvpy.annotation.base.AnnotationLabel import AnnotationLabel
from cvpy.annotation.base.AnnotationType import AnnotationType
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.cvat.CVATTask import CVATTask
from cvpy.annotation.cvat.CVATProject import CVATProject


class TestCVATTask(unittest.TestCase):

    def setUp(self) -> None:
        # Setup CAS connection and CASlib
        self.cas_connection = swat.CAS(TestCVATTask.cas_host, TestCVATTask.cas_port, protocol='http')
        self.cas_connection.loadactionset('image')
        self.cas_connection.addcaslib(name='dlib',
                                      activeOnAdd=False,
                                      path=TestCVATTask.datapath,
                                      dataSource='PATH',
                                      subdirectories=True)

        # Load the images in a CAS Table
        cas_table_encoded = self.cas_connection.CASTable('cas_table_encoded')
        self.cas_connection.image.loadimages(labellevels=5,
                                             casout=cas_table_encoded,
                                             caslib='dlib',
                                             decode=False)

        self.image_table = ImageTable(cas_table_encoded)

    def tearDown(self) -> None:
        self.cas_connection.close()

    # Create an instance of CVATTask
    def test_cvat_task(self):

        # Create a CVATProject that the tasks will be tied to.
        url = TestCVATTask.cvat_url

        project_name = 'Test Project'
        annotation_type = AnnotationType.OBJECT_DETECTION

        mountain_label = AnnotationLabel(name='Mountain', color='orange')
        person_label = AnnotationLabel(name='Person', color='green')

        labels = [mountain_label, person_label]

        credentials = Credentials(self.cvat_username, self.cvat_password)
        cvat_project = CVATProject(url=url, cas_connection=self.cas_connection, credentials=credentials,
                                   project_name=project_name, annotation_type=annotation_type,
                                   labels=labels)

        # Create the CVATTask object and then the task in CVAT itself.
        cvat_task = CVATTask(self.image_table, cvat_project)

        self.assertEqual(cvat_task.image_table, self.image_table)
        self.assertEqual(cvat_task.project, cvat_project)
        self.assertEqual(cvat_task.start_image_id, 0)
        self.assertEqual(cvat_task.end_image_id, self.image_table.table.tableinfo().TableInfo.Rows.values[0] - 1)

        # Check that the task_id exists before we try to do a GET request with the id.
        self.assertIsNotNone(cvat_task.task_id)

        # Get the general task data and veerify the task was posted to the correct project.
        response = requests.get(f'{url}/api/tasks/{cvat_task.task_id}', headers=credentials.get_auth_header())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['project_id'], cvat_project.project_id)

        # Delete the project from CVAT (which will also delete tasks associated with the project).
        cvat_project._delete_project_in_cvat()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCVATTask.cvat_url = sys.argv.pop(1)
        TestCVATTask.cas_host = sys.argv.pop(1)
        TestCVATTask.cas_port = sys.argv.pop(1)
        TestCVATTask.cvat_username = sys.argv.pop(1)
        TestCVATTask.cvat_password = sys.argv.pop(1)
        TestCVATTask.datapath = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

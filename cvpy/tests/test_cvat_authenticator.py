import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

import cvpy
import xmlrunner
from cvpy.annotation.base.Credentials import Credentials
from cvpy.annotation.cvat.CVATAuthenticator import CVATAuthenticator


class TestCVATAuthenticator(unittest.TestCase):

    def test_gen_cvat_token(self):
        # Mock the CVAT URL and username input
        cvpy.annotation.cvat.CVATAuthenticator.input = Mock()
        cvpy.annotation.cvat.CVATAuthenticator.input.side_effect = [TestCVATAuthenticator.cvat_url,
                                                                    TestCVATAuthenticator.cvat_username]

        # Mock the CVAT password input
        cvpy.annotation.cvat.CVATAuthenticator.getpass.getpass = Mock(return_value=TestCVATAuthenticator.cvat_password)

        # Call the function to generate .cvatauth file
        CVATAuthenticator.generate_cvat_token()

        # Verify .cvatauth file exists
        assert (Path(Path.home(), Credentials.DEFAULT_ANNOTATION_AUTH_FILE).exists())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCVATAuthenticator.cvat_url = sys.argv.pop(1)
        TestCVATAuthenticator.cvat_username = sys.argv.pop(1)
        TestCVATAuthenticator.cvat_password = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

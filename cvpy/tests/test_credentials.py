import sys
import unittest
from pathlib import PosixPath, Path

import xmlrunner

from cvpy.annotation.base.Credentials import Credentials


class TestCredentials(unittest.TestCase):

    # Create Credentials object with username and password
    def test_credentials_user_password(self):
        username = 'test_user'
        password = 'test_password'

        credentials = Credentials(username=username, password=password)

        self.assertEqual(credentials.username, username)
        self.assertEqual(credentials.password, password)
        self.assertIsNone(credentials.token)

    # Create Credentials object with a token; verify return value of get_auth_header()
    def test_credentials_with_token(self):
        token = 'abc1def2ghi'
        credentials = Credentials(token=token)

        self.assertIsNotNone(credentials.token)
        self.assertEqual(credentials.get_auth_header(), dict(Authorization=f'token {token}'))

    # Call get_auth_header before token is set
    def test_credentials_token_not_set(self):
        try:
            username = 'test_user'
            password = 'test_password'

            credentials = Credentials(username=username, password=password)
            credentials.get_auth_header()
        except Exception as e:
            self.assertEqual(str(e), 'Token is not set.')

    # Read credentials from the default file ~/.annotation_auth
    def test_credentials_default_authfile(self):
        default_auth_file_path = Path(Path.home(), Credentials.DEFAULT_ANNOTATION_AUTH_FILE)
        self.assertTrue(default_auth_file_path.exists(), f'The default file {default_auth_file_path} does not exist.')

        credentials = Credentials()
        self.assertTrue(credentials.token or (credentials.username and credentials.password))

    # Read token from a user specified auth file
    def test_credentials_authfile_with_token(self):
        auth_file_path = Path(TestCredentials.auth_file_with_token)
        self.assertTrue(auth_file_path.exists(), f'The file {auth_file_path} does not exist.')

        credentials = Credentials(auth_file=TestCredentials.auth_file_with_token)
        self.assertIsNotNone(credentials.token)

    # Read username and password from a user specified auth file
    def test_credentials_authfile_with_username_password(self):
        auth_file_path = Path(TestCredentials.auth_file_with_username_password)
        self.assertTrue(auth_file_path.exists(), f'The file {auth_file_path} does not exist.')

        credentials = Credentials(auth_file=TestCredentials.auth_file_with_username_password)
        self.assertIsNotNone(credentials.username)
        self.assertIsNotNone(credentials.password)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCredentials.auth_file_with_username_password = sys.argv.pop(1)
        TestCredentials.auth_file_with_token = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

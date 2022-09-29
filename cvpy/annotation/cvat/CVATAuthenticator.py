import getpass
import json
import stat
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlparse

import requests
from cvpy.annotation.base.Credentials import Credentials


class CVATAuthenticator(object):
    '''
    Defines a class with methods for CVAT authentication.
    '''

    # Max attempts for the user to provide valid URL, username and password before exiting
    MAX_ATTEMPTS = 3

    @staticmethod
    def generate_cvat_token():
        '''
        Authenticate a user against a CVAT server.

        This function prompts the user to enter a CVAT server URL, username and password.
        In case of successful authentication, the function writes the token returned by CVAT
        in a file named .cvatauth in the user's home directory.
        '''

        print('Enter the following details to generate and save a CVAT token. The token will be saved '
              'in a file named .cvatauth under your home directory.')

        # Get cvat_url from user input; if invalid, prompt the user to enter it again
        cvat_url = None
        success = False

        attempt = 0
        while not success and attempt < CVATAuthenticator.MAX_ATTEMPTS:
            cvat_url = input('Enter CVAT Application URL: ')
            result = urlparse(cvat_url)
            success = all([result.scheme, result.netloc])
            if not success:
                print('The URL you entered is invalid.')
            attempt += 1

        # Exit if URL is invalid
        if not success:
            exit(0)

        # Prompt user to enter username and password, and try to authenticate
        response = None
        attempt = 0
        success = False
        while not success and attempt < CVATAuthenticator.MAX_ATTEMPTS:
            username = input('Enter your username: ')
            password = getpass.getpass('Enter your password: ')

            credentials = Credentials(username=username, password=password)
            success, message, response = CVATAuthenticator.authenticate(cvat_url, credentials)
            del password

            if not success:
                print(f'Authentication failed: {message}')

            attempt += 1

        # Exit if authentication was not successful
        if not success:
            exit(0)

        # Extract the CVAT token from the response
        if response is not None:
            token = response.json()['key']

            # Write the token in .cvatauth file in the user's home directory
            file = Path(Path.home(), Credentials.DEFAULT_ANNOTATION_AUTH_FILE)
            with file.open("w", encoding="utf-8") as fh:
                fh.write(token)

            # Update file permissions to be read/write only by the user
            file.chmod(stat.S_IRUSR | stat.S_IWUSR)

            print(f'CVAT token successfully written to the file: {file}.')
        else:
            print(f'An unknown error has occurred.')

    @staticmethod
    def authenticate(url: str, credentials: Credentials):

        # Authenticates against the CVAT server
        response = requests.post(f'{url}/api/auth/login',
                                 data=dict(username=credentials.username, password=credentials.password))

        success = True
        message = None
        if response.status_code != HTTPStatus.OK:
            success = False
            response_json = json.loads(response.text)
            if 'non_field_errors' in response_json:
                message = ''.join(response_json['non_field_errors'])
            else:
                message = response.text

        return success, message, response

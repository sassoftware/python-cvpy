import os
import stat
from pathlib import PosixPath


class Credentials(object):

    def __init__(self, username: str = None, password: str = None, token: str = None, auth_file: str = None) -> None:
        '''
        Constructs a Credentials object. The auth_file with a token is recommended for a higher level of security.
        This auth file must not be readable or writable by the group or others. The file should have a single line with
        either a token, or comma-separated user and password. If auth_file parameter is not provided, this
        constructor reads the default auth file ~/.annotation_auth.

        :param username: the annotation server user name
        :param password: the annotation server password
        :param auth_file: the path to a file with comma separated annotation server user name and password
        '''
        self._username = username
        self._password = password
        self._auth_file = auth_file
        self._token = token

        # If (username and password) or token is provided, then don't read auth_file (default or username-provided)
        if (self._username and self._password) or (self._token):
            return

        # Check if default .annotation_auth file is present
        if not username and not password and not auth_file:
            default_auth_file = PosixPath('~/.annotation_auth').expanduser()
            if default_auth_file.is_file():
                auth_file = default_auth_file.as_posix()

        if auth_file:
            # Expand shortcuts like ~, .., etc.
            auth_file = PosixPath(auth_file).expanduser().as_posix()

            # Raise an exception if the file is readable/writable by the group or others
            mode = os.stat(auth_file).st_mode
            if (mode & stat.S_IRGRP) or (mode & stat.S_IWGRP) or (mode & stat.S_IROTH) or (mode & stat.S_IWOTH):
                raise Exception('Annotation server auth file must not be readable or writable by the group or others.')

            # Read the first line
            auth_fh = open(auth_file, 'r')
            auth_fields = auth_fh.readline().split(',')
            auth_fh.close()

            if len(auth_fields) == 1:  # Set token
                self._token = auth_fields[0].strip()
            elif len(auth_fields) == 2:  # # Set username and password
                self._username = auth_fields[0].strip()
                self._password = auth_fields[1].strip()
            else:
                raise Exception('Invalid annotation server auth file')

        if not self._token and (not self._username or not self._password):
            raise Exception('Either token or username and password must be provided as parameters or in the auth_file.')

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, username: str):
        self._username = username

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str):
        self._password = password

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    def get_auth_header(self) -> dict:
        if not self.token:
            raise Exception('Token is not set.')
        return dict(Authorization=f'token {self.token}')

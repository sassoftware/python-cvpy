from pathlib import Path


class Credentials(object):
    """ 
    Construct an object that contains authentication information. 
    
    The auth_file with a token is recommended for a higher level of security.
    This auth file must not be readable or writable by the group or others. The file should have a single line with
    either a token, or comma-separated user and password. If auth_file parameter is not provided, this
    constructor reads the default auth file ~/.annotation_auth.

    Parameters
    ----------
    username: 
        Specifies the annotation server user name.
    password: 
        Specifies the annotation server password.
    auth_file: 
        Specifies the path to a file with comma separated annotation server user name and password.

    """

    DEFAULT_ANNOTATION_AUTH_FILE = '.annotation_auth'

    def __init__(self, username: str = None, password: str = None, token: str = None, auth_file: str = None) -> None:
        self._username = username
        self._password = password
        self._auth_file = auth_file
        self._token = token

        # If (username and password) or token is provided, then don't read auth_file (default or user provided)
        if (self._username and self._password) or (self._token):
            return

        # Create a path object from auth_file if specified
        if auth_file:
            auth_file = Path(auth_file)
        else:
            # Check if default .annotation_auth file is present
            if not username and not password and not auth_file:
                default_auth_file = Path(Path.home(), Credentials.DEFAULT_ANNOTATION_AUTH_FILE)
                if default_auth_file.exists():
                    auth_file = default_auth_file

        if auth_file:
            # Read the first line
            with auth_file.open(mode='r') as fh:
                line = fh.readline()

            if line:
                auth_fields = line.split(',')

                if len(auth_fields) == 1:  # Set token
                    self._token = auth_fields[0].strip()
                elif len(auth_fields) == 2:  # # Set username and password
                    self._username = auth_fields[0].strip()
                    self._password = auth_fields[1].strip()
                else:
                    raise Exception(f'Invalid annotation server auth file: {auth_file}')

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

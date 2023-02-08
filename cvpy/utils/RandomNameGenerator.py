import uuid


class RandomNameGenerator(object):
    def generate_name(self, prefix: str = 'temp') -> str:
        unique_id = uuid.uuid1()

        # Add a prefix and return random name string
        return f"{prefix}_{unique_id}"

import re

from swat.cas import CASResults


def assert_contains_message(results, expected_msg):
    if not isinstance(results, CASResults):
        raise TypeError("ERROR: Parameter 'results' expects a CASResults")
    elif not isinstance(expected_msg, str):
        raise TypeError("ERROR: Parameter 'expectedMsg' expects a string")

    for i in range(len(results.messages)):
        if re.search(expected_msg, results.messages[i]):
            return
    raise ValueError('\nMessage: ' + ', '.join(results.messages) + '\nExpected message: ' + expected_msg)

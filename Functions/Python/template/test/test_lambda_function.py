"""Created By: Andrew Ryan DeFilippis"""

import contextlib
import re
import unittest
from io import StringIO

import context
import lambda_function


class TestLambdaFunction(unittest.TestCase):
    """Test all the Lambda Function things!
    """

    def test_cwlogs_event_format(self):
        """Verify the format of a log event sent to CWLogs.
        """

        log = lambda_function.CWLogs(context)

        output = StringIO()

        with contextlib.redirect_stdout(output):
            log.event('Message')

        output = output.getvalue().strip()

        event = re.match((
            "^LOG "
            "RequestId: "
            "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
            "\t"
            "Message$"
        ), output)

        self.assertIsNotNone(event)

    def test_invocation_response(self):
        """Verify successful invocation of the Function.
        """

        expected_result = {'Hello': 'World!'}
        result = lambda_function.local_test()

        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()

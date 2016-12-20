"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

from json import dumps, loads

# Disable 'testing_locally' when deploying to AWS Lambda
testing_locally = True
verbose = True


class CWLogs(object):
    """Define the structure of log events to match all other CloudWatch Log Events logged by AWS Lambda.
    """

    def __init__(self, context):
        """Define the instance of the context object.

        :param context: Lambda context object
        """

        self.context = context

    def event(self, message, event_prefix='LOG'):
        # type: (any, str) -> None
        """Print an event into the CloudWatch Logs stream for the Function's invocation.

        :param message: The information to be logged (required)
        :param event_prefix: The prefix that appears before the 'RequestId' (default 'LOG')
        :return:
        """

        print('{} RequestId: {}\t{}'.format(
            event_prefix,
            self.context.aws_request_id,
            message
        ))

        return None


def lambda_handler(event, context):
    """AWS Lambda executes the 'lambda_handler' function on invocation.

    :param event: Ingested JSON event object provided at invocation
    :param context: Lambda context object, containing information specific to the invocation and Function
    :return: Final response to AWS Lambda, and passed to the invoker if the invocation type is RequestResponse
    """

    # Instantiate our CloudWatch logging class
    log = CWLogs(context)

    if verbose is True:
        log.event('Event: {}'.format(dumps(event)))

    log.event('Hello World!')

    return None


def local_test():
    """Testing on a local development machine (outside of AWS Lambda) is made possible by...
    """

    import context

    with open('event.json', 'r') as f:
        event = loads(f.read())

    print('\nFunction Log:\n')

    lambda_handler(event, context)

if testing_locally is True:
    local_test()

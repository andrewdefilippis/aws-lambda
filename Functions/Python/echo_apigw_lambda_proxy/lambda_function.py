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

    if verbose:
        log.event('Event: {}'.format(dumps(event)))

    # Define the response values
    status_code = 200
    headers = {
        'Content-Type': 'application/json'
    }
    body = dumps(event)
    body_is_base64_encoded = False

    # Build the APIGW Lambda Proxy response
    apigw_lambda_proxy_response = {
        'statusCode': int(status_code),
        'headers': dict(headers),
        'body': str(body),
        'isBase64Encoded': bool(body_is_base64_encoded)
    }

    if verbose:
        log.event('Response: {}'.format(dumps(apigw_lambda_proxy_response)))

    return apigw_lambda_proxy_response


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

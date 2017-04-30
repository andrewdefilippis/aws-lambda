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


class APIGWProxy(object):
    """Define the Lambda Proxy interaction with AWS API Gateway.
    """

    def __init__(self, log):
        """Define the instance of the log object.
        
        "param log: CloudWatch Logs context object
        """

        self.log = log

    def response(self, status_code, body_is_base64_encoded=False, headers=None, body=None):
        # type: (int, bool, dict, str) -> dict
        """Return an API Gateway Lambda Proxy response object.
        
        :param status_code: The response status code.
        :param body_is_base64_encoded: Is the body a base64 encoded string?
        :param headers: The response headers.
        :param body: The response body.
        :return: An API Gateway Lambda Proxy response object.
        """

        response_object = {'statusCode': int(status_code)}

        if headers is not None:
            response_object['headers'] = dict(headers)

        if body is not None:
            response_object['body'] = str(body)
            response_object['isBase64Encoded'] = bool(body_is_base64_encoded)

        # Log the API Gateway Lambda Proxy response object
        if verbose:
            self.log.event('Response: {}'.format(dumps(response_object)))

        return response_object


def lambda_handler(event, context):
    """AWS Lambda executes the 'lambda_handler' function on invocation.

    :param event: Ingested JSON event object provided at invocation
    :param context: Lambda context object, containing information specific to the invocation and Function
    :return: Final response to AWS Lambda, and passed to the invoker if the invocation type is RequestResponse
    """

    # Instantiate our CloudWatch logging class
    log = CWLogs(context)

    # Instantiate our API Gateway Lambda Proxy class
    apigw = APIGWProxy(log)

    # Log the event object provided to the Lambda Function at invocation
    if verbose:
        log.event('Event: {}'.format(dumps(event)))

    # Return a Lambda Proxy API response to API Gateway
    return apigw.response(
        status_code=200,
        headers={
            'Content-Type': 'application/json'
        },
        body=dumps(event),
        body_is_base64_encoded=False
    )


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

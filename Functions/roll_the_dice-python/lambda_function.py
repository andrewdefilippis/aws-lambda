"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

from json import dumps, loads
from random import randint

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


class APIGWProxyIntegration(object):
    """Define the unique formatting of a response to API Gateway for Proxy Integration.
    """

    def __init__(self, context):
        """Instantiate logging class and define the default response headers.

        :param context: Lambda context object
        """

        self.log = CWLogs(context)
        self.default_response_headers = {
            'Content-Type': 'application/json',  # JSON all the things, or at least the default Content-Type
            'Internal-Request-ID': '{}'.format(context.aws_request_id)  # Pass back the Lambda Function request ID
        }

    def response(self, status_code, body=None, headers=None):
        # type: (int, str, dict) -> dict
        """Build the Lambda Function response for API Gateway Proxy Integration.

        :param status_code: HTTP response status code (required)
        :param body: String of response body payload (default None)
        :param headers: Dictionary of header values (default default_headers)
        :return: Response data formatted for API Gateway Proxy Integration
        """

        response_data = {'statusCode': int(status_code)}  # "statusCode" must be an integer

        if headers is None:  # Override the default headers if custom headers are specified
            headers = self.default_response_headers

        if headers is not None:     # Although not required with the above "self.default_response_headers"
                                    # assigned to "headers", it is good to have the check in place.
            response_data['headers'] = loads(dumps(headers))  # "headers" must be a dictionary

        if body is not None:
            response_data['body'] = str(body)  # "body" must be a string

        if verbose is True:
            self.log.event('Response: {}'.format(dumps(response_data)))
        else:
            self.log.event('Response: HTTP status code is {}'.format(status_code))

        return response_data


class RollTheDice(object):
    """Roll the dice to find out what you get.
    """

    def __init__(self, context):
        """Instantiate logging and response classes.

        :param context: Lambda context object
        """

        self.log = CWLogs(context)
        self.apigw = APIGWProxyIntegration(context)

    def roll(self, count, sides):
        # type: (int, int) -> dict
        """Roll the dice using the integer values for count and sides.

        :param count: The number of dice being rolled (required)
        :param sides: The number of sides per dice (required)
        :return: Fully built response to be returned as the final response from Lambda
        """

        min_dice = 1  # Hopefully we want at least 1 dice
        max_dice = 10  # Max number of dice is an artificial limitation which can be increased.
        min_sides = 2  # Yes, "2" sides means you can produce a coin-flip.
        max_sides = 120  # Max sides/dice matches physical limitation of sides/dice.

        try:
            # Make sure the values are int
            count = int(count)
            sides = int(sides)

            if not min_dice <= count <= max_dice or not min_sides <= sides <= max_sides:
                err_code = 400
                err_str = (
                    "The dice count must be from \"{}\" to \"{}\", "
                    "and the number of sides must by from \"{}\" to \"{}\".".format(
                        min_dice,
                        max_dice,
                        min_sides,
                        max_sides
                    )
                )

                err_body = dumps({'errorMessage': '{}'.format(err_str)})

                if verbose is True:
                    self.log.event('Error: {} - {}'.format(err_code, err_body))

                return self.apigw.response(err_code, err_body)

            else:
                rolls = {'dice': {}}
                count += 1  # Starts dice count at '1' instead of '0' for pretty printing

                for dice in range(1, count):
                    rolls['dice'][dice] = {}
                    rolls['dice'][dice]['roll'] = randint(1, sides)

                rolls = dumps(rolls)  # Encode the dictionary as a JSON object

                return self.apigw.response(200, rolls)

        except (TypeError, ValueError) as e:
            err_code = 400
            err_body = dumps({'errorMessage': 'The values for "count" and "sides" must be integers.'})

            if verbose is True:
                self.log.event('Error: {} - {} {}'.format(err_code, type(e), e))

            return self.apigw.response(err_code, err_body)


def lambda_handler(event, context):
    """AWS Lambda executes the 'lambda_handler' function on invocation.

    :param event: Ingested JSON event object provided at invocation
    :param context: Lambda context object, containing information specific to the invocation and Function
    :return: Final response to AWS Lambda, and passed to the invoker if the invocation type is RequestResponse
    """

    # Instantiate our CloudWatch logging, API Gateway Proxy Integration
    # response building, and rolling of the dice classes.
    log = CWLogs(context)
    apigw = APIGWProxyIntegration(context)
    rtd = RollTheDice(context)

    try:
        if verbose is True:
            log.event('Event: {}'.format(dumps(event)))

        method = event['requestContext']['httpMethod']

        try:
            count = event['queryStringParameters']['count']
            sides = event['queryStringParameters']['sides']
        except (TypeError, KeyError) as e:
            status_code = 400
            err_str = (
                "Integer values for \"count\" and "
                "\"sides\" query strings must be provided."
            )
            err_body = dumps({'errorMessage': '{}'.format(err_str)})

            if verbose is True:
                log.event('Error: {} - {} {}'.format(status_code, type(e), e))

            return apigw.response(status_code, err_body)

        if verbose is True:
            log.event('Request: httpMethod is {}'.format(method))
            log.event('Request: count is {}'.format(count))
            log.event('Request: sides is {}'.format(sides))

        if method in ('GET', 'POST'):  # Time to roll
            return rtd.roll(
                count,
                sides
            )

        else:
            # Return the response code 405 'Method Not Allowed'
            status_code = 405
            err_body = dumps({'errorMessage': 'Method Not Allowed'})

            if verbose is True:
                log.event('Error: {} - {}'.format(status_code, err_body))

            return apigw.response(status_code, err_body)

    except Exception as e:
        status_code = 500
        err_body = dumps({'errorMessage': 'Internal Server Error'})

        log.event('Error: {} - {} {}'.format(status_code, type(e), e))

        return apigw.response(status_code, err_body)


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

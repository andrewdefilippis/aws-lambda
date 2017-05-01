"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

import random
import re
import string

import boto3
import os
from botocore.config import Config
from botocore.exceptions import ClientError
from json import dumps, loads

# Disable 'testing_locally' when deploying to AWS Lambda.
testing_locally = True
verbose = True
debug = False

# Set the Lambda Function environment variable named "ddbTable" with
# the table name or statically set the DDB Table name below.
DDB_TABLE = ""
# Define length of unique IDs.
ID_LENGTH = 7

# Debug level logging.
if debug:
    boto3.set_stream_logger(name='botocore')
    verbose = True

# Initiate boto3 DynamoDB client.
ddb_conf = Config(connect_timeout=0.5, read_timeout=1)
ddbc = boto3.client('dynamodb', config=ddb_conf)


class CWLogs(object):
    """Define the structure of log events to match all other CloudWatch Log Events logged by AWS Lambda.
    """

    def __init__(self, context):
        """Define the instance of the context object.

        :param context: The Lambda context object.
        """

        self.context = context

    def event(self, message, event_prefix='LOG'):
        # type: (any, str) -> None
        """Print an event into the CloudWatch Logs stream for the Function's invocation.

        :param message: The information to be logged (required).
        :param event_prefix: The prefix that appears before the 'RequestId' (default 'LOG').
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
        
        "param log: CloudWatch Logs context object.
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

        # Log the API Gateway Lambda Proxy response object.
        if verbose:
            self.log.event('Response: {}'.format(dumps(response_object)))

        return response_object

    def status_301(self, location):
        # type: (str) -> dict
        """Return a response with a 301 status code.
        
        :param location: URL to be redirected to.
        :return: An API Gateway Lambda Proxy response object.
        """

        return self.response(
            status_code=301,
            headers={
                'Content-Type': 'text/html',
                'Location': location
            }
        )

    def status_400(self):
        # type: () -> dict
        """Return a response with a 400 status code.
        
        :return: An API Gateway Lambda Proxy response object.
        """

        return self.response(
            status_code=400,
            headers={
                'Content-Type': 'text/html'
            },
            body='<html><head><title>400 - Bad Request</head><body><center><h1>400 - Bad Request</h1></center></body></html>'
        )

    def status_404(self):
        # type: () -> dict
        """Return a response with a 404 status code.
        
        :return: An API Gateway Lambda Proxy response object.
        """

        return self.response(
            status_code=404,
            headers={
                'Content-Type': 'text/html'
            },
            body='<html><head><title>404 - Page Not Found</head><body><center><h1>404 - Page Not Found</h1></center></body></html>'
        )

    def status_405(self):
        # type: () -> dict
        """Return a response with a 405 status code.
        
        :return: An API Gateway Lambda Proxy response object.
        """

        return self.response(
            status_code=405,
            headers={
                'Content-Type': 'text/html'
            },
            body='<html><head><title>405 - Method Not Allowed</head><body><center><h1>405 - Method Not Allowed</h1></center></body></html>'
        )

    def status_500(self):
        # type: () -> dict
        """Return a response with a 500 status code.
        
        :return: An API Gateway Lambda Proxy response object.
        """

        return self.response(
            status_code=500,
            headers={
                'Content-Type': 'text/html'
            },
            body='<html><head><title>500 - Internal Server Error</head><body><center><h1>500 - Internal Server Error</h1></center></body></html>'
        )


class DynamoDBLogic(object):
    """Define the get_item and put_item request structure for shortened IDs.
    """

    def __init__(self, event, log, id_length):
        """Define the instance of the log object and id_length value.
        
        :param event: Ingested JSON event object provided at invocation.
        :param log: CloudWatch Logs context object.
        :param id_length: Length of the resource IDs being generated.
        """

        self.event = event
        self.log = log
        self.id_length = id_length

    def get_url(self):
        # type: (str) -> str
        """Retrieve a stored URL from DynamoDB based on the resource ID.
        
        :return: URL stored in DynamoDB associated with the specified resource ID.
        """
        try:
            path = self.event['resource']
            url_id = path.split("/")[1]

            try:
                # The ID must match the expected length.
                if len(url_id) != ID_LENGTH:
                    raise ValueError('Invalid ID Length')
                # Only "/a1b2c3d" and "/a1b2c3d/" are valid paths.
                elif len(path.split("/")[2]) > 0:
                    raise ValueError('Invalid Path')
            except IndexError:
                # The path is a match to what we expect to receive.
                pass

            # Return the URL stored in DynamoDB.
            ddb_response = ddbc.get_item(
                TableName=os.getenv('ddbTable', DDB_TABLE),
                Key={
                    'ID': {'S': url_id}
                }
            )

            # Log the DynamoDB response object.
            if verbose:
                self.log.event('DDB: {}'.format(ddb_response))

            try:
                url = ddb_response['Item']['Endpoint']['S']
            except KeyError:
                raise KeyError('Item does not exist')

            return url
        except Exception:
            raise

    def set_url(self, url):
        # type: (int, str) -> str
        """Store a URL and unique ID in DynamoDB.
        
        :param url: URL to be stored in DynamoDB.
        :return: Unique resource ID associated with the URL.
        """
        try:
            url_id = id_gen(self.id_length)
            location = url

            # Store the URL and unique resource ID in DynamoDB if the resource ID does not already exist.
            ddb_response = ddbc.put_item(
                TableName=os.getenv('ddbTable', DDB_TABLE),
                Item={
                    'ID': {'S': url_id},
                    'Endpoint': {'S': location}
                },
                ConditionExpression='attribute_not_exists(Endpoint)'
            )

            # Log the DynamoDB response object.
            if verbose:
                self.log.event('DDB: {}'.format(ddb_response))

            return url_id
        except ClientError as e:
            # If an item with the same unique resource ID already exists, then generate a new one.
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.set_url(url)
            else:
                raise
        except Exception:
            raise


def id_gen(id_length):
    # type: (int) -> str
    """Generate a unique alpha-numeric ID of a specified length.
    
    :param id_length: Length of unique string.
    :return: Unique string.
    """

    selection = string.ascii_letters + string.digits
    return ''.join(random.choice(selection) for _ in range(id_length))


def lambda_handler(event, context):
    """AWS Lambda executes the 'lambda_handler' function on invocation.

    :param event: Ingested JSON event object provided at invocation.
    :param context: Lambda context object, containing information specific to the invocation and Function.
    :return: Final response to AWS Lambda, and passed to the invoker if the invocation type is RequestResponse.
    """

    # Instantiate our CloudWatch logging class.
    log = CWLogs(context)

    # Instantiate our API Gateway Lambda Proxy class.
    apigw = APIGWProxy(log)

    # Instantiate our DynamoDB URL logic class.
    dynamodb = DynamoDBLogic(event, log, ID_LENGTH)

    # Log the event object provided to the Lambda Function at invocation.
    if verbose:
        log.event('Event: {}'.format(dumps(event)))

    # Request processing logic.
    try:
        if event['httpMethod'] == 'GET':
            try:
                # Request the URL from DynamoDB.
                location = dynamodb.get_url()
            except ValueError as e:
                log.event('Error: {}'.format(e))
                return apigw.status_404()
            except KeyError as e:
                log.event('Error: {}'.format(e))
                return apigw.status_404()
            except Exception:
                raise

            # Return "301: Permanent Redirect" with the location stored in DynamoDB.
            return apigw.status_301(location)
        elif event['httpMethod'] == 'POST':
            try:
                url = event['headers']['URL']

                # Check for a valid URL.
                if not re.match('^[a-z0-9]+://.*', url):
                    raise KeyError('Missing protocol prefix in URL')

                # Store the URL in DynamoDB.
                url_id = dynamodb.set_url(url=url)
            except KeyError as e:
                log.event('Error: {}'.format(e))
                return apigw.status_400()
            except Exception:
                raise

            # Return "200: Ok" with the shortened URL.
            return apigw.response(
                status_code=200,
                headers={'Content-Type': 'application/json'},
                body=dumps({'UrlId': url_id})
            )
        else:
            # Return "405: Method Not Allowed".
            return apigw.status_405()
    except Exception as e:
        log.event('Error: {}'.format(e))

        # Return "500: Internal Server Error".
        return apigw.status_500()


def local_test():
    """Testing on a local development machine (outside of AWS Lambda) is made possible by...
    """

    import context

    with open('event.json', 'r') as f:
        event = loads(f.read())

    print('\nFunction Log:\n')

    lambda_handler(event, context)


if testing_locally:
    local_test()

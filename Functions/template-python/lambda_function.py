"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

from json import dumps, loads


# Disable 'testing_locally' when deploying to AWS Lambda
testing_locally = True
verbose = True


class CWLogs(object):
    def __init__(self, context):
        self.context = context

    def event(self, message, event_prefix='LOG'):
        print('{} RequestId: {}\t{}'.format(
            event_prefix,
            self.context.aws_request_id,
            message
        ))


def lambda_handler(event, context):
    log = CWLogs(context)

    if verbose is True:
        log.event('Event: {}'.format(dumps(event)))

    log.event('Hello World!')

    return None


def local_test():
    import context

    with open('event.json', 'r') as f:
        event = loads(f.read())

    print('\nFunction Log:\n')

    lambda_handler(event, context)

if testing_locally is True:
    local_test()

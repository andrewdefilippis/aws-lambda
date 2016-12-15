"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

from json import dumps, loads


def lambda_handler(event, context):
    print('LOG RequestId: {}\tResponse:\n\n{}'.format(
        context.aws_request_id,
        None
    ))

    return None


# Comment or remove everything below before deploying to Lambda.
def local_testing():
    import context

    with open('event.json', 'r') as f:
        event = loads(f.read())

    print("Event:\n\n{}\n\nFunction Output:\n".format(
        dumps(
            event,
            indent=4
        )
    ))

    lambda_handler(event, context)


local_testing()

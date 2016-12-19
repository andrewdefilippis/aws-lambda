"""Created By: Andrew Ryan DeFilippis"""

from inspect import stack, getmodule
from uuid import uuid4 as uuid
from random import randrange

# Setup for retrieving the Function name (from the top-lvl dir name)
frame = stack()[1]
module = getmodule(frame[0])

aws_request_id = uuid()
function_name = module.__file__.split('/')[-2].split('.')[0]
function_version = '$LATEST'
invoked_function_arn = 'arn:aws:lambda:us-west-2:123412341234:function:{}'.format(function_name)
memory_limit_in_mb = '128'
log_group_name = '/aws/lambda/{}'.format(function_name)
log_stream_name = '2016/12/15/[$LATEST]{}'.format(('%032x' % randrange(16**32))[:32])


class identity:
    def __init__(self):
        pass

    cognito_identity_id = 'us-west-2:{}'.format(uuid())
    cognito_identity_pool_id = 'us-west-2:{}'.format(uuid())


class client_context:
    def __init__(self):
        pass

    custom = {'customKey': 'customVal'}
    env = {'envKey': 'envVal'}

    class client:
        def __init__(self):
            pass

        installation_id = '1'
        app_title = 'mainApp'
        app_version_name = '1.0.0'
        app_version_code = 'mainAppCode'
        app_package_name = 'mainPackage'


def get_remaining_time_in_millis():
    return 2999

"""Created By: Andrew Ryan DeFilippis"""

from random import randrange
from uuid import uuid4 as uuid

import os

# Setup for retrieving the Function name (from the top-lvl dir name)
file_path = os.path.realpath(__file__)

aws_request_id = str(uuid())
function_name = file_path.split('/')[-2]
function_version = '$LATEST'
invoked_function_arn = 'arn:aws:lambda:us-west-2:123412341234:function:{}'.format(function_name)
memory_limit_in_mb = '128'
log_group_name = '/aws/lambda/{}'.format(function_name)
log_stream_name = '2016/12/15/[$LATEST]{}'.format(('%032x' % randrange(16 ** 32))[:32])


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

"""Created By: Andrew Ryan DeFilippis"""

print('Lambda cold-start...')

from json import dumps, loads
from boto3 import resource, client
from email import message_from_string
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Disable 'testing_locally' when deploying to AWS Lambda
testing_locally = False
verbose = False


# Define the S3 bucket name and key prefix (Ex. 'users/' *Remember to include the trailing slash)
# Curly-braces "{}" in the key prefix are replaced with the username in the SES Inbound email: 'username'@domain.tld
ses_inbound_s3_bucket = 'email-bucket-name-here'
s3_key_prefix = 'users/{}/messages/'

# Define the regions for the S3 bucket and SES outbound
s3_region = 'us-west-2'
ses_region = 'us-west-2'

# Define where all of the emails will be sent
dest_email_addr = 'email-addr-goes-here@domain.tld'

# The header block above the body of the forwarded email
forward_statement = (
    "---------- Forwarded message ----------\n"
    "From: {}\n"
    "Date: {}\n"
    "Subject: {}\n"
    "To: {}\n"
    "\n"
)


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

    log.event('Creating S3 resource and SES client instances')

    s3_resource = resource('s3', region_name=s3_region)
    ses_client = client('ses', region_name=ses_region)

    for record in event['Records']:
        log.event('Parsing the event record')

        recipient = record['ses']['receipt']['recipients'][0]
        username = recipient.split("@")[0]
        msg_id = record['ses']['mail']['messageId']

        msg_key_prefix = s3_key_prefix.format(username)
        s3_msg_key = msg_key_prefix + msg_id

        log.event('Retrieving email message')

        s3_obj = s3_resource.Object(ses_inbound_s3_bucket, s3_msg_key)
        s3_msg_body = s3_obj.get()["Body"].read()
        msg_body = message_from_string(s3_msg_body)

        log.event('Generating new email message.')

        new_email = MIMEBase("multipart", "mixed")

        new_email['Subject'] = 'Fwd: {}'.format(msg_body['subject'])
        new_email['From'] = recipient
        new_email['To'] = dest_email_addr

        new_email.attach(MIMEText(forward_statement.format(
            msg_body['from'],
            msg_body['date'],
            msg_body['subject'],
            msg_body['to']
        )))

        if msg_body.is_multipart():
            inner_msg = MIMEMultipart("alternative")
            for part in msg_body.get_payload():
                inner_msg.attach(part)
            new_email.attach(inner_msg)
        else:
            new_email.attach(MIMEText(msg_body.get_payload()))

        if verbose is True:
            log.event('Email Message: {}'.format(str(new_email).splitlines()))

        log.event('Sending new email message to SES')

        ses_response = ses_client.send_raw_email(
            Source=new_email['From'],
            Destinations=[new_email['To']],
            RawMessage={
                'Data': new_email.as_string()
            }
        )

        log.event('SES Response: {}'.format(dumps(ses_response)))

    return None


def local_test():
    import context

    with open('event.json', 'r') as f:
        event = loads(f.read())

    print('\nFunction Log:\n')

    lambda_handler(event, context)

if testing_locally is True:
    local_test()

# ses_inbound_forwarder-python

Forward emails that are delivered to SES Inbound to an email address you choose.

This Function requires three variable changes:
* Define the S3 bucket name and key prefix (Ex. 'users/' *Remember to include the trailing slash)
    * Curly-braces "{}" in the key prefix are replaced with the username in the SES Inbound email: 'username'@domain.tld
        * `ses_inbound_s3_bucket = 'email-bucket-name-here'`
        * `s3_key_prefix = 'users/{}/messages/'`
* Define where all of the emails will be sent
    * `dest_email_addr = 'email-addr-goes-here@domain.tld'`

The use of this Function is dependent on the configuration of SES Inbound and Outbound.  Some of the required steps include:
* Verifying a domain in SES Outbound for sending emails via the AWS SES Console.
* Creating DNS records (MX and TXT), enabling DKIM, and enabling SNS notifications for complaints and bounces.
* Verifying a new email address in the SES console, where you will be delivering your emails to (if it is a different domain than the one in step #1).
* Creating a Rule Set in Email Receiving (SES Inbound) with individual rules that specify:
    * A single recipient ('username@domain.tld')
    * A set of actions that include:
        * `S3`
            * With the email bucket specified
            * An object key prefix of `users/username/messages` where the 'username' is the same as the recipient's username
        * `Lambda`
            * With the `ses_inbound_forwarder-python` Function selected
            * Invocation type `Event`

## Includes

**lambda_function.py**
> The main application that is executed by AWS Lambda upon invocation.
* **Note:** Before packaging this code and deploying to AWS Lambda, remove or comment the included code for testing locally.

**event.json**
> Test JSON event data ingested by the main application.
* **NOTE:** This event is a duplicate of the **AWS Lambda Test Event** named `SES Email Receiving`, which can be viewed in the AWS Lambda Console under 'Actions > Configure test event', after creating your Function.

**context.py**
> An emulated AWS Lambda Python Context Object utilized by the main application.

**README.md**
> It's what you are currently reading.

# url_shortening_service

*Application logic for a serverless URL shortening service utilizing AWS API Gateway, Lambda, and DynamoDB.*

----

## Requirements

The use of this Function is dependent on the configuration of AWS API Gateway Proxy Integration to AWS Lambda, and a DynamoDB Table with a Primary Key named `ID`.

## Includes

* **lambda_function.py**
  * *The main application that is executed by AWS Lambda upon invocation.*
  * **Note:** Before packaging this code and deploying to AWS Lambda, set the variable `testing_locally` to `False`.

* **event.json**
  * *Test JSON event data ingested by the main application.*
  * **Note:** This event is a duplicate of the AWS Lambda Test Event `API Gateway AWS Proxy`, but modified to include the `"isBase64Encoded": false` parameter.
  * *The event is configured for adding a new URL to DynamoDB.*

* **context.py**
  * *An emulated AWS Lambda Python Context Object utilized by the main application.*

* **README.md**
  * *It's what you are currently reading.*
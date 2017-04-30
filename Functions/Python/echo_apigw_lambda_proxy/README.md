# echo_apigw_lambda_proxy

*Respond with the ingested API Gateway Lambda Proxy event.*

----

## Includes

* **lambda_function.py**
  * *The main application that is executed by AWS Lambda upon invocation.*
  * **Note:** Before packaging this code and deploying to AWS Lambda, set the variable `testing_locally` to `False`.

* **event.json**
  * *Test JSON event data ingested by the main application.*
  * **Note:** This event is a duplicate of the AWS Lambda Test Event `API Gateway AWS Proxy`, but modified to include the `"isBase64Encoded": false` parameter.

* **context.py**
  * *An emulated AWS Lambda Python Context Object utilized by the main application.*

* **README.md**
  * *It's what you are currently reading.*
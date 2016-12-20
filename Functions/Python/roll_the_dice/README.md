# roll_the_dice

*Roll the dice by going serverless and integrating this Function with API Gateway.*

----

## Requirements

The use of this Function is dependent on the configuration of AWS API Gateway Proxy Integration to AWS Lambda.  Some of the required steps include:
* **Quick but limited integration:**
  * Create the `roll_the_dice-python` Lambda Function.
  * Create an  `API Gateway Lambda Trigger` on the Function.
    * Set API name to `roll_the_dice`.
    * Set Deployment stage to `prod`.
    * Set Security to `open`.
      * This will allow you to make requests without having to use SigV4 signing, but leaves your API endpoint open to being called by anyone who has the external `execute-api` URL.
    * Save the Trigger.
  * Copy the `execute-api` URL from the Triggers tab.
  * In your `web browser`, `Postman`, or `curl`, append the correct query strings to the external `execute-api` URL as `https://1234567890.execute-api.us-west-2.amazonaws.com/roll_the_dice-python?count=5&sides=6`.
  * Send the request, and review the response.
* **Long but fully configurable integration:**
  * Create the `roll_the_dice-python` Lambda Function.
  * Create an API in API Gateway named `roll_the_dice`.
  * Create a sub-resource under the `/` resource called `roll_the_dice-python`.
  * Create an `ANY` type method with a Proxy Integration to the Lambda Function `roll_the_dice-python`.
  * Deploy the API to a `Stage` by going to the `Actions` dropdown and selecting `Deploy API`.
    * For the first time deploying to a Stage, create a new Stage named `dev` or `prod`.
  * In the `Stages` console window, copy the external `execute-api` URL.
  * In your `web browser`, `Postman`, or `curl`, append the correct resource and query strings to the external `execute-api` URL as `https://1234567890.execute-api.us-west-2.amazonaws.com/roll_the_dice-python?count=5&sides=6`.
  * Send the request and review the response.

## Includes

* **lambda_function.py**
  * *The main application that is executed by AWS Lambda upon invocation.*
  * **Note:** Before packaging this code and deploying to AWS Lambda, set the variable `testing_locally` to `False`.

* **event.json**
  * *Test JSON event data ingested by the main application.*
  * **NOTE:** This event is a slightly modified version of the **AWS Lambda Test Event** named `API Gateway AWS Proxy`, which can be viewed in the AWS Lambda Console under 'Actions > Configure test event', after creating your Function.

* **context.py**
  * *An emulated AWS Lambda Python Context Object utilized by the main application.*

* **README.md**
  * *It's what you are currently reading.*
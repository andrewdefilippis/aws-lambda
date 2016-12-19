# echo-python

*Respond with the ingested event.*

----

## Includes

* **lambda_function.py**
  * *The main application that is executed by AWS Lambda upon invocation.*
  * **Note:** Before packaging this code and deploying to AWS Lambda, set the variable `testing_locally` to `False`.

* **event.json**
  * *Test JSON event data ingested by the main application.*

* **context.py**
  * *An emulated AWS Lambda Python Context Object utilized by the main application.*

* **README.md**
  * *It's what you are currently reading.*
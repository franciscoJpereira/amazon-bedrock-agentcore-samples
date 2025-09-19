import utils
#### Create a sample AWS Lambda function that you want to convert into MCP tools
lambda_resp = utils.create_gateway_lambda("lambda_function_code.zip")

if lambda_resp is not None:
    if lambda_resp['exit_code'] == 0:
        print("Lambda function created with ARN: ", lambda_resp['lambda_function_arn'])
    else:
        print("Lambda function creation failed with message: ", lambda_resp['lambda_function_arn'])
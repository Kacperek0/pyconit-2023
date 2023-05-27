import os
import subprocess

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_apigateway as api_gw
)
from constructs import Construct

class PyconIt2023Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        layer = self.create_dependencies_layer('pycon-it-2023')

        table = dynamodb.Table(
            self, 'PullRequests',
            partition_key=dynamodb.Attribute(
                name='timestamp',
                type=dynamodb.AttributeType.STRING
            )
        )

        integration_responses = [
            {
                'statusCode': '200'
            },
            {
                'statusCode': '500',
                'selectionPattern': '^Unexpected error$',
            }
        ]

        method_responses = [
            {
                'statusCode': '200',
                'responseModels': {
                    'application/json': api_gw.Model.EMPTY_MODEL,
                },
            },
            {
                'statusCode': '500',
                'responseModels': {
                    'application/json': api_gw.Model.EMPTY_MODEL,
                },
            }
        ]

        gateway = self.create_api_gateway('pycon-it-2023')

        resource = gateway.root.add_resource('pull-requests')

        functions = (
            'get',
            'post'
        )

        for function_name in functions:
            lambda_function = self.create_lambda_function(
                function_name,
                layer,
                table
            )

            resource.add_method(
                function_name.capitalize(),
                api_key_required=True,
                integration=api_gw.LambdaIntegration(
                    handler=lambda_function,
                    proxy=False,
                    integration_responses=integration_responses,
                ),
                method_responses=method_responses
            )

            if function_name == 'get':
                table.grant_read_data(lambda_function)
            elif function_name == 'post':
                table.grant_write_data(lambda_function)

    def create_api_gateway(
        self,
        gw_name: str,
    ) -> api_gw.RestApi:
        gateway = api_gw.RestApi(
            self, f'{gw_name}Api',
            rest_api_name=gw_name,
        )

        plan = gateway.add_usage_plan(
            f'{gw_name}UsagePlan',
            name=gw_name,
            throttle=api_gw.ThrottleSettings(
                rate_limit=100,
                burst_limit=200
            )
        )

        key = gateway.add_api_key(f'{gw_name}Key')
        plan.add_api_key(key)
        plan.add_api_stage(
            stage=gateway.deployment_stage
        )

        return gateway

    def create_lambda_function(
        self,
        function_name: str,
        lambda_layer: _lambda.LayerVersion,
        dynamo_table: dynamodb.Table
    ) -> _lambda.Function:
        lambda_function = _lambda.Function(
            self,
            f'{function_name}-pycon-it-lambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('code'),
            handler=f'{function_name}.lambda_handler',
            timeout=Duration.seconds(30),
            memory_size=128,
            layers=[
                lambda_layer
            ],
            environment={
                'DYNAMO_TABLE': dynamo_table.table_name
            }
        )

        return lambda_function

    def create_dependencies_layer(self, function_name: str) -> _lambda.LayerVersion:
        requirements_file = 'code/requirements.txt'
        output_dir = '.lambda_dependencies/' + function_name
        # Install requirements for layer in the output_dir
        if not os.environ.get('SKIP_PIP'):
        # Note: Pip will create the output dir if it does not exist
            subprocess.check_call(
            f'pip install -r {requirements_file} -t {output_dir}/python'.split()
            )
        return _lambda.LayerVersion(
            self,
            function_name + '-dependencies',
            code=_lambda.Code.from_asset(output_dir)
        )

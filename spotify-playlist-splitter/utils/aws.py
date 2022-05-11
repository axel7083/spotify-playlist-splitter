import os
from typing import Optional
import boto3


def get_api_gateway_endpoint(
        stack_name: str = os.getenv('AWS_STACK_NAME', 'SpotifyPlaylistSplitter'),
        aws_region: str = os.environ['AWS_REGION']
) -> Optional[str]:
    """
    This method requires the lambda function to have the CloudFormationDescribeStacksPolicy policy granted
    :param stack_name: The stack name the resources are deployed in
    :param aws_region: The region the resources are deployed in
    :return: the url of the api gateway ex: "https://xxxxxxx.execute-api.aaaaaa.amazonaws.com/Prod/api/"
    """
    client = boto3.client("cloudformation", region_name=aws_region)

    try:
        response = client.describe_stacks(StackName=stack_name)
    except Exception as e:
        raise Exception(
            f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{stack_name}" exists.'
        ) from e

    stacks = response["Stacks"]

    stack_outputs = stacks[0]["Outputs"]
    for output in stack_outputs:
        if output["OutputKey"] == 'SpotifyPlaylistSplitterApi':
            return output['OutputValue']

    return None

from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
)
from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Start with a minimal VPC because the ECS cluster, Fargate tasks,
        # and ALB will all need network placement. Keep it inexpensive for
        # now by avoiding NAT gateways until the service layer is added.


#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.infrastructure_stack import InfrastructureStack


app = cdk.App()
InfrastructureStack(
    app,
    "InfrastructureStack",
    # Deploy into the AWS account and region selected by your current CLI
    # credentials. That keeps the tutorial workflow simple: log in with the
    # AWS CLI first, then let CDK target that account and region.
    env=cdk.Environment(
        account=app.node.try_get_context("account") or os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=app.node.try_get_context("region") or os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()

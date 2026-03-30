import aws_cdk as core
import aws_cdk.assertions as assertions

from infrastructure.infrastructure_stack import InfrastructureStack


def test_stack_creates_expected_core_resources() -> None:
    app = core.App(
        context={
            "ecrRepositoryName": "aws-fastapi-foundation",
            "imageTag": "0.1.1",
        }
    )
    stack = InfrastructureStack(app, "infrastructure")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::ECS::Cluster", 1)
    template.resource_count_is("AWS::Logs::LogGroup", 1)
    template.resource_count_is("AWS::ElasticLoadBalancingV2::LoadBalancer", 1)
    template.resource_count_is("AWS::ECS::Service", 1)


def test_stack_configures_health_check_and_autoscaling() -> None:
    app = core.App(
        context={
            "ecrRepositoryName": "aws-fastapi-foundation",
            "imageTag": "0.1.1",
        }
    )
    stack = InfrastructureStack(app, "infrastructure")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties(
        "AWS::ElasticLoadBalancingV2::TargetGroup",
        {
            "HealthCheckPath": "/health",
        },
    )
    template.has_resource_properties(
        "AWS::ApplicationAutoScaling::ScalableTarget",
        {
            "MinCapacity": 1,
            "MaxCapacity": 3,
        },
    )

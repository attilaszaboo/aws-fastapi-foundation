import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions

from infrastructure.infrastructure_stack import InfrastructureStack


@pytest.fixture(scope="module")
def template() -> assertions.Template:
    app = core.App(
        context={
            "ecrRepositoryName": "aws-fastapi-foundation",
            "imageTag": "0.1.1",
        }
    )
    stack = InfrastructureStack(app, "infrastructure")
    return assertions.Template.from_stack(stack)


def test_stack_creates_expected_core_resources(template: assertions.Template) -> None:
    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::ECS::Cluster", 1)
    template.resource_count_is("AWS::Logs::LogGroup", 1)
    template.resource_count_is("AWS::ElasticLoadBalancingV2::LoadBalancer", 1)
    template.resource_count_is("AWS::ECS::Service", 1)


def test_stack_configures_health_check_and_autoscaling(template: assertions.Template) -> None:
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

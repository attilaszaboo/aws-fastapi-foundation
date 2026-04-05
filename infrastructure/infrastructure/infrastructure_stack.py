from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
)
from constructs import Construct


class InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Keep the configuration surface small for the first deployment.
        # The repository name and image tag can be overridden at deploy time:
        #   cdk deploy -c ecrRepositoryName=aws-fastapi-foundation -c imageTag=<image_tag>
        ecr_repository_name = (
            self.node.try_get_context("ecrRepositoryName")
            or "aws-fastapi-foundation"
        )
        image_tag = self.node.try_get_context("imageTag") or "latest"

        # The VPC is the network boundary for the whole service.
        #
        # For the first milestone, keep it inexpensive and easy to inspect:
        # - use two Availability Zones for a production-shaped layout
        # - create only public subnets for now
        # - do not create NAT gateways yet, because they add fixed cost
        #
        # Later, when you want a more production-like setup, you can move the
        # ECS tasks to private subnets and add NAT gateways or VPC endpoints.
        vpc = ec2.Vpc(
            self,
            "FoundationVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        # The ECS cluster is a logical home for container services.
        # Fargate is the compute engine that will run the tasks for us, so
        # we do not need to manage EC2 instances in this learning project.
        cluster = ecs.Cluster(
            self,
            "FoundationCluster",
            vpc=vpc,
            container_insights=True,
        )

        # Put the application logs in a dedicated CloudWatch log group so the
        # running service is easier to inspect and clean up later.
        log_group = logs.LogGroup(
            self,
            "FoundationLogGroup",
            log_group_name="/aws/ecs/aws-fastapi-foundation",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Reuse the ECR repository that the GitHub release workflow already
        # pushes images into. This keeps build/publish separate from runtime.
        repository = ecr.Repository.from_repository_name(
            self,
            "FoundationRepository",
            repository_name=ecr_repository_name,
        )

        # This higher-level construct wires the main runtime pieces together:
        # - ECS service
        # - task definition
        # - Application Load Balancer
        # - listener
        # - target group
        #
        # That keeps the first deployment focused on architecture rather than
        # boilerplate ELB and ECS resource wiring.
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FoundationService",
            cluster=cluster,
            public_load_balancer=True,
            desired_count=1,
            cpu=256,
            memory_limit_mib=512,
            assign_public_ip=True,
            task_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    repository,
                    tag=image_tag,
                ),
                container_port=8000,
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="app",
                    log_group=log_group,
                ),
            ),
        )

        # The ALB should treat /health as the source of truth for whether the
        # application is ready to receive traffic.
        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
        )

        # Let ECS add or remove tasks based on CPU utilization so the service
        # can respond to load without changing the infrastructure manually.
        # The minimum stays at one task so the API remains available, and the
        # maximum is intentionally small for this learning project.
        scaling = service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=3,
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=60,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        # Stack outputs make the deployment result easy to discover after
        # cdk deploy finishes.
        CfnOutput(self, "VpcId", value=vpc.vpc_id)
        CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        CfnOutput(self, "ServiceName", value=service.service.service_name)
        CfnOutput(
            self,
            "LoadBalancerDnsName",
            value=service.load_balancer.load_balancer_dns_name,
        )
        CfnOutput(self, "ImageTag", value=image_tag)

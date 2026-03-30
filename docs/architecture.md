# Architecture

This document describes:

- the current repository architecture
- the current deployed AWS architecture
- why ECS on Fargate was chosen over EC2, Lambda, and App Runner
- how CI, ECR, IAM, networking, ALB, health checks, and observability fit together

It is written as a learning document and as a concise reference for the project.

## 1. Current repository architecture

This repository currently contains:

- a small FastAPI application with `/hello`, `/health`, `/version`, and `/docs`
- unit tests with `pytest`
- linting and formatting with `ruff`
- Docker packaging
- GitHub Actions CI
- GitHub Actions release workflow for publishing images to Amazon ECR
- GitHub Actions deploy workflow for promoting a chosen image tag to ECS
- AWS CDK infrastructure code for ECS Fargate deployment

Application characteristics:

- stateless
- no database
- no authentication
- no background workers
- packaged as a single Docker container

## 2. Current deployed AWS architecture

The currently deployed system is:

```text
Developer -> GitHub -> GitHub Actions -> Amazon ECR -> ECS Service on Fargate -> ALB -> Internet client
                                                           |
                                                           -> CloudWatch Logs
```

Implemented pieces:

1. GitHub Actions CI validates linting, tests, and Docker builds.
2. A manual GitHub Actions release workflow publishes versioned images to Amazon ECR using GitHub OIDC and an AWS IAM role.
3. A separate manual GitHub Actions deploy workflow runs `cdk deploy` with a chosen image tag and smoke-tests the public `/health` endpoint.
4. AWS CDK defines and updates the runtime infrastructure.
5. ECS runs the FastAPI container on Fargate.
6. An internet-facing Application Load Balancer exposes the service publicly.
7. The ALB health check uses `/health`.
8. Container logs are written to CloudWatch Logs.
9. ECS service autoscaling is configured using CPU utilization.

Current network layout:

1. A VPC spans two Availability Zones.
2. The ALB runs in public subnets.
3. The Fargate tasks also currently run in public subnets.
4. The Fargate tasks are currently assigned public IPs.

This is a deliberate simplification for the first deployed version because it:

- keeps the runtime path easy to understand
- avoids NAT gateway cost
- reduces the number of moving parts during initial learning

## 3. Why ECS on Fargate for this project

For this project, ECS on Fargate is the best fit because it matches the learning goal better than EC2, Lambda, or App Runner.

### Why not EC2

EC2 would add host-management concerns such as:

- instance sizing
- OS patching
- cluster capacity management
- instance lifecycle

Those are real production concerns, but they are not the focus of this project. Fargate removes that layer and lets the project focus on containerized application delivery.

### Why not Lambda

Lambda can run container images, but it changes the delivery and runtime model.

Reasons:

1. This app is currently packaged as a continuously running Uvicorn-hosted web service.
2. Lambda would push the architecture toward API Gateway or Lambda Function URLs instead of ECS + ALB.
3. The goal here is to learn a container-service deployment model, not a serverless function model.

### Why not App Runner

App Runner is simpler, but it hides more of the platform building blocks.

Reasons:

1. ECS + Fargate + ALB is closer to the architecture language many teams use for containerized APIs.
2. This project is partly about learning the moving parts directly: VPC, task definitions, security groups, target groups, and health checks.
3. App Runner is faster to get running, but ECS on Fargate provides more architectural learning value for this project.

## 4. How the architecture fits together

### CI

CI validates:

- linting
- tests
- Docker build

This protects the deployable artifact before anything is published.

### ECR

Amazon ECR is the image registry.

Role in the architecture:

1. GitHub Actions pushes versioned images there.
2. ECS task definitions reference those images.
3. Fargate pulls the image at task startup.

This cleanly separates build, storage, and runtime.

### IAM

IAM provides the security boundaries.

In this project, the main roles are:

1. GitHub Actions role
   - assumed through GitHub OIDC
   - allows the workflow to publish images to ECR

2. ECS task execution role
   - allows ECS/Fargate to pull images from ECR
   - allows ECS/Fargate to send logs to CloudWatch Logs

3. ECS task role
   - would be used by the application code if it needed AWS API access
   - currently minimal because the MVP app does not use AWS SDK calls

### Networking

The current deployed network design is:

1. an internet-facing ALB
2. ECS tasks in public subnets
3. security groups controlling ingress between the ALB and the tasks

### ALB

The Application Load Balancer is the public traffic entry point.

It provides:

- a public DNS name
- layer-7 HTTP routing
- health checks
- routing only to healthy targets

That makes it a good fit for a FastAPI web API.

### Health checks

The most important health check currently is the ALB target group health check against `/health`.

That means:

- if the app responds successfully on `/health`, the task can receive traffic
- if it does not, the ALB stops sending traffic to it

### Observability

The current observability baseline is:

- CloudWatch Logs for container logs
- ECS service and task health
- ALB target health

That is enough for the current project phase.

## 5. End-to-end request flow

Runtime request path:

1. A client sends a request to the ALB DNS name.
2. The ALB listener receives the request.
3. The ALB forwards the request to the target group.
4. The target group routes the request to a healthy ECS task.
5. The FastAPI app handles the request on port `8000`.
6. The response returns through the ALB to the client.

## 6. End-to-end deployment flow

Current deployment flow:

1. Code changes are committed to GitHub.
2. GitHub Actions CI runs linting, tests, and Docker build validation.
3. A manual release workflow builds and pushes a tagged image to ECR.
4. A separate manual deploy workflow runs `cdk deploy` with the chosen image tag.
5. CDK updates the ECS task definition and ECS service to use that image tag.
6. ECS starts the new Fargate task revision.
7. The ALB health check confirms the new task is healthy.
8. Traffic is routed to healthy task(s).
9. Logs are written to CloudWatch Logs.

## 7. Why this architecture is useful for learning

This project teaches the modern cloud-native equivalents of concerns that also exist in mature software delivery more broadly:

- deployment pipeline
- artifact management
- environment configuration
- runtime ownership
- system boundaries
- failure modes
- observability
- operational tradeoffs

It is not just "learning AWS." It is learning how a modern backend service is built, packaged, deployed, and operated.

## 8. Planned evolution

The most likely next improvements are:

1. move ECS tasks to private subnets and add the required egress path
2. add HTTPS with ACM and DNS
3. expand the application with real business logic

## 9. How CDK should authenticate to AWS

For local CDK use, prefer the same authentication methods that the AWS CLI uses:

- `aws configure`
- named AWS CLI profiles
- AWS SSO

CDK can also use standard AWS environment variables such as:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `AWS_REGION`

But do not store AWS credentials in a project `.env` file.

Preferred local workflow:

1. authenticate with the AWS CLI
2. verify with `aws sts get-caller-identity`
3. run `cdk synth`, `cdk diff`, or `cdk deploy`

## Official references

- AWS App Runner source image:
  - https://docs.aws.amazon.com/apprunner/latest/dg/service-source-image.html
- AWS App Runner overview:
  - https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html
- Amazon ECS task execution IAM role:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
- Amazon ECS task IAM role:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html
- IAM roles for Amazon ECS:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-ecs-iam-role-overview.html
- ECS service load balancing:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html
- Using an ALB with ECS:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/alb.html
- ECS container health checks:
  - https://docs.aws.amazon.com/AmazonECS/latest/developerguide/healthcheck.html
- Application Load Balancer overview:
  - https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html

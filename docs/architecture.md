# Architecture

This document describes:

- the current architecture of this repository
- the current deployed architecture in AWS
- the intended target architecture on AWS
- why ECS on Fargate is the preferred deployment path for this project
- how CI, ECR, IAM, networking, ALB, health checks, and observability fit together

It is written as a learning document and as a foundation for interview preparation.

## 1. Current architecture

The repository currently implements a minimal containerized FastAPI service with CI and image publishing.

### Application layer

The application is a small FastAPI API with these endpoints:

- `/hello`
- `/health`
- `/version`
- `/docs`

Characteristics:

- stateless
- no database
- no authentication
- no background workers
- packaged as a single Docker container

### Build and test layer

The repository currently uses:

- `uv` for dependency management and execution
- `ruff` for linting and formatting
- `pytest` for unit tests
- Docker for packaging

CI currently does the following on pull requests and `main`:

1. install dependencies
2. run Ruff
3. run pytest
4. build the Docker image

This is useful because it verifies both application correctness and container build correctness before deployment.

### Image publishing layer

The release workflow currently:

1. is manually triggered
2. assumes an AWS IAM role using GitHub OIDC
3. logs into Amazon ECR
4. builds the Docker image
5. pushes the image to ECR using a chosen tag

This means the repository already supports:

- reproducible container builds
- versioned image publishing
- secure GitHub Actions to AWS authentication without long-lived AWS keys

### Important architectural limitation today

The system currently stops at:

- "image is stored in ECR"

It does not yet provide:

- a running container service in AWS
- a public endpoint
- load balancing
- service health management
- runtime observability through deployed infrastructure

That is the gap the ECS Fargate + ALB architecture will close.

## 2. Current deployed architecture in AWS

The first deployed AWS version is intentionally simpler than the longer-term target architecture.

Current deployed shape:

```text
Internet client -> ALB -> ECS Service on Fargate -> FastAPI container
                                   |
                                   -> CloudWatch Logs
```

Implemented characteristics:

1. CDK defines the infrastructure.
2. The container image is pulled from Amazon ECR.
3. ECS runs the FastAPI container on Fargate.
4. An internet-facing Application Load Balancer exposes the service publicly.
5. The ALB health check uses `/health`.
6. Container logs are written to CloudWatch Logs.

Current networking shape:

1. A VPC spans two Availability Zones.
2. The ALB runs in public subnets.
3. The Fargate tasks also currently run in public subnets.
4. The Fargate tasks are currently assigned public IPs.

This is not the final intended networking design.

It was chosen intentionally for the first iteration because:

- it keeps the deployment path easier to understand
- it avoids NAT gateway cost during early learning
- it reduces the number of moving parts while validating the containerized service end to end

So the current deployed architecture should be understood as:

- a simplified first milestone that proves the runtime path works

## 3. Target architecture

The intended target is:

```text
Developer -> GitHub -> GitHub Actions -> Amazon ECR -> ECS Service on Fargate -> ALB -> Internet client
                                                           |
                                                           -> CloudWatch Logs
```

More specifically:

1. GitHub Actions builds and pushes a versioned Docker image to Amazon ECR.
2. AWS CDK defines and deploys the runtime infrastructure.
3. An ECS task definition references the ECR image.
4. ECS on Fargate runs one or more copies of the container.
5. An Application Load Balancer exposes a public HTTP or HTTPS endpoint.
6. The ALB forwards traffic to healthy ECS tasks.
7. Container logs go to CloudWatch Logs.

The intended networking shape is more production-like:

1. A VPC spans at least two Availability Zones.
2. The ALB is internet-facing and runs in public subnets.
3. ECS tasks run in private subnets.
4. Security groups restrict task access so only the ALB can reach the application port.
5. NAT gateways or VPC endpoints are introduced only when needed.

This target shape is not necessary to prove the first deployment, but it is the more realistic direction for later refinement.

## 4. Why ECS on Fargate for this project

For this project, ECS on Fargate is the best fit because it matches my learning goals better than EC2, Lambda, or App Runner.

### Why not EC2

EC2 would mean managing the underlying hosts myself.

That adds concerns such as:

- instance sizing
- OS patching
- instance lifecycle
- cluster capacity management
- AMI selection
- more operational overhead

Those are real production concerns, but they are not the main point of this project.

This project is trying to teach:

- containerized API delivery
- AWS service composition
- IAM
- networking
- CI/CD
- production-shaped deployment flow

Fargate is better because it removes the host-management layer and lets me focus on the application service architecture.

### Why not Lambda

Lambda can run container images, but it is not the best conceptual fit for this service.

Reasons:

1. The app is written as a continuously running web server.
   - FastAPI in this repo is packaged to run under Uvicorn as a long-running process.
   - Lambda uses an event-driven execution model instead of a continuously running container service.

2. Lambda would introduce a different integration model.
   - You would usually front it with API Gateway or a Lambda Function URL.
   - That is a different architecture from ECS + ALB.

3. Lambda is a weaker fit for my stated production-style learning path.
   - ECS teaches container service deployment directly.
   - Lambda teaches serverless function delivery, which is valuable but different.

4. I want to learn a stack often seen in container-based backend platforms.
   - ECS + Fargate + ALB is directly aligned with that.

Lambda is a valid AWS option, but it would change the architecture and the learning target.

### Why not App Runner

App Runner is the simplest route from container image to public service. AWS states that App Runner can take a source image from ECR and handle starting, running, scaling, and load balancing the service.

That simplicity is the main reason not to choose it here.

Reasons:

1. App Runner hides more of the underlying platform decisions.
   - That is good for speed.
   - It is weaker for learning the pieces that matter in production discussions.

2. ECS + Fargate + ALB is closer to the architecture vocabulary many teams actually use for containerized APIs on AWS.

3. This project is partly about technical credibility.
   - Being able to explain VPC, subnets, task definitions, security groups, target groups, and ALB health checks is more valuable for my learning goal than saying "App Runner deployed it for me."

4. My current project narrative already points toward ECS/Fargate/ALB.
   - Choosing that path keeps the architecture coherent.

App Runner is a good platform for fast results. ECS on Fargate is the better platform for deliberate learning in this project.

## 5. How the architecture fits together

This section explains the important moving parts and how requests and deployments flow through the system.

### CI

CI validates the code before deployment.

In this project, CI should answer:

- does the app still lint cleanly?
- do the tests still pass?
- does the container still build?

This matters because a deployment pipeline that publishes broken images is not trustworthy.

CI is the gate that protects the deployable artifact.

### ECR

Amazon ECR is the image registry.

Role in the architecture:

1. GitHub Actions pushes versioned images there.
2. ECS task definitions reference images stored there.
3. Fargate pulls the image at task startup.

This separates:

- build time
- image storage
- runtime execution

That separation is important in production systems because it gives you a stable artifact that can be promoted and redeployed.

### IAM

IAM is the permission system that ties the workflow together safely.

In this architecture, there are several distinct permission boundaries:

1. GitHub Actions to AWS
   - GitHub Actions assumes an IAM role using OIDC.
   - This lets the workflow push images to ECR without storing long-lived AWS secrets in GitHub.

2. ECS task execution role
   - According to AWS ECS documentation, the task execution role is what lets ECS and Fargate pull images from private ECR and send logs to CloudWatch Logs.
   - This role is for the platform to run the task, not for your app code.

3. ECS task role
   - This role is for the application code inside the container if it needs AWS API access.
   - For the current MVP, you likely do not need much or any task-role permission because the app has no persistence and no AWS SDK usage.

The architectural lesson is that IAM roles should reflect separate responsibilities rather than one broad permission bucket.

### Networking

Networking provides controlled reachability.

The longer-term intended network design is:

1. A VPC spans at least two Availability Zones.
2. The ALB is internet-facing.
3. ECS tasks run in private subnets.
4. Security groups enforce allowed traffic.

Typical security group flow:

1. The ALB security group allows inbound `80` or `443` from the internet.
2. The ECS task security group allows inbound `8000` only from the ALB security group.

That means:

- clients talk to the ALB
- the ALB talks to the tasks
- the tasks are not directly exposed to the internet

This is an important production pattern because it centralizes public ingress and reduces unnecessary exposure.

The current deployed first iteration is simpler:

1. the ALB is public
2. the ECS tasks are also in public subnets
3. the ECS tasks currently have public IPs
4. the service still relies on the ALB for normal ingress

This is acceptable for the first milestone, but it is not the ideal final network posture.

### ALB

The Application Load Balancer is the public traffic entry point.

Why it exists:

- it provides a stable public DNS name
- it routes HTTP/HTTPS traffic to ECS tasks
- it performs health checks
- it only sends traffic to healthy targets

AWS documents ALB as a layer-7 load balancer for HTTP/HTTPS traffic. That makes it the right fit for a FastAPI web API.

In the first version of this project, ALB gives you:

- a public endpoint that `curl` can call
- a realistic way to expose the service
- a place to add HTTPS later

### Health checks

Health checks exist at two related but distinct layers.

1. ALB target group health checks
   - These are external health checks.
   - The ALB calls something like `/health`.
   - If the target is unhealthy, the ALB stops routing traffic to it.

2. ECS container health checks
   - These are internal checks run by ECS inside the container.
   - AWS documents these as commands executed locally in the container.
   - If the container is unhealthy, ECS can replace the task.

For the first milestone, ALB health checks are the most important because they directly control whether the service receives traffic.

The existing `/health` endpoint makes this straightforward.

### Observability

For this project, observability starts with the basics:

- container logs in CloudWatch Logs
- ECS service status
- task health
- ALB target health

This is enough to answer first-line operational questions such as:

- did the container start?
- is the app responding?
- is the target healthy?
- are requests reaching the service?

Later, observability can expand to:

- structured application logging
- metrics and alarms
- ALB access logs
- tracing

For now, CloudWatch logs plus health status is the correct minimum viable observability setup.

## 6. End-to-end request flow

Here is the runtime request path once the AWS deployment exists:

1. A client sends `GET /hello` to the ALB DNS name.
2. The ALB listener receives the request.
3. The ALB forwards the request to the target group.
4. The target group routes the request to a healthy ECS task.
5. The FastAPI app inside the Fargate task handles the request on port `8000`.
6. The response flows back through the ALB to the client.

## 7. End-to-end deployment flow

Here is the deployment path for the target design:

1. Code changes are committed to GitHub.
2. CI runs lint, tests, and Docker build validation.
3. A release workflow builds and pushes a tagged image to ECR.
4. CDK deploys or updates the ECS task definition and ECS service.
5. ECS starts new Fargate task(s) using the specified ECR image.
6. The ALB health check verifies the new task is healthy.
7. Traffic is routed to healthy task(s).
8. Logs are written to CloudWatch Logs.

This connects the following:

- source control
- build validation
- artifact registry
- infrastructure as code
- runtime deployment
- operational verification

## 8. Why this architecture is good for learning

For my background, this architecture is useful because it teaches the modern cloud-native equivalents of concerns I already understand from mature software delivery:

- deployment pipeline
- artifact management
- environment configuration
- runtime ownership
- system boundaries
- failure modes
- observability
- operational tradeoffs

It is not just "learning AWS." It is learning how modern backend delivery systems are composed.

## 9. Interview framing for an engineering manager

For engineering manager positioning, the value is not "I now know CDK deeply."

The stronger framing is:

- I used a deliberately small project to understand the practical mechanics of modern AWS container delivery.
- I wanted hands-on exposure to how CI, container registries, IAM, networking, load balancing, health checks, and runtime observability fit together.
- I chose ECS on Fargate behind an ALB because it is production-shaped without adding unnecessary EC2 host management.
- I used CDK so the infrastructure was explicit, reviewable, and repeatable.

That framing works because it signals:

- technical currency
- practical judgment
- respect for operational detail
- ability to reason across organizational boundaries, not just write application code

### What to emphasize in interviews

Emphasize these points:

1. You intentionally chose a small service so the infrastructure and delivery mechanics were easy to inspect.
2. You selected ECS on Fargate over simpler and more abstract options because you wanted direct exposure to the core AWS building blocks used in container-based systems.
3. You understand the difference between:
   - build artifact creation
   - image publishing
   - infrastructure provisioning
   - runtime deployment
   - health validation
4. You can explain the security and operational boundaries clearly:
   - GitHub OIDC role
   - ECS execution role
   - task role
   - ALB security group
   - task security group

### What not to claim

Avoid claiming:

- deep production AWS operations experience from one project
- advanced CDK mastery
- large-scale SRE depth

A more credible statement is:

- I built this to become conversant and hands-on with the current cloud-native delivery model, and I can explain the architecture, tradeoffs, and operational workflow clearly.

That is honest and strong.

## 10. Planned evolution

The architecture should evolve in this order:

1. ECS Fargate + ALB over HTTP in the current simplified network layout
2. CloudWatch log verification and smoke testing
3. move ECS tasks to private subnets and add the required egress path
4. HTTPS with ACM and Route 53
5. small autoscaling policy
6. deployment automation from GitHub Actions

This order keeps learning incremental and keeps the system understandable.

## 11. How CDK should authenticate to AWS

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

For this project, the preferred approach is:

1. authenticate with the AWS CLI
2. verify with `aws sts get-caller-identity`
3. run `cdk synth`, `cdk diff`, or `cdk deploy`

That is cleaner, safer, and closer to real-world usage than keeping long-lived AWS keys in the repository.

## Official references

These sources were used for the service comparisons and architecture notes:

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

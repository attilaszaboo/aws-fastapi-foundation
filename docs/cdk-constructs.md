# CDK Constructs

This document explains the CDK construct model at the level you need for this project:

- low-level vs high-level constructs
- why `ApplicationLoadBalancedFargateService` is useful
- how to discover what CDK code to write
- how to find the right class in the Python API reference

## 1. What a construct is

In CDK, a construct is a building block.

A construct can represent:

- one AWS resource
- a small helper abstraction
- a higher-level pattern made of many AWS resources

Examples:

- `aws_cdk.aws_ec2.Vpc`
- `aws_cdk.aws_ecs.Cluster`
- `aws_cdk.aws_logs.LogGroup`
- `aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService`

The key idea is:

- some constructs map closely to a single AWS resource
- some constructs create several resources together

## 2. Low-level vs high-level constructs

### Low-level constructs

These are closer to raw AWS resources.

Examples:

- `aws_cdk.aws_ec2.Vpc`
- `aws_cdk.aws_ecs.Cluster`
- `aws_cdk.aws_logs.LogGroup`
- `aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer`

You use these when you want direct control over individual infrastructure components.

### High-level constructs

These are convenience patterns that wire multiple resources together.

Example:

- `aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService`

This is useful because it can create or wire:

- an ECS Fargate service
- a task definition
- an Application Load Balancer
- a listener
- a target group

This means you write less code and focus on architecture instead of repetitive plumbing.

## 3. Why `ApplicationLoadBalancedFargateService` is a good fit here

For this project, that construct is a good choice because your goal is not to become an expert in every ELB and ECS property immediately.

Your goal is:

- deploy a small FastAPI container on ECS Fargate
- put an ALB in front of it
- keep the system understandable

`ApplicationLoadBalancedFargateService` gets you there with a small amount of code while still exposing the important concepts:

- cluster
- service
- task definition
- load balancer
- target group

That is exactly the right abstraction level for a first deployment.

## 4. What resources you will likely define directly

Even when you use `ApplicationLoadBalancedFargateService`, you will still often define some supporting resources explicitly.

For this project, the likely set is:

- `aws_cdk.aws_ec2.Vpc`
- `aws_cdk.aws_ecs.Cluster`
- `aws_cdk.aws_logs.LogGroup`
- `aws_cdk.aws_ecr.Repository` reference to your existing ECR repo
- `aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService`

That gives you a good balance:

- direct control over the core environment
- less boilerplate for ECS + ALB wiring

## 5. How to learn what CDK code to write

The practical way is:

1. decide what AWS architecture you want
2. list the main AWS resources involved
3. map each AWS service to its CDK module and class
4. read one API page per resource
5. start from the smallest working example

For your project, that looks like this:

### AWS architecture you want

- VPC
- ECS cluster
- Fargate service
- ALB
- CloudWatch logs
- existing ECR image

### CDK classes that likely map to that

- VPC -> `aws_cdk.aws_ec2.Vpc`
- ECS cluster -> `aws_cdk.aws_ecs.Cluster`
- Log group -> `aws_cdk.aws_logs.LogGroup`
- ECR repo -> `aws_cdk.aws_ecr.Repository`
- Fargate + ALB pattern -> `aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService`

From there, you only need to learn a few constructor arguments at first.

## 6. How to find the CDK Python API page for a class

This is the lookup pattern:

1. identify the Python import path
2. search that exact class name with "AWS CDK Python"
3. open the Python API reference page

### Example: VPC

Python import:

```python
from aws_cdk import aws_ec2 as ec2
```

Class:

```python
ec2.Vpc
```

What to search:

```text
AWS CDK Python Vpc aws_ec2
```

Official API page:

- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/Vpc.html

### Example: ECS cluster

Python import:

```python
from aws_cdk import aws_ecs as ecs
```

Class:

```python
ecs.Cluster
```

Official API page:

- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Cluster.html

### Example: CloudWatch log group

Python import:

```python
from aws_cdk import aws_logs as logs
```

Class:

```python
logs.LogGroup
```

Official API page:

- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_logs/LogGroup.html

### Example: Fargate + ALB pattern

Python import:

```python
from aws_cdk import aws_ecs_patterns as ecs_patterns
```

Class:

```python
ecs_patterns.ApplicationLoadBalancedFargateService
```

Official API page:

- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html

## 7. How to read a CDK API page without getting overwhelmed

When you open a CDK class page, do not try to read everything.

Read in this order:

1. one-line description
2. example section
3. constructor signature
4. only the few arguments you need right now

For example, on `ApplicationLoadBalancedFargateService`, the first arguments to care about are:

- `cluster`
- `desired_count`
- `cpu`
- `memory_limit_mib`
- `task_image_options`
- `public_load_balancer`

For `task_image_options`, the important fields are typically:

- `image`
- `container_port`
- `log_driver`

Everything else can wait until you actually need it.

## 8. The practical code-discovery loop

A good way to work is:

1. pick one resource
2. find its class page
3. copy the smallest example
4. adapt only the required properties
5. run `cdk synth`
6. inspect what CDK generated

That is much more effective than trying to understand the entire API first.

## 9. What you probably need first for this repo

If you want the shortest path to a working stack, learn these five classes first:

1. `aws_cdk.aws_ec2.Vpc`
2. `aws_cdk.aws_ecs.Cluster`
3. `aws_cdk.aws_logs.LogGroup`
4. `aws_cdk.aws_ecr.Repository`
5. `aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService`

That is enough for a solid first deployment.

## 10. Recommended learning approach for your project

Do not start with the full CDK docs.

Start with:

1. `Vpc`
2. `Cluster`
3. `ApplicationLoadBalancedFargateService`

Then add:

4. `LogGroup`
5. `Repository`

That keeps the learning surface small while still teaching the important infrastructure shape.

## Official references

- `Vpc`:
  - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/Vpc.html
- `Cluster`:
  - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs/Cluster.html
- `LogGroup`:
  - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_logs/LogGroup.html
- `Repository`:
  - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecr/Repository.html
- `ApplicationLoadBalancedFargateService`:
  - https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html

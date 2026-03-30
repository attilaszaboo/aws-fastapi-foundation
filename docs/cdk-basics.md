# CDK Basics

This document explains the minimum AWS CDK concepts you need for this project:

- CDK app vs stack
- `cdk synth`
- `cdk diff`
- `cdk deploy`

The goal is not to cover all of CDK. The goal is to give you a working mental model so you can use it without getting lost in the documentation.

## 1. What CDK is

AWS CDK lets you define AWS infrastructure in code.

Instead of writing raw CloudFormation YAML or JSON, you write Python code that describes resources such as:

- VPCs
- ECS clusters
- Fargate services
- load balancers
- IAM roles

CDK then generates CloudFormation from that code and uses CloudFormation to create or update the resources in AWS.

The most important mental model is:

```text
CDK Python code -> CloudFormation template -> AWS resources
```

So CDK is not a separate provisioning engine. It is a higher-level way to define CloudFormation stacks.

## 2. CDK app vs stack

This is the most important concept to understand first.

### CDK app

A CDK app is the top-level program.

It is the Python entry point that creates one or more stacks.

In your CDK project, this is typically the file:

- `infrastructure/app.py`

The app is responsible for:

- starting the CDK program
- creating stack objects
- optionally passing configuration into those stacks

Think of the app as:

- the root container for your infrastructure definition

### CDK stack

A stack is a deployable unit of infrastructure.

A stack usually groups resources that belong together and are created and updated together.

Examples of what a stack might contain:

- one VPC
- one ECS cluster
- one ALB
- one ECS service

Or, in larger systems, separate stacks might exist for:

- networking
- application runtime
- databases

For your project, one stack is enough.

Think of a stack as:

- one CloudFormation stack
- one unit you can `synth`, `diff`, `deploy`, and `destroy`

### App vs stack in one sentence

- app = the whole CDK program
- stack = one deployable chunk of AWS infrastructure defined by that program

### Example mental picture

```text
app.py
  -> creates InfrastructureStack
       -> defines VPC, ECS cluster, ALB, Fargate service
```

## 3. What happens when CDK runs

When you run a CDK command, CDK executes your app code.

That means:

1. Python runs `app.py`
2. `app.py` creates one or more stacks
3. each stack creates AWS resource definitions in memory
4. CDK converts that into a CloudFormation template

That is why CDK is often described as "infrastructure as code" rather than "configuration only."

You are writing a program that produces infrastructure definitions.

## 4. `cdk synth`

### What it does

`cdk synth` means:

- synthesize the CloudFormation template

It runs your CDK app and outputs the CloudFormation template that CDK generated from your Python code.

### Why it exists

It lets you answer:

- "What exactly will CDK generate from my code?"

This is useful because CDK can be abstract.
High-level constructs can create many AWS resources behind the scenes.

For example, a single higher-level ECS pattern can create:

- load balancer
- listener
- target group
- ECS service
- task definition
- roles
- log group wiring

`cdk synth` lets you inspect the resulting template.

### How to think about it

Think of `cdk synth` as:

- "compile my infrastructure code into CloudFormation"

### When to use it

Use it when:

- you want to confirm your CDK code is valid
- you want to inspect what resources are being generated
- you want to debug why CDK is creating something unexpected

### Typical command

```bash
cdk synth
```

### Output

You will see a generated CloudFormation template in the terminal, and CDK also writes output under:

- `cdk.out/`

## 5. `cdk diff`

### What it does

`cdk diff` compares:

- what is currently deployed in AWS
- what your current local CDK code would deploy

### Why it exists

It lets you answer:

- "If I deploy now, what will change?"

This is one of the most useful commands because it reduces the risk of making infrastructure changes blindly.

### How to think about it

Think of `cdk diff` as:

- "preview the infrastructure changes"

It is similar in purpose to checking a Git diff before committing code.

### What kinds of changes it can show

- new resources
- deleted resources
- modified resource properties
- IAM policy changes

### When to use it

Use it before `cdk deploy`, especially when:

- you changed resource definitions
- you changed ports, subnets, security groups, or IAM
- you are learning and want to understand the impact of your code

### Typical command

```bash
cdk diff
```

### Why it matters for this project

In this repo, `cdk diff` will help you see whether a code change would:

- replace the ECS service
- change the ALB
- alter security groups
- update the task definition

That is exactly the kind of change-awareness you want in production-style work.

## 6. `cdk deploy`

### What it does

`cdk deploy` creates or updates the stack in AWS.

Under the hood, CDK:

1. runs the app
2. synthesizes the CloudFormation template
3. submits the stack to CloudFormation
4. waits for CloudFormation to create or update resources

### Why it exists

It is the command that actually applies your infrastructure changes.

### How to think about it

Think of `cdk deploy` as:

- "take my CDK code and make AWS match it"

### Typical command

```bash
cdk deploy
```

You can also deploy a specific stack by name if your app contains more than one.

### What you should expect

On first deploy:

- resources get created

On later deploys:

- only the changed resources are updated, if possible

### Important detail

`cdk deploy` does not directly create resources itself. CloudFormation performs the actual stack create or update.

That matters because when something fails, you often investigate in:

- CDK output
- CloudFormation events
- the AWS console for the affected service

## 7. Practical workflow

For normal day-to-day use, the workflow is usually:

1. edit CDK code
2. run `cdk synth`
3. run `cdk diff`
4. run `cdk deploy`

## 8. How this maps to your project

For this repository, the likely future CDK flow will be:

### App

Your CDK app will live under:

- `infrastructure/app.py`

Its job is to instantiate your stack.

### Stack

Your stack will likely define:

- VPC
- ECS cluster
- Fargate service
- ALB
- security groups
- log group

### `cdk synth`

Use it to inspect the generated CloudFormation for that infrastructure.

### `cdk diff`

Use it to see whether your latest changes would modify:

- networking
- ECS service configuration
- task definitions
- IAM resources

### `cdk deploy`

Use it to actually create the AWS infrastructure and update it later.

## 9. Common misunderstandings

### "CDK is the infrastructure"

Not exactly.

CDK is the code layer you write.
CloudFormation is the deployment engine underneath.

### "`cdk synth` deploys resources"

No.

It only generates the CloudFormation template.

### "`cdk diff` changes AWS"

No.

It only previews changes.

### "`cdk deploy` always recreates everything"

No.

CloudFormation tries to update only what changed, though some kinds of changes require resource replacement.

## 10. Short analogy

If you want a very compact analogy:

- app = the whole Python infrastructure program
- stack = one deployable AWS environment chunk
- `cdk synth` = compile infrastructure code
- `cdk diff` = preview infra changes
- `cdk deploy` = apply infra changes in AWS

## 11. Minimum you need to remember

If you only remember five things, remember these:

1. CDK lets you define AWS infrastructure in Python.
2. A CDK app can contain one or more stacks.
3. A stack is the deployable unit.
4. `cdk synth` shows the generated CloudFormation.
5. `cdk diff` previews changes and `cdk deploy` applies them.

## Official references

- AWS CDK apps:
  - https://docs.aws.amazon.com/cdk/v2/guide/apps.html
- AWS CDK stacks:
  - https://docs.aws.amazon.com/cdk/v2/guide/stacks.html
- AWS CDK constructs:
  - https://docs.aws.amazon.com/cdk/v2/guide/constructs.html
- `cdk synth`:
  - https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-synth.html
- `cdk diff`:
  - https://docs.aws.amazon.com/cdk/v2/guide/ref-cli-cmd-diff.html
- `cdk deploy`:
  - https://docs.aws.amazon.com/cdk/v2/guide/deploy.html

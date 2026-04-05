# Infrastructure

AWS CDK app that defines the ECS Fargate stack for this project.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Preview changes:

```bash
cdk diff -c imageTag=<image_tag> -c ecrRepositoryName=aws-fastapi-foundation
```

Deploy:

```bash
cdk deploy -c imageTag=<image_tag> -c ecrRepositoryName=aws-fastapi-foundation
```

Destroy the stack:

```bash
cdk destroy InfrastructureStack
```

Run tests:

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

See the [root README](../README.md) for full deployment instructions.

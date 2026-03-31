# AWS FastAPI Foundation

Minimal FastAPI application for learning Python backend development, containerization, CI/CD, and AWS deployment with ECS Fargate, ALB, ECR, and CDK.

## Local Prerequisites

- Python 3.12+
- `uv`
- Docker

## AWS Deployment Prerequisites

- AWS account
- AWS CLI configured and authenticated
- Node.js and `npm`
- AWS CDK CLI
- Amazon ECR repo for this project

Install the CDK CLI:

```bash
npm install -g aws-cdk
```

Verify AWS access:

```bash
aws sts get-caller-identity
```

## Documentation

Use this README as the entry point, then go deeper with these documents:

- [Architecture](/home/aszabo/src/aws-fastapi-foundation/docs/architecture.md): current repository and AWS architecture, deployment flow, and service tradeoffs
- [CDK Basics](/home/aszabo/src/aws-fastapi-foundation/docs/cdk-basics.md): tutorial-style explanation of app vs stack, `cdk synth`, `cdk diff`, and `cdk deploy`
- [CDK Constructs](/home/aszabo/src/aws-fastapi-foundation/docs/cdk-constructs.md): how to find and use the main CDK constructs used by this project
- [ECS Fargate CDK Plan](/home/aszabo/src/aws-fastapi-foundation/docs/ecs-fargate-cdk-plan.md): phased deployment plan and implementation notes from building the project

## Install dependencies

```bash
uv sync
```

## Local development

Run the development server:

```bash
uv run fastapi dev app/main.py
```

The app will be available at:

- `http://127.0.0.1:8000/hello`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/version`
- `http://127.0.0.1:8000/docs`

## Quality checks

Run lint checks:

```bash
uv run ruff check .
```

Format code:

```bash
uv run ruff format .
```

Run tests:

```bash
uv run pytest
```

## Docker

Build the image from the repo root:

```bash
docker build -t aws-fastapi-foundation:local .
```

Run the container and publish port `8000` to the host:

```bash
docker run --rm -p 8000:8000 aws-fastapi-foundation:local
```

Then open:

- `http://127.0.0.1:8000/hello`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/version`
- `http://127.0.0.1:8000/docs`

Inspect the image with an interactive shell:

```bash
docker run --rm -it aws-fastapi-foundation:local bash
```

## AWS Deployment

The application is deployed to AWS as a containerized ECS service on Fargate behind an Application Load Balancer.
The infrastructure is defined with AWS CDK under `infrastructure/`.

Normal GitHub-based deployment flow:

1. Build and publish a tagged image to Amazon ECR.
2. Run the deploy workflow with the image tag to run.
3. Let ECS roll the service forward behind the ALB.

Use the `Deploy` GitHub Actions workflow when:

- you want the normal project deployment path
- you want to promote a chosen image tag into ECS
- you want the workflow to smoke-test the public `/health` endpoint after deployment

Use local/manual CDK commands when:

- you are developing or debugging the infrastructure itself
- you want to inspect `cdk diff` locally before changing AWS
- you are experimenting with CDK changes before relying on GitHub Actions

Local/manual CDK deployment:

```bash
cd infrastructure
cdk diff -c imageTag=0.1.1 -c ecrRepositoryName=aws-fastapi-foundation
cdk deploy -c imageTag=0.1.1 -c ecrRepositoryName=aws-fastapi-foundation
```

The stack currently provisions:

- VPC
- ECS cluster
- CloudWatch log group
- ECS Fargate service
- Application Load Balancer
- ALB health checks using `/health`
- ECS autoscaling based on CPU utilization

## Release New Version To ECS

This project keeps artifact publishing and runtime deployment as separate steps.
That means:

- the release workflow publishes a tagged image to Amazon ECR
- the deploy workflow chooses which image tag ECS should run

This project's ECS service does not automatically run the newest image in ECR.
The CDK stack decides which image tag the ECS task definition should use.

To release a new app version, for example `0.2.0`:

1. Update the application code and version.
2. Run the `Release` GitHub Actions workflow with image tag `0.2.0`.
3. Run the `Deploy` GitHub Actions workflow with image tag `0.2.0`.

What this does:

- publishes the new image tag to ECR first
- updates the ECS task definition to point at that ECR image tag
- lets ECS roll the service forward to new task(s)
- keeps the ALB routing traffic only to healthy tasks

After deployment, verify the running version:

```bash
curl http://YOUR_ALB_DNS_NAME/version
```

## GitHub Actions

The repository contains two GitHub Actions workflows:

- CI: runs Ruff, pytest, and Docker build validation on pull requests and on `main`
- Release: manually builds and pushes a tagged Docker image to Amazon ECR using GitHub OIDC and an AWS IAM role
- Deploy: manually runs `cdk deploy` with a chosen image tag and smoke-tests the public `/health` endpoint

## Tech stack

- FastAPI
- Uvicorn
- uv
- Ruff
- Pytest
- Docker
- GitHub Actions
- Amazon ECR
- Amazon ECS on Fargate
- Application Load Balancer
- AWS CDK

## Lessons learned

### Using UV

uv does a lot of things for you. `uv run` executes `uv sync` automatically, installs your local project in editable mode (`pip install -e .` equivalent) into `.venv`, plus all dependencies from `pyproject.toml`

### importlib.metadata

I used `importlib.metadata` to read the version that originates in `pyproject.toml`.
`importlib.metadata` reads the installed project metadata (e.g. `aws_fastapi_foundation-0.1.0.dist-info/` in `.venv.`). 
`uv sync` needs a build backend to be specified in `pyproject.toml` for it to install the project files (by default it updates and installs the dependencies only).
I used uv_build, and I had to tell it where the import module is because it's not in a `src/<project_name>` folder. See the `[tool.uv.build-backend]` config section.

### Claude Sonnet 4.6 vs GPT-5.3-Codex and GPT-5.4

I caught Claude to make things up repeatedly even though the CLAUDE.md file included instructions to search the docs when asked about tools, APIs, etc.
GPT did not hallucinate.

### GitHub Actions to publish a container image to AWS ECR

#### GitHub OIDC provider in AWS
This is the authentication bridge between GitHub Actions and AWS.
GitHub Actions does not automatically have AWS access.
The OIDC provider tells AWS:
- "I recognize GitHub-issued identity tokens"
- "GitHub workflows may authenticate using those tokens"

#### IAM role
This is the AWS identity the workflow assumes.
The release workflow does not act as your AWS user.
It assumes a dedicated IAM role, such as `github-actions-ecr-release`.
That role is what the workflow becomes inside AWS for the duration of the job.

#### Trust policy on the IAM role
This controls who is allowed to assume the role.
For this setup, the trust policy should allow:
- GitHub's OIDC provider
- only this repository
- ideally only the `main` branch

So the trust policy answers:
- who may assume this role?

Mental model:
- trust policy = admission rules

#### Permissions policy on the IAM role
This controls what the role can do after it is assumed.
For this setup, it should allow:
- `ecr:GetAuthorizationToken`
- uploading image layers
- publishing images
- only to the target ECR repository

So the permissions policy answers:
- what may this role do?

Mental model:
- permissions policy = allowed actions after entry

#### GitHub repository secrets and variables
These connect the workflow to your AWS setup without hardcoding values.
They are configuration inputs for the workflow.
- secret: `AWS_ROLE_TO_ASSUME` for the ECR release workflow
- secret: `AWS_DEPLOY_ROLE_TO_ASSUME` for the CDK deploy workflow
- variable: `AWS_REGION`
- variable: `ECR_REPOSITORY`

#### Flow
- You manually run the GitHub release workflow.
- GitHub Actions starts a runner.
- The workflow builds the Docker image from the repository.
- The job obtains a GitHub OIDC token.
- AWS checks whether the IAM role trust policy allows that GitHub identity.
- If allowed, AWS lets the job assume the IAM role through STS.
- The assumed role receives the permissions defined by its permissions policy.
- The workflow logs in to ECR.
- The workflow pushes the tagged Docker image to the target ECR repository.

### AWS CDK - IaC

CDK is a powerful tool for defining AWS infrastructure using familiar programming languages such as Python. But it's no small feat to learning it in detail.
Luckily once you understand the high level concepts in CDK and you have a good grasp of what your AWS infrastructure should look like for your application or service, you can use the AWS CDK Developer Reference guide to look up the classes and functions that map to the AWS infrastructure building blocks you have identified.

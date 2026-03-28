# AWS FastAPI Foundation

Minimal FastAPI application for learning Python backend development, containerization, and AWS deployment.

## Prerequisites

- Python 3.12+
- `uv`
- Docker

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

## Tech stack

- FastAPI
- Uvicorn
- uv
- Ruff
- Pytest
- Docker

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
- secret: `AWS_ROLE_TO_ASSUME`
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

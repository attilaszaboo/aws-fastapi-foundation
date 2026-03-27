# Simple FastAPI app deployed to AWS

This is a "hello-world" FastAPI app deployed to AWS with the goal of learning the tech stack.

## Project scaffolding

```
uv init
uv add fastapi[standard]
uv add --dev pytest ruff
```

## Local dev instructions

- Linting:
```
uv run ruff check .
```

- Formatting
```
uv run ruff format .
```

- Running tests
```
uv run pytest
```

- Starting the FastAPI server in dev mode:
```
uv run fastapi dev
```

This will start the server at http://127.0.0.1:8000
Docs will be at http://127.0.0.1:8000/docs

## Container build instructions

## AWS Architecture diagram

## Tech Stack
- uv package manager
- [FastAPI](https://fastapi.tiangolo.com/)


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

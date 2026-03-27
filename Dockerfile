# Use the official uv image as a source for the uv executables.
FROM ghcr.io/astral-sh/uv:0.9.5 AS uv

# Use a small official Python 3.12 base image for the application runtime.
FROM python:3.12-slim

# Prevent Python from writing .pyc files at runtime as docker images are typically immutable and .pyc files are not necessary.
ENV PYTHONDONTWRITEBYTECODE=1

# Send Python logs directly and immediately to stdout and stderr.
ENV PYTHONUNBUFFERED=1

# Ask uv to precompile bytecode during installation (build time) to avoid the overhead of doing it at runtime.
ENV UV_COMPILE_BYTECODE=1

# Copy installed files instead of using filesystem links for a more predictable Docker image.
ENV UV_LINK_MODE=copy

# Tell uv to create the virtual environment at /app/.venv.
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Make executables from the virtual environment available on PATH.
ENV PATH="/app/.venv/bin:$PATH"

# Copy the uv executable from the named uv stage into this image's /bin directory.
COPY --from=uv /uv /bin/uv

# Copy the uvx executable from the named uv stage into this image's /bin directory.
COPY --from=uv /uvx /bin/uvx

# Run the remaining instructions from /app by default. 
# This will also create the /app directory in the container if it doesn't exist and set it as the working directory for subsequent instructions.
WORKDIR /app

# Copy the package metadata and lockfile needed for dependency installation.
COPY pyproject.toml uv.lock README.md ./

# Copy the application source code into the image.
COPY app ./app

# Install the app and its production dependencies from the lockfile.
# This will also precompile bytecode for the app and its dependencies due to the UV_COMPILE_BYTECODE environment variable set earlier.
# This will create a virtual environment at /app/.venv due to the UV_PROJECT_ENVIRONMENT environment variable set earlier.
# This will install uvicorn as the ASGI server for running the FastAPI application in production.
RUN uv sync --frozen --no-dev --no-editable

# Create a non-root user for running the application.
# Give the non-root user ownership of the application directory.
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# Switch the container runtime user from root to appuser.
USER appuser

# The application listens on port 8000.
EXPOSE 8000

# Start the FastAPI application with Uvicorn in a way that is reachable from outside the container.
# This command will be run when the container starts. It uses the uvicorn executable installed in the virtual environment to run the FastAPI application defined in app/main.py, making it available on all network interfaces (
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

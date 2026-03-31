from importlib import metadata

from fastapi import FastAPI

__version__ = metadata.version("aws-fastapi-foundation")
ROOT_MESSAGE = (
    "This backend is a minimal FastAPI service for learning Python, "
    "containers, CI/CD, and AWS deployment."
)

app = FastAPI(
    title="AWS FastAPI Foundation",
    summary=metadata.metadata("aws-fastapi-foundation")["Summary"],
    version=__version__,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint that describes the purpose of this backend."""
    return {"message": ROOT_MESSAGE}


@app.get("/hello")
def read_hello(name: str | None = None) -> dict[str, str]:
    """Return a greeting, optionally personalized with a name."""
    if name:
        return {"message": f"Hello {name}! Nice to talk to you."}

    return {"message": "Hello, World!"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint that returns the status of the application."""
    return {"status": "ok"}


@app.get("/version")
def get_version() -> dict[str, str]:
    """Endpoint that returns the current version of the application."""
    return {"version": __version__}

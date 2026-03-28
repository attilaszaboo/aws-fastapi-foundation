from fastapi import FastAPI
from importlib import metadata

__version__ = metadata.version("aws-fastapi-foundation")

app = FastAPI(
    title="AWS FastAPI Foundation", 
    summary=metadata.metadata("aws-fastapi-foundation")["Summary"],
    version=__version__
)


@app.get("/hello")
def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    """Health check endpoint that returns the status of the application."""
    return {"status": "ok"}


@app.get("/version")
def get_version():
    """Endpoint that returns the current version of the application."""
    return {"version": __version__}

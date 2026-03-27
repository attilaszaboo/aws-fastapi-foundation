from fastapi import FastAPI
from importlib.metadata import version

__version__ = version("aws-fastapi-foundation")

app = FastAPI(title="AWS FastAPI Foundation", version=__version__)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def get_version():
    return {"version": __version__}
from fastapi.testclient import TestClient

from app.main import ROOT_MESSAGE, __version__, app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": ROOT_MESSAGE}


def test_hello() -> None:
    response = client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_hello_with_name() -> None:
    response = client.get("/hello", params={"name": "Attila"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello Attila! Nice to talk to you."}


def test_hello_with_empty_name() -> None:
    response = client.get("/hello", params={"name": ""})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": __version__}

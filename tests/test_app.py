"""
Unit tests for the ticket API.

These run in the CI pipeline's build-test job before anything gets
containerized or deployed. Ff any test here fails, the pipeline stops
and nothing downstream (Docker build, security scan, deploy) executes.
"""

import pytest

from app import app as flask_app


@pytest.fixture
def client():
    """
    Provides a fresh Flask test client for each test function.

    TESTING mode disables error catching during request handling, so
    exceptions in the app surface directly in the test output instead
    of being wrapped in a generic 500 response.
    """
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_health(client):
    """
    The /health endpoint is used by the deploy pipeline and any uptime
    monitoring. If this breaks, deploys and health checks silently fail.
    """
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_ticket(client):
    """Happy path: valid input should create a ticket and return it."""
    resp = client.post("/tickets", json={"subject": "Login broken", "body": "Cannot log in since update."})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["subject"] == "Login broken"
    assert body["status"] == "open"
    assert "id" in body  # confirms the server assigned an id, not just echoed input


def test_create_ticket_missing_fields(client):
    """
    Validation check: the API should reject incomplete tickets with a 400,
    not silently accept them or throw an unhandled 500.
    """
    resp = client.post("/tickets", json={"subject": "Missing body"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_ticket_not_found(client):
    """Requesting a ticket id that doesn't exist should 404, not error out."""
    resp = client.get("/tickets/9999")
    assert resp.status_code == 404


def test_get_ticket_roundtrip(client):
    """
    End-to-end check: a ticket created via POST should be retrievable
    via GET using the id the server returned, catches bugs where the
    in-memory store isn't actually persisting between requests.
    """
    create_resp = client.post("/tickets", json={"subject": "Test", "body": "Body text"})
    ticket_id = create_resp.get_json()["id"]

    get_resp = client.get(f"/tickets/{ticket_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["id"] == ticket_id
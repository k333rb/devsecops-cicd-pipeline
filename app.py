"""Minimal ticket API, sample app for the CI/CD pipeline portfolio project."""

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory store for demo purposes only.
_tickets = {}
_next_id = 1


@app.route("/health", methods=["GET"])
def health():
    """Liveness check used by the deploy step and any uptime monitoring."""
    return jsonify(status="ok"), 200


@app.route("/tickets", methods=["POST"])
def create_ticket():
    """Create a new support ticket."""
    global _next_id
    data = request.get_json(silent=True) or {}
    subject = data.get("subject")
    body = data.get("body")

    if not subject or not body:
        return jsonify(error="subject and body are required"), 400

    ticket = {
        "id": _next_id,
        "subject": subject,
        "body": body,
        "status": "open",
    }
    _tickets[_next_id] = ticket
    _next_id += 1
    return jsonify(ticket), 201


@app.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    """Retrieve a single ticket by id."""
    ticket = _tickets.get(ticket_id)
    if ticket is None:
        return jsonify(error="ticket not found"), 404
    return jsonify(ticket), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
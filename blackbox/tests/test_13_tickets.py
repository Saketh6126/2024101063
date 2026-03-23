"""
test_13_tickets.py
------------------
T-01 to T-17: Support ticket schema, validation, and status transition tests.
"""

import pytest
from conftest import get, post, put


def _create_ticket(subject="Test subject here", message="Valid test message body"):
    return post("/support/ticket", {"subject": subject, "message": message})


def _get_ticket_id(r):
    data = r.json()
    ticket = data.get("ticket", data)
    tid = ticket.get("ticket_id")
    if not tid:
        pytest.skip("Could not extract ticket_id")
    return tid


class TestSupportTickets:

    def test_T01_get_tickets_schema(self):
        """T-01: GET /support/tickets → 200, confirm schema keys."""
        r = get("/support/tickets")
        assert r.status_code == 200
        tickets = r.json()
        assert isinstance(tickets, list)
        if tickets:
            t = tickets[0]
            assert "ticket_id" in t or "id" in t, "Missing ticket_id in schema"

    def test_T02_create_ticket_status_open(self):
        """T-02: New ticket → 200/201, status=OPEN."""
        r = _create_ticket()
        assert r.status_code in (200, 201)
        data = r.json()
        ticket = data.get("ticket", data)
        assert ticket.get("status") == "OPEN", \
            f"Expected status='OPEN', got '{ticket.get('status')}'"

    def test_T03_subject_4_chars_returns_400(self):
        """T-03: subject with 4 chars (< 5) → 400."""
        r = _create_ticket(subject="Abcd")
        assert r.status_code == 400

    def test_T04_subject_boundary_5_chars_accepted(self):
        """T-04: subject with exactly 5 chars → 200/201."""
        r = _create_ticket(subject="Abcde")
        assert r.status_code in (200, 201)

    def test_T05_subject_boundary_100_chars_accepted(self):
        """T-05: subject with exactly 100 chars → 200/201."""
        r = _create_ticket(subject="A" * 100)
        assert r.status_code in (200, 201)

    def test_T06_subject_101_chars_returns_400(self):
        """T-06: subject with 101 chars → 400."""
        r = _create_ticket(subject="A" * 101)
        assert r.status_code == 400

    def test_T07_message_empty_returns_400(self):
        """T-07: message='' → 400."""
        r = _create_ticket(message="")
        assert r.status_code == 400

    def test_T08_message_boundary_1_char_accepted(self):
        """T-08: message with exactly 1 char → 200/201."""
        r = _create_ticket(message="A")
        assert r.status_code in (200, 201)

    def test_T09_message_boundary_500_chars_accepted(self):
        """T-09: message with exactly 500 chars → 200/201."""
        r = _create_ticket(message="A" * 500)
        assert r.status_code in (200, 201)

    def test_T10_message_501_chars_returns_400(self):
        """T-10: message with 501 chars → 400."""
        r = _create_ticket(message="A" * 501)
        assert r.status_code == 400

    def test_T11_message_saved_verbatim(self):
        """T-11: message stored exactly as written (no modification)."""
        msg = "Exact verbatim message @#$%! with special chars"
        r = _create_ticket(message=msg)
        assert r.status_code in (200, 201)
        data = r.json()
        ticket = data.get("ticket", data)
        assert ticket.get("message") == msg, \
            f"Message stored as '{ticket.get('message')}', expected '{msg}'"

    def test_T12_transition_open_to_in_progress(self):
        """T-12: OPEN → IN_PROGRESS → 200."""
        tid = _get_ticket_id(_create_ticket())
        r = put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        assert r.status_code == 200

    def test_T13_transition_in_progress_to_closed(self):
        """T-13: IN_PROGRESS → CLOSED → 200."""
        tid = _get_ticket_id(_create_ticket())
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        r = put(f"/support/tickets/{tid}", {"status": "CLOSED"})
        assert r.status_code == 200

    def test_T14_skip_open_to_closed_returns_400(self):
        """T-14: OPEN → CLOSED (skipping IN_PROGRESS) → 400."""
        tid = _get_ticket_id(_create_ticket())
        r = put(f"/support/tickets/{tid}", {"status": "CLOSED"})
        assert r.status_code == 400

    def test_T15_backward_in_progress_to_open_returns_400(self):
        """T-15: IN_PROGRESS → OPEN (backward) → 400."""
        tid = _get_ticket_id(_create_ticket())
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        r = put(f"/support/tickets/{tid}", {"status": "OPEN"})
        assert r.status_code == 400

    def test_T16_closed_to_in_progress_returns_400(self):
        """T-16: CLOSED → IN_PROGRESS → 400."""
        tid = _get_ticket_id(_create_ticket())
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        put(f"/support/tickets/{tid}", {"status": "CLOSED"})
        r = put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        assert r.status_code == 400

    def test_T17_closed_to_open_returns_400(self):
        """T-17: CLOSED → OPEN → 400."""
        tid = _get_ticket_id(_create_ticket())
        put(f"/support/tickets/{tid}", {"status": "IN_PROGRESS"})
        put(f"/support/tickets/{tid}", {"status": "CLOSED"})
        r = put(f"/support/tickets/{tid}", {"status": "OPEN"})
        assert r.status_code == 400

import app.graph.nodes as nodes

def test_valid_booking_request():
    state = {
        "action": "book_appointment",
        "caller_name": "Test User",
        "requested_start": "2026-09-20T14:00:00-04:00",
    }
    result = nodes.validate_request(state)
    assert result["status"] == "validated"
    assert result["error"] is None

def test_booking_missing_name():
    state = {
        "action": "book_appointment",
        "requested_start": "2026-09-20T14:00:00-04:00",
    }

    result = nodes.validate_request(state)
    assert result["status"] == "needs_information"
    assert "caller_name" in result["error"]

def test_unknown_action():
    state = {
        "action": "something_fake"
    }

    result = nodes.validate_request(state)
    assert result["status"] == "error"

def test_available_slot(monkeypatch):
    monkeypatch.setattr(nodes,"check_availability",lambda start_time: True)
    state = {
        "requested_start": "2026-09-20T14:00:00-04:00"
    }

    result = nodes.check_availability_node(state)
    assert result["status"] == "available"

def test_unavailable_slot(monkeypatch):
    monkeypatch.setattr(nodes,"check_availability",lambda start_time: False)
    state = {
        "requested_start": "2026-09-20T14:00:00-04:00"
    }
    result = nodes.check_availability_node(state)
    assert result["status"] == "unavailable"

def test_successful_booking(monkeypatch):
    def fake_create_appointment(caller_name, start_time):
        return {
            "appointment_id": "fake-event-123",
            "start_time": start_time
        }

    monkeypatch.setattr(nodes,"create_appointment",fake_create_appointment)
    state = {
        "caller_name": "Test User",
        "requested_start": "2026-09-20T14:00:00-04:00"
    }
    result = nodes.book_appointment_node(state)
    assert result["status"] == "success"
    assert result["appointment_id"] == "fake-event-123"

def test_appointment_not_found(monkeypatch):
    monkeypatch.setattr(nodes,"find_appointment",lambda appointment_id: None)
    state = {
        "appointment_id": "missing-id"
    }
    result = nodes.find_existing_appointment_node(state)
    assert result["status"] == "appointment_not_found"

def test_successful_cancellation(monkeypatch):
    monkeypatch.setattr(nodes,"cancel_appointment",lambda appointment_id: True)
    state = {
        "appointment_id": "fake-event-123"
    }
    result = nodes.cancel_appointment_node(state)
    assert result["status"] == "success"
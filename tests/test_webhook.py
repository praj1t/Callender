from fastapi.testclient import TestClient
import app.main as main

client = TestClient(main.app)

def test_vapi_webhook(monkeypatch):
    def fake_graph_invoke(state, config):
        return {
            "status": "success",
            "result_message": "Appointment booked.",
            "appointment_id": "fake-event-123"
        }

    monkeypatch.setattr(main.appointment_graph,"invoke",fake_graph_invoke)

    payload = {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "fake-call-123"
            },
            "toolCallList": [
                {
                    "id": "tool-call-123",
                    "type": "function",
                    "function": {
                        "name": "book_appointment",
                        "arguments": {
                            "caller_name": "Test User",
                            "requested_start": "2026-09-20T14:00:00-04:00"
                        }
                    }
                }
            ]
        }
    }

    response = client.post("/vapi/webhook",json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["toolCallId"] == "tool-call-123"
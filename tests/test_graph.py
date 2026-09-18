import uuid

import app.graph.nodes as nodes
from app.graph.workflow import appointment_graph


def test_graph_routes_booking(monkeypatch):

    monkeypatch.setattr(nodes,"check_availability",lambda start_time: True)
    monkeypatch.setattr(nodes,"create_appointment",lambda caller_name,
        start_time: {
            "appointment_id": "graph-test-id",
            "start_time": start_time
        })

    state = {
        "action": "book_appointment",
        "caller_name": "Graph Test",
        "requested_start": "2026-09-20T14:00:00-04:00",
    }

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = appointment_graph.invoke(state,config=config)

    assert result["status"] == "success"
    assert result["appointment_id"] == "graph-test-id"
    assert "node_timings_ms" in result
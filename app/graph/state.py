from typing import TypedDict

class AppointmentState(TypedDict, total=False):
    action: str
    caller_name: str
    appointment_id: str
    requested_start: str
    status: str
    result_message: str
    error: str | None
    node_timings_ms: dict[str, float]
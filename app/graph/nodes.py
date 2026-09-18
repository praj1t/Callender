from datetime import datetime
from app.graph.state import AppointmentState
from app.services.appointment_service import (check_availability,create_appointment,find_appointment,reschedule_appointment,cancel_appointment)

def validate_request(state: AppointmentState):
    action = state.get("action")
    required_fields = {
        "check_availability": ["requested_start"],
        "book_appointment": ["caller_name","requested_start"],
        "reschedule_appointment": ["appointment_id","requested_start"],
        "cancel_appointment": ["appointment_id"]
    }

    if action not in required_fields:
        return {
            "status": "error",
            "error": "Unknown appointment action."
        }

    missing_fields = []


    for field in required_fields[action]:
        if not state.get(field):
            missing_fields.append(field)

    if missing_fields:
        return {
            "status": "needs_information",
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }

    if state.get("requested_start"):
        try:
            requested_start = datetime.fromisoformat(state["requested_start"])

            if requested_start.tzinfo is None:
                return {
                    "status": "error",
                    "error": "requested_start must include a timezone."
                }
        except ValueError:
            return {
                "status": "error",
                "error": "Invalid requested_start datetime."
            }
    return {
        "status": "validated",
        "error": None
    }


def check_availability_node(state: AppointmentState):

    available = check_availability(state["requested_start"])
    if available:
        return {
            "status": "available",
            "result_message": "That appointment time is available.",
            "error": None
        }
    return {
        "status": "unavailable",
        "result_message": "That appointment time is not available.",
        "error": None
    }

def book_appointment_node(state: AppointmentState):
    appointment = create_appointment(caller_name=state["caller_name"],start_time=state["requested_start"])
    if appointment is None:
        return {
            "status": "unavailable",
            "result_message": "That appointment time is no longer available."
        }
    return {
        "status": "success",
        "appointment_id": appointment["appointment_id"],
        "result_message": (f"Appointment booked successfully for {appointment['start_time']}."),
        "error": None
    }

def find_existing_appointment_node(state: AppointmentState):
    appointment = find_appointment(state["appointment_id"])
    if appointment is None:
        return {
            "status": "appointment_not_found",
            "result_message": "I could not find that appointment."
        }
    return {
        "status": "appointment_found",
        "error": None
    }

def reschedule_appointment_node(state: AppointmentState):
    appointment = reschedule_appointment(
        appointment_id=state["appointment_id"],
        new_start_time=state["requested_start"]
    )
    if appointment is None:
        return {
            "status": "unavailable",
            "result_message": "The new appointment time is not available."
        }
    return {
        "status": "success",
        "result_message": (
        f"Appointment rescheduled successfully from {appointment['old_start_time']} to {appointment['new_start_time']}."),
        "error": None
    }

def cancel_appointment_node(state: AppointmentState):
    cancelled = cancel_appointment(state["appointment_id"])
    if not cancelled:
        return {
            "status": "appointment_not_found",
            "result_message": "I could not find that appointment."
        }
    return {
        "status": "success",
        "result_message": "Appointment cancelled successfully.",
        "error": None
    }

def handle_error(state: AppointmentState):
    error_message = state.get("error","Something went wrong.")
    return {
        "status": "error",
        "result_message": error_message
    }

def finalize_response(state: AppointmentState):
    if state.get("result_message"):
        return {}
    return {
        "result_message": "Request completed."
    }
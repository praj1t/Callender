from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import logging
import time
from app.graph.state import AppointmentState
from app.graph.nodes import (
    validate_request,
    check_availability_node,
    book_appointment_node,
    find_existing_appointment_node,
    reschedule_appointment_node,
    cancel_appointment_node,
    handle_error,
    finalize_response,
)

logger = logging.getLogger(__name__)

def timed_node(node_name, node_function):
    def wrapped_node(state, config):
        start = time.perf_counter()
        result = node_function(state)
        elapsed_ms = round((time.perf_counter() - start) * 1000,2)
        timings = state.get("node_timings_ms", {}).copy()
        timings[node_name] = elapsed_ms
        call_id = config["configurable"].get("thread_id","unknown")
        status = result.get("status",state.get("status", "unknown"))

        logger.info(
            "call_id=%s action=%s node=%s status=%s latency_ms=%.2f",
            call_id,
            state.get("action"),
            node_name,
            status,
            elapsed_ms,
        )
        result["node_timings_ms"] = timings
        return result
    return wrapped_node

def route_after_validation(state: AppointmentState):
    if state["status"] != "validated":
        return "error"

    action = state["action"]

    if action == "check_availability":
        return "check_availability"

    if action == "book_appointment":
        return "check_availability"

    if action == "reschedule_appointment":
        return "find_existing"

    if action == "cancel_appointment":
        return "find_existing"

def route_after_availability(state: AppointmentState):
    if state["status"] == "unavailable":
        return "finalize"

    action = state["action"]

    if action == "check_availability":
        return "finalize"

    if action == "book_appointment":
        return "book"

    if action == "reschedule_appointment":
        return "reschedule"

def route_after_find(state: AppointmentState):

    if state["status"] == "appointment_not_found":
        return "finalize"

    if state["action"] == "reschedule_appointment":
        return "check_availability"

    if state["action"] == "cancel_appointment":
        return "cancel"

builder = StateGraph(AppointmentState)
builder.add_node("validate",timed_node("validate", validate_request))
builder.add_node("check_availability",timed_node("check_availability", check_availability_node))
builder.add_node("book",timed_node("book", book_appointment_node))
builder.add_node("find_existing",timed_node("find_existing", find_existing_appointment_node))
builder.add_node("reschedule",timed_node("reschedule", reschedule_appointment_node))
builder.add_node("cancel",timed_node("cancel", cancel_appointment_node))
builder.add_node("handle_error",timed_node("handle_error", handle_error))
builder.add_node("finalize",timed_node("finalize", finalize_response))

builder.add_edge(START, "validate")
builder.add_conditional_edges("validate",route_after_validation,
    {
        "error": "handle_error",
        "check_availability": "check_availability",
        "find_existing": "find_existing",
    })
builder.add_conditional_edges("check_availability",route_after_availability,
    {
        "finalize": "finalize",
        "book": "book",
        "reschedule": "reschedule",
    })
builder.add_conditional_edges("find_existing",route_after_find,
    {
        "finalize": "finalize",
        "check_availability": "check_availability",
        "cancel": "cancel",
    })

builder.add_edge("book", "finalize")
builder.add_edge("reschedule", "finalize")
builder.add_edge("cancel", "finalize")
builder.add_edge("handle_error", "finalize")

builder.add_edge("finalize", END)

memory = InMemorySaver()

appointment_graph = builder.compile(checkpointer=memory)
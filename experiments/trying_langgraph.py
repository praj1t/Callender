from app.graph.workflow import appointment_graph

appointment_id = "sqc8lnodtabe4tnnd96f30efl4"

reschedule_request = {
    "action": "reschedule_appointment",
    "appointment_id": appointment_id,
    "requested_start": "2026-09-18T16:00:00-04:00",
}

reschedule_result = appointment_graph.invoke(reschedule_request,
                                             config={"configurable": {"thread_id": "phase3-reschedule"}})

print("\nRESCHEDULE RESULT")
print(reschedule_result)

cancel_request = {
    "action": "cancel_appointment",
    "appointment_id": appointment_id,
}

cancel_result = appointment_graph.invoke(cancel_request,config={"configurable": {"thread_id": "phase3-cancel"}})

print("\nCANCEL RESULT")
print(cancel_result)
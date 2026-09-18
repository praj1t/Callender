from app.services.appointment_service import (
    create_appointment,
    cancel_appointment,
)


start_time = "2026-09-17T15:00:00-04:00"

appointment = create_appointment(
    caller_name="Test User",
    phone_number="1234567890",
    start_time=start_time,
)

print("Created:", appointment)

if appointment:
    input("Check Google Calendar, then press Enter to delete it...")

    deleted = cancel_appointment(
        appointment["appointment_id"]
    )

    print("Deleted:", deleted)
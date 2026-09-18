import json
from fastapi import FastAPI, Request
import logging
import time
from app.graph.workflow import appointment_graph

app = FastAPI(title="Vapi LangGraph Appointment Agent")

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")

logger = logging.getLogger(__name__)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    request_start = time.perf_counter()
    payload = await request.json()
    message = payload.get("message", {})

    if message.get("type") != "tool-calls":
        return {}

    call = message.get("call", {})
    call_id = call.get("id")
    tool_calls = message.get("toolCallList", [])

    results = []
    for tool_call in tool_calls:
        tool_call_id = tool_call["id"]
        function = tool_call["function"]
        tool_name = function["name"]
        arguments = function.get("arguments", {})

        graph_input = {"action": tool_name,**arguments}
        config = {"configurable": {"thread_id": call_id}}
        graph_result = appointment_graph.invoke(graph_input,config=config)

        total_latency_ms = round((time.perf_counter() - request_start) * 1000,2)

        logger.info(
            "call_id=%s action=%s status=%s total_backend_ms=%.2f",
            call_id,
            tool_name,
            graph_result.get("status"),
            total_latency_ms,
        )

        result_for_vapi = {
            "status": graph_result.get("status"),
            "message": graph_result.get("result_message")
        }

        if graph_result.get("appointment_id"):
            result_for_vapi["appointment_id"] = graph_result["appointment_id"]

        results.append({
            "toolCallId": tool_call_id,
            "result": json.dumps(result_for_vapi)
        })

    return {"results": results}
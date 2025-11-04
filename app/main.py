import os
from fastapi import FastAPI, Header
from dotenv import load_dotenv
from app.utils.rpc import JSONRPCRequest, make_result_response, make_error_response
from app.agents.picker import pick_random_verse
from app.agents.generator import generate_structured_devotional
from app.agents.devotional_agent import DevotionalAgent

load_dotenv()

A2A_API_KEY = os.getenv("A2A_API_KEY", "dev-key")  # change in .env for production

app = FastAPI(title="Devotional Agent (A2A / Telex compatible)")


@app.get("/.well-known/agent.json")
def agent_card():
    return {
        "name": "DailyDevotionalAgent",
        "version": "1.0.0",
        "description": "Generates daily devotionals from a local Bible DB",
        "methods": [
            {"name": "pick_verse", "desc": "Pick a random Bible verse; optional params: {topic}"},
            {"name": "generate_devotional", "desc": "Generate a devotional from a given verse; params: {reference, text, tone?}"},
            {"name": "run_devotional_workflow", "desc": "Run a full workflow: pick -> generate -> archive; params: {topic?, tone?, archive?(bool)}"},
        ],
        "protocol": "JSON-RPC 2.0",
    }


@app.post("/a2a")
def a2a(rpc: JSONRPCRequest, x_api_key: str | None = Header(None)):
    """
    A2A entrypoint for Telex-compatible JSON-RPC calls.
    """
    # --- Authorization ---
    if not x_api_key or x_api_key != A2A_API_KEY:
        return make_error_response("unknown", -32600, "Invalid or missing A2A API key")

    # --- Dispatch ---
    try:
        method = rpc.method
        params = rpc.params or {}

        if method == "pick_verse":
            topic = params.get("topic")
            ref, text = pick_random_verse(topic)
            result = {"reference": ref, "text": text}
            return make_result_response(rpc.id, result)

        elif method == "generate_devotional":
            ref = params.get("reference")
            text = params.get("text")
            tone = params.get("tone", "encouraging")
            if not ref or not text:
                return make_error_response(rpc.id, -32602, "Missing params: 'reference' and 'text' required")
            dev = generate_structured_devotional(ref, text, tone)
            return make_result_response(rpc.id, dev)

        elif method == "run_devotional_workflow":
            topic = params.get("topic")
            tone = params.get("tone", "encouraging")
            archive = params.get("archive", True)
            agent = DevotionalAgent()
            dev = agent.run(topic=topic, tone=tone, archive=archive)
            return make_result_response(rpc.id, dev)

        else:
            return make_error_response(rpc.id, -32601, "Method not found")

    except Exception as e:
        return make_error_response(rpc.id, -32000, f"Internal error: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}

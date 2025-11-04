# app/utils/rpc.py
from pydantic import BaseModel
from typing import Any, Optional, Dict

class JSONRPCRequest(BaseModel):
    jsonrpc: str
    id: str
    method: str
    params: Optional[Dict] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Any] = None
    error: Optional[Dict] = None

def make_result_response(rpc_id: str, result: Any) -> JSONRPCResponse:
    return JSONRPCResponse(id=rpc_id, result=result)

def make_error_response(rpc_id: str, code: int, message: str, data: Optional[Any] = None) -> JSONRPCResponse:
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return JSONRPCResponse(id=rpc_id, error=err)
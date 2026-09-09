"""
V1 Canonical AI Agent Tools Router.

Exposes grounded deterministic tool calling endpoints and JSON-Schema manifests
for OpenAI Function Calling, Anthropic Claude Tool Use, Gemini Function Calling,
LangChain, AutoGen, and CrewAI autonomous agents.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.intelligence import get_agent_tools_manifest, execute_agent_tool

router = APIRouter(prefix="/agents", tags=["V1 Agent Tools"])


class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool input arguments matching schema")


@router.get("/tools")
def list_agent_tools():
    """
    Retrieve OpenAI / Anthropic / Gemini function-calling JSON Schema tool manifest.
    Enables external autonomous agents to discover available clean energy intelligence capabilities.
    """
    return {
        "status": "success",
        "tools_count": len(get_agent_tools_manifest()),
        "tools": get_agent_tools_manifest()
    }


@router.post("/execute-tool")
def run_agent_tool(
    payload: ToolExecutionRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a registered intelligence tool on behalf of an autonomous AI agent.
    Returns deterministic, grounded empirical outputs from the database and scoring engines.
    """
    result = execute_agent_tool(
        tool_name=payload.tool_name,
        arguments=payload.arguments,
        db=db
    )

    if "error" in result and "is not recognized" in str(result.get("error")):
        raise HTTPException(status_code=400, detail=result)

    return {
        "status": "success",
        "tool_name": payload.tool_name,
        "output": result
    }

"""
workiq_routes.py - FastAPI routes for WorkIQ with user authentication

Handles WorkIQ function calls from Azure AI Foundry agents with proper user context
"""

import os
import asyncio
import subprocess
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

router = APIRouter()

class WorkIQRequest(BaseModel):
    tool_name: str
    user_email: str  
    parameters: Dict[str, Any]

class WorkIQAuthenticatedCall:
    """Handles authenticated WorkIQ calls with user context switching"""
    
    def __init__(self):
        self.active_servers: Dict[str, dict] = {}
        
    async def call_workiq_for_user(self, user_email: str, tool_name: str, parameters: dict) -> Any:
        """Execute WorkIQ tool with user authentication"""
        
        print(f"📞 WorkIQ call for {user_email}: {tool_name}")
        
        # Method 1: Dynamic server per user
        server_params = StdioServerParameters(
            command="npx",
            args=["@microsoft/workiq", "mcp", "--account", user_email]
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Remove user_email from parameters since WorkIQ doesn't need it
                    workiq_params = parameters.copy()
                    if "user_email" in workiq_params:
                        del workiq_params["user_email"]
                    
                    result = await session.call_tool(tool_name, workiq_params)
                    
                    if result.content:
                        return result.content[0].text if result.content[0] else "No response"
                    else:
                        return "No content returned"
                        
        except Exception as e:
            print(f"❌ WorkIQ error for {user_email}: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"WorkIQ authentication or execution failed: {str(e)}"
            )

# Global instance
workiq_caller = WorkIQAuthenticatedCall()

@router.post("/workiq/execute")
async def execute_workiq_function(request: WorkIQRequest):
    """
    Execute a WorkIQ function with user authentication
    
    This endpoint is called by Azure AI Foundry agents when they need to execute
    WorkIQ tools with user context.
    """
    
    try:
        result = await workiq_caller.call_workiq_for_user(
            user_email=request.user_email,
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        
        return {
            "success": True,
            "result": result,
            "user": request.user_email,
            "tool": request.tool_name
        }
        
    except Exception as e:
        print(f"🚨 WorkIQ execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workiq/tools")
async def get_workiq_tools():
    """Get available WorkIQ tools (for development/debugging)"""
    
    server_params = StdioServerParameters(
        command="npx",
        args=["@microsoft/workiq", "mcp"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                
                return {
                    "success": True,
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "schema": tool.inputSchema if hasattr(tool, 'inputSchema') else None
                        }
                        for tool in tools.tools
                    ]
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback_tools": [
                "workiq_get_calendar_events",
                "workiq_get_emails", 
                "workiq_get_tasks"
            ]
        }

@router.post("/workiq/test")
async def test_workiq_for_user(user_email: str = Body(..., embed=True)):
    """Test WorkIQ authentication for specific user"""
    
    try:
        # Test with a simple query
        result = await workiq_caller.call_workiq_for_user(
            user_email=user_email,
            tool_name="get_calendar_events",
            parameters={"query": "today"}
        )
        
        return {
            "success": True,
            "message": f"WorkIQ authentication successful for {user_email}",
            "test_result": result[:200] + "..." if len(str(result)) > 200 else result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"WorkIQ authentication failed for {user_email}"
        }
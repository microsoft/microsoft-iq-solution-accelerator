"""
workiq_process_bridge.py - WorkIQ Authentication via Process Bridge

Since MCP doesn't support --account, we bridge to WorkIQ CLI processes with authentication
"""

import asyncio
import subprocess
import json
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class WorkIQProcessCall:
    """Execute WorkIQ via CLI processes with user authentication"""
    
    @staticmethod
    async def call_workiq_with_account(user_email: str, query: str) -> str:
        """Call WorkIQ CLI with user account authentication"""
        
        print(f"🔐 Calling WorkIQ for {user_email}: {query}")
        
        try:
            # Use WorkIQ CLI directly with account parameter
            cmd = [
                "npx", "@microsoft/workiq", 
                "--account", user_email,
                "ask", 
                "-q", query
            ]
            
            # Run with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=60.0  # 60 second timeout
                )
                
                if process.returncode == 0:
                    result = stdout.decode('utf-8').strip()
                    print(f"✅ WorkIQ success for {user_email}")
                    return result
                else:
                    error_msg = stderr.decode('utf-8').strip()
                    print(f"❌ WorkIQ error for {user_email}: {error_msg}")
                    raise HTTPException(
                        status_code=500, 
                        detail=f"WorkIQ CLI error: {error_msg}"
                    )
                    
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise HTTPException(
                    status_code=408, 
                    detail="WorkIQ request timed out"
                )
                
        except Exception as e:
            print(f"🚨 WorkIQ process error: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to execute WorkIQ: {str(e)}"
            )

workiq_process = WorkIQProcessCall()

class WorkIQQueryRequest(BaseModel):
    user_email: str
    query: str

@router.post("/workiq/ask")
async def ask_workiq(request: WorkIQQueryRequest):
    """
    Execute WorkIQ query with user authentication via CLI bridge
    
    This bypasses MCP limitations by calling WorkIQ CLI directly
    """
    
    try:
        result = await workiq_process.call_workiq_with_account(
            user_email=request.user_email,
            query=request.query
        )
        
        return {
            "success": True,
            "result": result,
            "user": request.user_email,
            "method": "cli_bridge"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workiq/calendar")
async def get_calendar(request: WorkIQQueryRequest):
    """Get calendar events via WorkIQ CLI"""
    
    # Enhance query for calendar-specific request or use default
    if not request.query or request.query.strip() == "":
        calendar_query = "What meetings and calendar events do I have today?"
    else:
        calendar_query = f"What meetings and calendar events do I have? {request.query}"
    
    request.query = calendar_query
    return await ask_workiq(request)

@router.post("/workiq/emails") 
async def get_emails(request: WorkIQQueryRequest):
    """Get emails via WorkIQ CLI"""
    
    # Enhance query for email-specific request or use default
    if not request.query or request.query.strip() == "":
        email_query = "Show me my recent emails"
    else:
        email_query = f"Show me my recent emails. {request.query}"
    
    request.query = email_query
    return await ask_workiq(request)
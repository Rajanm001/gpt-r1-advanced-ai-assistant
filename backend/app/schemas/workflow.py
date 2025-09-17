"""
GPT.R1 - Workflow Schemas
Pydantic schemas for agentic workflow operations
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class StepType(str, Enum):
    """Workflow step types"""
    ORCHESTRATE = "orchestrate"
    ANALYZE = "analyze"
    SEARCH = "search"
    SYNTHESIZE = "synthesize"
    VALIDATE = "validate"
    RESPOND = "respond"

class WorkflowStep(BaseModel):
    """Individual workflow step"""
    step_type: StepType
    success: bool = True
    output_data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
    error_message: Optional[str] = None

class WorkflowExecution(BaseModel):
    """Complete workflow execution"""
    workflow_id: str
    user_query: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    success: bool = True
    final_response: str = ""
    execution_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)

class OrchestrationResult(BaseModel):
    """Result from multi-tool orchestration"""
    success: bool
    workflow_id: str
    tools_orchestrated: int
    execution_time: float
    final_result: Dict[str, Any]
    quality_validation: Dict[str, Any]
    tool_breakdown: Dict[str, Dict[str, Any]]
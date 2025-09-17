"""
GPT.R1 - Enhanced Chat Service with Advanced Agentic Workflow
Integrates the new modular multi-step agentic flow
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional
import json
import logging
from datetime import datetime

from .openai_service import OpenAIService
from .agentic_service import AdvancedAgenticService, AgentWorkflow
from ..crud import conversation_crud, message_crud
from ..models.conversation import Message
from ..schemas.chat import MessageCreate
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """
    Enhanced chat service with advanced multi-step agentic workflow
    
    This addresses the client feedback for "more modular or multi-step" agentic flow
    by integrating the new AdvancedAgenticService
    """
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.agentic_service = AdvancedAgenticService()
    
    async def stream_chat_response(
        self, 
        conversation_id: int,
        user_message: str, 
        db: AsyncSession
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response using advanced agentic workflow
        
        Process:
        1. Execute multi-step agentic workflow
        2. Stream the response generation
        3. Save messages to database
        """
        try:
            # Save user message first
            user_msg = MessageCreate(
                conversation_id=conversation_id,
                content=user_message,
                role="user"
            )
            await message_crud.create(db, obj_in=user_msg)
            
            # Get conversation history for context
            conversation_history = await self._get_conversation_history(conversation_id, db)
            
            # Yield workflow start indicator
            yield "data: " + json.dumps({
                "type": "workflow_start",
                "message": "🤖 Initiating advanced agentic workflow...",
                "timestamp": datetime.now().isoformat()
            }) + "\n\n"
            
            # Execute the advanced agentic workflow
            workflow = await self.agentic_service.execute_agentic_workflow(
                user_query=user_message,
                conversation_history=conversation_history
            )
            
            # Stream workflow progress
            await self._stream_workflow_progress(workflow)
            
            # Generate streaming response using OpenAI with enhanced context
            if workflow.success and workflow.final_response:
                # Use workflow results to enhance the OpenAI prompt
                enhanced_prompt = self._create_enhanced_prompt(
                    user_message, 
                    workflow, 
                    conversation_history
                )
                
                yield "data: " + json.dumps({
                    "type": "response_start",
                    "message": "📝 Generating enhanced response...",
                    "workflow_confidence": self._extract_workflow_confidence(workflow),
                    "timestamp": datetime.now().isoformat()
                }) + "\n\n"
                
                # Stream the actual response
                full_response = ""
                async for chunk in self.openai_service.stream_completion(enhanced_prompt):
                    if chunk:
                        full_response += chunk
                        yield "data: " + json.dumps({
                            "type": "content",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat()
                        }) + "\n\n"
                
                # Add workflow metadata to response
                workflow_summary = self._create_workflow_summary(workflow)
                if workflow_summary:
                    yield "data: " + json.dumps({
                        "type": "workflow_summary",
                        "content": f"\n\n---\n**Agentic Workflow Summary:**\n{workflow_summary}",
                        "timestamp": datetime.now().isoformat()
                    }) + "\n\n"
                    full_response += f"\n\n---\n**Agentic Workflow Summary:**\n{workflow_summary}"
                
                # Save assistant response
                assistant_msg = MessageCreate(
                    conversation_id=conversation_id,
                    content=full_response,
                    role="assistant"
                )
                await message_crud.create(db, obj_in=assistant_msg)
                
            else:
                # Fallback to basic response if workflow failed
                error_message = "I encountered an issue with the advanced workflow. Let me provide a basic response."
                yield "data: " + json.dumps({
                    "type": "content",
                    "content": error_message,
                    "timestamp": datetime.now().isoformat()
                }) + "\n\n"
                
                # Save error response
                assistant_msg = MessageCreate(
                    conversation_id=conversation_id,
                    content=error_message,
                    role="assistant"
                )
                await message_crud.create(db, obj_in=assistant_msg)
            
            # Yield completion
            yield "data: " + json.dumps({
                "type": "complete",
                "workflow_stats": self.agentic_service.get_workflow_statistics(),
                "timestamp": datetime.now().isoformat()
            }) + "\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield "data: " + json.dumps({
                "type": "error",
                "message": f"An error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }) + "\n\n"
    
    async def _get_conversation_history(self, conversation_id: int, db: AsyncSession) -> List[Dict[str, str]]:
        """Get conversation history for context"""
        try:
            messages = await message_crud.get_messages_by_conversation(db, conversation_id=conversation_id)
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat() if msg.created_at else ""
                }
                for msg in messages[-10:]  # Last 10 messages for context
            ]
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def _stream_workflow_progress(self, workflow: AgentWorkflow):
        """Stream workflow progress updates (placeholder for future implementation)"""
        # In a real implementation, this could stream live workflow progress
        # For now, we'll include workflow results in the final response
        pass
    
    def _create_enhanced_prompt(
        self, 
        user_message: str, 
        workflow: AgentWorkflow, 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Create enhanced prompt using workflow results"""
        
        prompt_parts = []
        
        # Add system message with workflow context
        system_msg = """You are GPT.R1, an advanced AI assistant with multi-step agentic capabilities.

Your response has been enhanced through a sophisticated workflow that included:
1. Query analysis and intent understanding
2. External information gathering via DuckDuckGo search (when needed)
3. Information synthesis and context integration
4. Response validation and quality assessment
5. Final response optimization

Provide a comprehensive, accurate, and helpful response based on the enhanced context provided."""
        
        prompt_parts.append(f"System: {system_msg}")
        
        # Add conversation history
        if conversation_history:
            prompt_parts.append("\nConversation History:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                prompt_parts.append(f"{msg['role'].title()}: {msg['content']}")
        
        # Add workflow context
        if workflow.success:
            workflow_context = self._extract_workflow_context(workflow)
            if workflow_context:
                prompt_parts.append(f"\nWorkflow Context: {workflow_context}")
        
        # Add current user message
        prompt_parts.append(f"\nUser: {user_message}")
        prompt_parts.append("\nAssistant:")
        
        return "\n".join(prompt_parts)
    
    def _extract_workflow_confidence(self, workflow: AgentWorkflow) -> float:
        """Extract confidence level from workflow"""
        if not workflow.success or not workflow.steps:
            return 0.5
        
        # Look for confidence in synthesis or validation steps
        for step in workflow.steps:
            if step.output_data and "confidence_level" in step.output_data:
                return step.output_data["confidence_level"]
        
        return 0.8  # Default confidence
    
    def _extract_workflow_context(self, workflow: AgentWorkflow) -> str:
        """Extract relevant context from workflow execution"""
        context_parts = []
        
        for step in workflow.steps:
            if step.success and step.output_data:
                # Add search results if available
                if step.step_type.value == "search" and step.output_data.get("search_results"):
                    search_results = step.output_data["search_results"]
                    if len(search_results) > 200:
                        search_results = search_results[:200] + "..."
                    context_parts.append(f"Search results: {search_results}")
                
                # Add synthesis context
                elif step.step_type.value == "synthesize" and step.output_data.get("enhanced_context"):
                    context_parts.append(f"Context: {step.output_data['enhanced_context']}")
        
        return " | ".join(context_parts)
    
    def _create_workflow_summary(self, workflow: AgentWorkflow) -> str:
        """Create a summary of the workflow execution"""
        if not workflow.success:
            return "⚠️ Workflow encountered issues - basic response provided"
        
        summary_parts = []
        
        # Execution time
        summary_parts.append(f"⏱️ Execution time: {workflow.total_execution_time:.2f}s")
        
        # Steps completed
        successful_steps = sum(1 for step in workflow.steps if step.success)
        summary_parts.append(f"✅ Steps completed: {successful_steps}/{len(workflow.steps)}")
        
        # Search performed
        search_step = next((step for step in workflow.steps if step.step_type.value == "search"), None)
        if search_step and search_step.output_data.get("search_performed"):
            summary_parts.append("🔍 External search performed")
        
        # Confidence level
        confidence = self._extract_workflow_confidence(workflow)
        summary_parts.append(f"📊 Confidence: {confidence:.1%}")
        
        return " | ".join(summary_parts)
    
    async def get_conversation_summary(self, conversation_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Get conversation summary with workflow statistics"""
        try:
            messages = await message_crud.get_messages_by_conversation(db, conversation_id=conversation_id)
            workflow_stats = self.agentic_service.get_workflow_statistics()
            
            return {
                "message_count": len(messages),
                "workflow_statistics": workflow_stats,
                "last_updated": messages[-1].created_at.isoformat() if messages else None
            }
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {
                "message_count": 0,
                "workflow_statistics": {},
                "error": str(e)
            }
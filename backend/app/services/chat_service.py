"""
GPT.R1 - Enhanced Chat Service with Advanced Agentic Workflow
Integrates the new modular multi-step agentic flow with tool orchestration
Enhanced with RAG capabilities for internet search integration
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional
import json
import logging
from datetime import datetime

from .openai_service import OpenAIService
from .agentic_service import AdvancedAgenticService, AgentWorkflow
from ..agents.rag_agent import enhance_with_rag
from ..crud import conversation_crud, message_crud
from ..models.conversation import Message
from ..schemas.chat import MessageCreate
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class EnhancedChatService:
    """
    Enhanced chat service with advanced multi-step agentic workflow and tool orchestration
    
    This addresses the client feedback for sophisticated multi-tool orchestration
    by integrating the new AdvancedAgenticService with orchestration capabilities
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
        Stream chat response using advanced agentic workflow with tool orchestration
        
        Enhanced Process:
        1. Execute multi-tool orchestration workflow
        2. Stream real-time workflow progress
        3. Generate enhanced response with OpenAI
        4. Save messages to database with metadata
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
            
            # RAG Enhancement - Check if search is needed
            yield f"data: {json.dumps({'type': 'rag_start', 'message': '🔍 Analyzing query for real-time information needs...', 'step': 'rag_analysis', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            enhanced_message, used_search = await enhance_with_rag(user_message)
            
            if used_search:
                yield f"data: {json.dumps({'type': 'rag_complete', 'message': '✅ Enhanced with real-time search results', 'search_used': True, 'timestamp': datetime.now().isoformat()})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'rag_complete', 'message': '📚 Using existing knowledge base', 'search_used': False, 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Yield workflow start indicator
            yield f"data: {json.dumps({'type': 'workflow_start', 'message': '🤖 Initiating advanced multi-tool orchestration...', 'step': 'initialize', 'timestamp': datetime.now().isoformat()})}\n\n"
            
            # Execute the advanced agentic workflow with orchestration
            workflow = await self.agentic_service.execute_agentic_workflow(
                user_query=enhanced_message,  # Use RAG-enhanced message
                conversation_history=conversation_history
            )
            
            # Stream workflow progress with detailed step information
            await self._stream_workflow_progress(workflow)
            
            # Generate streaming response using OpenAI with enhanced context
            if workflow.success and workflow.final_response:
                # Use workflow results to enhance the OpenAI prompt
                enhanced_prompt = self._create_enhanced_prompt(
                    enhanced_message,  # Use RAG-enhanced message
                    workflow, 
                    conversation_history
                )
                
                # Extract orchestration metadata
                orchestration_confidence = self._extract_orchestration_confidence(workflow)
                tools_used = self._extract_tools_used(workflow)
                
                yield f"data: {json.dumps({'type': 'response_start', 'message': '📝 Generating enhanced response...', 'workflow_confidence': orchestration_confidence, 'tools_used': tools_used, 'rag_enhanced': used_search, 'timestamp': datetime.now().isoformat()})}\n\n"
                
                # Stream the actual response
                full_response = ""
                try:
                    async for chunk in self.openai_service.stream_completion(enhanced_prompt):
                        if chunk and chunk.strip():
                            full_response += chunk
                            yield f"data: {json.dumps({'type': 'content', 'content': chunk, 'timestamp': datetime.now().isoformat()})}\n\n"
                            
                            # Add small delay to ensure proper streaming
                            await asyncio.sleep(0.01)
                            
                except Exception as stream_error:
                    logger.error(f"OpenAI streaming error: {stream_error}")
                    # Fallback to workflow response if OpenAI fails
                    fallback_response = workflow.final_response
                    full_response = fallback_response
                    
                    yield f"data: {json.dumps({'type': 'content', 'content': fallback_response, 'timestamp': datetime.now().isoformat()})}\n\n"
                
                # Add workflow metadata to response
                workflow_summary = self._create_workflow_summary(workflow)
                if workflow_summary:
                    summary_content = f"\n\n---\n**🔧 Multi-Tool Orchestration Summary:**\n{workflow_summary}"
                    yield f"data: {json.dumps({'type': 'workflow_summary', 'content': summary_content, 'timestamp': datetime.now().isoformat()})}\n\n"
                    full_response += summary_content
                
                # Save assistant response with metadata
                assistant_msg = MessageCreate(
                    conversation_id=conversation_id,
                    content=full_response,
                    role="assistant",
                    metadata={"workflow_id": workflow.workflow_id, "tools_used": tools_used}
                )
                await message_crud.create(db, obj_in=assistant_msg)
                
            else:
                # Enhanced fallback with workflow error details
                error_details = self._extract_workflow_errors(workflow)
                fallback_message = f"I encountered an issue with the advanced workflow ({error_details}). Let me provide a direct response."
                
                yield f"data: {json.dumps({'type': 'content', 'content': fallback_message, 'timestamp': datetime.now().isoformat()})}\n\n"
                
                # Generate basic response
                try:
                    basic_prompt = f"User message: {user_message}\n\nProvide a helpful response:"
                    async for chunk in self.openai_service.stream_completion(basic_prompt):
                        if chunk and chunk.strip():
                            fallback_message += chunk
                            yield f"data: {json.dumps({'type': 'content', 'content': chunk, 'timestamp': datetime.now().isoformat()})}\n\n"
                            await asyncio.sleep(0.01)
                except Exception as fallback_error:
                    logger.error(f"Fallback streaming error: {fallback_error}")
                    fallback_message += "\n\nI'm experiencing technical difficulties. Please try your request again."
                
                # Save fallback response
                assistant_msg = MessageCreate(
                    conversation_id=conversation_id,
                    content=fallback_message,
                    role="assistant",
                    metadata={"fallback": True, "workflow_error": error_details}
                )
                await message_crud.create(db, obj_in=assistant_msg)
            
            # Yield completion with comprehensive stats
            completion_stats = {
                "type": "complete",
                "workflow_stats": self.agentic_service.get_workflow_statistics(),
                "orchestration_stats": self._get_orchestration_stats(workflow),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_stats)}\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'An error occurred: {str(e)}', 'timestamp': datetime.now().isoformat()})}\n\n"
    
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
        """Stream workflow progress updates with orchestration details"""
        try:
            for i, step in enumerate(workflow.steps):
                step_name = step.step_type.value
                success_status = "✅" if step.success else "❌"
                
                progress_data = {
                    "type": "workflow_progress",
                    "step": step_name,
                    "step_number": i + 1,
                    "total_steps": len(workflow.steps),
                    "status": success_status,
                    "description": step.description,
                    "execution_time": step.execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add orchestration details if available
                if step_name == "orchestrate" and step.output_data:
                    progress_data["orchestration_details"] = {
                        "tools_orchestrated": step.output_data.get("tools_orchestrated", 0),
                        "orchestration_successful": step.output_data.get("orchestration_successful", False)
                    }
                
                # Simulate streaming delay for realistic progress
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error streaming workflow progress: {e}")
    
    def _create_enhanced_prompt(
        self, 
        user_message: str, 
        workflow: AgentWorkflow, 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Create enhanced prompt using workflow results and orchestration insights"""
        
        prompt_parts = []
        
        # Add system message with enhanced workflow context
        system_msg = """You are GPT.R1, an advanced AI assistant with sophisticated multi-tool orchestration capabilities.

Your response has been enhanced through an advanced workflow that included:
1. Multi-tool orchestration with 4 specialized AI tools
2. Query analysis and intent understanding
3. External information gathering via DuckDuckGo search (when needed)
4. Multi-source information synthesis with conflict detection
5. Comprehensive quality validation and fact-checking
6. Response optimization based on orchestration insights

Provide a comprehensive, accurate, and helpful response based on the enhanced context and orchestration results provided."""
        
        prompt_parts.append(f"System: {system_msg}")
        
        # Add conversation history
        if conversation_history:
            prompt_parts.append("\nConversation History:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                prompt_parts.append(f"{msg['role'].title()}: {msg['content']}")
        
        # Add workflow context with orchestration insights
        if workflow.success:
            workflow_context = self._extract_workflow_context(workflow)
            if workflow_context:
                prompt_parts.append(f"\nEnhanced Workflow Context: {workflow_context}")
            
            # Add orchestration insights
            orchestration_insights = self._extract_orchestration_insights(workflow)
            if orchestration_insights:
                prompt_parts.append(f"\nOrchestration Insights: {orchestration_insights}")
        
        # Add current user message
        prompt_parts.append(f"\nUser: {user_message}")
        prompt_parts.append("\nAssistant:")
        
        return "\n".join(prompt_parts)
    
    def _extract_orchestration_confidence(self, workflow: AgentWorkflow) -> float:
        """Extract orchestration confidence from workflow"""
        try:
            for step in workflow.steps:
                if step.step_type.value == "orchestrate" and step.output_data:
                    quality_validation = step.output_data.get("quality_validation", {})
                    return quality_validation.get("quality_score", 0.8)
            return 0.8
        except Exception:
            return 0.8
    
    def _extract_tools_used(self, workflow: AgentWorkflow) -> List[str]:
        """Extract list of tools used in orchestration"""
        try:
            for step in workflow.steps:
                if step.step_type.value == "orchestrate" and step.output_data:
                    tool_breakdown = step.output_data.get("tool_breakdown", {})
                    return list(tool_breakdown.keys())
            return []
        except Exception:
            return []
    
    def _extract_workflow_errors(self, workflow: AgentWorkflow) -> str:
        """Extract error details from failed workflow"""
        try:
            errors = []
            for step in workflow.steps:
                if not step.success and step.error:
                    errors.append(f"{step.step_type.value}: {step.error}")
            return "; ".join(errors) if errors else "Unknown error"
        except Exception:
            return "Error details unavailable"
    
    def _get_orchestration_stats(self, workflow: AgentWorkflow) -> Dict[str, Any]:
        """Get orchestration statistics from workflow"""
        try:
            for step in workflow.steps:
                if step.step_type.value == "orchestrate" and step.output_data:
                    return {
                        "tools_orchestrated": step.output_data.get("tools_orchestrated", 0),
                        "execution_time": step.output_data.get("execution_time", 0),
                        "orchestration_successful": step.output_data.get("orchestration_successful", False),
                        "quality_score": step.output_data.get("quality_validation", {}).get("quality_score", 0)
                    }
            return {}
        except Exception:
            return {}
    
    def _create_workflow_summary(self, workflow: AgentWorkflow) -> str:
        """Create a summary of the workflow execution"""
        try:
            summary_parts = []
            
            # Basic workflow info
            summary_parts.append(f"• Workflow ID: {workflow.workflow_id}")
            summary_parts.append(f"• Total Steps: {len(workflow.steps)}")
            summary_parts.append(f"• Execution Time: {workflow.total_execution_time:.2f}s")
            summary_parts.append(f"• Success: {'✅' if workflow.success else '❌'}")
            
            # Orchestration details
            orchestration_stats = self._get_orchestration_stats(workflow)
            if orchestration_stats:
                summary_parts.append(f"• Tools Orchestrated: {orchestration_stats.get('tools_orchestrated', 0)}")
                summary_parts.append(f"• Quality Score: {orchestration_stats.get('quality_score', 0):.2f}")
            
            # Step details
            step_summaries = []
            for step in workflow.steps:
                status = "✅" if step.success else "❌"
                step_summaries.append(f"{status} {step.step_type.value.title()} ({step.execution_time:.2f}s)")
            
            if step_summaries:
                summary_parts.append(f"• Steps: {', '.join(step_summaries)}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating workflow summary: {e}")
            return "Workflow summary unavailable"
    
    def _extract_workflow_context(self, workflow: AgentWorkflow) -> str:
        """Extract relevant context from workflow results"""
        try:
            context_parts = []
            
            for step in workflow.steps:
                if step.success and step.output_data:
                    step_type = step.step_type.value
                    
                    if step_type == "analyze":
                        intent = step.output_data.get("intent", "")
                        if intent:
                            context_parts.append(f"Intent: {intent}")
                    
                    elif step_type == "search" and step.output_data.get("search_performed"):
                        results = step.output_data.get("search_results", "")
                        if results:
                            context_parts.append(f"Search Results: {results[:200]}...")
                    
                    elif step_type == "synthesize":
                        confidence = step.output_data.get("confidence_level", 0)
                        context_parts.append(f"Synthesis Confidence: {confidence:.2f}")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error extracting workflow context: {e}")
            return ""
    
    def _extract_orchestration_insights(self, workflow: AgentWorkflow) -> str:
        """Extract orchestration insights from workflow"""
        try:
            for step in workflow.steps:
                if step.step_type.value == "orchestrate" and step.output_data:
                    final_result = step.output_data.get("final_result", {})
                    insights = final_result.get("integrated_insights", [])
                    if insights:
                        return " | ".join(insights[:3])  # Top 3 insights
            return ""
        except Exception:
            return ""
    
    def _extract_workflow_confidence(self, workflow: AgentWorkflow) -> float:
        """Extract confidence level from workflow"""
        if not workflow.success or not workflow.steps:
            return 0.5
        
        # Look for confidence in synthesis or validation steps
        for step in workflow.steps:
            if step.output_data and "confidence_level" in step.output_data:
                return step.output_data["confidence_level"]
        
        return 0.8  # Default confidence
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get chat service workflow statistics"""
        return self.agentic_service.get_workflow_statistics()
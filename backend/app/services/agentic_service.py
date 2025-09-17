"""
GPT.R1 - Advanced Multi-Step Agentic AI System
Enhanced modular agentic flow with multi-tool orchestration
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from .rag_service import RAGService
from .multi_tool_orchestrator import AdvancedToolOrchestrator

logger = logging.getLogger(__name__)

class AgentStepType(Enum):
    """Types of agent steps in the workflow"""
    ORCHESTRATE = "orchestrate"  # NEW: Multi-tool orchestration step
    ANALYZE = "analyze"
    SEARCH = "search"
    SYNTHESIZE = "synthesize"
    VALIDATE = "validate"
    RESPOND = "respond"

@dataclass
class AgentStep:
    """Individual step in the agentic workflow"""
    step_type: AgentStepType
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = None
    success: bool = False
    execution_time: float = 0.0
    error: Optional[str] = None

@dataclass
class AgentWorkflow:
    """Complete agentic workflow execution"""
    workflow_id: str
    user_query: str
    steps: List[AgentStep]
    final_response: str = ""
    total_execution_time: float = 0.0
    success: bool = False

class AdvancedAgenticService:
    """
    Advanced multi-step agentic AI system with multi-tool orchestration
    
    Enhanced to address feedback for sophisticated multi-tool orchestration
    """
    
    def __init__(self):
        self.rag_service = RAGService()
        self.orchestrator = AdvancedToolOrchestrator()  # NEW: Multi-tool orchestrator
        self.workflow_history = []
    
    async def execute_agentic_workflow(self, user_query: str, conversation_history: List[Dict] = None) -> AgentWorkflow:
        """
        Execute enhanced multi-step agentic workflow with tool orchestration
        
        Enhanced Steps:
        1. ORCHESTRATE - Multi-tool workflow planning and execution
        2. ANALYZE - Deep query intent analysis
        3. SEARCH - Advanced information gathering
        4. SYNTHESIZE - Sophisticated information integration
        5. VALIDATE - Comprehensive quality validation
        6. RESPOND - Enhanced response generation
        """
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        workflow = AgentWorkflow(
            workflow_id=workflow_id,
            user_query=user_query,
            steps=[]
        )
        
        start_time = datetime.now()
        
        try:
            # Step 1: ORCHESTRATE - Multi-Tool Workflow Orchestration (NEW)
            orchestrate_step = await self._step_orchestrate_tools(user_query, conversation_history)
            workflow.steps.append(orchestrate_step)
            
            if not orchestrate_step.success:
                logger.warning("Orchestration step failed, falling back to traditional workflow")
            
            # Step 2: ANALYZE - Enhanced Query Intent Analysis
            analyze_step = await self._step_analyze_query(user_query, conversation_history, orchestrate_step.output_data)
            workflow.steps.append(analyze_step)
            
            if not analyze_step.success:
                return await self._handle_workflow_failure(workflow, "Analysis step failed")
            
            # Step 3: SEARCH - Advanced Information Gathering
            search_step = await self._step_search_information(analyze_step.output_data, orchestrate_step.output_data)
            workflow.steps.append(search_step)
            
            # Step 4: SYNTHESIZE - Sophisticated Information Integration
            synthesize_step = await self._step_synthesize_information(
                user_query, 
                analyze_step.output_data,
                search_step.output_data if search_step.success else {},
                conversation_history,
                orchestrate_step.output_data  # Include orchestration results
            )
            workflow.steps.append(synthesize_step)
            
            if not synthesize_step.success:
                return await self._handle_workflow_failure(workflow, "Synthesis step failed")
            
            # Step 4: VALIDATE - Response Quality Check
            validate_step = await self._step_validate_response(synthesize_step.output_data)
            workflow.steps.append(validate_step)
            
            # Step 5: RESPOND - Final Response Generation
            respond_step = await self._step_generate_response(
                synthesize_step.output_data,
                validate_step.output_data
            )
            workflow.steps.append(respond_step)
            
            if respond_step.success:
                workflow.final_response = respond_step.output_data.get("response", "")
                workflow.success = True
            
        except Exception as e:
            logger.error(f"Agentic workflow error: {e}")
            workflow = await self._handle_workflow_failure(workflow, str(e))
        
        finally:
            end_time = datetime.now()
            workflow.total_execution_time = (end_time - start_time).total_seconds()
            self.workflow_history.append(workflow)
        
        return workflow
    
    async def _step_orchestrate_tools(self, user_query: str, conversation_history: List[Dict] = None) -> AgentStep:
        """
        Step 1: Multi-tool orchestration for sophisticated workflow planning
        """
        step = AgentStep(
            step_type=AgentStepType.ORCHESTRATE,
            description="Orchestrate multiple AI tools for comprehensive query processing",
            input_data={"query": user_query, "history": conversation_history or []}
        )
        
        start_time = datetime.now()
        
        try:
            # Prepare context for orchestrator
            context = {
                "conversation_history": conversation_history or [],
                "sources": []
            }
            
            # Execute multi-tool orchestration
            orchestration_result = await self.orchestrator.orchestrate_workflow(user_query, context)
            
            if orchestration_result["success"]:
                step.output_data = {
                    "orchestration_successful": True,
                    "workflow_id": orchestration_result["workflow_id"],
                    "tools_orchestrated": orchestration_result["tools_orchestrated"],
                    "execution_time": orchestration_result["execution_time"],
                    "final_result": orchestration_result["final_result"],
                    "quality_validation": orchestration_result["quality_validation"],
                    "tool_breakdown": orchestration_result["tool_breakdown"],
                    "orchestration_metadata": orchestration_result["orchestration_metadata"]
                }
                step.success = True
                
                logger.info(f"Multi-tool orchestration completed: {orchestration_result['tools_orchestrated']} tools orchestrated")
            else:
                step.output_data = {
                    "orchestration_successful": False,
                    "error": orchestration_result.get("error", "Unknown orchestration error"),
                    "fallback_to_traditional": True
                }
                step.success = False
                logger.warning("Multi-tool orchestration failed, will fallback to traditional workflow")
                
        except Exception as e:
            step.error = str(e)
            step.output_data = {
                "orchestration_successful": False,
                "error": str(e),
                "fallback_to_traditional": True
            }
            logger.error(f"Tool orchestration failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_analyze_query(self, user_query: str, conversation_history: List[Dict] = None, orchestration_data: Dict[str, Any] = None) -> AgentStep:
        """
        Step 2: Enhanced analyze user query with orchestration insights
        """
        step = AgentStep(
            step_type=AgentStepType.ANALYZE,
            description="Enhanced query analysis with orchestration insights",
            input_data={"query": user_query, "history": conversation_history or [], "orchestration": orchestration_data or {}}
        )
        
        start_time = datetime.now()
        
        try:
            # Enhanced analysis with orchestration insights
            analysis = {
                "query_type": self._classify_query_type(user_query),
                "requires_search": self._requires_external_search(user_query),
                "complexity": self._assess_query_complexity(user_query),
                "context_needed": len(conversation_history or []) > 0,
                "intent": self._extract_user_intent(user_query)
            }
            
            # Enhance with orchestration data if available
            if orchestration_data and orchestration_data.get("orchestration_successful"):
                analysis.update({
                    "orchestration_enhanced": True,
                    "tools_used": orchestration_data.get("tools_orchestrated", 0),
                    "orchestration_confidence": orchestration_data.get("quality_validation", {}).get("quality_score", 0),
                    "multi_tool_insights": orchestration_data.get("final_result", {}).get("integrated_insights", [])
                })
            else:
                analysis["orchestration_enhanced"] = False
            
            step.output_data = analysis
            step.success = True
            
            logger.info(f"Enhanced query analysis completed: {analysis['query_type']}, orchestration_enhanced: {analysis['orchestration_enhanced']}")
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Enhanced query analysis failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_search_information(self, analysis_data: Dict[str, Any], orchestration_data: Dict[str, Any] = None) -> AgentStep:
        """
        Step 3: Enhanced search for external information with orchestration insights
        """
        step = AgentStep(
            step_type=AgentStepType.SEARCH,
            description="Enhanced search with orchestration insights",
            input_data={"analysis": analysis_data, "orchestration": orchestration_data or {}}
        )
        
        start_time = datetime.now()
        
        try:
            if analysis_data.get("requires_search", False):
                # Use RAG service for DuckDuckGo search
                search_query = self._optimize_search_query(analysis_data["intent"])
                search_results = await self.rag_service.get_context_from_search(search_query)
                
                step.output_data = {
                    "search_performed": True,
                    "search_query": search_query,
                    "search_results": search_results,
                    "result_quality": self._assess_search_quality(search_results)
                }
                
                logger.info(f"Search completed for: {search_query}")
            else:
                step.output_data = {
                    "search_performed": False,
                    "reason": "No external search required"
                }
                
                logger.info("Search skipped - not required for this query")
            
            step.success = True
            
        except Exception as e:
            step.error = str(e)
            step.output_data = {"search_performed": False, "error": str(e)}
            logger.warning(f"Search step failed: {e}")
            # Search failure is not critical - continue workflow
            step.success = True
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_synthesize_information(self, user_query: str, analysis: Dict, search_data: Dict, history: List[Dict], orchestration_data: Dict = None) -> AgentStep:
        """
        Step 4: Enhanced synthesize all available information with orchestration insights
        """
        step = AgentStep(
            step_type=AgentStepType.SYNTHESIZE,
            description="Enhanced synthesis with multi-tool orchestration insights",
            input_data={
                "query": user_query,
                "analysis": analysis,
                "search_data": search_data,
                "history": history,
                "orchestration": orchestration_data or {}
            }
        )
        
        start_time = datetime.now()
        
        try:
            # Enhanced synthesis with orchestration insights
            synthesis = {
                "enhanced_context": self._build_enhanced_context(analysis, search_data, history, orchestration_data),
                "response_strategy": self._determine_response_strategy(analysis, orchestration_data),
                "confidence_level": self._calculate_confidence_level(analysis, search_data, orchestration_data),
                "information_sources": self._identify_information_sources(search_data, orchestration_data)
            }
            
            # Include orchestration insights if available
            if orchestration_data and orchestration_data.get("orchestration_successful"):
                synthesis.update({
                    "orchestration_enhanced": True,
                    "multi_tool_insights": orchestration_data.get("final_result", {}).get("integrated_insights", []),
                    "tool_contributions": orchestration_data.get("final_result", {}).get("tool_contributions", {}),
                    "orchestration_confidence": orchestration_data.get("quality_validation", {}).get("quality_score", 0)
                })
            else:
                synthesis["orchestration_enhanced"] = False
            
            step.output_data = synthesis
            step.success = True
            
            logger.info(f"Information synthesis completed with confidence: {synthesis['confidence_level']}")
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Synthesis step failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_validate_response(self, synthesis_data: Dict[str, Any]) -> AgentStep:
        """
        Step 4: Validate response quality and accuracy
        """
        step = AgentStep(
            step_type=AgentStepType.VALIDATE,
            description="Validate response quality and accuracy",
            input_data=synthesis_data
        )
        
        start_time = datetime.now()
        
        try:
            validation = {
                "quality_score": self._assess_response_quality(synthesis_data),
                "accuracy_check": self._verify_information_accuracy(synthesis_data),
                "completeness": self._check_response_completeness(synthesis_data),
                "recommendations": self._generate_improvement_recommendations(synthesis_data)
            }
            
            step.output_data = validation
            step.success = True
            
            logger.info(f"Response validation completed: quality={validation['quality_score']}")
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Validation step failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_generate_response(self, synthesis_data: Dict, validation_data: Dict) -> AgentStep:
        """
        Step 5: Generate final response based on all previous steps
        """
        step = AgentStep(
            step_type=AgentStepType.RESPOND,
            description="Generate final response",
            input_data={"synthesis": synthesis_data, "validation": validation_data}
        )
        
        start_time = datetime.now()
        
        try:
            # Generate enhanced response using all gathered information
            response = self._create_enhanced_response(synthesis_data, validation_data)
            
            step.output_data = {
                "response": response,
                "response_length": len(response),
                "includes_sources": synthesis_data.get("information_sources", []) != [],
                "confidence": validation_data.get("quality_score", 0.8)
            }
            
            step.success = True
            
            logger.info(f"Final response generated: {len(response)} characters")
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Response generation failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    # Helper methods for each step
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of user query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what", "how", "why", "when", "where", "who"]):
            return "informational"
        elif any(word in query_lower for word in ["create", "make", "build", "generate", "write"]):
            return "creative"
        elif any(word in query_lower for word in ["analyze", "compare", "evaluate", "assess"]):
            return "analytical"
        elif any(word in query_lower for word in ["help", "assistance", "support"]):
            return "assistance"
        else:
            return "general"
    
    def _requires_external_search(self, query: str) -> bool:
        """Determine if query requires external search"""
        search_indicators = [
            "current", "latest", "recent", "today", "now", "news",
            "weather", "stock", "price", "events", "happening",
            "2024", "2025", "this year", "real-time"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in search_indicators)
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess the complexity of the query"""
        word_count = len(query.split())
        
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "medium"
        else:
            return "complex"
    
    def _extract_user_intent(self, query: str) -> str:
        """Extract the main intent from user query"""
        # Simple intent extraction - could be enhanced with NLP
        return query.strip()
    
    def _optimize_search_query(self, intent: str) -> str:
        """Optimize query for search engines"""
        # Remove conversational elements and optimize for search
        search_query = intent.replace("?", "").strip()
        return search_query
    
    def _assess_search_quality(self, search_results: str) -> float:
        """Assess the quality of search results"""
        if not search_results:
            return 0.0
        
        # Simple quality assessment based on length and content
        quality = min(len(search_results) / 1000, 1.0)  # Normalize to 0-1
        return quality
    
    def _build_enhanced_context(self, analysis: Dict, search_data: Dict, history: List[Dict], orchestration_data: Dict = None) -> str:
        """Build enhanced context from all sources including orchestration"""
        context_parts = []
        
        if history:
            context_parts.append("Conversation history available")
        
        if search_data.get("search_performed") and search_data.get("search_results"):
            context_parts.append(f"External information: {search_data['search_results'][:500]}...")
        
        # Include orchestration context
        if orchestration_data and orchestration_data.get("orchestration_successful"):
            tools_used = orchestration_data.get("tools_orchestrated", 0)
            context_parts.append(f"Multi-tool orchestration: {tools_used} tools coordinated")
            
            insights = orchestration_data.get("final_result", {}).get("integrated_insights", [])
            if insights:
                context_parts.append(f"Orchestration insights: {', '.join(insights[:3])}")
        
        return " | ".join(context_parts)
    
    def _determine_response_strategy(self, analysis: Dict, orchestration_data: Dict = None) -> str:
        """Determine the best strategy for response generation with orchestration enhancement"""
        query_type = analysis.get("query_type", "general")
        
        strategy_map = {
            "informational": "provide_detailed_facts",
            "creative": "generate_creative_content",
            "analytical": "provide_structured_analysis",
            "assistance": "offer_helpful_guidance",
            "general": "conversational_response"
        }
        
        base_strategy = strategy_map.get(query_type, "conversational_response")
        
        # Enhance strategy based on orchestration results
        if orchestration_data and orchestration_data.get("orchestration_successful"):
            tools_used = orchestration_data.get("tools_orchestrated", 0)
            if tools_used >= 3:
                base_strategy = f"multi_tool_enhanced_{base_strategy}"
        
        return base_strategy
    
    def _calculate_confidence_level(self, analysis: Dict, search_data: Dict, orchestration_data: Dict = None) -> float:
        """Calculate confidence level with orchestration enhancement"""
        base_confidence = 0.7
        
        if search_data.get("search_performed") and search_data.get("search_results"):
            base_confidence += 0.2
        
        if analysis.get("complexity") == "simple":
            base_confidence += 0.1
        
        # Boost confidence with successful orchestration
        if orchestration_data and orchestration_data.get("orchestration_successful"):
            orchestration_confidence = orchestration_data.get("quality_validation", {}).get("quality_score", 0)
            tools_used = orchestration_data.get("tools_orchestrated", 0)
            
            # Add confidence boost based on orchestration success
            confidence_boost = (orchestration_confidence * 0.2) + (tools_used * 0.05)
            base_confidence += min(confidence_boost, 0.25)  # Max 25% boost
        
        return min(base_confidence, 1.0)
    
    def _identify_information_sources(self, search_data: Dict, orchestration_data: Dict = None) -> List[str]:
        """Identify sources of information used including orchestration tools"""
        sources = []
        
        if search_data.get("search_performed"):
            sources.append("DuckDuckGo Search")
        
        sources.append("AI Knowledge Base")
        
        # Add orchestration tool sources
        if orchestration_data and orchestration_data.get("orchestration_successful"):
            tool_breakdown = orchestration_data.get("tool_breakdown", {})
            for tool_name, tool_result in tool_breakdown.items():
                if tool_result.get("success"):
                    tool_type = tool_result.get("tool_type", "unknown")
                    sources.append(f"Multi-Tool Orchestration: {tool_name} ({tool_type})")
        
        return sources
        
        return sources
    
    def _assess_response_quality(self, synthesis_data: Dict) -> float:
        """Assess the quality of the synthesized response"""
        confidence = synthesis_data.get("confidence_level", 0.7)
        context_quality = 0.8 if synthesis_data.get("enhanced_context") else 0.5
        
        return (confidence + context_quality) / 2
    
    def _verify_information_accuracy(self, synthesis_data: Dict) -> bool:
        """Verify information accuracy (simplified)"""
        # In a real implementation, this could use fact-checking APIs
        return True
    
    def _check_response_completeness(self, synthesis_data: Dict) -> bool:
        """Check if response addresses all aspects of the query"""
        return synthesis_data.get("enhanced_context") is not None
    
    def _generate_improvement_recommendations(self, synthesis_data: Dict) -> List[str]:
        """Generate recommendations for response improvement"""
        recommendations = []
        
        if synthesis_data.get("confidence_level", 0) < 0.7:
            recommendations.append("Consider gathering more information")
        
        if not synthesis_data.get("information_sources"):
            recommendations.append("Include external sources for verification")
        
        return recommendations
    
    def _create_enhanced_response(self, synthesis_data: Dict, validation_data: Dict) -> str:
        """Create the final enhanced response"""
        # This would integrate with the OpenAI service to generate the actual response
        # For now, return a structured response format
        
        base_response = "Based on the analysis and available information: "
        
        if synthesis_data.get("enhanced_context"):
            base_response += f"\n\nContext: {synthesis_data['enhanced_context']}"
        
        if synthesis_data.get("information_sources"):
            sources = ", ".join(synthesis_data["information_sources"])
            base_response += f"\n\nSources: {sources}"
        
        confidence = validation_data.get("quality_score", 0.8)
        base_response += f"\n\nConfidence Level: {confidence:.1%}"
        
        return base_response
    
    async def _handle_workflow_failure(self, workflow: AgentWorkflow, error_message: str) -> AgentWorkflow:
        """Handle workflow failure gracefully"""
        workflow.success = False
        workflow.final_response = f"I encountered an issue processing your request: {error_message}. Let me provide a basic response instead."
        
        logger.error(f"Workflow {workflow.workflow_id} failed: {error_message}")
        
        return workflow
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about workflow execution"""
        if not self.workflow_history:
            return {"total_workflows": 0}
        
        total_workflows = len(self.workflow_history)
        successful_workflows = sum(1 for w in self.workflow_history if w.success)
        avg_execution_time = sum(w.total_execution_time for w in self.workflow_history) / total_workflows
        
        return {
            "total_workflows": total_workflows,
            "success_rate": successful_workflows / total_workflows,
            "average_execution_time": avg_execution_time,
            "last_workflow_success": self.workflow_history[-1].success if self.workflow_history else None
        }
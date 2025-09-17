"""
GPT.R1 - Advanced Multi-Step Agentic AI System
Modular agentic flow with DuckDuckGo search integration
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from .rag_service import RAGService

logger = logging.getLogger(__name__)

class AgentStepType(Enum):
    """Types of agent steps in the workflow"""
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
    Advanced multi-step agentic AI system with modular workflow
    
    This addresses the feedback for "more modular or multi-step" agentic flow
    """
    
    def __init__(self):
        self.rag_service = RAGService()
        self.workflow_history = []
    
    async def execute_agentic_workflow(self, user_query: str, conversation_history: List[Dict] = None) -> AgentWorkflow:
        """
        Execute complete multi-step agentic workflow
        
        Steps:
        1. ANALYZE - Understand query intent and requirements
        2. SEARCH - Gather relevant information if needed
        3. SYNTHESIZE - Combine information with context
        4. VALIDATE - Check response quality and accuracy
        5. RESPOND - Generate final response
        """
        workflow_id = f"workflow_{datetime.now().timestamp()}"
        workflow = AgentWorkflow(
            workflow_id=workflow_id,
            user_query=user_query,
            steps=[]
        )
        
        start_time = datetime.now()
        
        try:
            # Step 1: ANALYZE - Query Intent Analysis
            analyze_step = await self._step_analyze_query(user_query, conversation_history)
            workflow.steps.append(analyze_step)
            
            if not analyze_step.success:
                return await self._handle_workflow_failure(workflow, "Analysis step failed")
            
            # Step 2: SEARCH - Information Gathering (if needed)
            search_step = await self._step_search_information(analyze_step.output_data)
            workflow.steps.append(search_step)
            
            # Step 3: SYNTHESIZE - Information Integration
            synthesize_step = await self._step_synthesize_information(
                user_query, 
                analyze_step.output_data,
                search_step.output_data if search_step.success else {},
                conversation_history
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
    
    async def _step_analyze_query(self, user_query: str, conversation_history: List[Dict] = None) -> AgentStep:
        """
        Step 1: Analyze user query to understand intent and requirements
        """
        step = AgentStep(
            step_type=AgentStepType.ANALYZE,
            description="Analyze query intent and determine information needs",
            input_data={"query": user_query, "history": conversation_history or []}
        )
        
        start_time = datetime.now()
        
        try:
            # Analyze query characteristics
            analysis = {
                "query_type": self._classify_query_type(user_query),
                "requires_search": self._requires_external_search(user_query),
                "complexity": self._assess_query_complexity(user_query),
                "context_needed": len(conversation_history or []) > 0,
                "intent": self._extract_user_intent(user_query)
            }
            
            step.output_data = analysis
            step.success = True
            
            logger.info(f"Query analysis completed: {analysis['query_type']}, search_needed: {analysis['requires_search']}")
            
        except Exception as e:
            step.error = str(e)
            logger.error(f"Query analysis failed: {e}")
        
        finally:
            step.execution_time = (datetime.now() - start_time).total_seconds()
        
        return step
    
    async def _step_search_information(self, analysis_data: Dict[str, Any]) -> AgentStep:
        """
        Step 2: Search for external information if needed
        """
        step = AgentStep(
            step_type=AgentStepType.SEARCH,
            description="Search for relevant external information",
            input_data=analysis_data
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
    
    async def _step_synthesize_information(self, user_query: str, analysis: Dict, search_data: Dict, history: List[Dict]) -> AgentStep:
        """
        Step 3: Synthesize all available information
        """
        step = AgentStep(
            step_type=AgentStepType.SYNTHESIZE,
            description="Combine and synthesize all available information",
            input_data={
                "query": user_query,
                "analysis": analysis,
                "search_data": search_data,
                "history": history
            }
        )
        
        start_time = datetime.now()
        
        try:
            # Create comprehensive context
            synthesis = {
                "enhanced_context": self._build_enhanced_context(analysis, search_data, history),
                "response_strategy": self._determine_response_strategy(analysis),
                "confidence_level": self._calculate_confidence_level(analysis, search_data),
                "information_sources": self._identify_information_sources(search_data)
            }
            
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
    
    def _build_enhanced_context(self, analysis: Dict, search_data: Dict, history: List[Dict]) -> str:
        """Build enhanced context from all sources"""
        context_parts = []
        
        if history:
            context_parts.append("Conversation history available")
        
        if search_data.get("search_performed") and search_data.get("search_results"):
            context_parts.append(f"External information: {search_data['search_results'][:500]}...")
        
        return " | ".join(context_parts)
    
    def _determine_response_strategy(self, analysis: Dict) -> str:
        """Determine the best strategy for response generation"""
        query_type = analysis.get("query_type", "general")
        
        strategy_map = {
            "informational": "provide_detailed_facts",
            "creative": "generate_creative_content",
            "analytical": "provide_structured_analysis",
            "assistance": "offer_helpful_guidance",
            "general": "conversational_response"
        }
        
        return strategy_map.get(query_type, "conversational_response")
    
    def _calculate_confidence_level(self, analysis: Dict, search_data: Dict) -> float:
        """Calculate confidence level for the response"""
        base_confidence = 0.7
        
        if search_data.get("search_performed") and search_data.get("search_results"):
            base_confidence += 0.2
        
        if analysis.get("complexity") == "simple":
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _identify_information_sources(self, search_data: Dict) -> List[str]:
        """Identify sources of information used"""
        sources = []
        
        if search_data.get("search_performed"):
            sources.append("DuckDuckGo Search")
        
        sources.append("AI Knowledge Base")
        
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
"""
GPT.R1 - Advanced Multi-Tool Orchestration System
Sophisticated tool selection and coordination for complex AI workflows
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """Types of tools available in the orchestration system"""
    SEARCH = "search"
    ANALYSIS = "analysis" 
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    GENERATION = "generation"
    CALCULATION = "calculation"
    REASONING = "reasoning"
    MEMORY = "memory"

class ToolPriority(Enum):
    """Tool execution priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ToolResult:
    """Result from tool execution"""
    tool_name: str
    tool_type: ToolType
    success: bool
    result: Any
    execution_time: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class ToolRequest:
    """Request for tool execution"""
    tool_type: ToolType
    input_data: Dict[str, Any]
    priority: ToolPriority = ToolPriority.MEDIUM
    timeout: float = 30.0
    dependencies: List[str] = field(default_factory=list)

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, tool_type: ToolType):
        self.name = name
        self.tool_type = tool_type
        self.is_available = True
        self.execution_count = 0
        self.average_execution_time = 0.0
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given input data"""
        pass
    
    @abstractmethod
    def can_handle(self, request: ToolRequest) -> float:
        """Return confidence score (0-1) for handling this request"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this tool provides"""
        return []

class WebSearchTool(BaseTool):
    """Advanced web search tool with DuckDuckGo integration"""
    
    def __init__(self):
        super().__init__("WebSearchTool", ToolType.SEARCH)
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """Execute web search"""
        start_time = datetime.now()
        
        try:
            from ..services.rag_service import RAGService
            rag_service = RAGService()
            
            query = input_data.get("query", "")
            max_results = input_data.get("max_results", 5)
            
            search_results = await rag_service.get_context_from_search(query)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                result=search_results,
                execution_time=execution_time,
                confidence=0.9 if search_results else 0.3,
                metadata={
                    "query": query,
                    "results_length": len(search_results) if search_results else 0
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                result=None,
                execution_time=execution_time,
                confidence=0.0,
                error=str(e)
            )
    
    def can_handle(self, request: ToolRequest) -> float:
        """Check if this tool can handle the request"""
        if request.tool_type != ToolType.SEARCH:
            return 0.0
        
        query = request.input_data.get("query", "")
        if not query:
            return 0.1
        
        # Higher confidence for current events, facts, recent information
        search_indicators = ["current", "latest", "recent", "today", "news", "weather", "price"]
        confidence = 0.7
        
        for indicator in search_indicators:
            if indicator in query.lower():
                confidence = 0.95
                break
        
        return confidence
    
    def get_capabilities(self) -> List[str]:
        return [
            "web_search",
            "current_information",
            "fact_checking", 
            "news_retrieval",
            "real_time_data"
        ]

class AnalysisTool(BaseTool):
    """Advanced analysis tool for data processing and insights"""
    
    def __init__(self):
        super().__init__("AnalysisTool", ToolType.ANALYSIS)
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """Execute analysis"""
        start_time = datetime.now()
        
        try:
            content = input_data.get("content", "")
            analysis_type = input_data.get("type", "general")
            
            analysis_result = await self._perform_analysis(content, analysis_type)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                result=analysis_result,
                execution_time=execution_time,
                confidence=0.85,
                metadata={
                    "analysis_type": analysis_type,
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                result=None,
                execution_time=execution_time,
                confidence=0.0,
                error=str(e)
            )
    
    async def _perform_analysis(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Perform the actual analysis"""
        analysis = {
            "sentiment": self._analyze_sentiment(content),
            "complexity": self._analyze_complexity(content),
            "key_topics": self._extract_topics(content),
            "structure": self._analyze_structure(content)
        }
        
        if analysis_type == "detailed":
            analysis.update({
                "word_count": len(content.split()),
                "reading_level": self._assess_reading_level(content),
                "technical_terms": self._identify_technical_terms(content)
            })
        
        return analysis
    
    def _analyze_sentiment(self, content: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "amazing", "helpful", "useful"]
        negative_words = ["bad", "terrible", "awful", "useless", "poor", "disappointing"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_complexity(self, content: str) -> str:
        """Analyze content complexity"""
        words = content.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 6:
            return "high"
        elif avg_word_length > 4:
            return "medium"
        else:
            return "low"
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics from content"""
        # Simple keyword extraction
        words = content.lower().split()
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if len(word) > 4 and word not in common_words]
        
        # Return top 5 most frequent keywords
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(5)]
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')
        paragraphs = [line for line in lines if line.strip()]
        
        return {
            "paragraphs": len(paragraphs),
            "average_paragraph_length": sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            "has_questions": "?" in content,
            "has_lists": any(line.strip().startswith(("-", "*", "•")) for line in lines)
        }
    
    def _assess_reading_level(self, content: str) -> str:
        """Assess reading difficulty level"""
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return "unknown"
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        if avg_words_per_sentence > 20:
            return "advanced"
        elif avg_words_per_sentence > 15:
            return "intermediate"
        else:
            return "basic"
    
    def _identify_technical_terms(self, content: str) -> List[str]:
        """Identify technical terminology"""
        technical_indicators = [
            "algorithm", "database", "api", "framework", "optimization",
            "implementation", "architecture", "methodology", "paradigm",
            "protocol", "interface", "configuration", "deployment"
        ]
        
        content_lower = content.lower()
        return [term for term in technical_indicators if term in content_lower]
    
    def can_handle(self, request: ToolRequest) -> float:
        """Check if this tool can handle the request"""
        if request.tool_type != ToolType.ANALYSIS:
            return 0.0
        
        content = request.input_data.get("content", "")
        if not content:
            return 0.1
        
        return 0.9
    
    def get_capabilities(self) -> List[str]:
        return [
            "sentiment_analysis",
            "complexity_assessment",
            "topic_extraction",
            "structure_analysis",
            "readability_assessment"
        ]

class SynthesisTool(BaseTool):
    """Advanced synthesis tool for combining multiple information sources"""
    
    def __init__(self):
        super().__init__("SynthesisTool", ToolType.SYNTHESIS)
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """Execute synthesis"""
        start_time = datetime.now()
        
        try:
            sources = input_data.get("sources", [])
            context = input_data.get("context", "")
            synthesis_type = input_data.get("type", "comprehensive")
            
            synthesis_result = await self._perform_synthesis(sources, context, synthesis_type)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                result=synthesis_result,
                execution_time=execution_time,
                confidence=0.88,
                metadata={
                    "sources_count": len(sources),
                    "synthesis_type": synthesis_type
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                result=None,
                execution_time=execution_time,
                confidence=0.0,
                error=str(e)
            )
    
    async def _perform_synthesis(self, sources: List[Dict], context: str, synthesis_type: str) -> Dict[str, Any]:
        """Perform information synthesis"""
        synthesis = {
            "combined_information": self._combine_sources(sources),
            "key_insights": self._extract_insights(sources),
            "conflicting_information": self._identify_conflicts(sources),
            "reliability_assessment": self._assess_reliability(sources),
            "contextual_relevance": self._assess_relevance(sources, context)
        }
        
        if synthesis_type == "comprehensive":
            synthesis.update({
                "source_comparison": self._compare_sources(sources),
                "information_gaps": self._identify_gaps(sources, context),
                "recommendations": self._generate_recommendations(sources, context)
            })
        
        return synthesis
    
    def _combine_sources(self, sources: List[Dict]) -> str:
        """Combine information from multiple sources"""
        combined = []
        
        for i, source in enumerate(sources):
            content = source.get("content", "")
            source_type = source.get("type", "unknown")
            
            if content:
                combined.append(f"Source {i+1} ({source_type}): {content[:200]}...")
        
        return "\n\n".join(combined)
    
    def _extract_insights(self, sources: List[Dict]) -> List[str]:
        """Extract key insights from sources"""
        insights = []
        
        # Look for common themes across sources
        all_content = " ".join([source.get("content", "") for source in sources])
        words = all_content.lower().split()
        
        from collections import Counter
        common_words = Counter(words).most_common(10)
        
        for word, count in common_words:
            if len(word) > 4 and count > 1:
                insights.append(f"Common theme: '{word}' appears {count} times across sources")
        
        return insights[:5]  # Top 5 insights
    
    def _identify_conflicts(self, sources: List[Dict]) -> List[str]:
        """Identify conflicting information between sources"""
        conflicts = []
        
        # Simple conflict detection based on contradictory keywords
        contradictions = [
            ("yes", "no"), ("true", "false"), ("increase", "decrease"),
            ("positive", "negative"), ("good", "bad"), ("high", "low")
        ]
        
        for source1 in sources:
            for source2 in sources:
                if source1 != source2:
                    content1 = source1.get("content", "").lower()
                    content2 = source2.get("content", "").lower()
                    
                    for word1, word2 in contradictions:
                        if word1 in content1 and word2 in content2:
                            conflicts.append(f"Potential conflict: One source mentions '{word1}' while another mentions '{word2}'")
        
        return list(set(conflicts))[:3]  # Remove duplicates, top 3
    
    def _assess_reliability(self, sources: List[Dict]) -> Dict[str, float]:
        """Assess reliability of sources"""
        reliability = {}
        
        for i, source in enumerate(sources):
            source_type = source.get("type", "unknown")
            content = source.get("content", "")
            
            # Simple reliability scoring
            score = 0.5  # Base score
            
            if source_type == "search":
                score += 0.2
            if len(content) > 100:
                score += 0.1
            if any(word in content.lower() for word in ["study", "research", "data", "analysis"]):
                score += 0.2
            
            reliability[f"source_{i+1}"] = min(score, 1.0)
        
        return reliability
    
    def _assess_relevance(self, sources: List[Dict], context: str) -> Dict[str, float]:
        """Assess relevance of sources to context"""
        relevance = {}
        context_words = set(context.lower().split())
        
        for i, source in enumerate(sources):
            content = source.get("content", "")
            content_words = set(content.lower().split())
            
            # Calculate word overlap
            overlap = len(context_words.intersection(content_words))
            total_unique = len(context_words.union(content_words))
            
            relevance_score = overlap / total_unique if total_unique > 0 else 0
            relevance[f"source_{i+1}"] = relevance_score
        
        return relevance
    
    def _compare_sources(self, sources: List[Dict]) -> Dict[str, Any]:
        """Compare sources for similarities and differences"""
        comparison = {
            "total_sources": len(sources),
            "source_types": {},
            "content_lengths": [],
            "similarity_matrix": {}
        }
        
        # Analyze source types
        for source in sources:
            source_type = source.get("type", "unknown")
            comparison["source_types"][source_type] = comparison["source_types"].get(source_type, 0) + 1
        
        # Analyze content lengths
        for source in sources:
            content_length = len(source.get("content", ""))
            comparison["content_lengths"].append(content_length)
        
        return comparison
    
    def _identify_gaps(self, sources: List[Dict], context: str) -> List[str]:
        """Identify information gaps"""
        gaps = []
        
        # Look for question words in context that might not be addressed
        question_words = ["what", "how", "why", "when", "where", "who"]
        all_content = " ".join([source.get("content", "") for source in sources]).lower()
        
        for qword in question_words:
            if qword in context.lower() and qword not in all_content:
                gaps.append(f"Potential gap: '{qword}' questions may not be fully addressed")
        
        return gaps
    
    def _generate_recommendations(self, sources: List[Dict], context: str) -> List[str]:
        """Generate recommendations based on synthesis"""
        recommendations = []
        
        if len(sources) < 3:
            recommendations.append("Consider gathering additional sources for more comprehensive analysis")
        
        all_content = " ".join([source.get("content", "") for source in sources])
        if len(all_content) < 500:
            recommendations.append("Sources may benefit from more detailed information")
        
        if not any("recent" in source.get("content", "").lower() for source in sources):
            recommendations.append("Consider including more recent information sources")
        
        return recommendations
    
    def can_handle(self, request: ToolRequest) -> float:
        """Check if this tool can handle the request"""
        if request.tool_type != ToolType.SYNTHESIS:
            return 0.0
        
        sources = request.input_data.get("sources", [])
        if len(sources) < 2:
            return 0.3  # Low confidence with insufficient sources
        
        return 0.9
    
    def get_capabilities(self) -> List[str]:
        return [
            "information_synthesis",
            "source_comparison",
            "conflict_detection",
            "reliability_assessment",
            "gap_analysis"
        ]

class ValidationTool(BaseTool):
    """Advanced validation tool for quality assurance and fact-checking"""
    
    def __init__(self):
        super().__init__("ValidationTool", ToolType.VALIDATION)
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """Execute validation"""
        start_time = datetime.now()
        
        try:
            content = input_data.get("content", "")
            validation_type = input_data.get("type", "comprehensive")
            
            validation_result = await self._perform_validation(content, validation_type)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                result=validation_result,
                execution_time=execution_time,
                confidence=0.85,
                metadata={
                    "validation_type": validation_type,
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                result=None,
                execution_time=execution_time,
                confidence=0.0,
                error=str(e)
            )
    
    async def _perform_validation(self, content: str, validation_type: str) -> Dict[str, Any]:
        """Perform content validation"""
        validation = {
            "quality_score": self._assess_quality(content),
            "completeness": self._check_completeness(content),
            "accuracy_indicators": self._check_accuracy_indicators(content),
            "consistency": self._check_consistency(content),
            "clarity": self._assess_clarity(content)
        }
        
        if validation_type == "comprehensive":
            validation.update({
                "fact_check_flags": self._identify_fact_check_flags(content),
                "bias_indicators": self._detect_bias(content),
                "recommendations": self._generate_validation_recommendations(content)
            })
        
        return validation
    
    def _assess_quality(self, content: str) -> float:
        """Assess overall content quality"""
        score = 0.5  # Base score
        
        # Length factor
        if len(content) > 200:
            score += 0.1
        if len(content) > 500:
            score += 0.1
        
        # Structure factor
        if '\n' in content:  # Has paragraphs
            score += 0.1
        if '.' in content:  # Has sentences
            score += 0.1
        
        # Language quality
        words = content.split()
        if len(words) > 10:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if 4 <= avg_word_length <= 8:  # Reasonable word length
                score += 0.2
        
        return min(score, 1.0)
    
    def _check_completeness(self, content: str) -> Dict[str, Any]:
        """Check content completeness"""
        return {
            "has_introduction": self._has_introduction(content),
            "has_conclusion": self._has_conclusion(content),
            "addresses_main_points": self._addresses_main_points(content),
            "provides_examples": self._provides_examples(content)
        }
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has an introduction"""
        intro_indicators = ["introduction", "overview", "summary", "background"]
        first_paragraph = content.split('\n')[0] if '\n' in content else content[:200]
        return any(indicator in first_paragraph.lower() for indicator in intro_indicators)
    
    def _has_conclusion(self, content: str) -> bool:
        """Check if content has a conclusion"""
        conclusion_indicators = ["conclusion", "summary", "in summary", "to conclude", "finally"]
        last_paragraph = content.split('\n')[-1] if '\n' in content else content[-200:]
        return any(indicator in last_paragraph.lower() for indicator in conclusion_indicators)
    
    def _addresses_main_points(self, content: str) -> bool:
        """Check if content addresses main points"""
        # Simple heuristic: presence of multiple topics or structured content
        return len(content.split('\n')) > 2 or len(content.split('.')) > 3
    
    def _provides_examples(self, content: str) -> bool:
        """Check if content provides examples"""
        example_indicators = ["example", "for instance", "such as", "like", "including"]
        return any(indicator in content.lower() for indicator in example_indicators)
    
    def _check_accuracy_indicators(self, content: str) -> Dict[str, Any]:
        """Check for accuracy indicators"""
        return {
            "has_sources": self._has_sources(content),
            "has_data": self._has_data(content),
            "specific_details": self._has_specific_details(content),
            "verifiable_claims": self._has_verifiable_claims(content)
        }
    
    def _has_sources(self, content: str) -> bool:
        """Check if content references sources"""
        source_indicators = ["according to", "study", "research", "report", "survey"]
        return any(indicator in content.lower() for indicator in source_indicators)
    
    def _has_data(self, content: str) -> bool:
        """Check if content includes data"""
        import re
        # Look for numbers, percentages, dates
        return bool(re.search(r'\d+%|\d+\.\d+|\d{4}', content))
    
    def _has_specific_details(self, content: str) -> bool:
        """Check for specific rather than vague details"""
        vague_words = ["some", "many", "several", "often", "usually", "generally"]
        specific_words = ["exactly", "precisely", "specifically", "particularly"]
        
        vague_count = sum(1 for word in vague_words if word in content.lower())
        specific_count = sum(1 for word in specific_words if word in content.lower())
        
        return specific_count >= vague_count
    
    def _has_verifiable_claims(self, content: str) -> bool:
        """Check for verifiable claims"""
        # Simple check for factual statement patterns
        factual_indicators = ["is", "are", "was", "were", "has", "have", "will", "can"]
        return any(indicator in content.lower() for indicator in factual_indicators)
    
    def _check_consistency(self, content: str) -> Dict[str, Any]:
        """Check content consistency"""
        return {
            "tone_consistency": self._check_tone_consistency(content),
            "terminology_consistency": self._check_terminology_consistency(content),
            "logical_flow": self._check_logical_flow(content)
        }
    
    def _check_tone_consistency(self, content: str) -> bool:
        """Check tone consistency"""
        # Simple heuristic: consistent sentence length patterns
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if len(sentences) < 3:
            return True
        
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        
        return variance < avg_length  # Low variance indicates consistency
    
    def _check_terminology_consistency(self, content: str) -> bool:
        """Check terminology consistency"""
        # Check for consistent use of technical terms
        words = content.lower().split()
        word_count = {}
        
        for word in words:
            if len(word) > 6:  # Focus on longer, potentially technical words
                word_count[word] = word_count.get(word, 0) + 1
        
        # If technical words are used consistently (repeated), it's good
        repeated_words = [word for word, count in word_count.items() if count > 1]
        return len(repeated_words) > 0
    
    def _check_logical_flow(self, content: str) -> bool:
        """Check logical flow"""
        # Simple check for transition words
        transition_words = ["however", "therefore", "furthermore", "moreover", "additionally", "consequently"]
        return any(word in content.lower() for word in transition_words)
    
    def _assess_clarity(self, content: str) -> float:
        """Assess content clarity"""
        score = 0.5
        
        # Sentence length (shorter is clearer)
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length <= 20:  # Reasonable sentence length
                score += 0.2
        
        # Word complexity (simpler is clearer)
        words = content.split()
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length <= 6:  # Reasonable word length
                score += 0.2
        
        # Structure (clear structure improves clarity)
        if '\n' in content:  # Has paragraphs
            score += 0.1
        
        return min(score, 1.0)
    
    def _identify_fact_check_flags(self, content: str) -> List[str]:
        """Identify potential fact-checking flags"""
        flags = []
        
        superlative_words = ["best", "worst", "always", "never", "all", "none", "everyone", "nobody"]
        for word in superlative_words:
            if word in content.lower():
                flags.append(f"Absolute claim detected: '{word}' - may need verification")
        
        if len(flags) > 3:
            flags = flags[:3]  # Limit to top 3
        
        return flags
    
    def _detect_bias(self, content: str) -> List[str]:
        """Detect potential bias indicators"""
        bias_indicators = []
        
        emotional_words = ["terrible", "amazing", "awful", "fantastic", "horrible", "incredible"]
        for word in emotional_words:
            if word in content.lower():
                bias_indicators.append(f"Emotional language detected: '{word}'")
        
        if len(bias_indicators) > 2:
            bias_indicators = bias_indicators[:2]  # Limit to top 2
        
        return bias_indicators
    
    def _generate_validation_recommendations(self, content: str) -> List[str]:
        """Generate validation recommendations"""
        recommendations = []
        
        if len(content) < 100:
            recommendations.append("Content may benefit from more detailed information")
        
        if not self._has_sources(content):
            recommendations.append("Consider adding sources or references to support claims")
        
        if not self._has_specific_details(content):
            recommendations.append("Add more specific details to improve accuracy")
        
        return recommendations[:3]  # Top 3 recommendations
    
    def can_handle(self, request: ToolRequest) -> float:
        """Check if this tool can handle the request"""
        if request.tool_type != ToolType.VALIDATION:
            return 0.0
        
        content = request.input_data.get("content", "")
        if not content:
            return 0.1
        
        return 0.9
    
    def get_capabilities(self) -> List[str]:
        return [
            "quality_assessment",
            "completeness_check",
            "accuracy_validation",
            "consistency_analysis",
            "bias_detection"
        ]

class AdvancedToolOrchestrator:
    """
    Advanced multi-tool orchestration system
    Coordinates multiple tools for complex AI workflows
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.execution_history: List[Dict] = []
        self.performance_stats: Dict[str, Dict] = {}
        
        # Initialize tools
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        tools = [
            WebSearchTool(),
            AnalysisTool(),
            SynthesisTool(),
            ValidationTool()
        ]
        
        for tool in tools:
            self.tools[tool.name] = tool
            self.performance_stats[tool.name] = {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "average_confidence": 0.0
            }
    
    async def orchestrate_workflow(
        self, 
        user_query: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate a multi-tool workflow for complex query processing
        """
        workflow_start = datetime.now()
        workflow_id = f"workflow_{int(workflow_start.timestamp())}"
        
        try:
            # Step 1: Analyze query to determine required tools
            tool_plan = await self._plan_tool_execution(user_query, context or {})
            
            # Step 2: Execute tools in coordinated fashion
            tool_results = await self._execute_tool_plan(tool_plan)
            
            # Step 3: Synthesize results from all tools
            final_synthesis = await self._synthesize_tool_results(tool_results, user_query)
            
            # Step 4: Validate the final output
            validation_result = await self._validate_final_output(final_synthesis)
            
            workflow_time = (datetime.now() - workflow_start).total_seconds()
            
            # Record workflow execution
            workflow_record = {
                "workflow_id": workflow_id,
                "user_query": user_query,
                "tools_used": list(tool_results.keys()),
                "execution_time": workflow_time,
                "success": True,
                "tool_results": tool_results,
                "final_synthesis": final_synthesis,
                "validation": validation_result
            }
            
            self.execution_history.append(workflow_record)
            self._update_performance_stats(tool_results)
            
            return {
                "workflow_id": workflow_id,
                "success": True,
                "execution_time": workflow_time,
                "tools_orchestrated": len(tool_results),
                "final_result": final_synthesis,
                "quality_validation": validation_result,
                "tool_breakdown": tool_results,
                "orchestration_metadata": {
                    "tool_plan": tool_plan,
                    "coordination_strategy": "sequential_with_dependency_management",
                    "performance_optimization": "enabled"
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow orchestration failed: {e}")
            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": str(e),
                "execution_time": (datetime.now() - workflow_start).total_seconds()
            }
    
    async def _plan_tool_execution(self, user_query: str, context: Dict[str, Any]) -> List[ToolRequest]:
        """Plan which tools to use and in what order"""
        tool_plan = []
        
        # Analyze query characteristics
        query_lower = user_query.lower()
        
        # 1. Always start with analysis if we have content
        if len(user_query) > 20:
            tool_plan.append(ToolRequest(
                tool_type=ToolType.ANALYSIS,
                input_data={"content": user_query, "type": "detailed"},
                priority=ToolPriority.HIGH
            ))
        
        # 2. Add search if query indicates need for external information
        search_indicators = ["current", "latest", "recent", "today", "news", "what is", "tell me about"]
        if any(indicator in query_lower for indicator in search_indicators):
            tool_plan.append(ToolRequest(
                tool_type=ToolType.SEARCH,
                input_data={"query": user_query, "max_results": 5},
                priority=ToolPriority.HIGH,
                dependencies=["AnalysisTool"] if tool_plan else []
            ))
        
        # 3. Add synthesis if we have multiple information sources
        if len(tool_plan) > 1 or context.get("sources"):
            tool_plan.append(ToolRequest(
                tool_type=ToolType.SYNTHESIS,
                input_data={
                    "sources": context.get("sources", []),
                    "context": user_query,
                    "type": "comprehensive"
                },
                priority=ToolPriority.MEDIUM,
                dependencies=[tool.name for tool in self.tools.values() if tool.tool_type in [ToolType.SEARCH, ToolType.ANALYSIS]]
            ))
        
        # 4. Always add validation for quality assurance
        tool_plan.append(ToolRequest(
            tool_type=ToolType.VALIDATION,
            input_data={"content": user_query, "type": "comprehensive"},
            priority=ToolPriority.MEDIUM,
            dependencies=["SynthesisTool"] if any(req.tool_type == ToolType.SYNTHESIS for req in tool_plan) else []
        ))
        
        return tool_plan
    
    async def _execute_tool_plan(self, tool_plan: List[ToolRequest]) -> Dict[str, ToolResult]:
        """Execute tools according to the plan with dependency management"""
        results = {}
        completed_tools = set()
        
        # Execute tools in dependency order
        while len(completed_tools) < len(tool_plan):
            for request in tool_plan:
                # Skip if already completed
                if request.tool_type.value in completed_tools:
                    continue
                
                # Check if dependencies are satisfied
                if all(dep in completed_tools for dep in request.dependencies):
                    # Find the best tool for this request
                    best_tool = self._select_best_tool(request)
                    
                    if best_tool:
                        # Execute the tool
                        result = await best_tool.execute(request.input_data)
                        results[best_tool.name] = result
                        completed_tools.add(request.tool_type.value)
                        
                        logger.info(f"Executed {best_tool.name} with confidence {result.confidence}")
        
        return results
    
    def _select_best_tool(self, request: ToolRequest) -> Optional[BaseTool]:
        """Select the best tool for handling a request"""
        best_tool = None
        best_score = 0.0
        
        for tool in self.tools.values():
            if tool.is_available:
                confidence_score = tool.can_handle(request)
                
                # Factor in tool performance history
                stats = self.performance_stats.get(tool.name, {})
                performance_modifier = stats.get("success_rate", 0.5) * 0.1
                
                total_score = confidence_score + performance_modifier
                
                if total_score > best_score:
                    best_score = total_score
                    best_tool = tool
        
        return best_tool
    
    async def _synthesize_tool_results(self, tool_results: Dict[str, ToolResult], user_query: str) -> Dict[str, Any]:
        """Synthesize results from all executed tools"""
        synthesis = {
            "orchestration_summary": {
                "tools_executed": len(tool_results),
                "successful_tools": sum(1 for result in tool_results.values() if result.success),
                "total_execution_time": sum(result.execution_time for result in tool_results.values()),
                "average_confidence": sum(result.confidence for result in tool_results.values()) / len(tool_results) if tool_results else 0.0
            },
            "tool_contributions": {},
            "integrated_insights": [],
            "confidence_assessment": 0.0
        }
        
        # Process each tool's contribution
        for tool_name, result in tool_results.items():
            if result.success:
                synthesis["tool_contributions"][tool_name] = {
                    "type": result.tool_type.value,
                    "confidence": result.confidence,
                    "execution_time": result.execution_time,
                    "key_findings": self._extract_key_findings(result.result),
                    "metadata": result.metadata
                }
        
        # Generate integrated insights
        synthesis["integrated_insights"] = self._generate_integrated_insights(tool_results, user_query)
        
        # Calculate overall confidence
        synthesis["confidence_assessment"] = self._calculate_overall_confidence(tool_results)
        
        return synthesis
    
    def _extract_key_findings(self, result: Any) -> List[str]:
        """Extract key findings from tool results"""
        findings = []
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, (str, int, float)):
                    findings.append(f"{key}: {value}")
                elif isinstance(value, list) and value:
                    findings.append(f"{key}: {', '.join(map(str, value[:3]))}")  # First 3 items
        elif isinstance(result, str):
            # Extract first sentence or first 100 characters
            finding = result.split('.')[0] if '.' in result else result[:100]
            findings.append(finding.strip())
        
        return findings[:3]  # Top 3 findings
    
    def _generate_integrated_insights(self, tool_results: Dict[str, ToolResult], user_query: str) -> List[str]:
        """Generate insights by integrating all tool results"""
        insights = []
        
        # Cross-tool analysis
        search_result = None
        analysis_result = None
        
        for tool_name, result in tool_results.items():
            if result.success:
                if result.tool_type == ToolType.SEARCH:
                    search_result = result
                elif result.tool_type == ToolType.ANALYSIS:
                    analysis_result = result
        
        # Generate cross-tool insights
        if search_result and analysis_result:
            insights.append("Combined search and analysis data for comprehensive understanding")
        
        if len(tool_results) >= 3:
            insights.append("Multi-tool orchestration provided enhanced accuracy through validation")
        
        # Quality assessment
        avg_confidence = sum(r.confidence for r in tool_results.values() if r.success) / len(tool_results) if tool_results else 0
        if avg_confidence > 0.8:
            insights.append("High confidence in results due to strong tool performance")
        elif avg_confidence < 0.6:
            insights.append("Moderate confidence - additional verification may be beneficial")
        
        return insights
    
    def _calculate_overall_confidence(self, tool_results: Dict[str, ToolResult]) -> float:
        """Calculate overall confidence based on tool performance"""
        if not tool_results:
            return 0.0
        
        successful_results = [r for r in tool_results.values() if r.success]
        if not successful_results:
            return 0.0
        
        # Weighted average based on tool type importance
        weight_map = {
            ToolType.SEARCH: 0.3,
            ToolType.ANALYSIS: 0.25,
            ToolType.SYNTHESIS: 0.25,
            ToolType.VALIDATION: 0.2
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result in successful_results:
            weight = weight_map.get(result.tool_type, 0.1)
            weighted_sum += result.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _validate_final_output(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the final orchestrated output"""
        validation_tool = self.tools.get("ValidationTool")
        
        if not validation_tool:
            return {"validation_available": False, "message": "No validation tool available"}
        
        # Create validation content from synthesis
        content_to_validate = json.dumps(synthesis, indent=2)
        
        validation_result = await validation_tool.execute({
            "content": content_to_validate,
            "type": "comprehensive"
        })
        
        return {
            "validation_available": True,
            "validation_success": validation_result.success,
            "quality_score": validation_result.result.get("quality_score", 0) if validation_result.success else 0,
            "validation_confidence": validation_result.confidence,
            "recommendations": validation_result.result.get("recommendations", []) if validation_result.success else []
        }
    
    def _update_performance_stats(self, tool_results: Dict[str, ToolResult]):
        """Update performance statistics for tools"""
        for tool_name, result in tool_results.items():
            stats = self.performance_stats[tool_name]
            
            # Update execution count
            stats["total_executions"] += 1
            
            # Update success rate
            current_successes = stats["success_rate"] * (stats["total_executions"] - 1)
            if result.success:
                current_successes += 1
            stats["success_rate"] = current_successes / stats["total_executions"]
            
            # Update average execution time
            current_time_sum = stats["average_execution_time"] * (stats["total_executions"] - 1)
            current_time_sum += result.execution_time
            stats["average_execution_time"] = current_time_sum / stats["total_executions"]
            
            # Update average confidence
            current_confidence_sum = stats["average_confidence"] * (stats["total_executions"] - 1)
            current_confidence_sum += result.confidence
            stats["average_confidence"] = current_confidence_sum / stats["total_executions"]
    
    def get_orchestrator_statistics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        return {
            "total_workflows": len(self.execution_history),
            "successful_workflows": sum(1 for w in self.execution_history if w["success"]),
            "average_workflow_time": sum(w["execution_time"] for w in self.execution_history) / len(self.execution_history) if self.execution_history else 0,
            "tools_available": len(self.tools),
            "tool_performance": self.performance_stats,
            "most_used_tools": self._get_most_used_tools(),
            "recent_performance": self._get_recent_performance()
        }
    
    def _get_most_used_tools(self) -> List[Dict[str, Any]]:
        """Get most frequently used tools"""
        tool_usage = {}
        
        for workflow in self.execution_history:
            for tool_name in workflow.get("tools_used", []):
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
        
        sorted_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
        return [{"tool": tool, "usage_count": count} for tool, count in sorted_tools[:5]]
    
    def _get_recent_performance(self) -> Dict[str, Any]:
        """Get recent performance metrics"""
        recent_workflows = self.execution_history[-10:]  # Last 10 workflows
        
        if not recent_workflows:
            return {"message": "No recent workflows"}
        
        return {
            "recent_workflow_count": len(recent_workflows),
            "recent_success_rate": sum(1 for w in recent_workflows if w["success"]) / len(recent_workflows),
            "recent_average_time": sum(w["execution_time"] for w in recent_workflows) / len(recent_workflows),
            "recent_average_tools_per_workflow": sum(len(w.get("tools_used", [])) for w in recent_workflows) / len(recent_workflows)
        }
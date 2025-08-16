"""
Web Research Analyst Agent - Specialized for comprehensive web research and analysis
"""

import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class WebResearchAnalyst(BaseAgent):
    """
    Specialized agent for web research, data gathering, and competitive analysis.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize Web Research Analyst with specialized instructions."""
        
        instructions = """
        You are a Web Research Analyst AI assistant specialized in comprehensive research and analysis using AI Foundry's native web search capabilities.
        
        Your core capabilities:
        1. **Deep Research**: Conduct thorough searches on any topic using your built-in web search
        2. **Data Analysis**: Analyze trends, patterns, and insights from gathered data
        3. **Competitive Analysis**: Research competitors, market positioning, and opportunities
        4. **Content Curation**: Find and curate relevant articles, resources, and references
        5. **Fact Verification**: Verify claims and cross-reference multiple sources
        6. **Industry Insights**: Provide context about industry trends and developments
        
        Your research methodology:
        - Use your native web search capabilities for comprehensive results
        - Cross-reference information from various sources
        - Prioritize authoritative and recent sources
        - Identify gaps in available information
        - Provide cited sources for all claims
        - Summarize complex information into actionable insights
        
        Output format:
        - Start with executive summary
        - Organize findings into clear sections
        - Include source citations
        - Highlight key insights and recommendations
        - Note any limitations or areas needing further research
        
        Always be thorough, accurate, and cite your sources using your built-in web search capabilities.
        """
        
        # Use AI Foundry's native web search capabilities (no explicit tools needed)
        tools = []
        
        super().__init__(
            project_client=project_client,
            agent_name="web_research_analyst",
            instructions=instructions,
            model=kwargs.get('model', 'gpt-4o'),
            tools=tools,
            agent_type="researcher"
        )
    
    def research_topic(self, topic: str, depth: str = "comprehensive") -> str:
        """
        Conduct research on a specific topic.
        
        Args:
            topic: The research topic
            depth: Research depth - "quick", "standard", or "comprehensive"
        
        Returns:
            Detailed research report
        """
        depth_instructions = {
            "quick": "Provide a concise overview with key points and 3-5 sources",
            "standard": "Conduct thorough research with detailed analysis and 8-10 sources", 
            "comprehensive": "Perform deep research with extensive analysis, multiple perspectives, and 15+ sources"
        }
        
        research_prompt = f"""
        Research Topic: {topic}
        
        Research Depth: {depth_instructions.get(depth, depth_instructions['standard'])}
        
        Please provide a comprehensive research report including:
        1. Executive Summary
        2. Key Findings
        3. Industry Context
        4. Trends and Patterns
        5. Competitive Landscape (if applicable)
        6. Recommendations
        7. Sources and References
        8. Areas for Further Research
        """
        
        return self.send_message(research_prompt)
    
    def competitive_analysis(self, company_or_product: str, competitors: List[str] = None) -> str:
        """
        Conduct competitive analysis.
        
        Args:
            company_or_product: Main subject for analysis
            competitors: Optional list of specific competitors to analyze
        
        Returns:
            Competitive analysis report
        """
        competitors_text = f"Focus on these specific competitors: {', '.join(competitors)}" if competitors else "Identify and analyze main competitors"
        
        analysis_prompt = f"""
        Competitive Analysis Request:
        
        Subject: {company_or_product}
        Competitors: {competitors_text}
        
        Please provide a detailed competitive analysis including:
        1. Market Overview
        2. Competitor Identification and Profiles
        3. Strengths and Weaknesses Analysis
        4. Market Positioning
        5. Pricing Strategies (if available)
        6. Product/Service Comparison
        7. Marketing and Messaging Analysis
        8. Market Share and Performance
        9. Opportunities and Threats
        10. Strategic Recommendations
        
        Include specific data points, metrics, and recent developments where available.
        """
        
        return self.send_message(analysis_prompt)
    
    def industry_trends_analysis(self, industry: str, timeframe: str = "current") -> str:
        """
        Analyze industry trends and developments.
        
        Args:
            industry: Industry to analyze
            timeframe: "current", "emerging", or "historical"
        
        Returns:
            Industry trends analysis
        """
        timeframe_focus = {
            "current": "Focus on current trends and recent developments (last 6-12 months)",
            "emerging": "Identify emerging trends and future predictions (next 2-5 years)",
            "historical": "Analyze historical trends and evolution over time"
        }
        
        trends_prompt = f"""
        Industry Trends Analysis:
        
        Industry: {industry}
        Timeframe: {timeframe_focus.get(timeframe, timeframe_focus['current'])}
        
        Please provide comprehensive industry analysis including:
        1. Industry Overview
        2. Key Trends and Patterns
        3. Market Drivers and Challenges
        4. Technology Impact
        5. Regulatory Environment
        6. Investment and Funding Trends
        7. Major Players and Market Dynamics
        8. Future Outlook and Predictions
        9. Opportunities for Innovation
        10. Strategic Implications
        
        Include specific examples, case studies, and data points where available.
        """
        
        return self.send_message(trends_prompt)
    
    def fact_check_and_verify(self, claims: List[str]) -> str:
        """
        Fact-check and verify specific claims.
        
        Args:
            claims: List of claims to verify
        
        Returns:
            Fact-checking report
        """
        claims_text = "\n".join([f"{i+1}. {claim}" for i, claim in enumerate(claims)])
        
        verification_prompt = f"""
        Fact-Checking Request:
        
        Please verify the following claims:
        {claims_text}
        
        For each claim, provide:
        1. Verification Status (Verified, Partially Verified, False, Insufficient Evidence)
        2. Evidence and Sources
        3. Context and Nuances
        4. Related Information
        5. Confidence Level
        
        Use authoritative sources and cross-reference information where possible.
        """
        
        return self.send_message(verification_prompt)
    
    def curate_resources(self, topic: str, resource_types: List[str] = None) -> str:
        """
        Curate relevant resources on a topic.
        
        Args:
            topic: Topic for resource curation
            resource_types: Types of resources - "articles", "tools", "courses", "books", etc.
        
        Returns:
            Curated resource list with descriptions
        """
        if resource_types is None:
            resource_types = ["articles", "tools", "guides", "reports"]
        
        resources_text = ", ".join(resource_types)
        
        curation_prompt = f"""
        Resource Curation Request:
        
        Topic: {topic}
        Resource Types: {resources_text}
        
        Please curate high-quality resources including:
        1. Top Articles and Publications
        2. Useful Tools and Platforms
        3. Educational Resources
        4. Industry Reports
        5. Expert Insights and Opinions
        6. Case Studies and Examples
        7. Community Resources
        8. Related Topics and Areas
        
        For each resource provide:
        - Title and Description
        - URL (if available)
        - Why it's valuable
        - Target audience
        - Key takeaways
        
        Prioritize recent, authoritative, and practical resources.
        """
        
        return self.send_message(curation_prompt)

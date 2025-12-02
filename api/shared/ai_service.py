"""
Azure OpenAI Service for SecAI Radar

Provides AI-powered features including:
- Natural language recommendations
- Gap explanations
- Report generation
- Evidence classification
"""

import os
from typing import List, Dict, Optional, Iterator
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionChunk

# Import Key Vault service for secure secret retrieval
try:
    from shared.key_vault import get_secret_from_key_vault_or_env
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    def get_secret_from_key_vault_or_env(secret_name: str, env_var_name: Optional[str] = None) -> Optional[str]:
        return os.getenv(env_var_name or secret_name)

class AzureOpenAIService:
    """Service for interacting with Azure OpenAI GPT models"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://zimax.cognitiveservices.azure.com/")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-5-chat")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-chat")
        
        # Get API key from Key Vault or environment variable
        self.api_key = get_secret_from_key_vault_or_env(
            secret_name="azure-openai-api-key",
            env_var_name="AZURE_OPENAI_API_KEY"
        )
        
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not self.api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY not found. Set it in Azure Key Vault (secret: 'azure-openai-api-key') "
                "or as environment variable AZURE_OPENAI_API_KEY"
            )
        
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        max_tokens: int = 16384,
        temperature: float = 1.0,
        top_p: float = 1.0,
    ):
        """
        Create a chat completion
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            
        Returns:
            Response object or stream iterator
        """
        response = self.client.chat.completions.create(
            stream=stream,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            model=self.deployment,
        )
        return response
    
    def generate_recommendation(
        self,
        control_id: str,
        control_title: str,
        gaps: List[Dict],
        tenant_tools: List[Dict],
        stream: bool = False
    ) -> str:
        """
        Generate AI-powered recommendations for a control based on gaps
        
        Args:
            control_id: Control identifier
            control_title: Control title/description
            gaps: List of hard/soft gaps with capability info
            tenant_tools: List of available tenant tools
            stream: Whether to stream the response
            
        Returns:
            Natural language recommendation text
        """
        system_prompt = """You are a security consultant expert specializing in Azure security assessments.
Your role is to provide clear, actionable recommendations for improving security control coverage.
Focus on practical, implementable advice that prioritizes tuning existing tools before suggesting new ones.
Be concise but thorough, explaining both what needs to be done and why."""
        
        hard_gaps = [g for g in gaps if "min" not in g]
        soft_gaps = [g for g in gaps if "min" in g]
        
        tools_summary = "\n".join([
            f"- {t.get('id', 'unknown')}: {t.get('name', '')} (Config Score: {t.get('configScore', 0):.1f})"
            for t in tenant_tools
        ])
        
        user_prompt = f"""Control: {control_id} - {control_title}

Gaps Identified:
{"Hard Gaps (missing capabilities): " + ", ".join([g.get('capabilityId', '') for g in hard_gaps]) if hard_gaps else "None"}
{"Soft Gaps (configuration issues): " + ", ".join([f"{g.get('capabilityId', '')} (current: {g.get('best', 0):.2f}, needed: {g.get('min', 0):.2f})" for g in soft_gaps]) if soft_gaps else "None"}

Available Tools:
{tools_summary}

Generate actionable recommendations for improving this control's coverage. Prioritize:
1. Tuning existing tools (raising ConfigScore)
2. Then consider adding new tools if gaps remain

Provide specific, actionable advice."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(
            messages=messages,
            stream=stream,
            temperature=0.7,
            max_tokens=2048
        )
        
        if stream:
            return response
        else:
            return response.choices[0].message.content
    
    def explain_gap(
        self,
        control_id: str,
        capability_id: str,
        gap_type: str,
        current_coverage: float,
        min_required: float,
        available_tools: List[str]
    ) -> str:
        """
        Generate natural language explanation for a specific gap
        
        Args:
            control_id: Control identifier
            capability_id: Capability that has a gap
            gap_type: 'hard' or 'soft'
            current_coverage: Current coverage score
            min_required: Minimum required coverage
            available_tools: List of tool IDs that could help
            
        Returns:
            Natural language explanation
        """
        system_prompt = """You are a security consultant explaining security control gaps to stakeholders.
Explain gaps in clear, non-technical language while being accurate and actionable."""
        
        gap_desc = "completely missing" if gap_type == "hard" else f"below required threshold (current: {current_coverage:.1%}, needed: {min_required:.1%})"
        
        user_prompt = f"""Control {control_id} has a {gap_type} gap for capability '{capability_id}'.

The capability is {gap_desc}.

Available tools that could address this: {', '.join(available_tools) if available_tools else 'None currently configured'}

Explain why this gap matters and what should be done to address it."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(
            messages=messages,
            stream=False,
            temperature=0.7,
            max_tokens=1024
        )
        
        return response.choices[0].message.content
    
    def generate_report_summary(
        self,
        tenant_id: str,
        summary_data: Dict,
        gaps_summary: List[Dict],
        include_usage: bool = False
    ) -> str | tuple[str, Optional[Dict]]:
        """
        Generate executive summary for an assessment report
        
        Args:
            tenant_id: Tenant identifier
            summary_data: Summary statistics by domain
            gaps_summary: List of gap details
            
        Returns:
            Executive summary text
        """
        system_prompt = """You are a security consultant writing an executive summary for a security assessment report.
Write in a professional, clear style suitable for security leadership and C-level executives.
Focus on key findings, risks, and recommended actions."""
        
        domains_summary = "\n".join([
            f"- {d.get('domain', '')}: {d.get('complete', 0)}/{d.get('total', 0)} controls complete"
            for d in summary_data.get('byDomain', [])
        ])
        
        total_gaps = len(gaps_summary)
        critical_gaps = len([g for g in gaps_summary if any(hg for hg in g.get('HardGaps', []))])
        
        user_prompt = f"""Generate an executive summary for security assessment of tenant '{tenant_id}'.

Domain Coverage:
{domains_summary}

Gap Summary:
- Total controls with gaps: {total_gaps}
- Controls with critical (hard) gaps: {critical_gaps}

Write a 3-4 paragraph executive summary covering:
1. Overall security posture assessment
2. Key strengths and gaps
3. Priority recommendations
4. Next steps"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(
            messages=messages,
            stream=False,
            temperature=0.8,
            max_tokens=2048
        )
        text = response.choices[0].message.content
        if include_usage:
            usage = getattr(response, "usage", None)
            return text, usage
        return text
    
    def classify_evidence(
        self,
        evidence_description: str,
        file_name: Optional[str] = None,
        include_usage: bool = False
    ) -> Dict[str, str] | tuple[Dict[str, str], Optional[Dict]]:
        """
        Classify evidence type and extract metadata
        
        Args:
            evidence_description: Description or content preview of evidence
            file_name: Optional file name
            
        Returns:
            Dict with classification and metadata
        """
        system_prompt = """You are a security assessment expert classifying evidence types.
Classify evidence into one of these categories:
- screenshot: Visual evidence (screenshots, diagrams)
- config_export: Configuration files or exports
- log: Log files or log exports
- policy: Policy documents or policy exports
- report: Assessment or audit reports
- other: Other types of evidence

Also identify:
- sensitivity_level: public, internal, confidential, restricted
- content_type: What the evidence contains (e.g., firewall rules, access logs, etc.)

Respond with JSON format."""
        
        user_prompt = f"""Classify this evidence:
Description: {evidence_description}
File: {file_name or 'N/A'}

Respond with JSON:
{{
    "category": "one of the categories above",
    "sensitivity_level": "one of the levels above",
    "content_type": "brief description",
    "confidence": 0.0-1.0
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(
            messages=messages,
            stream=False,
            temperature=0.3,
            max_tokens=512
        )
        
        import json
        try:
            content = response.choices[0].message.content
            # Extract JSON from response (might be wrapped in markdown)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
        except:
            parsed = {
                "category": "other",
                "sensitivity_level": "internal",
                "content_type": "unknown",
                "confidence": 0.0
            }
        if include_usage:
            usage = getattr(response, "usage", None)
            return parsed, usage
        return parsed
    
    def craft_visualization_prompt(
        self,
        user_intent: str,
        context_type: str = "assessment",
        assessment_data: Optional[Dict] = None,
        style: str = "diagram"
    ) -> Dict[str, str]:
        """
        Use Elena Bridges (Business Impact Strategist) agent to craft
        a contextually-aware visualization prompt.
        
        Elena excels at translating technical data into executive-ready
        visual communications.
        
        Args:
            user_intent: What the user wants to visualize
            context_type: Type of context (assessment, gaps, controls, tools)
            assessment_data: Optional assessment data for context
            style: Visualization style (diagram, infographic, chart, architecture)
            
        Returns:
            Dict with crafted prompt and metadata
        """
        # Elena Bridges - Business Impact Strategist system prompt
        elena_system_prompt = """You are Elena Bridges, the Business Impact Strategist for SecAI Radar.
You specialize in translating technical security findings into clear, executive-ready visualizations.

Your role is to craft the perfect visualization prompt that will generate:
- Professional, corporate-ready visuals
- Clear business context and impact messaging
- Logical information hierarchy
- Appropriate visual metaphors for security concepts

When crafting visualization prompts, you:
1. Understand the user's intent and the underlying data
2. Translate technical concepts into visual elements
3. Emphasize business impact and risk context
4. Ensure the visualization tells a clear story
5. Include specific layout, color, and style guidance

Output a detailed, actionable prompt for an AI image generator that will create
exactly what the executive stakeholders need to understand the security posture."""

        # Build context summary from assessment data
        context_summary = ""
        if assessment_data:
            if context_type == "assessment":
                summary = assessment_data.get("summary", {})
                by_domain = summary.get("byDomain", [])
                total_controls = summary.get("totalControls", 0)
                total_gaps = summary.get("totalGaps", 0)
                critical_gaps = summary.get("criticalGaps", 0)
                compliance_rate = ((total_controls - total_gaps) / total_controls * 100) if total_controls > 0 else 0
                
                domain_details = "\n".join([
                    f"  - {d.get('domain', 'Unknown')}: {d.get('complete', 0)}/{d.get('total', 0)} complete ({d.get('complete', 0) / d.get('total', 1) * 100:.0f}%)"
                    for d in by_domain
                ]) if by_domain else "  No domain data available"
                
                context_summary = f"""Assessment Context:
- Total Controls: {total_controls}
- Controls with Gaps: {total_gaps}
- Critical Gaps: {critical_gaps}
- Overall Compliance Rate: {compliance_rate:.0f}%

Domain Breakdown:
{domain_details}"""

            elif context_type == "gaps":
                gaps = assessment_data.get("gaps", [])
                hard_gap_count = sum(len(g.get("HardGaps", [])) for g in gaps)
                soft_gap_count = sum(len(g.get("SoftGaps", [])) for g in gaps)
                
                context_summary = f"""Gap Analysis Context:
- Total Controls with Gaps: {len(gaps)}
- Hard Gaps (missing capabilities): {hard_gap_count}
- Soft Gaps (configuration issues): {soft_gap_count}

Top affected controls: {', '.join([g.get('ControlID', 'Unknown')[:20] for g in gaps[:5]])}"""

            elif context_type == "tools":
                tools = assessment_data.get("tools", [])
                coverage = assessment_data.get("coverage", {})
                
                context_summary = f"""Tool Inventory Context:
- Total Tools Configured: {len(tools)}
- Overall Coverage: {coverage.get('overall', 0) * 100:.0f}%

Enabled Tools: {', '.join([t.get('name', t.get('id', 'Unknown'))[:20] for t in tools[:8]])}"""

        # Style-specific guidance
        style_guides = {
            "diagram": "Create a clear technical diagram with components, connections, and labels",
            "infographic": "Create an executive infographic with key metrics, icons, and visual hierarchy",
            "chart": "Create a data visualization chart suitable for board presentations",
            "architecture": "Create a system architecture diagram showing security layers and data flow"
        }
        
        user_prompt = f"""User wants to visualize: "{user_intent}"

Visualization Style Requested: {style} - {style_guides.get(style, style_guides['diagram'])}

{context_summary if context_summary else "No additional context provided."}

Craft a detailed prompt for an AI image generator (like Gemini) that will create
this visualization. Include:
1. Specific visual elements to include
2. Layout and composition guidance
3. Color scheme recommendations (professional, corporate-appropriate)
4. Text labels and annotations needed
5. Visual metaphors that will resonate with business stakeholders

Output ONLY the visualization prompt, ready to send to the image generator.
Do not include any preamble or explanation - just the crafted prompt."""

        messages = [
            {"role": "system", "content": elena_system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_completion(
            messages=messages,
            stream=False,
            temperature=0.8,  # Allow creativity
            max_tokens=1024
        )
        
        crafted_prompt = response.choices[0].message.content
        
        # Return structured response
        return {
            "crafted_prompt": crafted_prompt,
            "agent": "elena_bridges",
            "agent_role": "Business Impact Strategist",
            "style": style,
            "context_type": context_type,
            "original_intent": user_intent
        }
    
    def close(self):
        """Close the client connection"""
        if hasattr(self.client, 'close'):
            self.client.close()


# Singleton instance (lazy initialization)
_ai_service_instance: Optional[AzureOpenAIService] = None

def get_ai_service() -> AzureOpenAIService:
    """Get or create the AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        try:
            _ai_service_instance = AzureOpenAIService()
        except ValueError as e:
            # AI service not configured - return None or raise
            # For now, we'll allow it to be optional
            raise ValueError(f"AI service not available: {e}")
    return _ai_service_instance


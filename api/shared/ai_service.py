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
        gaps_summary: List[Dict]
    ) -> str:
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
        
        return response.choices[0].message.content
    
    def classify_evidence(
        self,
        evidence_description: str,
        file_name: Optional[str] = None
    ) -> Dict[str, str]:
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
            return json.loads(content)
        except:
            return {
                "category": "other",
                "sensitivity_level": "internal",
                "content_type": "unknown",
                "confidence": 0.0
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


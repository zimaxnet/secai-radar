"""
Content Safety Guardrails

Provides guardrails and content safety controls for agent interactions.
Implements input validation, output filtering, tool call authorization, and rate limiting.
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from shared.ai_service import get_ai_service

logger = logging.getLogger(__name__)


class GuardrailViolation(Exception):
    """Exception raised when a guardrail is violated"""
    def __init__(self, violation_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.violation_type = violation_type
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class GuardrailsService:
    """
    Service for enforcing guardrails and content safety.
    
    Provides:
    - Input validation (prompt injection detection)
    - Output filtering (PII, sensitive data)
    - Tool call authorization
    - Rate limiting per agent
    - Content safety checks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize guardrails service.
        
        Args:
            config_path: Optional path to guardrails configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize AI service for content safety checks
        try:
            self.ai_service = get_ai_service()
        except Exception as e:
            logger.warning(f"AI service not available for guardrails: {e}")
            self.ai_service = None
        
        # Rate limiting tracking
        self._rate_limit_tracker: Dict[str, List[datetime]] = defaultdict(list)
        
        # Tool authorization cache
        self._tool_authorizations: Dict[str, List[str]] = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load guardrails configuration"""
        default_config = {
            "input_validation": {
                "enabled": True,
                "prompt_injection_detection": True,
                "max_input_length": 10000
            },
            "output_filtering": {
                "enabled": True,
                "pii_detection": True,
                "sensitive_data_detection": True
            },
            "tool_authorization": {
                "enabled": True,
                "default_policy": "deny_all",
                "agent_tools": {}
            },
            "rate_limiting": {
                "enabled": True,
                "max_requests_per_minute": 60,
                "max_requests_per_hour": 1000
            },
            "content_safety": {
                "enabled": True,
                "check_output": True,
                "check_input": False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    # Merge with defaults
                    default_config.update(file_config)
            except Exception as e:
                logger.warning(f"Could not load guardrails config: {e}")
        
        return default_config
    
    def validate_input(
        self,
        agent_id: str,
        input_text: str,
        input_type: str = "prompt"
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate agent input for safety and compliance.
        
        Args:
            agent_id: Agent identifier
            input_text: Input text to validate
            input_type: Type of input (prompt, tool_parameter, etc.)
            
        Returns:
            Tuple of (is_valid, violation_message)
        """
        config = self.config.get("input_validation", {})
        if not config.get("enabled", True):
            return True, None
        
        # Check input length
        max_length = config.get("max_input_length", 10000)
        if len(input_text) > max_length:
            return False, f"Input exceeds maximum length of {max_length} characters"
        
        # Prompt injection detection
        if config.get("prompt_injection_detection", True):
            if self._detect_prompt_injection(input_text):
                return False, "Potential prompt injection detected"
        
        # Content safety check (if enabled)
        content_safety = self.config.get("content_safety", {})
        if content_safety.get("check_input", False):
            if not self._check_content_safety(input_text, "input"):
                return False, "Input failed content safety check"
        
        return True, None
    
    def filter_output(
        self,
        agent_id: str,
        output_text: str,
        output_type: str = "response"
    ) -> Tuple[str, List[str]]:
        """
        Filter agent output for PII and sensitive data.
        
        Args:
            agent_id: Agent identifier
            output_text: Output text to filter
            output_type: Type of output (response, tool_result, etc.)
            
        Returns:
            Tuple of (filtered_text, violations)
        """
        config = self.config.get("output_filtering", {})
        if not config.get("enabled", True):
            return output_text, []
        
        violations = []
        filtered_text = output_text
        
        # PII detection
        if config.get("pii_detection", True):
            pii_violations = self._detect_pii(output_text)
            if pii_violations:
                violations.extend(pii_violations)
                # Redact PII
                filtered_text = self._redact_pii(filtered_text)
        
        # Sensitive data detection
        if config.get("sensitive_data_detection", True):
            sensitive_violations = self._detect_sensitive_data(output_text)
            if sensitive_violations:
                violations.extend(sensitive_violations)
                # Redact sensitive data
                filtered_text = self._redact_sensitive_data(filtered_text)
        
        # Content safety check
        content_safety = self.config.get("content_safety", {})
        if content_safety.get("check_output", True):
            if not self._check_content_safety(output_text, "output"):
                violations.append("Content safety violation")
                filtered_text = "[Content filtered for safety]"
        
        return filtered_text, violations
    
    def authorize_tool_call(
        self,
        agent_id: str,
        tool_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if an agent is authorized to call a specific tool.
        
        Args:
            agent_id: Agent identifier
            tool_name: Name of the tool to call
            
        Returns:
            Tuple of (is_authorized, denial_reason)
        """
        config = self.config.get("tool_authorization", {})
        if not config.get("enabled", True):
            return True, None
        
        # Get agent's allowed tools
        agent_tools = config.get("agent_tools", {}).get(agent_id, [])
        default_policy = config.get("default_policy", "deny_all")
        
        # Check authorization
        if default_policy == "allow_all":
            return True, None
        elif default_policy == "deny_all":
            if tool_name in agent_tools:
                return True, None
            else:
                return False, f"Tool '{tool_name}' not authorized for agent '{agent_id}'"
        else:
            # Custom policy
            return True, None
    
    def check_rate_limit(
        self,
        agent_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if an agent has exceeded rate limits.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Tuple of (within_limit, violation_message)
        """
        config = self.config.get("rate_limiting", {})
        if not config.get("enabled", True):
            return True, None
        
        now = datetime.utcnow()
        requests = self._rate_limit_tracker[agent_id]
        
        # Remove old requests (older than 1 hour)
        requests = [r for r in requests if now - r < timedelta(hours=1)]
        self._rate_limit_tracker[agent_id] = requests
        
        # Check per-minute limit
        recent_minute = [r for r in requests if now - r < timedelta(minutes=1)]
        max_per_minute = config.get("max_requests_per_minute", 60)
        if len(recent_minute) >= max_per_minute:
            return False, f"Rate limit exceeded: {len(recent_minute)} requests in the last minute (limit: {max_per_minute})"
        
        # Check per-hour limit
        max_per_hour = config.get("max_requests_per_hour", 1000)
        if len(requests) >= max_per_hour:
            return False, f"Rate limit exceeded: {len(requests)} requests in the last hour (limit: {max_per_hour})"
        
        # Record this request
        requests.append(now)
        self._rate_limit_tracker[agent_id] = requests
        
        return True, None
    
    def _detect_prompt_injection(self, text: str) -> bool:
        """Detect potential prompt injection attempts"""
        # Common prompt injection patterns
        injection_patterns = [
            r"ignore\s+(previous|above|all)\s+(instructions|prompts|rules)",
            r"forget\s+(everything|all|previous)",
            r"you\s+are\s+now\s+(a|an)\s+",
            r"system\s*:\s*",
            r"<\|(system|user|assistant)\|>",
            r"\[INST\]",
            r"###\s*(system|instruction|prompt)",
        ]
        
        text_lower = text.lower()
        for pattern in injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _detect_pii(self, text: str) -> List[str]:
        """Detect personally identifiable information"""
        violations = []
        
        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            violations.append("Email address detected")
        
        # SSN pattern (US)
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            violations.append("SSN detected")
        
        # Credit card pattern
        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text):
            violations.append("Credit card number detected")
        
        # Phone number pattern
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            violations.append("Phone number detected")
        
        return violations
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        # Redact emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        
        # Redact SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
        
        # Redact credit cards
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD_REDACTED]', text)
        
        # Redact phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
        
        return text
    
    def _detect_sensitive_data(self, text: str) -> List[str]:
        """Detect sensitive data patterns"""
        violations = []
        
        # API keys pattern
        if re.search(r'(api[_-]?key|apikey)\s*[:=]\s*[\w-]+', text, re.IGNORECASE):
            violations.append("API key detected")
        
        # Password pattern
        if re.search(r'(password|passwd|pwd)\s*[:=]\s*\S+', text, re.IGNORECASE):
            violations.append("Password detected")
        
        # Access token pattern
        if re.search(r'(token|bearer)\s+[A-Za-z0-9_-]{20,}', text, re.IGNORECASE):
            violations.append("Access token detected")
        
        return violations
    
    def _redact_sensitive_data(self, text: str) -> str:
        """Redact sensitive data from text"""
        # Redact API keys
        text = re.sub(r'(api[_-]?key|apikey)\s*[:=]\s*[\w-]+', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
        
        # Redact passwords
        text = re.sub(r'(password|passwd|pwd)\s*[:=]\s*\S+', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
        
        # Redact tokens
        text = re.sub(r'(token|bearer)\s+[A-Za-z0-9_-]{20,}', r'\1 [REDACTED]', text, flags=re.IGNORECASE)
        
        return text
    
    def _check_content_safety(self, text: str, content_type: str) -> bool:
        """
        Check content safety using AI service.
        
        Args:
            text: Text to check
            content_type: Type of content (input, output)
            
        Returns:
            True if content is safe, False otherwise
        """
        if not self.ai_service:
            return True  # If AI service not available, allow by default
        
        try:
            system_prompt = """You are a content safety checker. Evaluate if the content is safe.

Unsafe content includes:
- Hate speech, harassment, or discrimination
- Violence or threats
- Sexual content
- Self-harm instructions
- Illegal activities

Respond with ONLY "SAFE" or "UNSAFE"."""
            
            user_prompt = f"Content to check ({content_type}):\n{text}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.ai_service.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return "SAFE" in result
        
        except Exception as e:
            logger.error(f"Error checking content safety: {e}")
            return True  # On error, allow by default


# Singleton instance
_guardrails_service: Optional[GuardrailsService] = None


def get_guardrails_service(config_path: Optional[str] = None) -> GuardrailsService:
    """Get or create the guardrails service instance"""
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService(config_path)
    return _guardrails_service


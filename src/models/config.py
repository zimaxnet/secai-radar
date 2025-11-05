"""
Model Configuration Loader

Loads and validates model configuration from config/models.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelRoleConfig:
    """Configuration for a specific model role"""
    provider: str
    deployment: str
    account: str
    resource_group: str
    subscription_id: str
    tenant_id: str
    parameters: Dict[str, Any]
    system_prompt: str
    endpoint: Optional[str] = None

    def __post_init__(self):
        """Build endpoint URL if not provided"""
        if not self.endpoint:
            # Azure OpenAI endpoint format
            self.endpoint = f"https://{self.account}.openai.azure.com"


@dataclass
class ModelConfig:
    """Complete model configuration"""
    roles: Dict[str, ModelRoleConfig]
    providers: Dict[str, Dict[str, Any]]
    fallbacks: Optional[Dict[str, ModelRoleConfig]] = None
    selection_strategy: str = "role_specific"


def load_model_config(config_path: Optional[Path] = None) -> ModelConfig:
    """
    Load model configuration from YAML file.
    
    Args:
        config_path: Path to models.yaml. If None, uses default location.
        
    Returns:
        ModelConfig object with loaded configuration
    """
    if config_path is None:
        # Default to config/models.yaml relative to project root
        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config" / "models.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Model config not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Load provider configurations
    providers = config_data.get("providers", {})
    
    # Load role configurations
    roles_config = config_data.get("roles", {})
    roles = {}
    
    for role_name, role_data in roles_config.items():
        roles[role_name] = ModelRoleConfig(
            provider=role_data["provider"],
            deployment=role_data["deployment"],
            account=role_data["account"],
            resource_group=role_data["resource_group"],
            subscription_id=role_data["subscription_id"],
            tenant_id=role_data["tenant_id"],
            parameters=role_data.get("parameters", {}),
            system_prompt=role_data.get("system_prompt", ""),
            endpoint=role_data.get("endpoint"),
        )
    
    # Load fallback configurations (optional)
    fallbacks_config = config_data.get("fallbacks", {})
    fallbacks = None
    if fallbacks_config:
        fallbacks = {}
        for role_name, fallback_data in fallbacks_config.items():
            fallbacks[role_name] = ModelRoleConfig(
                provider=fallback_data["provider"],
                deployment=fallback_data["deployment"],
                account=fallback_data["account"],
                resource_group=fallback_data.get("resource_group", ""),
                subscription_id=fallback_data.get("subscription_id", ""),
                tenant_id=fallback_data.get("tenant_id", ""),
                parameters=fallback_data.get("parameters", {}),
                system_prompt=fallback_data.get("system_prompt", ""),
                endpoint=fallback_data.get("endpoint"),
            )
    
    return ModelConfig(
        roles=roles,
        providers=providers,
        fallbacks=fallbacks,
        selection_strategy=config_data.get("selection_strategy", "role_specific"),
    )


def get_role_config(config: ModelConfig, role: str) -> ModelRoleConfig:
    """
    Get configuration for a specific role.
    
    Args:
        config: ModelConfig instance
        role: Role name (reasoning_model, classification_model, generation_model)
        
    Returns:
        ModelRoleConfig for the specified role
        
    Raises:
        KeyError: If role is not configured
    """
    if role not in config.roles:
        raise KeyError(f"Role '{role}' not configured. Available roles: {list(config.roles.keys())}")
    
    return config.roles[role]


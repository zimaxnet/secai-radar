"""
RBAC middleware for role-based access control
"""

from fastapi import HTTPException, status
from typing import List, Callable
from functools import wraps

# Role definitions
class Role:
    REGISTRY_ADMIN = "RegistryAdmin"
    POLICY_APPROVER = "PolicyApprover"
    EVIDENCE_VALIDATOR = "EvidenceValidator"
    VIEWER = "Viewer"
    AUTOMATION_OPERATOR = "AutomationOperator"


def require_role(allowed_roles: List[str]):
    """Decorator to require specific roles"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from kwargs (injected by dependency)
            user = kwargs.get("user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check roles (from token claims)
            user_roles = user.get("roles", [])
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_workspace_access(workspace_id_param: str = "workspace_id"):
    """Decorator to ensure user has access to workspace"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            workspace_id = kwargs.get(workspace_id_param)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check workspace membership (would query database)
            # For MVP, placeholder
            user_workspaces = user.get("workspaces", [])
            if workspace_id and workspace_id not in user_workspaces:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to workspace"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

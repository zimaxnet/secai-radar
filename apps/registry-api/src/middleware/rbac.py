"""
RBAC middleware for role-based access control (T-092).
Resolves workspace from query param workspace_id or header X-Workspace-Id;
enforces roles from workspace_members (DB) so all queries are workspace-scoped.
"""

from fastapi import HTTPException, status, Request, Depends
from typing import List, Callable
from functools import wraps
from sqlalchemy.orm import Session

# Role definitions
class Role:
    REGISTRY_ADMIN = "RegistryAdmin"
    POLICY_APPROVER = "PolicyApprover"
    EVIDENCE_VALIDATOR = "EvidenceValidator"
    VIEWER = "Viewer"
    AUTOMATION_OPERATOR = "AutomationOperator"


def _user_id_from_token(user: dict) -> str:
    """Extract user id from JWT (sub or oid)."""
    return str(user.get("sub") or user.get("oid") or "")


def require_role(allowed_roles: List[str]):
    """Decorator to require specific roles (from token claims). Use require_workspace_roles for DB-backed, workspace-scoped roles."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
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
    """Decorator to ensure user has access to workspace (legacy). Prefer get_workspace_context dependency."""
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
            user_workspaces = user.get("workspaces", [])
            if workspace_id and workspace_id not in user_workspaces:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to workspace"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def _get_workspace_context_dep(allowed_roles: List[str]):
    """Dependency: resolve workspace from query workspace_id or X-Workspace-Id; enforce membership and optional role. Returns {workspace_id, user_id, roles}."""
    from src.database import get_db
    from src.middleware.auth import get_current_user
    from src.repositories.workspace import get_workspace, get_user_roles_in_workspace

    async def dep(
        request: Request,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        workspace_id = request.query_params.get("workspace_id") or request.headers.get("X-Workspace-Id")
        if not workspace_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="workspace_id (query or X-Workspace-Id header) required")
        uid = _user_id_from_token(user)
        w = get_workspace(db, workspace_id)
        if not w:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        roles = get_user_roles_in_workspace(db, workspace_id, uid)
        if not roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to workspace")
        if allowed_roles and not any(r in roles for r in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires one of: {', '.join(allowed_roles)}")
        return {"workspace_id": workspace_id, "user_id": uid, "roles": roles}
    return dep


def require_workspace_roles(allowed_roles: List[str]):
    """Dependency factory for workspace-scoped RBAC. Pass to Depends(require_workspace_roles([Role.VIEWER, ...]))."""
    return _get_workspace_context_dep(allowed_roles)

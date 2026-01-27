"""
Unit tests for RBAC (T-092): workspace resolution and role enforcement.
"""

import pytest
from fastapi import Request
from unittest.mock import AsyncMock, MagicMock, patch

from src.middleware.rbac import Role, _user_id_from_token, require_workspace_roles


def test_role_constants():
    assert Role.REGISTRY_ADMIN == "RegistryAdmin"
    assert Role.POLICY_APPROVER == "PolicyApprover"
    assert Role.EVIDENCE_VALIDATOR == "EvidenceValidator"
    assert Role.VIEWER == "Viewer"
    assert Role.AUTOMATION_OPERATOR == "AutomationOperator"


def test_user_id_from_token_sub():
    assert _user_id_from_token({"sub": "user-123"}) == "user-123"


def test_user_id_from_token_oid():
    assert _user_id_from_token({"oid": "oid-456"}) == "oid-456"


def test_user_id_from_token_sub_preferred():
    assert _user_id_from_token({"sub": "a", "oid": "b"}) == "a"


def test_user_id_from_token_empty():
    assert _user_id_from_token({}) == ""


@pytest.mark.asyncio
async def test_require_workspace_roles_no_workspace_id_returns_400():
    from fastapi import HTTPException

    request = MagicMock(spec=Request)
    request.query_params = {}
    request.headers = {}
    user = {"sub": "u1"}
    db = MagicMock()

    dep = require_workspace_roles([])
    with pytest.raises(HTTPException) as exc_info:
        await dep(request=request, user=user, db=db)
    assert exc_info.value.status_code == 400
    assert "workspace_id" in (exc_info.value.detail or "")


@pytest.mark.asyncio
async def test_require_workspace_roles_workspace_not_found_returns_404():
    from src.middleware.rbac import _get_workspace_context_dep
    from fastapi import HTTPException

    request = MagicMock(spec=Request)
    request.query_params = {"workspace_id": "ws-1"}
    request.headers = {}
    user = {"sub": "u1"}
    db = MagicMock()

    with patch("src.repositories.workspace.get_workspace", return_value=None), \
         patch("src.repositories.workspace.get_user_roles_in_workspace"):
        dep = _get_workspace_context_dep([])
        with pytest.raises(HTTPException) as exc_info:
            await dep(request=request, user=user, db=db)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_require_workspace_roles_not_member_returns_403():
    from src.middleware.rbac import _get_workspace_context_dep
    from fastapi import HTTPException

    request = MagicMock(spec=Request)
    request.query_params = {"workspace_id": "ws-1"}
    request.headers = {}
    user = {"sub": "u1"}
    db = MagicMock()

    with patch("src.repositories.workspace.get_workspace", return_value={"workspace_id": "ws-1"}), \
         patch("src.repositories.workspace.get_user_roles_in_workspace", return_value=[]):
        dep = _get_workspace_context_dep([])
        with pytest.raises(HTTPException) as exc_info:
            await dep(request=request, user=user, db=db)
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_workspace_roles_member_with_role_returns_context():
    from src.middleware.rbac import _get_workspace_context_dep

    request = MagicMock(spec=Request)
    request.query_params = {"workspace_id": "ws-1"}
    request.headers = {}
    user = {"sub": "u1"}
    db = MagicMock()

    with patch("src.repositories.workspace.get_workspace", return_value={"workspace_id": "ws-1"}), \
         patch("src.repositories.workspace.get_user_roles_in_workspace", return_value=[Role.VIEWER]):
        dep = _get_workspace_context_dep([Role.VIEWER])
        ctx = await dep(request=request, user=user, db=db)
        assert ctx["workspace_id"] == "ws-1"
        assert ctx["user_id"] == "u1"
        assert Role.VIEWER in ctx["roles"]


@pytest.mark.asyncio
async def test_require_workspace_roles_member_without_required_role_returns_403():
    from src.middleware.rbac import _get_workspace_context_dep
    from fastapi import HTTPException

    request = MagicMock(spec=Request)
    request.query_params = {"workspace_id": "ws-1"}
    request.headers = {}
    user = {"sub": "u1"}
    db = MagicMock()

    with patch("src.repositories.workspace.get_workspace", return_value={"workspace_id": "ws-1"}), \
         patch("src.repositories.workspace.get_user_roles_in_workspace", return_value=[Role.VIEWER]):
        dep = _get_workspace_context_dep([Role.REGISTRY_ADMIN])
        with pytest.raises(HTTPException) as exc_info:
            await dep(request=request, user=user, db=db)
        assert exc_info.value.status_code == 403

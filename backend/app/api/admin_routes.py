from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.admin import require_admin
from app.schemas.admin_settings import (
    AdminSettingsResponse,
    ProviderUpdateRequest,
)
from app.services.admin_service import (
    admin_delete_document,
    delete_session,
    delete_user,
    get_all_documents,
    get_all_sessions,
    get_all_users,
    get_dashboard_stats,
    get_session_messages,
    reindex_document,
    update_user_role,
)
from app.services.settings_service import (
    SettingsService,
    get_admin_settings,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ── Dashboard ──────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_dashboard_stats(db)


# ── User Management ────────────────────────────────────────────────────────────

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_all_users(db)


@router.put("/users/{user_id}/promote")
def promote_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return update_user_role(db, user_id, "admin", current_user.id)


@router.put("/users/{user_id}/demote")
def demote_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return update_user_role(db, user_id, "user", current_user.id)


@router.delete("/users/{user_id}")
def remove_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"success": delete_user(db, user_id, current_user.id)}


# ── Document Management ────────────────────────────────────────────────────────

@router.get("/documents")
def documents(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_all_documents(db)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"success": admin_delete_document(db, document_id, current_user.id)}


@router.post("/documents/{document_id}/reindex")
def reindex(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"success": reindex_document(db, document_id, current_user.id)}


# ── Session Management ───────────────────────────────────────────────────────

@router.get("/sessions")
def sessions(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_all_sessions(db)


@router.get("/sessions/{session_id}")
def session_details(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_session_messages(db, session_id)


@router.delete("/sessions/{session_id}")
def remove_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"success": delete_session(db, session_id, current_user.id)}

# ── Logs ─────────────────────────────────────────────────────────────────────

@router.get("/logs")
def get_logs(
    current_user=Depends(require_admin),
):
    return {"message": "Logs available in Grafana Explore"}


# ── Settings ─────────────────────────────────────────────────────────────────

@router.get(
    "/settings",
    response_model=AdminSettingsResponse,
)
def settings(
    current_user=Depends(require_admin),
):
    return get_admin_settings()


@router.post("/settings/provider")
def update_provider(
    request: ProviderUpdateRequest,
    current_user=Depends(require_admin),
):
    SettingsService.set_provider(request.provider, request.model)
    return {"success": True, "provider": request.provider, "model": request.model}

@router.get("/providers")
def get_providers(
    current_user=Depends(require_admin),
):
    from app.llm.provider_manager import ProviderManager
    from app.services.settings_service import SettingsService
    
    provider_list = ProviderManager.list_providers()
    health_list = ProviderManager.health()
    metrics_list = ProviderManager.get_metrics()
    
    # Merge them
    merged = {}
    for p in provider_list:
        name = p["provider"]
        merged[name] = {
            "name": name,
            "configured": p["configured"],
            "active": p["active"],
            "streaming": True, # All current providers support streaming
            "status": "unhealthy",
            "requests": 0,
            "failures": 0,
            "latency_ms": 0,
            "model": SettingsService.get_model() if p["active"] else "default"
        }
    
    for h in health_list:
        if h["provider"] in merged:
            merged[h["provider"]]["status"] = h["status"]
            
    for m in metrics_list:
        if m["provider"] in merged:
            merged[m["provider"]]["requests"] = m["requests"]
            merged[m["provider"]]["failures"] = m["failures"]
            merged[m["provider"]]["latency_ms"] = m["average_latency_ms"]
            
    return {
        "active_provider": SettingsService.get_provider().lower(),
        "providers": list(merged.values()),
        "last_failover": ProviderManager.get_last_failover()
    }


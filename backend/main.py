from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Tenant, User, Number, Endpoint, Callflow, Lead, APIResponse

app = FastAPI(title="NovaPBX API", version="0.1.0")

# CORS for Vite dev server
frontend_origin = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test", response_model=APIResponse)
async def test():
    # Quick check that DB is reachable by listing collections
    try:
        _ = await db.list_collection_names()
        return APIResponse(success=True, message="OK", data={"db": True})
    except Exception as e:
        return APIResponse(success=False, message=f"DB error: {e}")


# Leads endpoint wired from the contact form
@app.post("/leads", response_model=APIResponse)
async def create_lead(payload: Lead):
    doc = await create_document("lead", payload.model_dump())
    return APIResponse(success=True, message="Lead captured", data={"id": doc.get("_id")})


# --- Multi-tenant foundations ---
@app.post("/tenants", response_model=APIResponse)
async def create_tenant(payload: Tenant):
    doc = await create_document("tenant", payload.model_dump())
    return APIResponse(success=True, message="Tenant created", data={"id": doc.get("_id")})


@app.get("/tenants", response_model=APIResponse)
async def list_tenants():
    items = await get_documents("tenant", {})
    return APIResponse(success=True, message="ok", data={"items": items})


@app.post("/users", response_model=APIResponse)
async def create_user(payload: User):
    doc = await create_document("user", payload.model_dump())
    return APIResponse(success=True, message="User created", data={"id": doc.get("_id")})


@app.get("/users", response_model=APIResponse)
async def list_users(tenant_id: str | None = None):
    filt = {"tenant_id": tenant_id} if tenant_id else {}
    items = await get_documents("user", filt)
    return APIResponse(success=True, message="ok", data={"items": items})


@app.post("/numbers", response_model=APIResponse)
async def create_number(payload: Number):
    doc = await create_document("number", payload.model_dump())
    return APIResponse(success=True, message="Number added", data={"id": doc.get("_id")})


@app.get("/numbers", response_model=APIResponse)
async def list_numbers(tenant_id: str | None = None):
    filt = {"tenant_id": tenant_id} if tenant_id else {}
    items = await get_documents("number", filt)
    return APIResponse(success=True, message="ok", data={"items": items})


@app.post("/endpoints", response_model=APIResponse)
async def create_endpoint(payload: Endpoint):
    doc = await create_document("endpoint", payload.model_dump())
    return APIResponse(success=True, message="Endpoint created", data={"id": doc.get("_id")})


@app.get("/endpoints", response_model=APIResponse)
async def list_endpoints(tenant_id: str | None = None):
    filt = {"tenant_id": tenant_id} if tenant_id else {}
    items = await get_documents("endpoint", filt)
    return APIResponse(success=True, message="ok", data={"items": items})


# Callflow builder primitives
@app.post("/callflows", response_model=APIResponse)
async def create_callflow(payload: Callflow):
    # Validate that entry_id exists within nodes
    node_ids = {n.id for n in payload.nodes}
    if payload.entry_id not in node_ids:
        raise HTTPException(status_code=400, detail="entry_id must exist in nodes")
    doc = await create_document("callflow", payload.model_dump())
    return APIResponse(success=True, message="Callflow created", data={"id": doc.get("_id")})


@app.get("/callflows", response_model=APIResponse)
async def list_callflows(tenant_id: str | None = None):
    filt = {"tenant_id": tenant_id} if tenant_id else {}
    items = await get_documents("callflow", filt)
    return APIResponse(success=True, message="ok", data={"items": items})

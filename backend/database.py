from __future__ import annotations

import os
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[DATABASE_NAME]
    return _db


# Expose db for convenience
db: AsyncIOMotorDatabase = get_db()


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    doc = {**data, "created_at": now, "updated_at": now}
    result = await db[collection_name].insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: int = 50,
    sort: Optional[List] = None,
) -> List[Dict[str, Any]]:
    q = filter_dict or {}
    cursor = db[collection_name].find(q)
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    items = []
    async for item in cursor:
        item["_id"] = str(item.get("_id"))
        items.append(item)
    return items

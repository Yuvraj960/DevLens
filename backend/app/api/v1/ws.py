import asyncio
import json
import uuid as _uuid
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import Job

router = APIRouter(tags=["WebSockets"])

TERMINAL_STATUSES = {"COMPLETE", "FAILED", "CANCELLED"}


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_websocket(websocket: WebSocket, job_id: str):
    await websocket.accept()
    r = None
    pubsub = None
    try:
        # --- H8 fix: Check if job already finished before subscribing ---
        try:
            job_uuid = _uuid.UUID(job_id)
        except ValueError:
            await websocket.send_text(json.dumps({"error": f"Invalid job_id: {job_id}"}))
            return

        async with AsyncSessionLocal() as session:
            stmt = select(Job).where(Job.id == job_uuid)
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()

        if job and job.status in TERMINAL_STATUSES:
            await websocket.send_text(json.dumps({
                "stage": job.stage or "Complete",
                "progress": job.progress or 100.0,
                "message": job.message or f"Job already {job.status.lower()}.",
                "status": job.status,
            }))
            return

        # --- Live subscription ---
        r = aioredis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        channel = f"job_channel:{job_id}"
        await pubsub.subscribe(channel)

        await websocket.send_text(json.dumps({
            "stage": job.stage if job else "Connected",
            "progress": job.progress if job else 0.0,
            "message": job.message if job else f"Connected to job stream {job_id}",
            "status": job.status if job else "IN_PROGRESS",
        }))

        while True:
            # Check for Redis messages with timeout
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"].decode("utf-8")
                await websocket.send_text(data)

                # Close socket when job complete or failed
                parsed = json.loads(data)
                if parsed.get("status") in TERMINAL_STATUSES:
                    break

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass
    finally:
        if pubsub:
            await pubsub.unsubscribe(f"job_channel:{job_id}")
            await pubsub.close()
        if r:
            await r.close()
        try:
            await websocket.close()
        except Exception:
            pass

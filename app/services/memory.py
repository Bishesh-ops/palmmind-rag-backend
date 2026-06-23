import json

import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def add_message_to_memory(session_id: str, role:str, content:str):
    key = f"chat_session:{session_id}"
    message = json.dumps({"role": role, "content": content})

    await redis_client.rpush(key, message)
    await redis_client.expire(key, 86400)

async def get_chat_history(session_id: str, limit: int = 6) -> list[dict]:
    key = f"chat_session:{session_id}"
    raw_messages = await redis_client.lrange(key, -limit, -1)
    return [json.loads(msg) for msg in raw_messages]

from elasticsearch import AsyncElasticsearch
from redis import Redis
from app.core.config import settings


async def get_elasticsearch() -> AsyncElasticsearch:
    es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
    try:
        yield es
    finally:
        await es.close()


async def get_redis() -> Redis:
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        redis.close()
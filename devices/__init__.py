
import json
import redis
import spin_store.settings as settings

pool = redis.ConnectionPool.from_url(settings.REDIS_URL)

__redis_instance = redis.Redis(connection_pool=pool)

def get_connection():
    return __redis_instance


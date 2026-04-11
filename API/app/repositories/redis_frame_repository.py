import redis
from .frame_repository import FrameRepository


class RedisFrameRepository(FrameRepository):

    def __init__(self, url="redis://localhost:6379/0", max_frames=10):
        self.redis = redis.Redis.from_url(url, decode_responses=True)
        self.max_frames = max_frames

    def save(self, camera_id: int, frame: str):
        key = f"camera:{camera_id}:frames"

        pipe = self.redis.pipeline()
        pipe.lpush(key, frame)
        pipe.ltrim(key, 0, self.max_frames - 1)
        pipe.execute()

    def get(self, camera_id: int):
        key = f"camera:{camera_id}:frames"
        return self.redis.lindex(key, 0)

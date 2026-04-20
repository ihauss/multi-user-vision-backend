import redis
from .frame_repository import FrameRepository


class RedisFrameRepository(FrameRepository):
    """
    Redis-based implementation of the FrameRepository.

    This repository stores frames in Redis using a list per camera:
        Key format: "camera:{camera_id}:frames"

    Behavior:
        - Frames are stored using LPUSH (newest at the head).
        - The list is trimmed to a maximum size (max_frames).
        - Retrieval returns the most recent frame.

    Suitable for:
        - Real-time applications
        - Multi-instance deployments
        - Scalable architectures

    Notes:
        - Uses Redis pipelines for atomic operations.
        - Frames are stored as strings (e.g., base64 encoded).
    """

    def __init__(self, url="redis://localhost:6379/0", max_frames=10):
        """
        Initialize Redis connection and configuration.

        Args:
            url (str): Redis connection URL.
            max_frames (int): Maximum number of frames to keep per camera.
        """
        # Create Redis client
        # decode_responses=True ensures returned values are strings (not bytes)
        self.redis = redis.Redis.from_url(url, decode_responses=True)

        # Maximum number of frames stored per camera
        self.max_frames = max_frames

    def save(self, camera_id: int, frame: str):
        """
        Store a frame in Redis.

        Args:
            camera_id (int): ID of the camera.
            frame (str): Encoded frame data.

        Behavior:
            - Inserts the new frame at the beginning of the list (LPUSH).
            - Trims the list to keep only the latest N frames.
            - Uses a pipeline to ensure atomicity and performance.
        """
        key = f"camera:{camera_id}:frames"

        # Use pipeline to group commands (atomic execution)
        pipe = self.redis.pipeline()

        # Add new frame to the head of the list
        pipe.lpush(key, frame)

        # Keep only the latest max_frames entries
        pipe.ltrim(key, 0, self.max_frames - 1)

        # Execute all commands
        pipe.execute()

    def get(self, camera_id: int):
        """
        Retrieve the latest frame for a given camera.

        Args:
            camera_id (int): ID of the camera.

        Returns:
            str or None:
                - Latest frame if available
                - None if no frame exists

        Behavior:
            - Reads the first element of the list (most recent frame).
            - Does NOT remove the frame from Redis.
        """
        key = f"camera:{camera_id}:frames"

        # Retrieve the most recent frame (index 0)
        return self.redis.lindex(key, 0)

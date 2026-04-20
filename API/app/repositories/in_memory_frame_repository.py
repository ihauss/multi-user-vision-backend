from .frame_repository import FrameRepository


class InMemoryFrameRepository(FrameRepository):
    """
    In-memory implementation of the FrameRepository.

    This repository stores frames in a Python dictionary where:
        - Key = camera_id
        - Value = list of frames (FIFO queue)

    Intended for:
        - Development
        - Testing
        - Non-production environments

    Notes:
        - Data is lost when the application restarts.
        - Not thread-safe (potential issues in multi-worker environments).
    """

    def __init__(self):
        """
        Initialize the in-memory storage.

        Structure:
            {
                camera_id: [frame1, frame2, ...]
            }
        """
        self.storage = {}

    def save(self, camera_id: int, frame: str):
        """
        Store a new frame for a given camera.

        Args:
            camera_id (int): ID of the camera.
            frame (str): Encoded frame data.

        Behavior:
            - Appends the frame to the list (queue behavior).
            - Creates a new list if the camera does not exist yet.
        """
        if camera_id not in self.storage:
            self.storage[camera_id] = []

        self.storage[camera_id].append(frame)

    def get(self, camera_id: int):
        """
        Retrieve the oldest frame for a given camera (FIFO).

        Args:
            camera_id (int): ID of the camera.

        Returns:
            str or None:
                - Oldest frame if available
                - None if no frame exists

        Behavior:
            - Removes and returns the first frame in the list.
            - Acts as a queue (FIFO).
        """
        if camera_id not in self.storage:
            return None

        return self.storage.get(camera_id).pop(0)

from abc import ABC, abstractmethod


class FrameRepository(ABC):
    """
    Abstract base class defining the interface for frame storage.

    This repository is responsible for storing and retrieving the latest
    frame associated with a camera.

    Implementations can vary depending on the backend:
        - In-memory (for development/testing)
        - Redis (for production / real-time systems)
        - Other storage systems if needed

    This abstraction allows decoupling business logic from storage details.
    """

    @abstractmethod
    def save(self, camera_id: int, frame: str):
        """
        Store a frame for a given camera.

        Args:
            camera_id (int): ID of the camera.
            frame (str): Encoded frame data (e.g., base64 image).

        Notes:
            - Implementations may overwrite previous frames or maintain a buffer.
            - Frame format is assumed to be pre-processed (e.g., encoded).
        """
        pass

    @abstractmethod
    def get(self, camera_id: int) -> str:
        """
        Retrieve the latest frame for a given camera.

        Args:
            camera_id (int): ID of the camera.

        Returns:
            str:
                - Encoded frame data if available
                - None or empty if no frame exists

        Notes:
            - Behavior depends on implementation (e.g., last frame, buffered frames).
        """
        pass

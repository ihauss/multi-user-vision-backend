from abc import ABC, abstractmethod

class FrameRepository(ABC):

    @abstractmethod
    def save(self, camera_id: int, frame: str):
        pass

    @abstractmethod
    def get(self, camera_id: int) -> str:
        pass


from app.repositories.in_memory_frame_repository import InMemoryFrameRepository


def test_save_and_get_frame():
    repo = InMemoryFrameRepository()

    repo.save(1, "frame1")

    assert repo.get(1) == "frame1"


def test_get_unknown_camera():
    repo = InMemoryFrameRepository()

    assert repo.get(999) is None

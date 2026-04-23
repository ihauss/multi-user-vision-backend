from pydantic import BaseModel


class FrameCreate(BaseModel):
    """
    Schema used to send a frame to the backend.

    Attributes:
        data (str): Encoded frame data (e.g., base64 string or raw string for testing).

    Notes:
        - In production, this typically represents an image encoded in base64.
        - The backend does not validate or decode the frame content.
        - Clients are responsible for proper encoding before sending.
    """
    data: str  # base64 or simple string for testing


class FrameResponse(BaseModel):
    """
    Schema used to return a frame to the client.

    Attributes:
        camera_id (int): ID of the camera.
        data (str): Encoded frame data.

    Notes:
        - Mirrors the format used in FrameCreate.
        - Returned data is typically the latest available frame.
    """
    camera_id: int
    data: str

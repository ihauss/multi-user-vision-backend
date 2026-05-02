import os
from dotenv import load_dotenv

if os.getenv("ENV") != "production":
    load_dotenv()

# Flag indicating whether Redis should be used as the frame/event storage backend.
# This allows switching between environments (e.g., local vs production).
USE_REDIS = os.getenv("USE_REDIS", "false").lower() in ("true", "1", "yes")

# Connection URL for Redis instance.
# Defaults to a local Redis server if not provided via environment variables.
REDIS_URL = os.getenv("REDIS_URL")

if USE_REDIS and not REDIS_URL:
    raise ValueError("REDIS_URL must be set when USE_REDIS is true")

# Secret key used for signing authentication tokens (e.g., JWT).
# This should NEVER be hardcoded in production.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")

# Algorithm used for signing JWT tokens.
# HS256 is a symmetric algorithm (same key used for signing and verification).
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Token expiration time (in minutes).
# Defines how long an access token remains valid after issuance.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

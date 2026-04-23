import os

# Flag indicating whether Redis should be used as the frame/event storage backend.
# This allows switching between environments (e.g., local vs production).
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"

# Connection URL for Redis instance.
# Defaults to a local Redis server if not provided via environment variables.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Secret key used for signing authentication tokens (e.g., JWT).
# This should NEVER be hardcoded in production.
SECRET_KEY = "super-secret-key"

# Algorithm used for signing JWT tokens.
# HS256 is a symmetric algorithm (same key used for signing and verification).
ALGORITHM = "HS256"

# Token expiration time (in minutes).
# Defines how long an access token remains valid after issuance.
ACCESS_TOKEN_EXPIRE_MINUTES = 60

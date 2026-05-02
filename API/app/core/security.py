from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict) -> str:
    """
    Generate a signed JWT access token.

    Args:
        data (dict): Payload to include in the token (e.g., {"sub": user_id}).

    Returns:
        str: Encoded JWT token.

    Workflow:
        1. Copy input payload to avoid mutation.
        2. Add expiration timestamp ("exp" claim).
        3. Sign and encode the token using the configured secret and algorithm.

    Notes:
        - The "exp" claim is required to enforce token expiration.
        - The SECRET_KEY must remain confidential.
        - The ALGORITHM defines how the token is signed (e.g., HS256).
    """
    to_encode = data.copy()

    # Define token issued time
    now = datetime.utcnow()

    # Define token expiration time
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add expiration claim to payload
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access"
    })

    # Encode and sign the JWT
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token (str): JWT token.

    Returns:
        dict: Decoded payload.

    Raises:
        jose.JWTError: If the token is invalid, expired, or tampered with.

    Notes:
        - Signature and expiration are verified automatically.
        - The calling function should handle exceptions appropriately.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")

    if not payload.get("sub"):
        raise ValueError("Invalid token payload")

    if payload.get("type") != "access":
        raise ValueError("Invalid token type")

    return payload


# Cryptographic context for password hashing and verification.
# Uses bcrypt to ensure strong protection against brute-force attacks.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Args:
        password (str): Raw user password.

    Returns:
        str: Secure hashed password.

    Notes:
        - Never store plaintext passwords.
        - Bcrypt automatically handles salting.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        password (str): Raw password provided by the user.
        hashed (str): Stored hashed password.

    Returns:
        bool:
            - True if the password matches
            - False otherwise

    Notes:
        - Uses secure comparison to prevent timing attacks.
    """
    return pwd_context.verify(password, hashed)

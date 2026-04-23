from passlib.context import CryptContext

# Cryptographic context used for hashing and verifying API keys.
# Bcrypt is chosen because it is a slow hashing algorithm, making brute-force attacks harder.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_api_key(api_key: str, hashed: str) -> bool:
    """
    Verify a raw API key against its hashed version.

    Args:
        api_key (str): Raw API key provided by the client (e.g., from Authorization header).
        hashed (str): Hashed API key stored in the database.

    Returns:
        bool:
            - True if the API key matches the stored hash
            - False otherwise

    Notes:
        - Uses bcrypt verification via passlib.
        - This function is secure against timing attacks thanks to the underlying implementation.
        - The raw API key is never stored or compared directly in plaintext.
    """
    return pwd_context.verify(api_key, hashed)

import base64
import pyotp

# 1) Convert hex seed -> Base32 seed
def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)      # convert hex -> bytes
    base32_seed = base64.b32encode(seed_bytes).decode("utf-8")
    return base32_seed

# 2) Generate a 6-digit TOTP code
def generate_totp_code(hex_seed: str) -> str:
    base32_seed = hex_to_base32(hex_seed)     # convert for TOTP use
    totp = pyotp.TOTP(base32_seed)            # SHA-1, 6 digits, 30s period
    return totp.now()                         # returns e.g. "123456"

# 3) Verify a TOTP code (±1 window = 30 seconds)
def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.verify(code, valid_window=valid_window)

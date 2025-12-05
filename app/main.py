import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# These are your helper modules in project root (/app)
from crypto_utils import load_private_key, decrypt_seed
from totp_utils import generate_totp_code, verify_totp_code

# Seed file location (shared by API + cron)
SEED_FILE_PATH = os.getenv("SEED_FILE_PATH", "/data/seed.txt")

app = FastAPI(title="PKI + TOTP 2FA Microservice")


# ---------- Request models ----------

class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# ---------- Health check (optional, but useful) ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- 1) POST /decrypt-seed ----------

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: DecryptRequest):
    """
    Accepts base64-encoded encrypted seed, decrypts using student private key,
    validates it, and stores hex seed at /data/seed.txt.
    """
    if not payload.encrypted_seed:
        raise HTTPException(status_code=400, detail="Missing encrypted_seed")

    try:
        # 1) Load student private key (mounted in /app)
        private_key = load_private_key("student_private.pem")

        # 2) Decrypt base64 string -> 64-char hex seed
        hex_seed = decrypt_seed(payload.encrypted_seed, private_key)
        hex_seed = hex_seed.strip()

        # Extra safety check
        if len(hex_seed) != 64:
            raise ValueError("Decrypted seed must be 64 characters")
        allowed = "0123456789abcdef"
        if any(c not in allowed for c in hex_seed):
            raise ValueError("Decrypted seed must be lowercase hex")

        # 3) Save to /data/seed.txt (volume)
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed + "\n")

        return {"status": "ok"}

    except Exception:
        # For security, do not leak internal error details
        raise HTTPException(status_code=500, detail="Decryption failed")


# ---------- 2) GET /generate-2fa ----------

@app.get("/generate-2fa")
def generate_2fa():
    """
    Reads hex seed from /data/seed.txt, generates current TOTP code,
    and returns {"code": "123456", "valid_for": seconds}.
    """
    # 1) Check seed file exists
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # 2) Read hex seed
    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()
        if not hex_seed:
            raise ValueError("Seed file is empty")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read seed")

    # 3) Generate TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate TOTP")

    # 4) Remaining validity seconds in this 30s window
    now = int(time.time())
    remaining = 30 - (now % 30)
    if remaining == 0:
        remaining = 30

    return {"code": code, "valid_for": remaining}


# ---------- 3) POST /verify-2fa ----------

@app.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):
    """
    Accepts {"code": "123456"}, validates against TOTP generated from seed
    with ±1 period (±30 seconds) tolerance.
    """
    if not payload.code:
        raise HTTPException(status_code=400, detail="Missing code")

    # 1) Check seed file exists
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    # 2) Read hex seed
    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()
        if not hex_seed:
            raise ValueError("Seed file is empty")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read seed")

    # 3) Verify TOTP code with ±1 period window
    try:
        is_valid = verify_totp_code(hex_seed, payload.code, valid_window=1)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to verify code")

    return {"valid": is_valid}

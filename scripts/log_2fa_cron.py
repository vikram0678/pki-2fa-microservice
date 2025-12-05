#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

import os
import sys
from datetime import datetime

# --- Make sure /app is in Python path so we can import totp_utils ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # /app/scripts
APP_ROOT = os.path.dirname(CURRENT_DIR)                       # /app
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from totp_utils import generate_totp_code

# Seed file location (inside container)
SEED_FILE_PATH = os.getenv("SEED_FILE_PATH", "/data/seed.txt")


def main():
    # 1) Read hex seed from /data/seed.txt
    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        if not hex_seed:
            # Seed file empty
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} - ERROR: Seed file is empty", file=sys.stderr)
            return

    except FileNotFoundError:
        # Seed not decrypted yet
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ERROR: Seed file not found", file=sys.stderr)
        return
    except Exception as e:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ERROR reading seed: {e}", file=sys.stderr)
        return

    # 2) Generate current TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - ERROR generating TOTP: {e}", file=sys.stderr)
        return

    # 3) Get current UTC timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 4) Print formatted line (cron will append this to /cron/last_code.txt)
    print(f"{timestamp} - 2FA Code: {code}")


if __name__ == "__main__":
    main()

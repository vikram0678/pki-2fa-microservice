from totp_utils import generate_totp_code, verify_totp_code

# Read decrypted hex seed (we created seed.txt earlier)
with open("seed.txt", "r") as f:
    hex_seed = f.read().strip()

# Generate OTP
code = generate_totp_code(hex_seed)
print("Current 2FA Code:", code)

# Verify OTP
print("Is this code valid?:", verify_totp_code(hex_seed, code))

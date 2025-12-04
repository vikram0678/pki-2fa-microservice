from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# 1) Load your private key from student_private.pem
def load_private_key(path: str):
      with open(path, "rb") as f:
            key_data = f.read()
      private_key = serialization.load_pem_private_key(
            key_data,
            password=None,  # no password
      )
      return private_key

# 2) Decrypt the encrypted seed
def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
      # Step 1: Base64 decode text -> bytes
      ciphertext = base64.b64decode(encrypted_seed_b64.strip())
      # print("Ciphertext length (bytes):", len(ciphertext))  # 👀 debug line
      # Step 2: Decrypt using RSA/OAEP + SHA256
      plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
            ),
      )

      # Step 3: Convert bytes -> string (expected hex)
      hex_seed = plaintext_bytes.decode("utf-8").strip()

      # Step 4: Validate it's a 64-character lowercase hex string
      if len(hex_seed) != 64:
            raise ValueError("Decrypted seed must be 64 characters")

      allowed = "0123456789abcdef"
      if any(c not in allowed for c in hex_seed):
            raise ValueError("Decrypted seed is not valid lowercase hex")

      # Step 5: Return final hex seed
      return hex_seed


def save_seed_to_file(hex_seed: str, path: str = "seed.txt"):
      """Save the decrypted hex seed to a file."""
      with open(path, "w") as f:
            f.write(hex_seed + "\n")

from crypto_utils import load_private_key, decrypt_seed, save_seed_to_file

# 1) Load your private key from file
private_key = load_private_key("student_private.pem")

# 2) Read the encrypted seed (base64 text) from file
with open("encrypted_seed.txt", "r") as f:
      encrypted_seed_b64 = f.read().strip()

# 3) Decrypt it
hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

# 4) Show result
print("Decrypted hex seed:", hex_seed)
print("Length:", len(hex_seed))

# 5) Save to local seed.txt (simulating /data/seed.txt)
save_seed_to_file(hex_seed, "seed.txt")
print("Saved decrypted seed to seed.txt")

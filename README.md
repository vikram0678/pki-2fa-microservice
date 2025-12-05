# PKI + TOTP 2FA Microservice

A secure authentication microservice using RSA-4096 encryption and TOTP-based two-factor authentication.

## Features

- RSA/OAEP-SHA256 encryption and decryption
- TOTP 2FA code generation (6 digits, 30-second validity)
- RESTful API with 3 endpoints
- Docker containerized with persistent storage
- Automated cron job logging every minute

## 🚀 How to Run (Docker)

### 1️⃣ Build and start the container

```bash
docker-compose up --build -d
```

### 2️⃣ Open API Docs

Visit in browser:

```
http://localhost:8080/docs
```

### 3️⃣ Test the endpoints

**Decrypt seed:**
```bash
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d '{"encrypted_seed": "YOUR_ENCRYPTED_SEED"}'
```

**Generate 2FA code:**
```bash
curl http://localhost:8080/generate-2fa
```

**Verify code:**
```bash
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "123456"}'
```

## 🌐 API Endpoints

### POST /decrypt-seed
Decrypts the encrypted seed and saves it to `/data/seed.txt`.

**Request:**
```json
{
  "encrypted_seed": "BASE64_STRING"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### GET /generate-2fa
Returns current 6-digit TOTP code + remaining seconds.

**Response:**
```json
{
  "code": "123456",
  "valid_for": 25
}
```

### POST /verify-2fa
Verifies whether the submitted code is valid.

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "valid": true
}
```

## ⏱ Cron Job (Every Minute)

The cron job runs:

```bash
python3 scripts/log_2fa_cron.py
```

And logs output like:

```
2025-12-05 08:56:06 - 2FA Code: 362510
```

Stored in:

```
/cron/last_code.txt
```

**View cron logs:**
```bash
docker compose exec app cat /cron/last_code.txt
```

## Technical Details

**Cryptography:**
- RSA 4096-bit keys
- RSA/OAEP with SHA-256 for encryption
- RSA-PSS with SHA-256 for signing
- TOTP with SHA-1, 30s period, 6 digits

**Docker:**
- Multi-stage build
- Port 8080 exposed
- Volumes: `/data` (seed), `/cron` (logs)
- UTC timezone

## Project Structure

```
pki-2fa-microservice/
│
├── app/main.py                 # API endpoints
├── scripts/log_2fa_cron.py     # Cron script
├── cron/2fa-cron               # Cron schedule (LF ending required)
│
├── crypto_utils.py             # RSA decrypt util
├── totp_utils.py               # TOTP generator & verifier
│
├── student_private.pem         # Student private key (required)
├── student_public.pem          # Student public key (required)
├── instructor_public.pem       # Instructor public key (required)
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitattributes
├── .gitignore

```

## Testing Persistence

**Restart container and verify seed persists:**
```bash
docker-compose restart
curl http://localhost:8080/generate-2fa
```

---

**Student ID:** 24P35A0534
**Repository:** https://github.com/vikram0678/pki-2fa-microservice
**Docker Image URL:** https://hub.docker.com/r/vikram034/pki-2fa

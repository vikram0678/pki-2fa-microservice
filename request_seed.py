import requests

student_id = "24P35A0534"
github_repo_url = "https://github.com/vikram0678/pki-2fa-microservice"

# Read your public key
with open("student_public.pem", "r") as f:
      public_key = f.read()

payload = {
      "student_id": student_id,
      "github_repo_url": github_repo_url,
      "public_key": public_key
}

api_url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

res = requests.post(api_url, json=payload)

print(res.json())

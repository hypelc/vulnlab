# VulnLab

A deliberately vulnerable Flask application for **local cybersecurity training only**.

## What it contains

- SQL injection-prone login
- IDOR / broken object-level authorization
- Reflected XSS
- Path traversal
- Broken authorization

The point is not to memorize payloads. Inspect the HTTP request in Burp, change one thing at a time, and explain why the application behaves differently.

## Run on Kali

```bash
unzip vulnlab.zip
cd vulnlab

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python app.py
```

Open:

```text
http://127.0.0.1:5000
```

To reset the database:

```text
http://127.0.0.1:5000/reset
```

## Suggested first session

1. Open the site normally.
2. Login as `alice / alice123`.
3. In Burp Proxy / HTTP history, identify:
   - method
   - path
   - headers
   - cookie
   - request body
   - response status
4. Send the login request to Repeater.
5. Inspect `/notes/1`, then change only the numeric ID.
6. Inspect `/search?q=test` and see where your input appears in the HTML response.
7. Inspect `/download?file=public.txt` and reason about how the server constructs the file path.
8. Inspect `/admin` and determine what the application uses to authorize the request.

## Notes template

For each endpoint, write:

```text
Endpoint:
Method:
Inputs controlled by the user:
Server behavior:
Security assumption:
What is wrong with that assumption:
Impact:
Secure fix:
```

## Safety

Run this application only on `127.0.0.1` inside your own VM. Do not expose it publicly, deploy it to Render/Vercel, or bind it to `0.0.0.0`.

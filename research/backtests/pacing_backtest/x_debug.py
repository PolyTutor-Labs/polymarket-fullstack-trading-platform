import sys, json, urllib.request, urllib.parse, urllib.error
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ENV = Path(__file__).resolve().parents[3] / ".env"
stored = None
for line in open(ENV, encoding='utf-8'):
    if line.startswith('X_BEARER_TOKEN='):
        stored = line.split('=', 1)[1].strip()
assert stored, "no X_BEARER_TOKEN in .env"


def hit(label, token, url):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as r:
            print(f"[{label}] HTTP {r.status} OK -> {json.loads(r.read())}")
    except urllib.error.HTTPError as e:
        print(f"[{label}] HTTP {e.code}  {e.read().decode()[:200]}")

U = 'https://api.x.com/2/users/by/username/elonmusk'
print("token length -> stored:", len(stored))
hit("decoded  /users", stored, U)
hit("decoded  /users (twitter.com)", stored, 'https://api.twitter.com/2/users/by/username/elonmusk')

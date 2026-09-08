import os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = service_account.Credentials.from_service_account_file(
    os.path.expanduser('~/.claude/google-service-account.json'),
    scopes=['https://www.googleapis.com/auth/drive'], subject=os.environ.get("GOOGLE_ACCOUNT_EMAIL"))
drive = build('drive','v3',credentials=creds)

OUT = (Path(__file__).resolve().parents[3] / 'research' / 'backtests' / 'pacing_backtest')
csv = OUT/'elon_backfill_2025-09_to_now.csv'
sz = csv.stat().st_size/1e6
print(f"uploading {csv.name} ({sz:.1f} MB)...")
meta = {'name':'elon_backfill_2025-09_to_now.csv'}
media = MediaFileUpload(str(csv), mimetype='text/csv', resumable=True)
f = drive.files().create(body=meta, media_body=media, fields='id,webViewLink', supportsAllDrives=True).execute()
print("DRIVE_LINK:", f['webViewLink'])
print("FILE_ID:", f['id'])

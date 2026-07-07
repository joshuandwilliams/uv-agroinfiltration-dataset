"""
Upload files from data/zenodo/ to a Zenodo draft record via the REST API.

Run this after saving the draft in the browser (at least one file must be
uploaded via the browser first to enable saving).

Usage:
    python scripts/upload_to_zenodo.py

You will be prompted for your Zenodo API token (Account → Applications →
Personal access tokens → deposit:write scope). Alternatively, set the
ZENODO_TOKEN environment variable before running.
"""

import getpass
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

RECORD_ID = "20493034"
BASE_URL = "https://zenodo.org"
ZENODO_DIR = Path(__file__).parent.parent / "data" / "zenodo"


def get_token() -> str:
    token = os.environ.get("ZENODO_TOKEN", "")
    if not token:
        token = getpass.getpass("Zenodo API token: ")
    return token.strip()


def get_bucket_url(token: str) -> str:
    r = requests.get(
        f"{BASE_URL}/api/deposit/depositions/{RECORD_ID}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["links"]["bucket"]


def existing_files(token: str) -> set:
    r = requests.get(
        f"{BASE_URL}/api/deposit/depositions/{RECORD_ID}/files",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    return {f["filename"] for f in r.json()}


def upload_file(bucket_url: str, filepath: Path, token: str) -> None:
    size_mb = filepath.stat().st_size / 1e6
    print(f"  Uploading {filepath.name} ({size_mb:.1f} MB)...", end=" ", flush=True)
    with open(filepath, "rb") as f:
        r = requests.put(
            f"{bucket_url}/{filepath.name}",
            data=f,
            headers={"Authorization": f"Bearer {token}"},
            timeout=3600,  # 1 hour — enough for large ZIPs
        )
    r.raise_for_status()
    print("done.")


def main() -> None:
    token = get_token()

    print(f"\nConnecting to Zenodo record {RECORD_ID}...")
    bucket_url = get_bucket_url(token)

    already_uploaded = existing_files(token)
    print(f"Already uploaded: {already_uploaded or 'none'}")

    files = sorted(f for f in ZENODO_DIR.iterdir() if f.is_file())
    to_upload = [f for f in files if f.name not in already_uploaded]

    if not to_upload:
        print("All files already uploaded.")
        return

    print(f"\nFiles to upload ({len(to_upload)}):")
    for f in to_upload:
        print(f"  {f.name}  ({f.stat().st_size / 1e6:.1f} MB)")

    print()
    for filepath in to_upload:
        upload_file(bucket_url, filepath, token)

    print(f"\nAll {len(to_upload)} file(s) uploaded successfully.")


if __name__ == "__main__":
    main()

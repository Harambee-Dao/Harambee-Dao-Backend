#!/usr/bin/env python3
"""
Simple demo client that calls the backend /api/testall endpoint.
Usage:
    python backend/api_demo.py --base-url http://127.0.0.1:8000
"""
import argparse
import sys
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    url = f"{args.base_url}/api/testall"
    try:
        r = requests.get(url, timeout=10)
        print(f"GET {url} -> {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"Error calling {url}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

import json
import zipfile
from io import BytesIO
from urllib.request import urlopen
import requests
import os
from datetime import datetime, timedelta

NVD_FEED_URL = "https://nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-recent.json.zip"
OSV_FEED_URL = "https://api.osv.dev/v1/querybatch"

def fetch_nvd_cves():
    try:
        resp = urlopen(NVD_FEED_URL)
        with zipfile.ZipFile(BytesIO(resp.read())) as zf:
            data = json.loads(zf.open("nvdcve-1.0-recent.json").read())
        return data.get("CVE_Items", [])
    except Exception as e:
        print(f"Error fetching NVD feed: {e}")
        return []

def fetch_osv_cves(days=1):
    try:
        since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        payload = {
            "queries": [{"published": since}]
        }
        response = requests.post(OSV_FEED_URL, json=payload, timeout=10)
        if response.ok:
            return response.json().get("results", [])
        else:
            return []
    except Exception as e:
        print(f"Error fetching OSV feed: {e}")
        return []

def get_latest_cves(limit=10, source="nvd"):
    if source == "nvd":
        cves = fetch_nvd_cves()
        sorted_cves = sorted(cves, key=lambda x: x.get("publishedDate", ""), reverse=True)
        return sorted_cves[:limit]
    else:
        osv = fetch_osv_cves()
        return osv[:limit]

if __name__ == "__main__":
    data = get_latest_cves(limit=5)
    for cve in data:
        cve_id = cve["cve"]["CVE_data_meta"]["ID"]
        desc = cve["cve"]["description"]["description_data"][0]["value"]
        print(f"[+] {cve_id}: {desc[:100]}...")

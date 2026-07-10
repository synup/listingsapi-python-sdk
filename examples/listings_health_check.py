"""Listings health check: Run a full listings audit with one workflow call.

Uses client.workflows.listings_health_audit() to check premium listings,
voice listings, duplicates, and connection status in a single pass.
Great for a nightly audit or pre-meeting dashboard refresh.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python listings_health_check.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

LOCATION_ID = 16808  # Replace with your location ID

# Run the audit
audit = client.workflows.listings_health_audit(LOCATION_ID)

# --- Health score ---
print(f"=== Listings Health Audit (Location {LOCATION_ID}) ===")
print(f"  Health score: {getattr(audit, 'health_score', 'N/A')}%")
print(f"  Synced:       {getattr(audit, 'synced_count', 'N/A')}")
print(f"  Issues:       {getattr(audit, 'issue_count', 'N/A')}")

# --- Issues detail ---
issues = getattr(audit, "issues", []) or []
if issues:
    print(f"\n=== Sync Issues ({len(issues)}) ===")
    for item in issues:
        if isinstance(item, dict):
            print(f"  [{item.get('syncStatus', '?')}] {item.get('site', 'Unknown')}")

# --- Duplicates ---
dupes = getattr(audit, "duplicates", []) or []
if dupes:
    print(f"\n=== Duplicates Found ({len(dupes)}) ===")
    for dup in dupes[:10]:
        if isinstance(dup, dict):
            print(f"  {dup.get('site', '?')}: {dup.get('title', dup.get('name', 'N/A'))}")
else:
    print("\n  No duplicate listings found.")

# --- Voice coverage ---
voice = getattr(audit, "voice", []) or []
print(f"\n=== Voice Listings ({len(voice)}) ===")
for v in voice:
    if isinstance(v, dict):
        print(f"  {v.get('site', v.get('assistant', 'Unknown'))}")

# --- Connection status ---
conn = getattr(audit, "connection_status", {})
print("\n=== Connection Status ===")
if isinstance(conn, dict):
    for key, val in conn.items():
        print(f"  {key}: {val}")
elif conn:
    print(f"  {conn}")

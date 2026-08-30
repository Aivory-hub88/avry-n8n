#!/usr/bin/env python3
"""Export the native-bridge n8n workflows.

As of 2026-08-30 these exports should need NO redaction: the bridge secret
moved out of the "Check Bridge Secret" node parameter and into the Webhook
node's headerAuth credential, so the definitions no longer carry it. The
redaction pass is kept as a safety net -- if it ever reports having replaced
something, a secret has crept back into a workflow parameter and that is the
bug to fix, not something to accept.

Credential *references* (id + name) are kept: they name n8n's own credential
store entries, which is structure, not secret material.
"""
import json, os, re, sys, urllib.request

OUT_DIR = sys.argv[1]
# The live native-bridge workflows. "Native Customer Service Bridge"
# (Q6ivz00vrr4hoA3x) is deliberately absent: it is archived, so the API
# refuses to update it and it cannot run.
WORKFLOW_IDS = [
    "ebaq7yFRfYdrL3gT",  # Native Leads Qualifier Bridge
    "Dgmai5aN8y1qRdyv",  # Native Finance Invoice Ops Bridge
    "MGg4Gtb6eH7TNt5j",  # Native Office Assistant Bridge
]


def api_key():
    with open("/home/ubuntu/AVRY-V2-Main/.env") as f:
        for line in f:
            if line.startswith("N8N_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("N8N_API_KEY not found")


def env_secrets():
    """Every value from the bridge's own .env, longest first so a value that
    contains another is replaced before its substring is."""
    out = {}
    try:
        with open("/home/ubuntu/aivory-native-bridge/.env") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    v = v.strip()
                    if len(v) >= 12:
                        out[v] = k.strip()
    except FileNotFoundError:
        pass
    return dict(sorted(out.items(), key=lambda kv: -len(kv[0])))


KEY = api_key()
SECRETS = env_secrets()


def fetch(wid):
    r = urllib.request.Request(
        f"http://127.0.0.1:5678/api/v1/workflows/{wid}",
        headers={"X-N8N-API-KEY": KEY},
    )
    with urllib.request.urlopen(r, timeout=40) as resp:
        return json.loads(resp.read())


os.makedirs(OUT_DIR, exist_ok=True)
for wid in WORKFLOW_IDS:
    wf = fetch(wid)
    # Drop instance-local bookkeeping that only creates diff noise.
    for k in ("createdAt", "updatedAt", "versionId", "triggerCount", "shared", "meta"):
        wf.pop(k, None)
    blob = json.dumps(wf, indent=2, sort_keys=True)

    for value, name in SECRETS.items():
        if value in blob:
            blob = blob.replace(value, f"<<REDACTED:{name}>>")
            print(f"  redacted {name}")

    # Deliberately EXCLUDES dashes: n8n node ids are UUIDs, which are
    # structure, not secrets. A real secret here is an unbroken 32+ char run.
    leftovers = [
        m for m in re.findall(r'[A-Za-z0-9]{32,}', blob)
        if re.search(r'\d', m) and re.search(r'[a-z]', m)
    ]
    if leftovers:
        print("  REFUSING TO WRITE — possible unredacted secret(s):", leftovers[:3])
        sys.exit(1)

    path = os.path.join(OUT_DIR, f"{wf['name'].lower().replace(' ', '-')}.json")
    with open(path, "w") as f:
        f.write(blob + "\n")
    print(f"  wrote {path} ({len(wf['nodes'])} nodes)")

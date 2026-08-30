# n8n workflows — native bridge

Exports of the live workflows behind Cerveau's native toolkits. Each agent
type has one webhook; every tool ("action") in that agent's bridge module
posts to it and the workflow branches internally on `action`.

Regenerate with `export.py <output-dir>` on the VPS.

## These exports carry no secrets — and that is enforced

Until 2026-08-30 the bridge shared secret sat as a **literal `rightValue`** in
each workflow's "Check Bridge Secret" IF node, so a raw export was a live
credential and the committed copy had to be redacted and was not importable.

That node is gone. Authentication is now the Webhook node's own `headerAuth`,
backed by a shared `httpHeaderAuth` credential ("Aivory Bridge Secret") held
in n8n's credential store. Two gains: the secret is out of the definition, and
an unauthenticated call is rejected by the webhook itself, before any node
runs, rather than one node into the flow.

`export.py` still runs a redaction pass. It should never fire. **If it reports
having redacted something, a secret has crept back into a workflow parameter —
that is the bug, not something to accept.** It also refuses to write if any
unbroken 32+ character alphanumeric run survives.

Node UUIDs are kept: structure, not secrets.

## Not exported

`Native Customer Service Bridge` (`Q6ivz00vrr4hoA3x`) is **archived**. The
public API refuses to update an archived workflow, so it still carries the old
literal secret in its definition and could not be migrated with the others. It
cannot run, so this is a disclosure concern rather than a live auth path —
worth resolving by unarchiving to patch it, or deleting it outright if it is
genuinely retired.

## Credential policy

- **Tenant credentials never enter n8n.** Toolkit calls go through Composio
  with the tenant's `user_id`; per-tenant mail credentials live encrypted in
  Postgres and are used by the bridge, not by an n8n node.
- **Aivory's own infrastructure credentials** (the `Aivory Postgres (native
  ops)` connection, provider API keys) belong in n8n's credential store —
  that is what it is for.
- **Nothing belongs in a node parameter.** That was the actual defect here.

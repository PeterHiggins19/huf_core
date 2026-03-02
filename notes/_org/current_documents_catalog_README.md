# Auto-generate current-documents catalog (HUF)

This patch adds a script that generates:

- `docs/current_documents.md` (public catalog page)
- `notes/_org/current_documents_orphans.md` (audit report: current docs that have **no rendered link** in docs pages)

Inputs:
- `notes/_org/doc_manifest.json`
- `docs/**/*.md` (to detect whether a current document is linked from any rendered doc page)

Policy enforced:
- Anything under `notes/current_documents/**` is authoritative.
- Rendered docs pages should link to authoritative sources using GitHub URLs.
- Wiki pages are not replaced automatically.

Created: 2026-03-02

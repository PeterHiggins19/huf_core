\
#!/usr/bin/env python
"""
Generate docs/current_documents.md from notes/_org/doc_manifest.json
and flag any current document without a public rendered link.

What counts as a "current document":
- any manifest entry whose canonical_path starts with:
  - notes/current_documents/staged/
  - notes/current_documents/inbox/

What counts as a "public rendered link":
- any occurrence in docs/**/*.md of either:
  - the exact canonical_path (relative), OR
  - a GitHub blob URL that ends with the canonical_path, OR
  - the file basename (fallback) as part of a URL or markdown link

Outputs:
- docs/current_documents.md
- notes/_org/current_documents_orphans.md

Dry-run by default; use --write to write files.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_REPO_URL = "https://github.com/PeterHiggins19/huf_core"
DEFAULT_BRANCH = "main"

MANIFEST = Path("notes/_org/doc_manifest.json")
DOCS_DIR = Path("docs")

OUT_PAGE = DOCS_DIR / "current_documents.md"
OUT_ORPHANS = Path("notes/_org/current_documents_orphans.md")

CURRENT_PREFIXES = (
    "notes/current_documents/staged/",
    "notes/current_documents/inbox/",
)

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

@dataclass
class Doc:
    doc_id: str
    canonical_path: str
    title: str
    lane: Optional[str]
    status: Optional[str]
    doc_version: Optional[str]

def gh_blob(repo_url: str, branch: str, rel_path: str) -> str:
    return f"{repo_url}/blob/{branch}/{rel_path}"

def load_manifest(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))

def collect_docs(manifest: Dict) -> List[Doc]:
    out: List[Doc] = []
    for d in manifest.get("documents", []):
        canon = d.get("canonical_path") or d.get("source_file") or ""
        if not isinstance(canon, str):
            continue
        if canon.startswith(CURRENT_PREFIXES):
            out.append(
                Doc(
                    doc_id=str(d.get("doc_id", "")),
                    canonical_path=canon,
                    title=str(d.get("title", "")) or Path(canon).stem,
                    lane=d.get("lane"),
                    status=d.get("status"),
                    doc_version=d.get("doc_version"),
                )
            )
    return out

def load_docs_corpus(docs_dir: Path) -> str:
    parts = []
    for p in sorted(docs_dir.rglob("*.md")):
        try:
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
    return "\n\n".join(parts)

def is_linked(corpus: str, doc: Doc, repo_url: str, branch: str) -> bool:
    canon = doc.canonical_path
    base = Path(canon).name

    if canon in corpus:
        return True

    if gh_blob(repo_url, branch, canon) in corpus:
        return True

    if re.search(re.escape(canon) + r"(\b|[\)#])", corpus):
        return True

    # Basename fallback (only count if appears inside a markdown link target or URL)
    for m in LINK_RE.finditer(corpus):
        target = m.group(1)
        if base in target:
            return True

    return False

def group_key(doc_id: str) -> Tuple[str, str, str]:
    parts = doc_id.split(".")
    if len(parts) >= 5 and parts[0] == "HUF":
        return parts[1], parts[2], parts[3]
    return "UNKNOWN", "UNKNOWN", "UNKNOWN"

def render_page(docs: List[Doc], repo_url: str, branch: str) -> str:
    rows = []
    for d in sorted(docs, key=lambda x: (group_key(x.doc_id), x.doc_id)):
        url = gh_blob(repo_url, branch, d.canonical_path)
        _, domain, dtype = group_key(d.doc_id)
        rows.append(
            f"| {domain} | {dtype} | `{d.doc_id}` | {d.status or ''} | {d.doc_version or ''} | {url} |"
        )

    return "\n".join(
        [
            "HUF-DOC: HUF.REL.DOCS.PAGE.CURRENT_DOCUMENTS | HUF:1.1.8 | DOC:v0.2.0 | STATUS:release | LANE:release | RO:Peter Higgins",
            "CODES: DOCS, CURRENT | ART: CM, AS, TR, EB | EVID:E1 | POSTURE:OP | WEIGHTS: OP=0.80 TOOL=0.20 PEER=0.00 | CAP: OP_MIN=0.51 TOOL_MAX=0.49 | CANON:docs/current_documents.md",
            "",
            "# Current Documents (authoritative)",
            "",
            "Policy: anything under `notes/current_documents/**` is authoritative.",
            "The public docs site contains rendered views for navigation and readability.",
            "",
            f"- Repo: {repo_url}",
            f"- Browse current documents: {repo_url}/tree/{branch}/notes/current_documents",
            "",
            "## Catalog",
            "",
            "| Domain | Type | Doc ID | Status | Doc ver | Current source-of-truth (GitHub) |",
            "|---|---|---|---|---|---|",
            *rows,
            "",
            "## Orphans",
            "",
            "An **orphan** is a current document that is not linked from any rendered page under `docs/`.",
            "See: `notes/_org/current_documents_orphans.md` for the audit report.",
            "",
        ]
    ) + "\n"

def render_orphans(orphans: List[Doc], repo_url: str, branch: str) -> str:
    lines = [
        "# Current documents orphan report",
        "",
        "These files are authoritative under `notes/current_documents/**` but are **not linked** from any rendered page under `docs/`.",
        "",
        f"Generated from: {MANIFEST.as_posix()}",
        "",
        "| Doc ID | Domain | Type | Status | Doc ver | Current source-of-truth | Suggested action |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in sorted(orphans, key=lambda x: x.doc_id):
        _, domain, dtype = group_key(d.doc_id)
        url = gh_blob(repo_url, branch, d.canonical_path)
        action = "Add link from a relevant docs page (books/index.md, partners, cases), or create a rendered view under docs/."
        lines.append(f"| `{d.doc_id}` | {domain} | {dtype} | {d.status or ''} | {d.doc_version or ''} | {url} | {action} |")
    lines.append("")
    return "\n".join(lines)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    ap.add_argument("--branch", default=DEFAULT_BRANCH)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--fail-on-orphans", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.exists():
        raise SystemExit(f"Missing {MANIFEST}. Run doc_inventory.py first.")

    manifest = load_manifest(MANIFEST)
    current_docs = collect_docs(manifest)

    corpus = load_docs_corpus(DOCS_DIR) if DOCS_DIR.exists() else ""
    orphans = [d for d in current_docs if not is_linked(corpus, d, args.repo_url, args.branch)]

    page = render_page(current_docs, args.repo_url, args.branch)
    orphan_report = render_orphans(orphans, args.repo_url, args.branch)

    print(f"[current_catalog] current_docs={len(current_docs)}")
    print(f"[current_catalog] orphans={len(orphans)}")

    if not args.write:
        print("[current_catalog] dry-run; use --write to write outputs")
        return 1 if (args.fail_on_orphans and orphans) else 0

    OUT_PAGE.parent.mkdir(parents=True, exist_ok=True)
    OUT_PAGE.write_text(page, encoding="utf-8", newline="\n")

    OUT_ORPHANS.parent.mkdir(parents=True, exist_ok=True)
    OUT_ORPHANS.write_text(orphan_report, encoding="utf-8", newline="\n")

    print(f"[current_catalog] wrote: {OUT_PAGE.as_posix()}")
    print(f"[current_catalog] wrote: {OUT_ORPHANS.as_posix()}")

    return 1 if (args.fail_on_orphans and orphans) else 0

if __name__ == "__main__":
    raise SystemExit(main())
